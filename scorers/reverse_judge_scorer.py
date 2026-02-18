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
from inspect_ai.model import get_model, ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, scorer, mean

from evals.utils.output_parser import parse_review_output


_JUDGE_SYSTEM = """\
You are evaluating whether an AI design reviewer's finding is genuine.

A finding is GENUINE if:
- It identifies a real problem visible in the provided document
- The problem is a design flaw, not a matter of style or implementation preference
- The claim is supported by or reasonably inferable from the document content

A finding is NOT_GENUINE if it falls into any of these false positive categories:
- Implementation detail: a coding or operational choice, not a design flaw
- Hallucinated constraint: references requirements or assumptions not present in the document
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


async def _reverse_judge_one(
    judge_model, finding: dict, doc_content: str
) -> tuple[bool, str]:
    """Ask LLM judge if an actual reviewer finding is genuine.

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


@scorer(metrics=[mean()])
def reverse_judge_precision(judge: str = "anthropic/claude-haiku-4-5-20251001"):
    """
    Score reviewer precision by asking a judge LLM per actual finding.

    For each finding the reviewer produced, asks the judge:
    "Is this finding genuine — real, document-visible, not a false positive?"

    Returns precision (genuine/total) as the score value. Empty output → 1.0
    (nothing produced, nothing hallucinated). Inspect AI's mean() averages
    precision across samples.

    Args:
        judge: Model to use for judging. Defaults to Haiku (cheap, fast).
    """
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
            _reverse_judge_one(judge_model, finding, doc_content)
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
                "is_genuine": is_genuine,
                "reasoning": reasoning,
            })

        total = len(actual_findings)
        precision = genuine_count / total
        not_genuine = [r["finding_title"] for r in judge_results if not r["is_genuine"]]

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
            }
        )

    return score
