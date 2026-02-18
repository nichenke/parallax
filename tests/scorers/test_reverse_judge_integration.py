"""Live judge calibration tests — call real Haiku judge at T=0.

Run with: pytest -m integration

These are excluded from the normal unit test suite (which mocks the judge).
They validate judge calibration using the actual requirements-v2 dataset:
- 3 positive cases: must_find entries confirmed GENUINE
- 1 negative case: context-dependent finding confirmed NOT_GENUINE

At T=0 the judge is deterministic, so these tests are stable across runs.
"""
import json
from pathlib import Path

import pytest

from inspect_ai.model import get_model
from scorers.reverse_judge_scorer import _reverse_judge_one


pytestmark = pytest.mark.integration

DATASET = (
    Path(__file__).parent.parent.parent
    / "datasets"
    / "inspect-ai-integration-requirements-v2"
)
DOC_CONTENT = (DATASET / "inspect-ai-integration-requirements-v2.md").read_text()
JUDGE = "anthropic/claude-haiku-4-5-20251001"


def load_finding(finding_id: str, jsonl_path: Path) -> dict:
    for line in jsonl_path.read_text().splitlines():
        if not line.strip():
            continue
        f = json.loads(line)
        if f["id"] == finding_id:
            return f
    raise ValueError(f"Finding {finding_id!r} not found in {jsonl_path}")


@pytest.mark.parametrize("finding_id", [
    "scope-guardian-004",
    "assumption-hunter-001",
    "success-validator-001",
])
async def test_judge_genuine_for_must_find_entries(finding_id):
    """Real judge confirms must_find entries are GENUINE (positive calibration)."""
    finding = load_finding(finding_id, DATASET / "must_find.jsonl")
    judge = get_model(JUDGE)
    is_genuine, reasoning = await _reverse_judge_one(judge, finding, DOC_CONTENT)
    assert is_genuine is True, (
        f"Expected GENUINE for {finding_id}, judge said NOT_GENUINE.\n"
        f"Reasoning: {reasoning}"
    )


async def test_judge_not_genuine_for_context_dependent_finding():
    """Real judge returns NOT_GENUINE for context-dependent finding (negative calibration).

    problem-framer-006 requires knowing what v1 had — not inferable from the v2
    document alone. The judge's 'context-dependent' false positive category should
    catch this. Validates that the judge doesn't say GENUINE to everything.
    """
    finding = load_finding(
        "problem-framer-006", DATASET / "context_dependent_findings.jsonl"
    )
    judge = get_model(JUDGE)
    is_genuine, reasoning = await _reverse_judge_one(judge, finding, DOC_CONTENT)
    assert is_genuine is False, (
        f"Expected NOT_GENUINE for problem-framer-006, judge said GENUINE.\n"
        f"Reasoning: {reasoning}"
    )
