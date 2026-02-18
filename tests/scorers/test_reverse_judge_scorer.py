"""Tests for reverse_judge_scorer — mocks the judge model to avoid LLM calls.

reverse_judge_precision: for each finding the reviewer produced, ask
"is this genuine and document-visible?" → precision = genuine / total.

Direction is REVERSED from llm_judge_match (which asks "did the reviewer find
this expected finding?"). Here we ask "is the reviewer's finding real?"
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scorers.reverse_judge_scorer import _reverse_judge_one, reverse_judge_precision


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_mock_model(response_text: str):
    """Return a mock judge model that always responds with response_text."""
    output = MagicMock()
    output.completion = response_text
    model = MagicMock()
    model.generate = AsyncMock(return_value=output)
    return model


DOC_CONTENT = """\
# Design: Eval Framework

## Problem Statement
The eval framework has no way to measure reviewer accuracy.

## Phase Map
- Phase 1: per-reviewer eval tasks
- Phase 2: N=3 runs per finding

## Open Questions
None specified.
"""

GENUINE_FINDING = {
    "type": "finding",
    "id": "problem-framer-001",
    "title": "No success criteria defined",
    "issue": "The document has no success criteria section.",
    "severity": "Critical",
}

HALLUCINATED_FINDING = {
    "type": "finding",
    "id": "assumption-hunter-099",
    "title": "Assumes quantum computing availability",
    "issue": "The design assumes quantum hardware that the document never mentions.",
    "severity": "Critical",
}

ACTUAL_JSONL = (
    '{"type": "finding", "id": "problem-framer-001", '
    '"title": "No success criteria defined", '
    '"issue": "The document has no success criteria section.", '
    '"severity": "Critical"}'
)


# ── _reverse_judge_one unit tests ────────────────────────────────────────────


def test_reverse_judge_one_genuine_returns_true():
    """Judge returning GENUINE → is_genuine=True."""
    model = make_mock_model("GENUINE\nThe document clearly omits success criteria.")
    is_genuine, reasoning = asyncio.run(
        _reverse_judge_one(model, GENUINE_FINDING, DOC_CONTENT)
    )
    assert is_genuine is True
    assert "GENUINE" in reasoning


def test_reverse_judge_one_not_genuine_returns_false():
    """Judge returning NOT_GENUINE → is_genuine=False."""
    model = make_mock_model("NOT_GENUINE\nThis claim is not supported by the document.")
    is_genuine, reasoning = asyncio.run(
        _reverse_judge_one(model, HALLUCINATED_FINDING, DOC_CONTENT)
    )
    assert is_genuine is False


def test_reverse_judge_one_case_insensitive():
    """GENUINE/NOT_GENUINE parsing is case-insensitive."""
    model = make_mock_model("genuine\nLooks real.")
    is_genuine, _ = asyncio.run(
        _reverse_judge_one(model, GENUINE_FINDING, DOC_CONTENT)
    )
    assert is_genuine is True


def test_reverse_judge_one_passes_full_document_to_judge():
    """Full document is passed to judge — no truncation (regression for truncation bug)."""
    long_doc = "# Design\n" + ("Important content. " * 1000)  # ~20k chars
    model = make_mock_model("GENUINE\nFound in document.")
    asyncio.run(_reverse_judge_one(model, GENUINE_FINDING, long_doc))
    call_args = model.generate.call_args
    messages = call_args[0][0]
    combined = " ".join(m.content for m in messages)
    # Full doc should be present — not truncated at 6000 chars
    assert "Important content." in combined
    assert len(combined) > 10_000


def test_reverse_judge_one_includes_false_positive_criteria_in_prompt():
    """Judge prompt contains all 6 explicit false positive categories from ADR-007."""
    model = make_mock_model("GENUINE\nOk.")
    asyncio.run(_reverse_judge_one(model, GENUINE_FINDING, DOC_CONTENT))
    call_args = model.generate.call_args
    messages = call_args[0][0]
    combined = " ".join(m.content for m in messages)
    # All 6 ADR-007 false positive categories must appear in the judge prompt
    assert "implementation detail" in combined.lower()
    assert "hallucinated" in combined.lower()
    assert "style preference" in combined.lower() or "stylistic" in combined.lower()
    assert "hypothetical" in combined.lower()
    assert "duplicate" in combined.lower()
    assert "context-dependent" in combined.lower() or "context dependent" in combined.lower()


def test_reverse_judge_one_includes_finding_in_prompt():
    """Judge prompt includes the actual finding's title and issue."""
    model = make_mock_model("GENUINE\nOk.")
    asyncio.run(_reverse_judge_one(model, GENUINE_FINDING, DOC_CONTENT))
    call_args = model.generate.call_args
    messages = call_args[0][0]
    combined = " ".join(m.content for m in messages)
    assert "No success criteria defined" in combined
    assert "no success criteria section" in combined


# ── reverse_judge_precision scorer integration tests ────────────────────────


def make_state(completion: str, doc_content: str, metadata_extra: dict | None = None):
    state = MagicMock()
    state.output.completion = completion
    state.metadata = {"doc_content": doc_content, **(metadata_extra or {})}
    return state


def run_scorer(scorer_fn, state, target=None):
    """Run an async Inspect AI scorer synchronously for testing."""
    inner = scorer_fn()
    return asyncio.run(inner(state, target))


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_all_genuine(mock_get_model):
    """All actual findings genuine → precision=1.0."""
    mock_get_model.return_value = make_mock_model("GENUINE\nReal finding.")
    state = make_state(ACTUAL_JSONL, DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    assert score.value == pytest.approx(1.0)
    assert score.metadata["genuine"] == 1
    assert score.metadata["total"] == 1


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_all_hallucinated(mock_get_model):
    """All actual findings hallucinated → precision=0.0."""
    mock_get_model.return_value = make_mock_model("NOT_GENUINE\nHallucinated.")
    state = make_state(ACTUAL_JSONL, DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    assert score.value == pytest.approx(0.0)
    assert score.metadata["genuine"] == 0
    assert score.metadata["total"] == 1


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_partial(mock_get_model):
    """Half genuine → precision=0.5."""
    responses = ["GENUINE\nReal.", "NOT_GENUINE\nFake."]
    call_count = 0

    async def alternating(messages, config=None):
        nonlocal call_count
        out = MagicMock()
        out.completion = responses[call_count % len(responses)]
        call_count += 1
        return out

    model = MagicMock()
    model.generate = alternating
    mock_get_model.return_value = model

    two_findings = "\n".join([ACTUAL_JSONL, ACTUAL_JSONL.replace("001", "002")])
    state = make_state(two_findings, DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    assert score.value == pytest.approx(0.5)
    assert score.metadata["genuine"] == 1
    assert score.metadata["total"] == 2


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_empty_reviewer_output(mock_get_model):
    """Reviewer produces no findings → precision=1.0 (nothing to hallucinate)."""
    mock_get_model.return_value = make_mock_model("GENUINE\nOk.")
    state = make_state("", DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    assert score.value == pytest.approx(1.0)
    assert score.metadata["total"] == 0
    mock_get_model.return_value.generate.assert_not_called()


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_malformed_jsonl_skipped(mock_get_model):
    """Malformed JSONL lines are skipped; valid findings still scored."""
    mock_get_model.return_value = make_mock_model("GENUINE\nReal finding.")
    output = "not json at all\n" + ACTUAL_JSONL + "\nalso not json"
    state = make_state(output, DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    assert score.metadata["total"] == 1


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_metadata_includes_per_finding_results(mock_get_model):
    """Score metadata includes per-finding judge results for debugging."""
    mock_get_model.return_value = make_mock_model("GENUINE\nClear design gap.")
    state = make_state(ACTUAL_JSONL, DOC_CONTENT)
    score = run_scorer(reverse_judge_precision, state)
    results = score.metadata["judge_results"]
    assert len(results) == 1
    assert results[0]["is_genuine"] is True
    assert "reasoning" in results[0]
    assert results[0]["finding_title"] == "No success criteria defined"


@patch("scorers.reverse_judge_scorer.get_model")
def test_precision_missing_doc_content_raises_clearly(mock_get_model):
    """Missing doc_content in metadata raises a clear error (not silent wrong result)."""
    mock_get_model.return_value = make_mock_model("GENUINE\nOk.")
    state = MagicMock()
    state.output.completion = ACTUAL_JSONL
    state.metadata = {}  # no doc_content
    with pytest.raises((KeyError, ValueError)):
        run_scorer(reverse_judge_precision, state)
