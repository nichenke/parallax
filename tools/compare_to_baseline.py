#!/usr/bin/env python3
"""
Compare latest eval run to stored baseline.
Usage: python tools/compare_to_baseline.py [baseline_path] [current_path]
"""
import json
import sys
import zipfile
from enum import Enum
from pathlib import Path


_REPO_ROOT = Path(__file__).parent.parent
BASELINE_PATH = _REPO_ROOT / "evals" / "baselines" / "v3_critical_baseline.json"
LOGS_DIR = _REPO_ROOT / "logs"
WARN_THRESHOLD = 0.05
FAIL_THRESHOLD = 0.10


class RegressionStatus(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


def _load_eval_log(path: Path) -> dict:
    """
    Load an Inspect AI log file and normalise it to the internal dict shape:

        {"results": [{"scores": [{"metadata": {recall, precision, f1}}]}]}

    Inspect AI writes logs as ZIP archives (*.eval) containing several JSON
    files.  The per-sample scorer metadata we need lives in reductions.json:

        reductions[0]["samples"][0]["metadata"] -> {recall, precision, f1, ...}

    Plain JSON files (e.g. hand-crafted baselines) are loaded as-is and must
    already conform to the internal shape.
    """
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            reductions = json.loads(zf.read("reductions.json"))
        # reductions is a list of scorer dicts; aggregate across samples by
        # averaging so that multi-sample runs produce a single metric set.
        metadata_list = reductions[0]["samples"]
        keys = ("recall", "precision", "f1")
        agg = {k: sum(s["metadata"][k] for s in metadata_list) / len(metadata_list)
               for k in keys}
        return {"results": [{"scores": [{"metadata": agg}]}]}
    else:
        return json.loads(path.read_text())


def _extract_metrics(run: dict) -> dict:
    """Extract recall/precision/f1 from the internal run dict."""
    try:
        scores = run["results"][0]["scores"][0]["metadata"]
        return {
            "recall": scores["recall"],
            "precision": scores["precision"],
            "f1": scores["f1"]
        }
    except (KeyError, IndexError) as e:
        raise ValueError(f"Cannot extract metrics from run: {e}")


def compare_runs(
    baseline: dict,
    current: dict,
    threshold: float = FAIL_THRESHOLD,
    warn_threshold: float = WARN_THRESHOLD,
) -> tuple[RegressionStatus, dict]:
    b = _extract_metrics(baseline)
    c = _extract_metrics(current)

    delta = {k: c[k] - b[k] for k in b}
    worst_drop = min(delta.values())

    if worst_drop < -threshold:
        status = RegressionStatus.FAIL
    elif worst_drop < -warn_threshold:
        status = RegressionStatus.WARN
    else:
        status = RegressionStatus.PASS

    return status, delta


def main():
    baseline_path = Path(sys.argv[1]) if len(sys.argv) > 1 else BASELINE_PATH
    if not baseline_path.exists():
        print(f"No baseline found at {baseline_path}. Run 'make baseline' first.")
        sys.exit(1)

    # Find most recent log — Inspect AI writes *.eval (ZIP) files, not *.json
    logs = sorted(
        list(LOGS_DIR.glob("*.eval")) + list(LOGS_DIR.glob("*.json")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not logs:
        print(f"No eval logs found in {LOGS_DIR}/. Run 'make eval' first.")
        sys.exit(1)

    current_path = Path(sys.argv[2]) if len(sys.argv) > 2 else logs[0]

    baseline = _load_eval_log(baseline_path)
    current = _load_eval_log(current_path)

    b_metrics = _extract_metrics(baseline)
    c_metrics = _extract_metrics(current)
    status, delta = compare_runs(baseline, current)

    b_git = baseline.get("metadata", {}).get("git", "unknown")
    c_git = current.get("metadata", {}).get("git", "unknown")

    print(f"\nComparing to baseline: {baseline_path}")
    print(f"\n  Baseline (git:{b_git}):  recall={b_metrics['recall']:.2f}  precision={b_metrics['precision']:.2f}  f1={b_metrics['f1']:.2f}")
    print(f"  Current  (git:{c_git}):  recall={c_metrics['recall']:.2f}  precision={c_metrics['precision']:.2f}  f1={c_metrics['f1']:.2f}")
    print(f"\n  Delta: recall={delta['recall']:+.2f}  precision={delta['precision']:+.2f}  f1={delta['f1']:+.2f}")
    print(f"  Status: {status.value}")

    if status == RegressionStatus.FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
