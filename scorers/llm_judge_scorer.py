# DEPRECATED: replaced by must_find_recall() (ADR-007 / Issue #71).
# Kept for reference. Do not use in reviewer_eval.py.
"""
LLM-as-judge scorer for finding detection.

Strategy: for each expected ground truth finding, ask a judge model
"did the reviewer identify this flaw (possibly with different wording)?"
Returns recall as the score value (0.0–1.0), enabling Inspect AI's
accuracy() metric to average across samples.

This replaces string title similarity (severity_scorer.py) which fails
when reviewers legitimately paraphrase finding descriptions.
Inspired by the code-review plugin (claude-plugins-official) which uses
per-finding 0–100 confidence scoring to filter false positives.
"""
import asyncio
from inspect_ai.model import get_model, ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, scorer, mean

from evals.utils.output_parser import parse_review_output


_JUDGE_SYSTEM = """\
You are evaluating whether an AI reviewer identified a known design flaw.
Answer with exactly YES or NO on the first line, followed by one sentence of reasoning.
Do not add any other text before YES or NO."""

_JUDGE_TEMPLATE = """\
Known flaw to check for:
  Title: {title}
  Issue: {issue}

Reviewer output (JSONL findings):
{output}

Did the reviewer identify this flaw, even if using different wording or framing?
A match counts if the reviewer's output conveys the same core problem, even with a different title."""


async def _judge_one(judge_model, expected: dict, actual_text: str) -> tuple[bool, str]:
    """Ask LLM judge if the expected finding was identified in the actual output.

    Returns:
        (matched, reasoning) — whether judge says YES and the one-line reasoning.
    """
    prompt = _JUDGE_TEMPLATE.format(
        title=expected.get("title", ""),
        issue=expected.get("issue", expected.get("description", "")),
        output=actual_text[:6000],
    )
    output = await judge_model.generate(
        [ChatMessageSystem(content=_JUDGE_SYSTEM), ChatMessageUser(content=prompt)],
        config=GenerateConfig(max_tokens=100, temperature=0.0),
    )
    first_line = output.completion.strip().splitlines()[0].strip().upper()
    matched = first_line.startswith("YES")
    reasoning = output.completion.strip()
    return matched, reasoning


@scorer(metrics=[mean()])
def llm_judge_match(judge: str = "anthropic/claude-haiku-4-5-20251001"):
    """
    Score finding detection by asking a judge LLM per expected finding.

    For each expected ground truth finding, asks the judge:
    "Did the reviewer identify this flaw (possibly with different wording)?"

    Returns recall (detected/expected) as the score value. Inspect AI's
    mean() metric averages recall across samples.

    Args:
        judge: Model to use for judging. Defaults to Haiku (cheap, fast).
    """
    async def score(state, target):
        actual_text = state.output.completion
        expected_findings = state.metadata.get("expected_findings", [])

        if not expected_findings:
            return Score(
                value=0.0,
                explanation="No expected findings in metadata.",
                metadata={"recall": 0.0, "judge_results": []}
            )

        # Parse actual JSONL output — pass full text to judge (not pre-filtered)
        # Judge sees everything the reviewer output, not just Critical findings
        judge_model = get_model(judge)

        # Run all judge calls in parallel
        tasks = [_judge_one(judge_model, exp, actual_text) for exp in expected_findings]
        results = await asyncio.gather(*tasks)

        judge_results = []
        detected = 0
        for exp, (matched, reasoning) in zip(expected_findings, results):
            if matched:
                detected += 1
            judge_results.append({
                "expected_id": exp.get("id"),
                "expected_title": exp.get("title"),
                "matched": matched,
                "reasoning": reasoning,
            })

        recall = detected / len(expected_findings)
        missed = [r["expected_title"] for r in judge_results if not r["matched"]]

        return Score(
            value=recall,
            explanation=(
                f"Judge detected {detected}/{len(expected_findings)} expected findings. "
                f"Recall: {recall:.2%}."
            ),
            metadata={
                "recall": recall,
                "detected": detected,
                "expected": len(expected_findings),
                "missed_titles": missed,
                "judge_results": judge_results,
            }
        )

    return score
