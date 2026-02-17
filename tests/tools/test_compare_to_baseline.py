import json
import pytest
from pathlib import Path
from tools.compare_to_baseline import compare_runs, RegressionStatus


def _make_result(recall: float, precision: float, f1: float) -> dict:
    return {
        "results": [{
            "scores": [{
                "metadata": {"recall": recall, "precision": precision, "f1": f1}
            }]
        }]
    }


def test_pass_within_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.91, 0.85, 0.88)
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.PASS


def test_warn_approaching_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.86, 0.80, 0.83)  # ~7% recall drop
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.WARN


def test_fail_exceeds_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.80, 0.75, 0.77)  # >10% recall drop
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.FAIL


def test_delta_values_correct():
    baseline = _make_result(0.90, 0.80, 0.85)
    current  = _make_result(0.85, 0.75, 0.80)
    _, delta = compare_runs(baseline, current, threshold=0.10)
    assert delta["recall"] == pytest.approx(-0.05, abs=1e-4)
    assert delta["precision"] == pytest.approx(-0.05, abs=1e-4)
    assert delta["f1"] == pytest.approx(-0.05, abs=1e-4)
