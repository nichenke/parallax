"""
Must-find recall scorer.

Strategy: for each document-visible required finding in must_find.jsonl
(pre-loaded into sample metadata), ask a judge model "did the reviewer
identify this flaw?" Returns recall (found / total_must_find) as the score.

Direction is the same as llm_judge_match (expected→actual), but the source is
the curated must-find list rather than the full ground truth. Must-find findings
are document-visible-only — context-dependent findings are excluded (tracked
separately in context_dependent_findings.jsonl).

The min_recall field per finding is stored in metadata for Phase 2 use (N≥3
runs). It is NOT enforced in MVP (N=1 gives only binary found/not-found).
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
A match counts if the reviewer's output conveys the same core problem."""


async def _judge_one(judge_model, must_find: dict, actual_text: str) -> tuple[bool, str]:
    """Ask judge if the must-find finding was identified in reviewer output."""
    prompt = _JUDGE_TEMPLATE.format(
        title=must_find.get("title", ""),
        issue=must_find.get("issue", ""),
        output=actual_text,
    )
    output = await judge_model.generate(
        [ChatMessageSystem(content=_JUDGE_SYSTEM), ChatMessageUser(content=prompt)],
        config=GenerateConfig(max_tokens=100, temperature=0.0),
    )
    first_line = output.completion.strip().splitlines()[0].strip().upper()
    found = first_line.startswith("YES")
    reasoning = output.completion.strip()
    return found, reasoning


@scorer(metrics=[mean()])
def must_find_recall(judge: str = "anthropic/claude-haiku-4-5-20251001"):
    """
    Score must-find recall by asking a judge LLM per required finding.

    For each finding in must_find_findings (loaded from must_find.jsonl),
    asks the judge: "Did the reviewer identify this flaw?"

    Returns recall (found/total) as the score value. No must-find list → 1.0
    with explanation (graceful skip — dataset not yet curated).

    Args:
        judge: Model to use for judging. Defaults to Haiku (cheap, fast).
    """
    async def score(state, target):
        actual_text = state.output.completion
        must_find_findings = state.metadata.get("must_find_findings")

        if must_find_findings is None:
            return Score(
                value=1.0,
                explanation="No must-find findings configured for this dataset.",
                metadata={"found": 0, "total": 0, "find_results": [], "missed_titles": []}
            )

        if not must_find_findings:
            return Score(
                value=1.0,
                explanation="Must-find list is empty — recall vacuously 1.0.",
                metadata={"found": 0, "total": 0, "find_results": [], "missed_titles": []}
            )

        judge_model = get_model(judge)

        tasks = [_judge_one(judge_model, mf, actual_text) for mf in must_find_findings]
        results = await asyncio.gather(*tasks)

        find_results = []
        found_count = 0
        for mf, (found, reasoning) in zip(must_find_findings, results):
            if found:
                found_count += 1
            find_results.append({
                "must_find_id": mf.get("id"),
                "must_find_title": mf.get("title"),
                "found": found,
                "reasoning": reasoning,
                "min_recall": mf.get("min_recall"),
            })

        total = len(must_find_findings)
        recall = found_count / total
        missed = [r["must_find_title"] for r in find_results if not r["found"]]

        return Score(
            value=recall,
            explanation=(
                f"Reviewer found {found_count}/{total} must-find findings. "
                f"Recall: {recall:.2%}."
            ),
            metadata={
                "found": found_count,
                "total": total,
                "recall": recall,
                "missed_titles": missed,
                "find_results": find_results,
            }
        )

    return score
