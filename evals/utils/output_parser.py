import json


def strip_fences(text: str) -> str:
    """
    Remove markdown code fences from text, returning only the inner content.
    Handles both ```json and plain ``` fences.
    """
    lines = text.splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            continue  # skip fence delimiter lines
        result.append(line)
    return "\n".join(result)


def parse_review_output(completion: str, severity_filter: str | None = None) -> list[dict]:
    """
    Parse model output text into structured findings.
    Strips markdown code fences before parsing.
    Expects JSONL format (one JSON object per line).
    Returns only type=finding records, optionally filtered by severity.
    Silently skips malformed lines.
    """
    completion = strip_fences(completion)
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
