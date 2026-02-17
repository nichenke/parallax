from difflib import SequenceMatcher
from inspect_ai.scorer import Score, scorer, accuracy


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_findings(
    actual: list[dict], expected: list[dict]
) -> tuple[list[dict], set[str | None]]:
    """
    Match actual review findings to expected ground truth findings.
    Strategy: exact ID match first, fuzzy title match fallback (>=0.8 similarity).
    Each actual finding can only satisfy one expected finding (no double-counting).

    Returns:
        (matched_expected, consumed_actual_ids) — the list of matched expected
        findings and the set of actual finding IDs that were consumed.
        consumed_actual_ids is needed by callers to compute false positives
        correctly after fuzzy matching, where actual IDs differ from expected IDs.
    """
    matched = []
    consumed_actual_ids: set[str | None] = set()
    actual_ids = {f.get("id") for f in actual}

    for exp in expected:
        exp_id = exp["id"]

        # Exact ID match — consume that actual finding
        if exp_id in actual_ids:
            if exp_id not in consumed_actual_ids:
                matched.append(exp)
                consumed_actual_ids.add(exp_id)
            continue

        # Fuzzy title match fallback — consume first unused actual that matches
        for act in actual:
            act_id = act.get("id")
            if act_id in consumed_actual_ids:
                continue
            if (
                act.get("severity") == exp.get("severity")
                and _title_similarity(act.get("title", ""), exp.get("title", "")) >= 0.8
            ):
                matched.append(exp)
                consumed_actual_ids.add(act_id)
                break

    return matched, consumed_actual_ids


def calculate_metrics(detected: int, actual: int, expected: int) -> tuple[float, float, float]:
    """Calculate recall, precision, F1."""
    recall = detected / expected if expected > 0 else 0.0
    precision = detected / actual if actual > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return recall, precision, f1


@scorer(metrics=[accuracy()])
def severity_calibration(recall_threshold: float = 0.90, precision_threshold: float = 0.80):
    """
    Validates Critical finding detection against ground truth.
    Thresholds: recall >=90%, precision >=80% (provisional — tune after first runs).
    """
    async def score(state, target):
        from evals.utils.output_parser import parse_review_output

        actual_findings = parse_review_output(state.output.completion, severity_filter="Critical")
        expected_findings = state.metadata.get("expected_findings", [])

        detected, consumed_actual_ids = match_findings(actual=actual_findings, expected=expected_findings)

        recall, precision, f1 = calculate_metrics(
            detected=len(detected),
            actual=len(actual_findings),
            expected=len(expected_findings)
        )

        passes = recall >= recall_threshold and precision >= precision_threshold

        missed = [f["id"] for f in expected_findings if f not in detected]
        false_positives = [
            f.get("id", f.get("title")) for f in actual_findings
            if f.get("id") not in consumed_actual_ids
        ]

        return Score(
            value=1.0 if passes else 0.0,
            answer=str([f["id"] for f in detected]),
            explanation=(
                f"Detected {len(detected)}/{len(expected_findings)} findings. "
                f"Recall: {recall:.2%}, Precision: {precision:.2%}, F1: {f1:.2%}. "
                f"{'PASS' if passes else 'FAIL'}"
            ),
            metadata={
                "recall": recall,
                "precision": precision,
                "f1": f1,
                "passes_threshold": passes,
                "missed_findings": missed,
                "false_positives": false_positives
            }
        )

    return score
