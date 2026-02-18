"""Tests for must_find_scorer — mocks the judge model to avoid LLM calls.

must_find_recall: for each document-visible required finding in must_find.jsonl,
ask "did the reviewer find this?" → recall = found / total_must_find.

Direction is same as llm_judge_match (expected→actual), but source is the
curated must-find list (not ground truth expected_findings).
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scorers.must_find_scorer import must_find_recall


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_mock_model(response_text: str):
    output = MagicMock()
    output.completion = response_text
    model = MagicMock()
    model.generate = AsyncMock(return_value=output)
    return model


MUST_FIND_A = {
    "id": "mf-001",
    "title": "No success criteria defined",
    "issue": "The document has no success criteria section.",
    "severity": "Critical",
    "min_recall": 0.8,
}

MUST_FIND_B = {
    "id": "mf-002",
    "title": "Phase 2 prerequisites unspecified",
    "issue": "Phase 2 has no stated prerequisites or entry gates.",
    "severity": "Important",
    "min_recall": 0.6,
}

ACTUAL_JSONL = (
    '{"type": "finding", "id": "problem-framer-001", '
    '"title": "Missing success criteria", '
    '"issue": "No explicit success criteria exist in the document.", '
    '"severity": "Critical"}'
)


# ── must_find_recall scorer integration tests ────────────────────────────────


def make_state(completion: str, must_find_findings: list[dict]):
    state = MagicMock()
    state.output.completion = completion
    state.metadata = {"must_find_findings": must_find_findings}
    return state


def run_scorer(scorer_fn, state, target=None):
    inner = scorer_fn()
    return asyncio.run(inner(state, target))


@patch("scorers.must_find_scorer.get_model")
def test_must_find_perfect_recall(mock_get_model):
    """All must-find findings detected → recall=1.0."""
    mock_get_model.return_value = make_mock_model("YES\nFound it.")
    state = make_state(ACTUAL_JSONL, [MUST_FIND_A])
    score = run_scorer(must_find_recall, state)
    assert score.value == pytest.approx(1.0)
    assert score.metadata["found"] == 1
    assert score.metadata["total"] == 1


@patch("scorers.must_find_scorer.get_model")
def test_must_find_zero_recall(mock_get_model):
    """No must-find findings detected → recall=0.0."""
    mock_get_model.return_value = make_mock_model("NO\nNot found.")
    state = make_state(ACTUAL_JSONL, [MUST_FIND_A])
    score = run_scorer(must_find_recall, state)
    assert score.value == pytest.approx(0.0)
    assert score.metadata["found"] == 0


@patch("scorers.must_find_scorer.get_model")
def test_must_find_partial_recall(mock_get_model):
    """Half of must-find findings detected → recall=0.5."""
    responses = ["YES\nFound.", "NO\nNot found."]
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

    state = make_state(ACTUAL_JSONL, [MUST_FIND_A, MUST_FIND_B])
    score = run_scorer(must_find_recall, state)
    assert score.value == pytest.approx(0.5)
    assert score.metadata["found"] == 1
    assert score.metadata["total"] == 2


@patch("scorers.must_find_scorer.get_model")
def test_must_find_empty_list(mock_get_model):
    """No must-find findings configured → score=1.0, no judge calls."""
    mock_get_model.return_value = make_mock_model("YES\nOk.")
    state = make_state(ACTUAL_JSONL, [])
    score = run_scorer(must_find_recall, state)
    assert score.value == pytest.approx(1.0)
    assert score.metadata["total"] == 0
    mock_get_model.return_value.generate.assert_not_called()


@patch("scorers.must_find_scorer.get_model")
def test_must_find_missing_metadata_returns_skip(mock_get_model):
    """Missing must_find_findings key → score=1.0 with explanation (graceful skip)."""
    mock_get_model.return_value = make_mock_model("YES\nOk.")
    state = MagicMock()
    state.output.completion = ACTUAL_JSONL
    state.metadata = {}  # no must_find_findings key
    score = run_scorer(must_find_recall, state)
    assert score.value == pytest.approx(1.0)
    assert "no must-find" in score.explanation.lower()


@patch("scorers.must_find_scorer.get_model")
def test_must_find_metadata_includes_per_finding_results(mock_get_model):
    """Score metadata includes per-finding found/not-found for diagnostic output."""
    mock_get_model.return_value = make_mock_model("YES\nFound it.")
    state = make_state(ACTUAL_JSONL, [MUST_FIND_A])
    score = run_scorer(must_find_recall, state)
    results = score.metadata["find_results"]
    assert len(results) == 1
    assert results[0]["found"] is True
    assert results[0]["must_find_id"] == "mf-001"
    assert results[0]["must_find_title"] == "No success criteria defined"
    assert "reasoning" in results[0]


@patch("scorers.must_find_scorer.get_model")
def test_must_find_metadata_includes_min_recall(mock_get_model):
    """Score metadata preserves min_recall from must-find spec for Phase 2 use."""
    mock_get_model.return_value = make_mock_model("YES\nFound it.")
    state = make_state(ACTUAL_JSONL, [MUST_FIND_A])
    score = run_scorer(must_find_recall, state)
    results = score.metadata["find_results"]
    assert results[0]["min_recall"] == 0.8


@patch("scorers.must_find_scorer.get_model")
def test_must_find_missed_titles_in_metadata(mock_get_model):
    """Metadata includes list of missed must-find titles for easy debugging."""
    mock_get_model.return_value = make_mock_model("NO\nNot found.")
    state = make_state(ACTUAL_JSONL, [MUST_FIND_A, MUST_FIND_B])
    score = run_scorer(must_find_recall, state)
    assert "No success criteria defined" in score.metadata["missed_titles"]
    assert "Phase 2 prerequisites unspecified" in score.metadata["missed_titles"]
