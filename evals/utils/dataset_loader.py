import json
from pathlib import Path
from inspect_ai.dataset import MemoryDataset, Sample, Dataset


def count_by_severity(findings: list[dict]) -> dict:
    counts = {"Critical": 0, "Important": 0, "Minor": 0}
    for f in findings:
        sev = f.get("severity")
        if sev in counts:
            counts[sev] += 1
    return counts


def read_jsonl(path: Path) -> list[dict]:
    lines = path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_validated_findings(
    dataset_path: str,
    reviewer_filter: str | None = None,
) -> Dataset:
    """Convert parallax validated JSONL findings → Inspect AI Dataset.

    Inspect AI Sample requires:
    - input: str | list[ChatMessage] — we use JSON string with design doc ref
    - target: str | list[str] — we use JSON-encoded list of expected finding IDs
    - metadata: dict — stores full ground truth (expected_findings, severity_distribution)

    Args:
        dataset_path: Path to dataset directory containing critical_findings.jsonl and metadata.json
        reviewer_filter: If provided, only include findings with matching reviewer field.
                         Use this for per-reviewer eval tasks (e.g., "assumption-hunter").
    """
    base = Path(dataset_path)
    findings = read_jsonl(base / "critical_findings.jsonl")
    metadata = json.loads((base / "metadata.json").read_text())

    # Only use confirmed real flaws as ground truth, optionally filtered by reviewer
    real_flaws = [
        f for f in findings
        if f.get("type") == "finding"
        and f.get("validation_status") == "real_flaw"
        and (reviewer_filter is None or f.get("reviewer") == reviewer_filter)
    ]

    if reviewer_filter is not None and not real_flaws:
        raise ValueError(
            f"reviewer_filter={reviewer_filter!r} returned 0 findings. "
            f"Check that findings have a 'reviewer' field matching this value, "
            f"and that matched findings have validation_status='real_flaw'."
        )

    doc_path_str = metadata["design_doc_path"]
    doc_path = Path(doc_path_str)
    if doc_path.is_absolute():
        pass  # use as-is
    elif "/" in doc_path_str or "\\" in doc_path_str:
        # repo-relative path (legacy) — resolve from repo root
        doc_path = Path(__file__).parent.parent.parent / doc_path
    else:
        # bare filename — resolve against dataset directory (frozen snapshot)
        doc_path = base / doc_path
    doc_content = doc_path.read_text()

    sample = Sample(
        input=doc_content,
        target=[f["id"] for f in real_flaws],
        metadata={
            **metadata,
            "expected_findings": real_flaws,
            "severity_distribution": count_by_severity(real_flaws)
        }
    )

    return MemoryDataset(samples=[sample])
