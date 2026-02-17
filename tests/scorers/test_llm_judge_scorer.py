"""Tests for llm_judge_scorer — mocks the judge model to avoid LLM calls."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scorers.llm_judge_scorer import _judge_one, llm_judge_match


# ── Fixtures ────────────────────────────────────────────────────────────────


def make_mock_model(response_text: str):
    """Return a mock judge model that always responds with response_text."""
    output = MagicMock()
    output.completion = response_text
    model = MagicMock()
    model.generate = AsyncMock(return_value=output)
    return model


EXPECTED_FINDING = {
    "id": "constraint-finder-002",
    "title": "API key security undefined",
    "issue": "No separation between work and personal API keys specified.",
    "severity": "Critical",
}

ACTUAL_TEXT_YES = (
    '{"type": "finding", "id": "constraint-finder-001", '
    '"title": "Credential separation not specified", '
    '"issue": "The requirements do not address how API credentials are separated between work (Bedrock IAM) and personal (direct API) contexts.", '
    '"severity": "Critical"}'
)

ACTUAL_TEXT_NO = (
    '{"type": "finding", "id": "constraint-finder-001", '
    '"title": "Timeline for Phase 0 missing", '
    '"issue": "Phase 0 has no start date or milestone tracking.", '
    '"severity": "Critical"}'
)


# ── _judge_one unit tests ────────────────────────────────────────────────────


def test_judge_one_yes_response():
    """Judge returning YES → matched=True."""
    model = make_mock_model("YES\nThe reviewer flagged credential separation.")
    matched, reasoning = asyncio.run(_judge_one(model, EXPECTED_FINDING, ACTUAL_TEXT_YES))
    assert matched is True
    assert "YES" in reasoning


def test_judge_one_no_response():
    """Judge returning NO → matched=False."""
    model = make_mock_model("NO\nThe reviewer did not address API key security.")
    matched, reasoning = asyncio.run(_judge_one(model, EXPECTED_FINDING, ACTUAL_TEXT_NO))
    assert matched is False


def test_judge_one_case_insensitive():
    """YES/NO parsing is case-insensitive (normalised to upper)."""
    model = make_mock_model("yes\nFound it.")
    matched, _ = asyncio.run(_judge_one(model, EXPECTED_FINDING, ACTUAL_TEXT_YES))
    assert matched is True


def test_judge_one_uses_title_and_issue_in_prompt():
    """Judge prompt includes the expected finding's title and issue."""
    model = make_mock_model("YES\nMatch found.")
    asyncio.run(_judge_one(model, EXPECTED_FINDING, ACTUAL_TEXT_YES))
    call_args = model.generate.call_args
    messages = call_args[0][0]  # first positional arg = list of messages
    combined = " ".join(m.content for m in messages)
    assert "API key security undefined" in combined
    assert "No separation between work and personal API keys" in combined


def test_judge_one_truncates_long_actual_output():
    """Actual output is truncated to avoid huge judge prompts."""
    long_text = "x" * 10_000
    model = make_mock_model("YES\nOk.")
    asyncio.run(_judge_one(model, EXPECTED_FINDING, long_text))
    call_args = model.generate.call_args
    messages = call_args[0][0]
    combined = " ".join(m.content for m in messages)
    # The combined prompt should be well under 10k characters from actual_text alone
    assert len(combined) < 9_000


# ── llm_judge_match scorer integration tests ────────────────────────────────


def make_state(completion: str, expected_findings: list[dict]):
    state = MagicMock()
    state.output.completion = completion
    state.metadata = {"expected_findings": expected_findings}
    return state


def run_scorer(scorer_fn, state, target=None):
    """Run an async Inspect AI scorer synchronously for testing."""
    inner = scorer_fn()  # call the @scorer-decorated factory → returns async score fn
    return asyncio.run(inner(state, target))


@patch("scorers.llm_judge_scorer.get_model")
def test_llm_judge_perfect_recall(mock_get_model):
    """All expected findings detected → recall=1.0."""
    mock_get_model.return_value = make_mock_model("YES\nFound it.")
    state = make_state(ACTUAL_TEXT_YES, [EXPECTED_FINDING])
    score = run_scorer(llm_judge_match, state)
    assert score.value == pytest.approx(1.0)
    assert score.metadata["detected"] == 1
    assert score.metadata["expected"] == 1


@patch("scorers.llm_judge_scorer.get_model")
def test_llm_judge_zero_recall(mock_get_model):
    """No expected findings detected → recall=0.0."""
    mock_get_model.return_value = make_mock_model("NO\nNot found.")
    state = make_state(ACTUAL_TEXT_NO, [EXPECTED_FINDING])
    score = run_scorer(llm_judge_match, state)
    assert score.value == pytest.approx(0.0)
    assert score.metadata["detected"] == 0


@patch("scorers.llm_judge_scorer.get_model")
def test_llm_judge_partial_recall(mock_get_model):
    """Half of expected findings detected → recall=0.5."""
    responses = ["YES\nFound.", "NO\nNot found."]
    call_count = 0

    async def alternating_generate(messages, config=None):
        nonlocal call_count
        out = MagicMock()
        out.completion = responses[call_count % len(responses)]
        call_count += 1
        return out

    model = MagicMock()
    model.generate = alternating_generate
    mock_get_model.return_value = model

    finding_b = {**EXPECTED_FINDING, "id": "constraint-finder-009", "title": "Circular validation"}
    state = make_state(ACTUAL_TEXT_YES, [EXPECTED_FINDING, finding_b])
    score = run_scorer(llm_judge_match, state)
    assert score.value == pytest.approx(0.5)
    assert score.metadata["detected"] == 1


@patch("scorers.llm_judge_scorer.get_model")
def test_llm_judge_empty_expected(mock_get_model):
    """No expected findings → score=0.0 without calling judge."""
    mock_get_model.return_value = make_mock_model("YES\nFound.")
    state = make_state(ACTUAL_TEXT_YES, [])
    score = run_scorer(llm_judge_match, state)
    assert score.value == pytest.approx(0.0)
    mock_get_model.return_value.generate.assert_not_called()


@patch("scorers.llm_judge_scorer.get_model")
def test_llm_judge_metadata_contains_reasoning(mock_get_model):
    """Score metadata includes per-finding judge reasoning for debugging."""
    mock_get_model.return_value = make_mock_model("YES\nClear match on credential concern.")
    state = make_state(ACTUAL_TEXT_YES, [EXPECTED_FINDING])
    score = run_scorer(llm_judge_match, state)
    results = score.metadata["judge_results"]
    assert len(results) == 1
    assert results[0]["matched"] is True
    assert "reasoning" in results[0]
    assert results[0]["expected_title"] == "API key security undefined"
