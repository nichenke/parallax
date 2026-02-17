import json


def parse_review_output(completion: str, severity_filter: str | None = None) -> list[dict]:
    """
    Parse model output text into structured findings.
    Expects JSONL format (one JSON object per line).
    Returns only type=finding records, optionally filtered by severity.
    Silently skips malformed lines.
    """
    findings = []
    for line in completion.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "finding":
            continue
        if severity_filter and obj.get("severity") != severity_filter:
            continue
        findings.append(obj)
    return findings
