import pytest
from scorers.severity_scorer import match_findings, calculate_metrics


FINDING_A = {
    "id": "v3-test-001", "title": "Ground truth validity assumed",
    "severity": "Critical", "issue": "No validation of v3 findings"
}
FINDING_B = {
    "id": "v3-test-002", "title": "API key security undefined",
    "severity": "Critical", "issue": "No key rotation policy"
}
FINDING_C = {
    "id": "v3-test-003", "title": "Python environment constraints missing",
    "severity": "Critical", "issue": "No Python version specified"
}


def test_match_findings_exact_id():
    """Exact ID match takes priority."""
    detected = match_findings(actual=[FINDING_A], expected=[FINDING_A])
    assert len(detected) == 1
    assert detected[0]["id"] == "v3-test-001"


def test_match_findings_no_match():
    """Non-matching findings return empty list."""
    different = {"id": "v3-other-001", "title": "Something else", "severity": "Critical", "issue": "Unrelated"}
    detected = match_findings(actual=[different], expected=[FINDING_A])
    assert detected == []


def test_match_findings_fuzzy_title_overlap():
    """Fuzzy match on title when IDs differ."""
    # Same title, different ID (e.g., fresh review rephrased slightly)
    rephrased = {
        "id": "v1-new-001",
        "title": "Ground truth validity assumption",  # ~90% overlap
        "severity": "Critical",
        "issue": "v3 findings not validated"
    }
    detected = match_findings(actual=[rephrased], expected=[FINDING_A])
    assert len(detected) == 1


def test_match_findings_partial_set():
    """Detects subset of expected findings."""
    expected = [FINDING_A, FINDING_B, FINDING_C]
    actual = [FINDING_A, FINDING_C]  # missed FINDING_B
    detected = match_findings(actual=actual, expected=expected)
    assert len(detected) == 2
    ids = [d["id"] for d in detected]
    assert "v3-test-001" in ids
    assert "v3-test-003" in ids


def test_calculate_metrics_perfect():
    recall, precision, f1 = calculate_metrics(detected=3, actual=3, expected=3)
    assert recall == pytest.approx(1.0)
    assert precision == pytest.approx(1.0)
    assert f1 == pytest.approx(1.0)


def test_calculate_metrics_half_recall():
    recall, precision, f1 = calculate_metrics(detected=1, actual=1, expected=2)
    assert recall == pytest.approx(0.5)
    assert precision == pytest.approx(1.0)
    assert f1 == pytest.approx(2/3, rel=1e-3)


def test_calculate_metrics_with_false_positives():
    recall, precision, f1 = calculate_metrics(detected=2, actual=4, expected=2)
    assert recall == pytest.approx(1.0)
    assert precision == pytest.approx(0.5)


def test_calculate_metrics_zero_actual():
    """Handle edge case: model returned no findings."""
    recall, precision, f1 = calculate_metrics(detected=0, actual=0, expected=3)
    assert recall == 0.0
    assert precision == 0.0
    assert f1 == 0.0
