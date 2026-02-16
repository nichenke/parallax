# Design: JSONL Schema for parallax:review

**Date:** 2026-02-16
**Status:** Approved
**Related:** Requirements v1.2, Design v4, ADR-001, ADR-002

---

## Overview

This document specifies the JSONL schema structure for parallax:review output artifacts. These schemas implement FR6.1 (JSONL canonical format), NFR2.4 (per-reviewer tracking), NFR2.5 (run-level metadata), and FR10 (pattern extraction/delta detection).

**Problem:** Requirements specify JSONL as canonical output format but don't define the schema structure. FR7.5 (schema validation) is blocked on this definition.

**Solution:** Four schema types with consolidated metadata approach:
1. **Reviewer findings JSONL** - per-reviewer findings (canonical format)
2. **Run metadata JSONL** - run-level + per-reviewer cost/token tracking
3. **Pattern extraction JSON** - semantic pattern grouping (post-synthesis)
4. **Delta detection JSON** - cross-iteration comparison

---

## Design Philosophy

### Key Principles

**1. Consolidated metadata**
- Single `run_metadata.jsonl` file contains all metadata (run-level + per-reviewer)
- Reviewer findings files contain pure data (no metadata header)
- Rationale: Single source of truth, easier to query, no duplication

**2. JSONL for streaming data, JSON for analysis**
- Reviewer findings use JSONL (line-by-line streaming, append-only)
- Pattern extraction and delta detection use JSON (post-synthesis, read-only)

**3. Inline disposition tracking**
- Disposition fields appended to finding objects during interactive processing
- No separate disposition file (keeps all context in one place)

**4. Globally unique finding IDs**
- Format: `v{iteration}-{reviewer}-{sequence}` (e.g., `v3-assumption-hunter-001`)
- Enforced at schema level, prevents collision when merging across reviewers

**5. Explicit schema versioning**
- Every file includes `"schema_version": "1.0.0"` field
- Enables graceful schema evolution, forward compatibility

---

## File Structure

```
docs/reviews/<topic>/
├── run_metadata.jsonl          # Run-level metadata + per-reviewer tracking
├── assumption-hunter.jsonl     # Reviewer findings (pure data)
├── edge-case-prober.jsonl      # Reviewer findings
├── feasibility-skeptic.jsonl   # Reviewer findings
├── first-principles.jsonl      # Reviewer findings
├── prior-art-scout.jsonl       # Reviewer findings
├── requirement-auditor.jsonl   # Reviewer findings
├── patterns-v3.json            # Pattern extraction (post-synthesis)
├── delta-v2-v3.json            # Delta detection (cross-iteration)
├── summary.md                  # Rendered from JSONL (human-readable)
└── [reviewer].md               # Rendered from JSONL (audit trail)
```

**Rendering:** Markdown files are generated from JSONL during synthesis. JSONL is source of truth.

---

## Schema 1: Reviewer Findings JSONL

**File naming:** `<reviewer-name>.jsonl` (e.g., `assumption-hunter.jsonl`)

**Structure:** Newline-delimited JSON objects. Three object types.

### Object Type: Finding

**Required fields:**

```json
{
  "type": "finding",
  "id": "v3-assumption-hunter-001",
  "title": "Auto-Fix Step Assumes It Can Correctly Identify Trivial Changes",
  "severity": "Critical",
  "phase": {
    "primary": "design",
    "contributing": null
  },
  "section": "Step 4: Auto-Fix (synthesis section)",
  "issue": "Design specifies auto-fix classifies findings as 'typos in markdown, missing file extensions, broken internal links' and applies them automatically. This assumes the system can reliably distinguish trivial mechanical fixes from semantic changes.",
  "why_it_matters": "Auto-fixes modify source files and commit changes automatically. A misclassified 'trivial' fix that changes meaning breaks the design.",
  "suggestion": "Add validation requirements to auto-fix specification: (1) Define 'conservative' with concrete examples, (2) Require diffs for user approval before application, (3) Add rollback mechanism."
}
```

**Optional fields (added during disposition):**

```json
{
  "disposition": "accepted",
  "disposition_note": "Will add validation workflow before auto-apply",
  "disposition_date": "2026-02-16T14:23:00Z",
  "disposition_by": "user"
}
```

**Field specifications:**

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `type` | string | Yes | `"finding"` | Object type discriminator |
| `id` | string | Yes | `v{N}-{reviewer}-{seq}` | Globally unique finding ID |
| `title` | string | Yes | - | Short finding title |
| `severity` | string | Yes | `"Critical"` \| `"Important"` \| `"Minor"` | Severity classification |
| `phase.primary` | string | Yes | `"survey"` \| `"calibrate"` \| `"design"` \| `"plan"` | Primary phase classification |
| `phase.contributing` | string\|null | Yes | Same as primary, or `null` | Contributing phase (upstream cause) |
| `section` | string | Yes | - | Design doc section affected |
| `issue` | string | Yes | - | What's wrong (detailed description) |
| `why_it_matters` | string | Yes | - | Impact if unaddressed |
| `suggestion` | string | Yes | - | How to fix or what to reconsider |
| `disposition` | string | No | `"accepted"` \| `"rejected"` | User decision (null before processing) |
| `disposition_note` | string | No | - | User's reasoning for disposition |
| `disposition_date` | string (ISO8601) | No | - | When disposition was made |
| `disposition_by` | string | No | `"user"` \| `"auto"` | Who made disposition |

### Object Type: Blind Spot Check

**Required fields:**

```json
{
  "type": "blind_spot_check",
  "content": "Given my focus on assumptions, I may have missed implementation-level edge cases around error handling, boundary conditions at scale, and integration failure modes. Edge Case Prober and Feasibility Skeptic should catch these."
}
```

**Field specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | `"blind_spot_check"` |
| `content` | string | Yes | Self-assessment of reviewer's limitations |

### Object Type: Reviewer Metadata (stub for failed reviewers)

**Used only when reviewer fails:**

```json
{
  "type": "reviewer_metadata",
  "reviewer": "edge-case-prober",
  "status": "failed",
  "error": "timeout_after_120s",
  "error_message": "Reviewer exceeded 120s timeout during synthesis phase",
  "partial_findings_count": 0
}
```

**Field specifications:**

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `type` | string | Yes | `"reviewer_metadata"` | Object type discriminator |
| `reviewer` | string | Yes | - | Reviewer name |
| `status` | string | Yes | `"completed"` \| `"failed"` \| `"partial"` | Completion status |
| `error` | string | No | - | Error code (required if status != completed) |
| `error_message` | string | No | - | Human-readable error description |
| `partial_findings_count` | number | Yes | - | Number of findings before failure (0 if none) |

### Example Files

**Successful reviewer** (assumption-hunter.jsonl):
```jsonl
{"type": "finding", "id": "v3-assumption-hunter-001", "title": "Auto-Fix Step Assumes...", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Step 4: Auto-Fix", "issue": "...", "why_it_matters": "...", "suggestion": "..."}
{"type": "finding", "id": "v3-assumption-hunter-002", "title": "Git-Based Iteration Tracking...", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Output Artifacts", "issue": "...", "why_it_matters": "...", "suggestion": "...", "disposition": "accepted", "disposition_note": "Add git requirement to constraints", "disposition_date": "2026-02-16T14:25:00Z", "disposition_by": "user"}
{"type": "blind_spot_check", "content": "Given my focus on assumptions, I may have missed..."}
```

**Failed reviewer** (edge-case-prober.jsonl):
```jsonl
{"type": "reviewer_metadata", "reviewer": "edge-case-prober", "status": "failed", "error": "timeout_after_120s", "error_message": "Reviewer exceeded 120s timeout during synthesis phase", "partial_findings_count": 0}
```

---

## Schema 2: Run Metadata JSONL

**File naming:** `run_metadata.jsonl` (single file per review run)

**Structure:** Single JSON object (one line)

### Complete Schema

```json
{
  "schema_version": "1.0.0",
  "type": "run_metadata",

  "run": {
    "id": "parallax-review-v3",
    "topic": "parallax-review-v1",
    "iteration": 3,
    "date": "2026-02-15T10:30:00Z",
    "stage": "design",
    "design_doc": "docs/plans/2026-02-15-parallax-review-design.md",
    "requirements_doc": "docs/problem-statements/design-orchestrator.md"
  },

  "prompts": {
    "stable_version": "1.0.0",
    "calibration_version": "2.3.0"
  },

  "model": {
    "vendor": "anthropic",
    "default_model_id": "claude-sonnet-4-5-20250929",
    "overrides": {}
  },

  "reviewers": [
    {
      "name": "assumption-hunter",
      "status": "completed",
      "model_id": "claude-sonnet-4-5-20250929",
      "tokens": {
        "input": 12450,
        "output": 3200,
        "cache_creation": 8500,
        "cache_read": 8500
      },
      "duration_seconds": 45.2,
      "findings_count": 12,
      "cost_usd": 0.08
    },
    {
      "name": "edge-case-prober",
      "status": "failed",
      "model_id": "claude-sonnet-4-5-20250929",
      "error": "timeout_after_120s",
      "tokens": null,
      "duration_seconds": 120.0,
      "findings_count": 0,
      "cost_usd": 0.0
    }
  ],

  "summary": {
    "reviewers_completed": 5,
    "reviewers_total": 6,
    "total_findings": 83,
    "findings_by_severity": {
      "Critical": 22,
      "Important": 47,
      "Minor": 14
    },
    "verdict": "revise",
    "total_cost_usd": 0.45,
    "total_duration_seconds": 312.5
  },

  "parameters": {
    "timeout_per_reviewer_seconds": 120,
    "minimum_reviewers_threshold": 4,
    "pattern_extraction_threshold": 50
  }
}
```

### Field Specifications

**run:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for this review execution |
| `topic` | string | User-provided topic label (folder name) |
| `iteration` | number | Iteration number (increments with each re-review) |
| `date` | string (ISO8601) | When review started |
| `stage` | string | `"requirements"` \| `"design"` \| `"plan"` |
| `design_doc` | string | Path to design artifact |
| `requirements_doc` | string | Path to requirements artifact |

**prompts:**

| Field | Type | Description |
|-------|------|-------------|
| `stable_version` | string | Version of cached persona/methodology/format (semver) |
| `calibration_version` | string | Version of calibration rules (changes frequently, semver) |

**model:**

| Field | Type | Description |
|-------|------|-------------|
| `vendor` | string | `"anthropic"` \| `"openai"` \| `"google"` |
| `default_model_id` | string | Model used unless overridden |
| `overrides` | object | Map of `reviewer_name → model_id` for per-reviewer tiering |

**reviewers[]:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Reviewer identifier |
| `status` | string | Yes | `"completed"` \| `"failed"` \| `"partial"` |
| `model_id` | string | Yes | Actual model used for this reviewer |
| `tokens` | object\|null | Yes | Token breakdown, null if failed before completion |
| `tokens.input` | number | If completed | Input tokens consumed |
| `tokens.output` | number | If completed | Output tokens generated |
| `tokens.cache_creation` | number | If completed | Tokens written to cache (0 if cache hit) |
| `tokens.cache_read` | number | If completed | Tokens read from cache (0 if cache miss) |
| `duration_seconds` | number | Yes | Wall clock time (includes retries) |
| `findings_count` | number | Yes | Number of findings produced (0 if failed) |
| `cost_usd` | number | Yes | Cost in USD (calculated from tokens + model pricing) |
| `error` | string | If failed | Error code |

**summary:**

| Field | Type | Description |
|-------|------|-------------|
| `reviewers_completed` | number | Count of completed reviewers |
| `reviewers_total` | number | Total reviewers dispatched |
| `total_findings` | number | Sum of findings across all reviewers |
| `findings_by_severity` | object | Breakdown: `{"Critical": N, "Important": N, "Minor": N}` |
| `verdict` | string | `"proceed"` \| `"revise"` \| `"escalate"` (computed by synthesizer) |
| `total_cost_usd` | number | Sum of per-reviewer costs |
| `total_duration_seconds` | number | Wall clock time for entire review |

**parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `timeout_per_reviewer_seconds` | number | Timeout configuration (FR7.2) |
| `minimum_reviewers_threshold` | number | Partial success threshold (FR7.1) |
| `pattern_extraction_threshold` | number | Finding count for interactive processing (FR10.4) |

---

## Schema 3: Pattern Extraction JSON

**File naming:** `patterns-v{N}.json` (e.g., `patterns-v3.json`)

**Structure:** Single JSON object (not JSONL)

### Complete Schema

```json
{
  "schema_version": "1.0.0",
  "type": "pattern_extraction",

  "metadata": {
    "review_run_id": "parallax-review-v3",
    "iteration": 3,
    "extraction_date": "2026-02-15T11:45:00Z",
    "total_findings": 83,
    "patterns_extracted": 12,
    "extraction_model": "claude-sonnet-4-5-20250929"
  },

  "patterns": [
    {
      "pattern_id": "p1",
      "title": "Missing authentication requirements",
      "finding_ids": [
        "v3-assumption-hunter-001",
        "v3-edge-case-prober-005",
        "v3-requirement-auditor-003"
      ],
      "finding_count": 3,
      "severity_range": ["Critical", "Important"],
      "affected_phases": {
        "primary": ["calibrate", "design"],
        "contributing": ["survey"]
      },
      "summary": "Multiple findings indicate that authentication and authorization requirements are missing or underspecified. Findings span requirement-level gaps (no auth specified) and design-level assumptions (endpoints assumed internal-only).",
      "actionable_next_step": "Add security requirements section to requirements doc, specifying authentication method, authorization model, and session management strategy.",
      "reviewers": ["assumption-hunter", "edge-case-prober", "requirement-auditor"]
    }
  ],

  "systemic_issues": [
    {
      "contributing_phase": "calibrate",
      "finding_count": 11,
      "percentage": 68.75,
      "threshold_exceeded": true,
      "description": "68% of findings with contributing phase trace to calibrate gaps, indicating systemic requirement quality issues."
    }
  ]
}
```

### Field Specifications

**metadata:**

| Field | Type | Description |
|-------|------|-------------|
| `review_run_id` | string | Links to run metadata |
| `iteration` | number | Iteration number |
| `extraction_date` | string (ISO8601) | When pattern extraction ran |
| `total_findings` | number | Total findings analyzed |
| `patterns_extracted` | number | Number of patterns identified (≤15 per FR10.1) |
| `extraction_model` | string | Model used for pattern extraction |

**patterns[]:**

| Field | Type | Description |
|-------|------|-------------|
| `pattern_id` | string | Simple sequential ID (p1, p2, ..., p15) |
| `title` | string | Pattern theme/title |
| `finding_ids` | array[string] | Finding IDs grouped under this pattern |
| `finding_count` | number | Length of finding_ids array |
| `severity_range` | array[string] | Unique severity values from grouped findings |
| `affected_phases.primary` | array[string] | Primary phases from grouped findings |
| `affected_phases.contributing` | array[string]\|null | Contributing phases, or null if none |
| `summary` | string | Semantic description of the pattern |
| `actionable_next_step` | string | What to do about this pattern |
| `reviewers` | array[string] | Reviewer names who flagged findings in this pattern |

**systemic_issues[]:**

| Field | Type | Description |
|-------|------|-------------|
| `contributing_phase` | string | Phase identified as systemic root cause |
| `finding_count` | number | Findings with this contributing phase |
| `percentage` | number | Percentage (finding_count / findings_with_contributing_phase_total) |
| `threshold_exceeded` | boolean | True if >30% (FR2.7 threshold) |
| `description` | string | Human-readable explanation |

**Constraints:**
- Maximum 15 patterns per extraction (FR10.1 cap)
- If >15 natural groupings exist, merge less critical patterns or rank by severity/consensus

---

## Schema 4: Delta Detection JSON

**File naming:** `delta-v{N-1}-v{N}.json` (e.g., `delta-v2-v3.json`)

**Structure:** Single JSON object comparing two pattern extraction runs

### Complete Schema

```json
{
  "schema_version": "1.0.0",
  "type": "delta_detection",

  "metadata": {
    "comparison": {
      "from_iteration": 2,
      "to_iteration": 3,
      "from_file": "patterns-v2.json",
      "to_file": "patterns-v3.json"
    },
    "detection_date": "2026-02-15T11:50:00Z",
    "detection_model": "claude-sonnet-4-5-20250929"
  },

  "summary": {
    "resolved_patterns": 3,
    "persisting_patterns": 5,
    "new_patterns": 4,
    "total_patterns_previous": 8,
    "total_patterns_current": 9
  },

  "resolved": [
    {
      "pattern_id_previous": "p2",
      "title": "Documentation debt",
      "resolution_evidence": "All 23 disposition items from v2 synchronized to design doc. Requirement Auditor v3 Finding 1 confirms resolution.",
      "affected_findings_resolved": 18
    }
  ],

  "persisting": [
    {
      "pattern_id_previous": "p1",
      "pattern_id_current": "p3",
      "title": "JSONL schema missing",
      "match_confidence": "high",
      "changes": {
        "finding_count_previous": 4,
        "finding_count_current": 4,
        "severity_escalation": false,
        "new_reviewers": []
      },
      "persistence_reason": "Acknowledged in requirements (FR7.5 dependency note) but schema not yet implemented. Deferred to Next Steps #5."
    }
  ],

  "new": [
    {
      "pattern_id_current": "p1",
      "title": "Auto-fix workflow safety concerns",
      "emergence_reason": "New design section added between v2 and v3 (Step 4: Auto-Fix). Pattern didn't exist in v2 because feature wasn't specified.",
      "affected_findings_count": 3,
      "severity_range": ["Critical"]
    }
  ],

  "insights": {
    "progress_summary": "Major improvement: documentation debt resolved (18 findings). New risks introduced: auto-fix workflow (3 Critical findings). Persistent blocker: JSONL schema (acknowledged, deferred).",
    "systemic_changes": {
      "v2_systemic_issue": "calibrate gaps (67% of findings)",
      "v3_systemic_issue": "calibrate gaps (68% of findings)",
      "interpretation": "Systemic issue persists despite documentation sync. Problem framing and build-vs-leverage decisions remain unaddressed."
    }
  }
}
```

### Field Specifications

**metadata:**

| Field | Type | Description |
|-------|------|-------------|
| `comparison.from_iteration` | number | Previous iteration number |
| `comparison.to_iteration` | number | Current iteration number |
| `comparison.from_file` | string | Previous pattern file |
| `comparison.to_file` | string | Current pattern file |
| `detection_date` | string (ISO8601) | When delta detection ran |
| `detection_model` | string | Model used for semantic matching |

**summary:**

| Field | Type | Description |
|-------|------|-------------|
| `resolved_patterns` | number | Patterns that no longer appear |
| `persisting_patterns` | number | Patterns that continue across iterations |
| `new_patterns` | number | Patterns that newly appeared |
| `total_patterns_previous` | number | Pattern count in v{N-1} |
| `total_patterns_current` | number | Pattern count in v{N} |

**resolved[]:**

| Field | Type | Description |
|-------|------|-------------|
| `pattern_id_previous` | string | Pattern ID from patterns-v{N-1}.json |
| `title` | string | Pattern title (from previous iteration) |
| `resolution_evidence` | string | Why this pattern is considered resolved |
| `affected_findings_resolved` | number | Count of findings that were part of this pattern |

**persisting[]:**

| Field | Type | Description |
|-------|------|-------------|
| `pattern_id_previous` | string | Pattern ID from v{N-1} |
| `pattern_id_current` | string | Pattern ID from v{N} (semantic match) |
| `title` | string | Pattern title (may differ slightly between iterations) |
| `match_confidence` | string | `"high"` \| `"medium"` \| `"low"` (LLM confidence in equivalence) |
| `changes.finding_count_previous` | number | Finding count in v{N-1} |
| `changes.finding_count_current` | number | Finding count in v{N} |
| `changes.severity_escalation` | boolean | True if severity increased |
| `changes.new_reviewers` | array[string] | Reviewers who flagged this pattern in v{N} but not v{N-1} |
| `persistence_reason` | string | Why this pattern wasn't resolved |

**new[]:**

| Field | Type | Description |
|-------|------|-------------|
| `pattern_id_current` | string | Pattern ID from patterns-v{N}.json |
| `title` | string | Pattern title |
| `emergence_reason` | string | Why this pattern appeared (new feature, missed before, etc.) |
| `affected_findings_count` | number | Finding count in v{N} |
| `severity_range` | array[string] | Severity values for this pattern |

**insights:**

| Field | Type | Description |
|-------|------|-------------|
| `progress_summary` | string | High-level narrative of what changed |
| `systemic_changes.v2_systemic_issue` | string | Systemic issue from previous iteration (if any) |
| `systemic_changes.v3_systemic_issue` | string | Systemic issue from current iteration (if any) |
| `systemic_changes.interpretation` | string | Comparison of systemic issues across iterations |

---

## Validation Rules

### Reviewer Findings JSONL

1. **File format:** Each line must be valid JSON
2. **Finding ID uniqueness:** Within a file, all finding IDs must be unique
3. **Finding ID format:** Must match `v\d+-[a-z-]+-\d{3}` (e.g., `v3-assumption-hunter-001`)
4. **Severity values:** Must be one of: `"Critical"`, `"Important"`, `"Minor"`
5. **Phase values:** Must be one of: `"survey"`, `"calibrate"`, `"design"`, `"plan"`, or `null` (for contributing only)
6. **Disposition values:** If present, must be: `"accepted"` or `"rejected"`
7. **Disposition completeness:** If `disposition` is set, `disposition_date` and `disposition_by` must also be set
8. **Object types:** Must be one of: `"finding"`, `"blind_spot_check"`, `"reviewer_metadata"`
9. **Blind spot check:** At most one per file
10. **Reviewer metadata:** Only present if status != "completed"

### Run Metadata JSONL

1. **File format:** Single line, valid JSON
2. **Reviewer names:** Must match filename pattern `[a-z-]+` (lowercase, hyphens only)
3. **Reviewer status:** Must be one of: `"completed"`, `"failed"`, `"partial"`
4. **Token fields:** Must be non-negative integers
5. **Cost calculation:** `cost_usd` should match calculated cost from tokens (warning if mismatch)
6. **Summary consistency:** `reviewers_completed + failed + partial == reviewers_total`
7. **Verdict values:** Must be one of: `"proceed"`, `"revise"`, `"escalate"`

### Pattern Extraction JSON

1. **Pattern count:** Maximum 15 patterns (FR10.1 cap)
2. **Pattern IDs:** Sequential (p1, p2, ..., p15)
3. **Finding references:** All `finding_ids` must reference valid findings from reviewer files
4. **Systemic threshold:** `threshold_exceeded` should be true only if `percentage > 30`

### Delta Detection JSON

1. **File references:** `from_file` and `to_file` must exist in same directory
2. **Iteration sequence:** `to_iteration == from_iteration + 1`
3. **Pattern references:** All pattern IDs must reference valid patterns in source files
4. **Match confidence:** Must be one of: `"high"`, `"medium"`, `"low"`

---

## Schema Evolution Strategy

### Versioning

- Use semantic versioning: `MAJOR.MINOR.PATCH`
- **MAJOR:** Breaking changes (field removal, type changes, structural changes)
- **MINOR:** Additive changes (new optional fields, new enum values)
- **PATCH:** Documentation clarifications, no schema changes

### Current Version: 1.0.0

Initial release. Implements FR6.1, NFR2.4, NFR2.5, FR10.1-FR10.5.

### Forward Compatibility

When reading files:
1. Check `schema_version` field first
2. If MAJOR version differs: warn user, attempt best-effort parsing
3. If MINOR version is newer: safely ignore unknown fields
4. If PATCH version differs: no special handling

### Backward Compatibility

When writing files:
1. Always include `schema_version` field
2. Never remove required fields in MINOR/PATCH updates
3. New optional fields must have sensible defaults when absent

---

## Implementation Notes

### Parsing Strategy

**Reviewer findings JSONL:**
```python
findings = []
blind_spot = None
metadata = None

for line in open("assumption-hunter.jsonl"):
    obj = json.loads(line)
    if obj["type"] == "finding":
        findings.append(obj)
    elif obj["type"] == "blind_spot_check":
        blind_spot = obj["content"]
    elif obj["type"] == "reviewer_metadata":
        metadata = obj
```

**Run metadata JSONL:**
```python
with open("run_metadata.jsonl") as f:
    metadata = json.loads(f.read())
```

### Rendering to Markdown

Synthesizer reads JSONL files and renders markdown:

1. Read `run_metadata.jsonl` for metadata
2. Read all `<reviewer>.jsonl` files for findings
3. Group findings by severity
4. Detect duplicates (synthesizer responsibility, not schema enforcement)
5. Generate `summary.md` and per-reviewer `.md` files

### Cost Calculation

```python
# Anthropic pricing (as of 2026-02-16)
PRICE_PER_MILLION = {
    "input": 3.00,           # $3/M input tokens
    "output": 15.00,         # $15/M output tokens
    "cache_write": 3.75,     # $3.75/M cache write
    "cache_read": 0.30       # $0.30/M cache read
}

def calculate_cost(tokens):
    return (
        tokens["input"] * PRICE_PER_MILLION["input"] / 1_000_000 +
        tokens["output"] * PRICE_PER_MILLION["output"] / 1_000_000 +
        tokens["cache_creation"] * PRICE_PER_MILLION["cache_write"] / 1_000_000 +
        tokens["cache_read"] * PRICE_PER_MILLION["cache_read"] / 1_000_000
    )
```

### Pattern Extraction Implementation

1. Read all reviewer findings
2. Use LLM to group semantically related findings (max 15 groups)
3. For each group: extract title, summary, actionable next step
4. Calculate systemic issues (FR2.7 logic: >30% threshold)
5. Write `patterns-v{N}.json`

### Delta Detection Implementation

1. Read `patterns-v{N-1}.json` and `patterns-v{N}.json`
2. Use LLM to semantically match patterns across iterations
3. Classify as resolved/persisting/new
4. For persisting: calculate changes (finding count, severity, reviewers)
5. Generate insights summary
6. Write `delta-v{N-1}-v{N}.json`

---

## Examples

### Complete Review Output (6 reviewers, 5 successful, 1 failed)

```
docs/reviews/parallax-review-v1/
├── run_metadata.jsonl                    # 1 line, ~2KB
├── assumption-hunter.jsonl               # 12 findings + blind spot, ~15KB
├── edge-case-prober.jsonl                # 1 line (stub), ~200B
├── feasibility-skeptic.jsonl             # 14 findings + blind spot, ~18KB
├── first-principles.jsonl                # 9 findings + blind spot, ~12KB
├── prior-art-scout.jsonl                 # 8 findings + blind spot, ~10KB
├── requirement-auditor.jsonl             # 18 findings + blind spot, ~22KB
├── patterns-v3.json                      # 12 patterns, ~8KB
├── delta-v2-v3.json                      # Delta analysis, ~6KB
├── summary.md                            # Rendered markdown, ~40KB
└── [6 reviewer].md files                 # Rendered markdown, ~80KB total
```

**Total storage:** ~213KB for complete review run (JSONL + JSON + rendered markdown)

**Token efficiency for synthesizer:**
- Reading 6 JSONL files: ~77KB = ~20k tokens
- vs reading 6 markdown files: ~120KB = ~30k tokens
- **Savings:** ~33% token reduction for synthesizer input

### Disposition Tracking Example

**Before processing** (assumption-hunter.jsonl line 1):
```json
{"type": "finding", "id": "v3-assumption-hunter-001", "title": "Auto-Fix Step Assumes...", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Step 4: Auto-Fix", "issue": "...", "why_it_matters": "...", "suggestion": "..."}
```

**After user accepts** (same line, appended):
```json
{"type": "finding", "id": "v3-assumption-hunter-001", "title": "Auto-Fix Step Assumes...", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Step 4: Auto-Fix", "issue": "...", "why_it_matters": "...", "suggestion": "...", "disposition": "accepted", "disposition_note": "Will add validation workflow before auto-apply", "disposition_date": "2026-02-16T14:23:00Z", "disposition_by": "user"}
```

**Git diff shows exactly what was decided:**
```diff
-{"type": "finding", "id": "v3-assumption-hunter-001", ..., "suggestion": "..."}
+{"type": "finding", "id": "v3-assumption-hunter-001", ..., "suggestion": "...", "disposition": "accepted", "disposition_note": "Will add validation workflow before auto-apply", "disposition_date": "2026-02-16T14:23:00Z", "disposition_by": "user"}
```

---

## Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| FR6.1 (JSONL canonical format) | Reviewer findings schema |
| FR6.2 (markdown rendered) | Markdown files generated from JSONL |
| FR4.3 (disposition tracking) | Inline disposition fields on finding objects |
| FR5.1 (finding ID format) | `v{iteration}-{reviewer}-{sequence}` enforced |
| NFR2.4 (per-reviewer tracking) | `reviewers[]` array in run metadata |
| NFR2.5 (run-level metadata) | `run`, `prompts`, `model`, `summary` in run metadata |
| FR10.1 (pattern extraction) | Pattern extraction JSON schema |
| FR10.2 (delta detection) | Delta detection JSON schema |
| FR7.5 (schema validation) | **Unblocked** - validation rules defined |

---

## Next Steps

1. **Implementation:**
   - Create JSON Schema files (`.schema.json`) for automated validation
   - Implement parsers for each schema type
   - Implement renderers (JSONL → markdown)
   - Add schema validation to FR7.5 (validate before synthesis)

2. **Testing:**
   - Validate existing v1 review output against schemas
   - Test disposition append workflow
   - Test pattern extraction with real findings
   - Test delta detection across v2→v3 iteration

3. **Documentation:**
   - Add schema documentation to reviewer prompts
   - Update design doc v4 with schema references
   - Update requirements doc: mark FR7.5 unblocked

4. **Integration:**
   - Update synthesizer to read JSONL instead of prompting reviewers for markdown
   - Update finding processing to append dispositions to JSONL
   - Implement pattern extraction + delta detection pipeline

---

## Design Decisions Summary

1. **Consolidated metadata** - Single `run_metadata.jsonl` file, not distributed across reviewer files
2. **Inline disposition** - Disposition fields appended to finding objects, not separate file
3. **Globally unique finding IDs** - Enforced at schema level, prevents collision
4. **JSONL for findings, JSON for analysis** - Streaming data vs read-only post-processing
5. **Explicit schema versioning** - Every file includes version, enables evolution
6. **Stub files for failures** - Failed reviewers get metadata-only JSONL file
7. **Pattern cap at 15** - Enforced per FR10.1, merge if >15 natural groupings
8. **Semantic delta detection** - LLM-based matching, not text hashing (supports Q3 resolution)
