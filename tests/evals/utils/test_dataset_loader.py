import json
import pytest
from pathlib import Path
from inspect_ai.dataset import MemoryDataset

from evals.utils.dataset_loader import load_validated_findings, count_by_severity


FIXTURES = Path("tests/fixtures")


def test_count_by_severity_empty():
    assert count_by_severity([]) == {"Critical": 0, "Important": 0, "Minor": 0}


def test_count_by_severity_mixed():
    findings = [
        {"severity": "Critical"},
        {"severity": "Critical"},
        {"severity": "Important"},
        {"severity": "Minor"},
    ]
    assert count_by_severity(findings) == {"Critical": 2, "Important": 1, "Minor": 1}


def test_load_validated_findings_returns_dataset(tmp_path):
    # Create minimal valid dataset
    findings = [
        {
            "type": "finding",
            "id": "v3-assumption-hunter-001",
            "title": "Ground truth validity assumed",
            "severity": "Critical",
            "phase": {"primary": "design", "contributing": None},
            "section": "Architecture",
            "issue": "No validation",
            "why_it_matters": "Circular dependency",
            "suggestion": "Validate first",
            "validated": True,
            "validation_status": "real_flaw",
            "validation_notes": "Confirmed",
            "validator_id": "nic",
            "validation_date": "2026-02-16"
        }
    ]
    metadata = {
        "source_review": "parallax-review-v1",
        "design_doc_path": "docs/plans/parallax-design-v4.md",
        "design_doc_hash": "abc123",
        "review_date": "2026-02-16",
        "validation_date": "2026-02-16",
        "validator": "nic",
        "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0,
        "skill_version": "git:abc123"
    }

    (tmp_path / "critical_findings.jsonl").write_text(
        json.dumps(findings[0]) + "\n"
    )
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))

    assert isinstance(dataset, MemoryDataset)
    assert len(dataset) == 1


def test_load_validated_findings_sample_structure(tmp_path):
    finding = {
        "type": "finding",
        "id": "v3-assumption-hunter-001",
        "title": "Test finding",
        "severity": "Critical",
        "phase": {"primary": "design", "contributing": None},
        "section": "Architecture",
        "issue": "Issue text",
        "why_it_matters": "Matters",
        "suggestion": "Fix it",
        "validated": True,
        "validation_status": "real_flaw",
        "validation_notes": "Notes",
        "validator_id": "nic",
        "validation_date": "2026-02-16"
    }
    metadata = {
        "source_review": "test",
        "design_doc_path": "docs/test.md",
        "design_doc_hash": "abc",
        "review_date": "2026-02-16",
        "validation_date": "2026-02-16",
        "validator": "nic",
        "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0,
        "skill_version": "git:abc"
    }

    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    sample = dataset[0]

    # input is a JSON string with design doc reference
    assert "design_doc" in sample.input
    # ground truth is in metadata (Inspect AI target must be str | list[str])
    assert "expected_findings" in sample.metadata
    assert len(sample.metadata["expected_findings"]) == 1
    assert sample.metadata["expected_findings"][0]["id"] == "v3-assumption-hunter-001"


def test_real_ground_truth_loads_correctly():
    """Real dataset must load 9 validated findings — catches empty file, corrupt JSONL, or wrong count."""
    dataset = load_validated_findings("datasets/inspect-ai-integration-requirements-light")
    sample = dataset[0]
    findings = sample.metadata["expected_findings"]
    assert len(findings) == 9
    assert all(f["validation_status"] == "real_flaw" for f in findings)
    assert all(f["severity"] == "Critical" for f in findings)


def test_load_validated_findings_filters_non_real_flaws(tmp_path):
    findings = [
        {
            "type": "finding", "id": "v3-test-001", "title": "Real",
            "severity": "Critical", "phase": {"primary": "design", "contributing": None},
            "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix",
            "validated": True, "validation_status": "real_flaw",
            "validation_notes": "N", "validator_id": "nic", "validation_date": "2026-02-16"
        },
        {
            "type": "finding", "id": "v3-test-002", "title": "False positive",
            "severity": "Critical", "phase": {"primary": "design", "contributing": None},
            "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix",
            "validated": True, "validation_status": "false_positive",
            "validation_notes": "N", "validator_id": "nic", "validation_date": "2026-02-16"
        }
    ]
    metadata = {
        "source_review": "test", "design_doc_path": "d", "design_doc_hash": "h",
        "review_date": "2026-02-16", "validation_date": "2026-02-16",
        "validator": "nic", "total_findings": 2,
        "severity_distribution": {"Critical": 2, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.5, "skill_version": "git:abc"
    }

    lines = "\n".join(json.dumps(f) for f in findings) + "\n"
    (tmp_path / "critical_findings.jsonl").write_text(lines)
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    sample = dataset[0]

    # Only real_flaw findings in ground truth
    assert len(sample.metadata["expected_findings"]) == 1
    assert sample.metadata["expected_findings"][0]["id"] == "v3-test-001"
