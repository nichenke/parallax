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
    doc = tmp_path / "doc.md"
    doc.write_text("# Test doc")
    metadata = {
        "source_review": "parallax-review-v1",
        "design_doc_path": str(doc),
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
    doc = tmp_path / "doc.md"
    doc.write_text("# Test requirements doc\n\nSome requirements here.")
    metadata = {
        "source_review": "test",
        "design_doc_path": str(doc),
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

    # input is the document content, not a path reference
    assert "# Test requirements doc" in sample.input
    # ground truth is in metadata (Inspect AI target must be str | list[str])
    assert "expected_findings" in sample.metadata
    assert len(sample.metadata["expected_findings"]) == 1
    assert sample.metadata["expected_findings"][0]["id"] == "v3-assumption-hunter-001"


def test_load_validated_findings_input_is_document_content(tmp_path):
    """Sample input must be document content, not a path — model has no file tools in eval context."""
    doc = tmp_path / "requirements.md"
    doc.write_text("# My Requirements\n\nSome content here.")
    finding = {
        "type": "finding", "id": "test-001", "title": "Test",
        "severity": "Critical", "validation_status": "real_flaw",
        "reviewer": "test"
    }
    metadata = {
        "source_review": "test", "design_doc_path": str(doc),
        "review_date": "2026-02-17", "validation_date": "2026-02-17",
        "validator": "nic", "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0, "skill_version": "v1"
    }
    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    assert "# My Requirements" in dataset[0].input
    assert "Some content here" in dataset[0].input


def test_real_ground_truth_loads_correctly():
    """Real dataset must load 10 validated findings — catches empty file, corrupt JSONL, or wrong count."""
    dataset_path = Path(__file__).parent.parent.parent.parent / "datasets" / "inspect-ai-integration-requirements-light"
    dataset = load_validated_findings(str(dataset_path))
    sample = dataset[0]
    findings = sample.metadata["expected_findings"]
    assert len(findings) == 10
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
    doc = tmp_path / "doc.md"
    doc.write_text("# Doc")
    metadata = {
        "source_review": "test", "design_doc_path": str(doc), "design_doc_hash": "h",
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


def test_load_validated_findings_raises_on_empty_reviewer_filter(tmp_path):
    """reviewer_filter that matches nothing must raise ValueError, not silently create empty dataset."""
    finding = {
        "type": "finding", "id": "v3-assumption-hunter-001", "title": "T",
        "severity": "Critical", "validation_status": "real_flaw",
        "reviewer": "assumption-hunter"
    }
    doc = tmp_path / "doc.md"
    doc.write_text("# Doc")
    metadata = {
        "source_review": "test", "design_doc_path": str(doc),
        "review_date": "2026-02-17", "validation_date": "2026-02-17",
        "validator": "nic", "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0, "skill_version": "v1"
    }
    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    with pytest.raises(ValueError, match="reviewer_filter='scope-guardian' returned 0 findings"):
        load_validated_findings(str(tmp_path), reviewer_filter="scope-guardian")


def test_load_validated_findings_reviewer_filter_returns_subset(tmp_path):
    """reviewer_filter returns only matching reviewer's findings."""
    findings = [
        {
            "type": "finding", "id": "f-001", "title": "A",
            "severity": "Critical", "validation_status": "real_flaw",
            "reviewer": "assumption-hunter"
        },
        {
            "type": "finding", "id": "f-002", "title": "B",
            "severity": "Critical", "validation_status": "real_flaw",
            "reviewer": "scope-guardian"
        },
    ]
    doc = tmp_path / "doc.md"
    doc.write_text("# Doc")
    metadata = {
        "source_review": "test", "design_doc_path": str(doc),
        "review_date": "2026-02-17", "validation_date": "2026-02-17",
        "validator": "nic", "total_findings": 2,
        "severity_distribution": {"Critical": 2, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0, "skill_version": "v1"
    }
    lines = "\n".join(json.dumps(f) for f in findings) + "\n"
    (tmp_path / "critical_findings.jsonl").write_text(lines)
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path), reviewer_filter="assumption-hunter")
    ids = [f["id"] for f in dataset[0].metadata["expected_findings"]]
    assert ids == ["f-001"]
    assert "f-002" not in ids


def test_load_validated_findings_local_snapshot_resolution(tmp_path):
    """design_doc_path with no path separator resolves to dataset directory (snapshot)."""
    # Snapshot file lives IN the dataset directory
    snapshot = tmp_path / "my-requirements.md"
    snapshot.write_text("# My Requirements\n\nSnapshot content here.")

    finding = {
        "type": "finding", "id": "snap-001", "title": "T",
        "severity": "Critical", "validation_status": "real_flaw",
        "reviewer": "assumption-hunter"
    }
    metadata = {
        "source_review": "test",
        "design_doc_path": "my-requirements.md",  # no slash = local snapshot
        "review_date": "2026-02-17", "validation_date": "2026-02-17",
        "validator": "nic", "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0, "skill_version": "v1"
    }
    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    assert "# My Requirements" in dataset[0].input
    assert "Snapshot content here" in dataset[0].input


def test_load_validated_findings_repo_relative_path_still_works(tmp_path):
    """design_doc_path containing '/' still resolves relative to repo root (legacy behavior)."""
    # Write a doc somewhere under tmp_path that simulates a repo path
    doc_dir = tmp_path / "docs" / "requirements"
    doc_dir.mkdir(parents=True)
    doc_file = doc_dir / "some-doc.md"
    doc_file.write_text("# Legacy Doc\n\nContent.")

    finding = {
        "type": "finding", "id": "leg-001", "title": "T",
        "severity": "Critical", "validation_status": "real_flaw",
    }
    metadata = {
        "source_review": "test",
        "design_doc_path": str(doc_file),  # absolute path — still works
        "review_date": "2026-02-17", "validation_date": "2026-02-17",
        "validator": "nic", "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0, "skill_version": "v1"
    }
    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    assert "# Legacy Doc" in dataset[0].input
