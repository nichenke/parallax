"""
Reverse LLM-as-judge scorer for reviewer precision.

Strategy: for each finding the reviewer actually produced, ask a judge model
"is this finding genuine — real, document-visible, and not a false positive?"
Returns precision (genuine / total_findings) as the score value.

Direction is REVERSED from llm_judge_match (which asks "did the reviewer find
this expected finding?"). Here we ask "is the reviewer's finding real?"

This dissolves the genuine-difference problem: we stop asking "did you find
what we expected?" and start asking "are your findings real?"

Key constraint (ADR-007): pass the FULL document to the judge — never truncate.
Findings may reference any part of the document.
"""
import asyncio
import re
from inspect_ai.model import get_model, ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, scorer, mean

from evals.utils.output_parser import parse_review_output


_JUDGE_SYSTEM = """\
You are evaluating whether an AI design reviewer's finding is genuine.

A finding is GENUINE if it identifies a real design gap or flaw visible in the provided document.

GENUINE includes:
- Undefined or vague terms in acceptance criteria — undefined terms are design gaps regardless of whether the vagueness is intentional
- Requirements that specify reporting a problem but not what action follows — reporting is not enforcement; missing enforcement is a genuine gap
- Findings that challenge whether a document's stated assumption is well-founded — questioning assumptions is legitimate design review, not a hallucinated constraint
- Real ambiguities that competent implementers would reasonably interpret differently

A finding is NOT_GENUINE if it falls into any of these false positive categories:
- Implementation detail: a coding or operational choice, not a design flaw
- Hallucinated constraint: references requirements or assumptions not present in the document — verify carefully against the full document before claiming something is absent
- Style preference: subjective formatting, naming, or structural preference with no design impact
- Hypothetical future concern: speculates about future requirements not relevant to the current design
- Duplicate: substantively the same flaw already identified in another finding
- Context-dependent: requires external knowledge (project history, MEMORY.md, prior sessions) to evaluate — cannot be assessed from the document alone

Answer with exactly GENUINE or NOT_GENUINE on the first line, followed by one sentence of reasoning.
Do not add any other text before GENUINE or NOT_GENUINE."""

_JUDGE_TEMPLATE = """\
Finding to evaluate:
  Title: {title}
  Issue: {issue}
  Severity: {severity}

Source document (evaluate the finding against this document only):
{doc_content}

Is this finding GENUINE or NOT_GENUINE?"""

# G-Eval variant: reasoning-first prompting (chain-of-thought before verdict).
# Forces the model to locate evidence in the document and apply each false-positive
# criterion explicitly before committing to a verdict.
_GEVAL_JUDGE_SYSTEM = """\
You are evaluating whether an AI design reviewer's finding is genuine.
Work through the evaluation steps before giving your verdict."""

_GEVAL_JUDGE_TEMPLATE = """\
Finding to evaluate:
  Title: {title}
  Issue: {issue}
  Severity: {severity}

Source document (evaluate the finding against this document only):
{doc_content}

Work through these evaluation steps:

Step 1 — Evidence: Find and quote the specific text in the document that this finding references. If relevant text cannot be found, state that explicitly.

Step 2 — Flaw type: Is this identifying a design gap or flaw, or is it an implementation detail, style preference, or operational choice with no design impact?

Step 3 — Constraint check: Does this finding reference any constraints, requirements, or assumptions NOT present in the document? If so, it is a hallucinated constraint.

Step 4 — Context independence: Can this finding be evaluated from this document alone, or does it require external knowledge (project history, prior sessions, other documents)?

Based on your analysis above, state your verdict on its own line as exactly one of:
Verdict: GENUINE
Verdict: NOT_GENUINE"""


async def _reverse_judge_one(
    judge_model, finding: dict, doc_content: str
) -> tuple[bool, str]:
    """Ask LLM judge if an actual reviewer finding is genuine (direct prompt).

    Passes the full document — no truncation. Findings may reference any section.

    Returns:
        (is_genuine, reasoning) — whether judge says GENUINE and the reasoning.
    """
    prompt = _JUDGE_TEMPLATE.format(
        title=finding.get("title", ""),
        issue=finding.get("issue", finding.get("description", "")),
        severity=finding.get("severity", ""),
        doc_content=doc_content,
    )
    output = await judge_model.generate(
        [ChatMessageSystem(content=_JUDGE_SYSTEM), ChatMessageUser(content=prompt)],
        config=GenerateConfig(max_tokens=150, temperature=0.0),
    )
    first_line = output.completion.strip().splitlines()[0].strip().upper()
    is_genuine = first_line.startswith("GENUINE") and not first_line.startswith("NOT_GENUINE")
    reasoning = output.completion.strip()
    return is_genuine, reasoning


async def _geval_judge_one(
    judge_model, finding: dict, doc_content: str
) -> tuple[bool, str]:
    """Ask LLM judge if a finding is genuine using G-Eval reasoning-first prompting.

    Forces chain-of-thought: the model locates evidence, classifies flaw type,
    checks for hallucinated constraints, and verifies context independence — before
    committing to a verdict. Verdict is parsed from the last 'Verdict:' line.

    Returns:
        (is_genuine, reasoning) — whether judge says GENUINE and the full reasoning.
    """
    prompt = _GEVAL_JUDGE_TEMPLATE.format(
        title=finding.get("title", ""),
        issue=finding.get("issue", finding.get("description", "")),
        severity=finding.get("severity", ""),
        doc_content=doc_content,
    )
    output = await judge_model.generate(
        [ChatMessageSystem(content=_GEVAL_JUDGE_SYSTEM), ChatMessageUser(content=prompt)],
        config=GenerateConfig(max_tokens=1000, temperature=0.0),
    )
    reasoning = output.completion.strip()

    # Parse verdict from last "Verdict: GENUINE/NOT_GENUINE" occurrence.
    # Strip markdown formatting (**, ##, *, -) before matching — models often
    # format the verdict line as "**Verdict: GENUINE**" or "## Verdict: NOT_GENUINE".
    matches = list(re.finditer(r"verdict:\s*(not_genuine|genuine)", reasoning, re.IGNORECASE))
    if matches:
        verdict_str = matches[-1].group(1).upper()
        is_genuine = verdict_str == "GENUINE"
    else:
        is_genuine = False  # no verdict found → default NOT_GENUINE

    return is_genuine, reasoning


@scorer(metrics=[mean()])
def reverse_judge_precision(
    judge: str = "anthropic/claude-haiku-4-5-20251001",
    prompt_style: str = "direct",
):
    """
    Score reviewer precision by asking a judge LLM per actual finding.

    For each finding the reviewer produced, asks the judge:
    "Is this finding genuine — real, document-visible, not a false positive?"

    Returns precision (genuine/total) as the score value. Empty output → 1.0
    (nothing produced, nothing hallucinated). Inspect AI's mean() averages
    precision across samples.

    Args:
        judge: Model to use for judging. Defaults to Haiku (cheap, fast).
        prompt_style: "direct" (verdict-first, max_tokens=150) or
                      "geval" (reasoning-first chain-of-thought, max_tokens=500).
    """
    judge_fn = _geval_judge_one if prompt_style == "geval" else _reverse_judge_one

    async def score(state, target):
        actual_text = state.output.completion
        doc_content = state.metadata["doc_content"]

        actual_findings = parse_review_output(actual_text)

        if not actual_findings:
            return Score(
                value=1.0,
                explanation="Reviewer produced no findings — precision vacuously 1.0.",
                metadata={"genuine": 0, "total": 0, "judge_results": []}
            )

        judge_model = get_model(judge)

        tasks = [
            judge_fn(judge_model, finding, doc_content)
            for finding in actual_findings
        ]
        results = await asyncio.gather(*tasks)

        judge_results = []
        genuine_count = 0
        for finding, (is_genuine, reasoning) in zip(actual_findings, results):
            if is_genuine:
                genuine_count += 1
            judge_results.append({
                "finding_id": finding.get("id"),
                "finding_title": finding.get("title"),
                "confidence": finding.get("confidence"),
                "is_genuine": is_genuine,
                "reasoning": reasoning,
            })

        total = len(actual_findings)
        precision = genuine_count / total
        not_genuine = [r["finding_title"] for r in judge_results if not r["is_genuine"]]

        # Confidence-stratified precision (calibration diagnostic).
        # High-confidence findings (≥80) should have near-100% precision if the
        # reviewer's self-assessment is well-calibrated. Mismatches signal prompt issues.
        high = [r for r in judge_results if (r["confidence"] or 0) >= 80]
        low = [r for r in judge_results if (r["confidence"] or 0) < 80]
        high_precision = sum(1 for r in high if r["is_genuine"]) / len(high) if high else None
        low_precision = sum(1 for r in low if r["is_genuine"]) / len(low) if low else None

        return Score(
            value=precision,
            explanation=(
                f"Judge found {genuine_count}/{total} findings genuine. "
                f"Precision: {precision:.2%}."
            ),
            metadata={
                "genuine": genuine_count,
                "total": total,
                "precision": precision,
                "not_genuine_titles": not_genuine,
                "judge_results": judge_results,
                "confidence_stratified": {
                    "high_confidence": {
                        "count": len(high),
                        "precision": high_precision,
                    },
                    "low_confidence": {
                        "count": len(low),
                        "precision": low_precision,
                    },
                },
            }
        )

    return score
