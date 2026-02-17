import pytest
from evals.utils.output_parser import parse_review_output, strip_fences


def test_parse_single_finding():
    completion = '{"type": "finding", "id": "v1-test-001", "title": "Test", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Architecture", "issue": "Missing validation", "why_it_matters": "Blocks eval", "suggestion": "Add validation"}'
    findings = parse_review_output(completion)
    assert len(findings) == 1
    assert findings[0]["id"] == "v1-test-001"


def test_parse_multiple_findings():
    lines = [
        '{"type": "finding", "id": "v1-test-001", "title": "A", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}',
        '{"type": "blind_spot_check", "content": "Checked assumptions"}',
        '{"type": "finding", "id": "v1-test-002", "title": "B", "severity": "Important", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}',
    ]
    findings = parse_review_output("\n".join(lines))
    # Only type=finding returned, not blind_spot_check
    assert len(findings) == 2
    assert all(f["type"] == "finding" for f in findings)


def test_parse_empty_completion():
    assert parse_review_output("") == []


def test_parse_malformed_json_skips_line():
    completion = 'not json\n{"type": "finding", "id": "v1-test-001", "title": "Valid", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}'
    findings = parse_review_output(completion)
    assert len(findings) == 1


def test_parse_filters_to_critical_only():
    lines = [
        '{"type": "finding", "id": "v1-test-001", "title": "A", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}',
        '{"type": "finding", "id": "v1-test-002", "title": "B", "severity": "Important", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}',
    ]
    findings = parse_review_output("\n".join(lines), severity_filter="Critical")
    assert len(findings) == 1
    assert findings[0]["severity"] == "Critical"


def test_strip_fences_removes_json_fence():
    fenced = '```json\n{"type": "finding", "id": "v1-test-001"}\n```'
    result = strip_fences(fenced)
    assert result.strip() == '{"type": "finding", "id": "v1-test-001"}'


def test_strip_fences_removes_plain_fence():
    fenced = '```\n{"type": "finding", "id": "v1-test-001"}\n```'
    result = strip_fences(fenced)
    assert result.strip() == '{"type": "finding", "id": "v1-test-001"}'


def test_strip_fences_passthrough_no_fences():
    raw = '{"type": "finding", "id": "v1-test-001"}'
    assert strip_fences(raw) == raw


def test_strip_fences_multiline_jsonl():
    fenced = '```json\n{"type": "finding", "id": "a"}\n{"type": "finding", "id": "b"}\n```'
    result = strip_fences(fenced)
    lines = [l for l in result.splitlines() if l.strip()]
    assert len(lines) == 2
    assert '"id": "a"' in lines[0]
    assert '"id": "b"' in lines[1]


def test_parse_review_output_handles_fenced_input():
    """End-to-end: fenced JSONL is parsed correctly after stripping."""
    fenced = '```json\n{"type": "finding", "id": "v1-test-001", "title": "T", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix"}\n```'
    findings = parse_review_output(fenced)
    assert len(findings) == 1
    assert findings[0]["id"] == "v1-test-001"
