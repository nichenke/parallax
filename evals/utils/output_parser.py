import json


def strip_fences(text: str) -> str:
    """
    Remove markdown code fences from text, returning only the inner content.
    Handles both ```json and plain ``` fences.

    Uses a filter approach (drop fence-marker lines) rather than a stateful
    toggle (drop content between markers). In the eval context this is sufficient:
    any non-JSONL content that survives stripping will fail json.loads() and be
    skipped by the parser. An unclosed fence is also handled correctly — content
    after an unclosed opening marker is preserved rather than silently dropped.
    """
    return "\n".join(
        line for line in text.splitlines()
        if not line.strip().startswith("```")
    )


def parse_review_output(completion: str, severity_filter: str | None = None) -> list[dict]:
    """
    Parse model output text into structured findings.
    Strips markdown code fences before parsing.
    Expects JSONL format (one JSON object per line).
    Returns only type=finding records, optionally filtered by severity.
    Silently skips malformed lines.
    """
    cleaned = strip_fences(completion)
    findings = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "finding":
            continue
        if severity_filter and obj.get("severity") != severity_filter:
            continue
        findings.append(obj)
    return findings
