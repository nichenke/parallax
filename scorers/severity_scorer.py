from difflib import SequenceMatcher
from inspect_ai.scorer import Score, scorer, accuracy

from evals.utils.output_parser import parse_review_output


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _actual_key(finding: dict) -> str | int:
    """Unique tracking key for an actual finding.

    Uses the finding's id string when present. Falls back to object identity
    (id(finding)) so that multiple id-less findings each get a distinct key
    and do not collide on None in the consumed set.
    """
    raw_id = finding.get("id")
    return raw_id if raw_id is not None else id(finding)


def match_findings(
    actual: list[dict], expected: list[dict]
) -> tuple[list[dict], set[str | int]]:
    """
    Match actual review findings to expected ground truth findings.
    Strategy: fuzzy title match (>=0.8 similarity) with severity agreement.
    Each actual finding can only satisfy one expected finding (no double-counting).

    IDs are not used for matching. Finding IDs are session-local sequence numbers
    assigned independently each run — they are not stable cross-run identifiers.
    The same flaw found in two runs will have different IDs but similar titles.

    Returns:
        (matched_expected, consumed_actual_keys) — the list of matched expected
        findings and the set of _actual_key() values that were consumed.
        consumed_actual_keys is needed by callers to compute false positives.
    """
    matched = []
    consumed_actual_keys: set[str | int] = set()

    for exp in expected:
        for act in actual:
            act_key = _actual_key(act)
            if act_key in consumed_actual_keys:
                continue
            if (
                act.get("severity") == exp.get("severity")
                and _title_similarity(act.get("title", ""), exp.get("title", "")) >= 0.8
            ):
                matched.append(exp)
                consumed_actual_keys.add(act_key)
                break

    return matched, consumed_actual_keys


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
        actual_findings = parse_review_output(state.output.completion, severity_filter="Critical")
        expected_findings = state.metadata.get("expected_findings", [])

        detected, consumed_actual_keys = match_findings(actual=actual_findings, expected=expected_findings)

        recall, precision, f1 = calculate_metrics(
            detected=len(detected),
            actual=len(actual_findings),
            expected=len(expected_findings)
        )

        passes = recall >= recall_threshold and precision >= precision_threshold

        missed = [f["id"] for f in expected_findings if f not in detected]
        false_positives = [
            f.get("id", f.get("title")) for f in actual_findings
            if _actual_key(f) not in consumed_actual_keys
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
