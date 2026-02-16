# JSONL Schema Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create JSON Schema files and validation tooling to unblock FR7.5 (schema validation before synthesis)

**Architecture:** JSON Schema specification files + Python validation script. No runtime implementation yet—just schema artifacts and validation. Future implementation will use these schemas for validation in the review pipeline.

**Tech Stack:** JSON Schema (Draft 2020-12), Python 3.11+, jsonschema library

---

## Prerequisites

**Check Python environment:**
```bash
python3 --version  # Should be 3.11+
pip3 show jsonschema || pip3 install jsonschema
```

---

## Task 1: Create Reviewer Findings Schema

**Files:**
- Create: `schemas/reviewer-findings-v1.0.0.schema.json`
- Reference: `docs/plans/2026-02-16-jsonl-schema-design.md` (Schema 1)

**Step 1: Create schemas directory**

```bash
mkdir -p schemas
```

**Step 2: Write JSON Schema for reviewer findings**

Create `schemas/reviewer-findings-v1.0.0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/nichenke/parallax/schemas/reviewer-findings-v1.0.0.schema.json",
  "title": "Parallax Reviewer Findings",
  "description": "Schema for reviewer findings JSONL output",
  "type": "object",
  "oneOf": [
    { "$ref": "#/$defs/finding" },
    { "$ref": "#/$defs/blind_spot_check" },
    { "$ref": "#/$defs/reviewer_metadata" }
  ],
  "$defs": {
    "finding": {
      "type": "object",
      "required": ["type", "id", "title", "severity", "phase", "section", "issue", "why_it_matters", "suggestion"],
      "properties": {
        "type": { "const": "finding" },
        "id": {
          "type": "string",
          "pattern": "^v\\d+-[a-z-]+-\\d{3}$",
          "description": "Format: v{iteration}-{reviewer}-{sequence}"
        },
        "title": { "type": "string", "minLength": 1 },
        "severity": {
          "type": "string",
          "enum": ["Critical", "Important", "Minor"]
        },
        "phase": {
          "type": "object",
          "required": ["primary", "contributing"],
          "properties": {
            "primary": {
              "type": "string",
              "enum": ["survey", "calibrate", "design", "plan"]
            },
            "contributing": {
              "oneOf": [
                { "type": "null" },
                { "type": "string", "enum": ["survey", "calibrate", "design", "plan"] }
              ]
            }
          }
        },
        "section": { "type": "string", "minLength": 1 },
        "issue": { "type": "string", "minLength": 1 },
        "why_it_matters": { "type": "string", "minLength": 1 },
        "suggestion": { "type": "string", "minLength": 1 },
        "disposition": {
          "type": "string",
          "enum": ["accepted", "rejected"]
        },
        "disposition_note": { "type": "string" },
        "disposition_date": {
          "type": "string",
          "format": "date-time"
        },
        "disposition_by": {
          "type": "string",
          "enum": ["user", "auto"]
        }
      },
      "allOf": [
        {
          "if": {
            "properties": { "disposition": { "type": "string" } },
            "required": ["disposition"]
          },
          "then": {
            "required": ["disposition_date", "disposition_by"]
          }
        }
      ]
    },
    "blind_spot_check": {
      "type": "object",
      "required": ["type", "content"],
      "properties": {
        "type": { "const": "blind_spot_check" },
        "content": { "type": "string", "minLength": 1 }
      }
    },
    "reviewer_metadata": {
      "type": "object",
      "required": ["type", "reviewer", "status", "partial_findings_count"],
      "properties": {
        "type": { "const": "reviewer_metadata" },
        "reviewer": {
          "type": "string",
          "pattern": "^[a-z-]+$"
        },
        "status": {
          "type": "string",
          "enum": ["completed", "failed", "partial"]
        },
        "error": { "type": "string" },
        "error_message": { "type": "string" },
        "partial_findings_count": {
          "type": "integer",
          "minimum": 0
        }
      },
      "allOf": [
        {
          "if": {
            "properties": { "status": { "enum": ["failed", "partial"] } }
          },
          "then": {
            "required": ["error"]
          }
        }
      ]
    }
  }
}
```

**Step 3: Commit**

```bash
git add schemas/reviewer-findings-v1.0.0.schema.json
git commit -m "feat(schemas): add reviewer findings JSON Schema v1.0.0

Implements validation for:
- Finding objects (with disposition tracking)
- Blind spot checks
- Reviewer metadata (failure stubs)

Unblocks FR7.5 (schema validation).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Create Run Metadata Schema

**Files:**
- Create: `schemas/run-metadata-v1.0.0.schema.json`
- Reference: `docs/plans/2026-02-16-jsonl-schema-design.md` (Schema 2)

**Step 1: Write JSON Schema for run metadata**

Create `schemas/run-metadata-v1.0.0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/nichenke/parallax/schemas/run-metadata-v1.0.0.schema.json",
  "title": "Parallax Run Metadata",
  "description": "Schema for run metadata JSONL output",
  "type": "object",
  "required": ["schema_version", "type", "run", "prompts", "model", "reviewers", "summary", "parameters"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version (MAJOR.MINOR.PATCH)"
    },
    "type": { "const": "run_metadata" },
    "run": {
      "type": "object",
      "required": ["id", "topic", "iteration", "date", "stage", "design_doc", "requirements_doc"],
      "properties": {
        "id": { "type": "string", "minLength": 1 },
        "topic": { "type": "string", "minLength": 1 },
        "iteration": { "type": "integer", "minimum": 1 },
        "date": { "type": "string", "format": "date-time" },
        "stage": {
          "type": "string",
          "enum": ["requirements", "design", "plan"]
        },
        "design_doc": { "type": "string", "minLength": 1 },
        "requirements_doc": { "type": "string", "minLength": 1 }
      }
    },
    "prompts": {
      "type": "object",
      "required": ["stable_version", "calibration_version"],
      "properties": {
        "stable_version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "calibration_version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        }
      }
    },
    "model": {
      "type": "object",
      "required": ["vendor", "default_model_id", "overrides"],
      "properties": {
        "vendor": {
          "type": "string",
          "enum": ["anthropic", "openai", "google"]
        },
        "default_model_id": { "type": "string", "minLength": 1 },
        "overrides": {
          "type": "object",
          "patternProperties": {
            "^[a-z-]+$": { "type": "string" }
          }
        }
      }
    },
    "reviewers": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "status", "model_id", "duration_seconds", "findings_count", "cost_usd"],
        "properties": {
          "name": {
            "type": "string",
            "pattern": "^[a-z-]+$"
          },
          "status": {
            "type": "string",
            "enum": ["completed", "failed", "partial"]
          },
          "model_id": { "type": "string", "minLength": 1 },
          "tokens": {
            "oneOf": [
              { "type": "null" },
              {
                "type": "object",
                "required": ["input", "output", "cache_creation", "cache_read"],
                "properties": {
                  "input": { "type": "integer", "minimum": 0 },
                  "output": { "type": "integer", "minimum": 0 },
                  "cache_creation": { "type": "integer", "minimum": 0 },
                  "cache_read": { "type": "integer", "minimum": 0 }
                }
              }
            ]
          },
          "duration_seconds": { "type": "number", "minimum": 0 },
          "findings_count": { "type": "integer", "minimum": 0 },
          "cost_usd": { "type": "number", "minimum": 0 },
          "error": { "type": "string" }
        },
        "allOf": [
          {
            "if": {
              "properties": { "status": { "const": "completed" } }
            },
            "then": {
              "required": ["tokens"],
              "properties": {
                "tokens": { "type": "object" }
              }
            }
          },
          {
            "if": {
              "properties": { "status": { "enum": ["failed", "partial"] } }
            },
            "then": {
              "required": ["error"]
            }
          }
        ]
      }
    },
    "summary": {
      "type": "object",
      "required": ["reviewers_completed", "reviewers_total", "total_findings", "findings_by_severity", "verdict", "total_cost_usd", "total_duration_seconds"],
      "properties": {
        "reviewers_completed": { "type": "integer", "minimum": 0 },
        "reviewers_total": { "type": "integer", "minimum": 1 },
        "total_findings": { "type": "integer", "minimum": 0 },
        "findings_by_severity": {
          "type": "object",
          "required": ["Critical", "Important", "Minor"],
          "properties": {
            "Critical": { "type": "integer", "minimum": 0 },
            "Important": { "type": "integer", "minimum": 0 },
            "Minor": { "type": "integer", "minimum": 0 }
          }
        },
        "verdict": {
          "type": "string",
          "enum": ["proceed", "revise", "escalate"]
        },
        "total_cost_usd": { "type": "number", "minimum": 0 },
        "total_duration_seconds": { "type": "number", "minimum": 0 }
      }
    },
    "parameters": {
      "type": "object",
      "required": ["timeout_per_reviewer_seconds", "minimum_reviewers_threshold", "pattern_extraction_threshold"],
      "properties": {
        "timeout_per_reviewer_seconds": { "type": "integer", "minimum": 1 },
        "minimum_reviewers_threshold": { "type": "integer", "minimum": 1 },
        "pattern_extraction_threshold": { "type": "integer", "minimum": 1 }
      }
    }
  }
}
```

**Step 2: Commit**

```bash
git add schemas/run-metadata-v1.0.0.schema.json
git commit -m "feat(schemas): add run metadata JSON Schema v1.0.0

Implements validation for:
- Run-level metadata (topic, stage, artifacts)
- Prompt version tracking (stable + calibration)
- Per-reviewer tracking (tokens, cost, duration)
- Summary aggregation (findings, verdict, cost)

Supports NFR2.4, NFR2.5 (cost/token tracking).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create Pattern Extraction Schema

**Files:**
- Create: `schemas/pattern-extraction-v1.0.0.schema.json`
- Reference: `docs/plans/2026-02-16-jsonl-schema-design.md` (Schema 3)

**Step 1: Write JSON Schema for pattern extraction**

Create `schemas/pattern-extraction-v1.0.0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/nichenke/parallax/schemas/pattern-extraction-v1.0.0.schema.json",
  "title": "Parallax Pattern Extraction",
  "description": "Schema for pattern extraction JSON output",
  "type": "object",
  "required": ["schema_version", "type", "metadata", "patterns", "systemic_issues"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "type": { "const": "pattern_extraction" },
    "metadata": {
      "type": "object",
      "required": ["review_run_id", "iteration", "extraction_date", "total_findings", "patterns_extracted", "extraction_model"],
      "properties": {
        "review_run_id": { "type": "string", "minLength": 1 },
        "iteration": { "type": "integer", "minimum": 1 },
        "extraction_date": { "type": "string", "format": "date-time" },
        "total_findings": { "type": "integer", "minimum": 0 },
        "patterns_extracted": {
          "type": "integer",
          "minimum": 0,
          "maximum": 15,
          "description": "Maximum 15 patterns per FR10.1"
        },
        "extraction_model": { "type": "string", "minLength": 1 }
      }
    },
    "patterns": {
      "type": "array",
      "maxItems": 15,
      "items": {
        "type": "object",
        "required": ["pattern_id", "title", "finding_ids", "finding_count", "severity_range", "affected_phases", "summary", "actionable_next_step", "reviewers"],
        "properties": {
          "pattern_id": {
            "type": "string",
            "pattern": "^p\\d+$",
            "description": "Format: p1, p2, ..., p15"
          },
          "title": { "type": "string", "minLength": 1 },
          "finding_ids": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "pattern": "^v\\d+-[a-z-]+-\\d{3}$"
            }
          },
          "finding_count": {
            "type": "integer",
            "minimum": 1
          },
          "severity_range": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "enum": ["Critical", "Important", "Minor"]
            }
          },
          "affected_phases": {
            "type": "object",
            "required": ["primary", "contributing"],
            "properties": {
              "primary": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["survey", "calibrate", "design", "plan"]
                }
              },
              "contributing": {
                "oneOf": [
                  { "type": "null" },
                  {
                    "type": "array",
                    "items": {
                      "type": "string",
                      "enum": ["survey", "calibrate", "design", "plan"]
                    }
                  }
                ]
              }
            }
          },
          "summary": { "type": "string", "minLength": 1 },
          "actionable_next_step": { "type": "string", "minLength": 1 },
          "reviewers": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "pattern": "^[a-z-]+$"
            }
          }
        }
      }
    },
    "systemic_issues": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["contributing_phase", "finding_count", "percentage", "threshold_exceeded", "description"],
        "properties": {
          "contributing_phase": {
            "type": "string",
            "enum": ["survey", "calibrate", "design", "plan"]
          },
          "finding_count": { "type": "integer", "minimum": 1 },
          "percentage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
          },
          "threshold_exceeded": {
            "type": "boolean",
            "description": "True if >30% per FR2.7"
          },
          "description": { "type": "string", "minLength": 1 }
        }
      }
    }
  }
}
```

**Step 2: Commit**

```bash
git add schemas/pattern-extraction-v1.0.0.schema.json
git commit -m "feat(schemas): add pattern extraction JSON Schema v1.0.0

Implements validation for:
- Pattern grouping (15 pattern cap per FR10.1)
- Finding references (globally unique IDs)
- Systemic issue detection (30% threshold per FR2.7)
- Actionable next steps

Supports FR10.1-FR10.5 (post-synthesis analysis).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create Delta Detection Schema

**Files:**
- Create: `schemas/delta-detection-v1.0.0.schema.json`
- Reference: `docs/plans/2026-02-16-jsonl-schema-design.md` (Schema 4)

**Step 1: Write JSON Schema for delta detection**

Create `schemas/delta-detection-v1.0.0.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/nichenke/parallax/schemas/delta-detection-v1.0.0.schema.json",
  "title": "Parallax Delta Detection",
  "description": "Schema for delta detection JSON output",
  "type": "object",
  "required": ["schema_version", "type", "metadata", "summary", "resolved", "persisting", "new", "insights"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "type": { "const": "delta_detection" },
    "metadata": {
      "type": "object",
      "required": ["comparison", "detection_date", "detection_model"],
      "properties": {
        "comparison": {
          "type": "object",
          "required": ["from_iteration", "to_iteration", "from_file", "to_file"],
          "properties": {
            "from_iteration": { "type": "integer", "minimum": 1 },
            "to_iteration": { "type": "integer", "minimum": 2 },
            "from_file": { "type": "string", "pattern": "^patterns-v\\d+\\.json$" },
            "to_file": { "type": "string", "pattern": "^patterns-v\\d+\\.json$" }
          }
        },
        "detection_date": { "type": "string", "format": "date-time" },
        "detection_model": { "type": "string", "minLength": 1 }
      }
    },
    "summary": {
      "type": "object",
      "required": ["resolved_patterns", "persisting_patterns", "new_patterns", "total_patterns_previous", "total_patterns_current"],
      "properties": {
        "resolved_patterns": { "type": "integer", "minimum": 0 },
        "persisting_patterns": { "type": "integer", "minimum": 0 },
        "new_patterns": { "type": "integer", "minimum": 0 },
        "total_patterns_previous": { "type": "integer", "minimum": 0 },
        "total_patterns_current": { "type": "integer", "minimum": 0 }
      }
    },
    "resolved": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern_id_previous", "title", "resolution_evidence", "affected_findings_resolved"],
        "properties": {
          "pattern_id_previous": {
            "type": "string",
            "pattern": "^p\\d+$"
          },
          "title": { "type": "string", "minLength": 1 },
          "resolution_evidence": { "type": "string", "minLength": 1 },
          "affected_findings_resolved": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "persisting": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern_id_previous", "pattern_id_current", "title", "match_confidence", "changes", "persistence_reason"],
        "properties": {
          "pattern_id_previous": {
            "type": "string",
            "pattern": "^p\\d+$"
          },
          "pattern_id_current": {
            "type": "string",
            "pattern": "^p\\d+$"
          },
          "title": { "type": "string", "minLength": 1 },
          "match_confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"]
          },
          "changes": {
            "type": "object",
            "required": ["finding_count_previous", "finding_count_current", "severity_escalation", "new_reviewers"],
            "properties": {
              "finding_count_previous": { "type": "integer", "minimum": 0 },
              "finding_count_current": { "type": "integer", "minimum": 0 },
              "severity_escalation": { "type": "boolean" },
              "new_reviewers": {
                "type": "array",
                "items": {
                  "type": "string",
                  "pattern": "^[a-z-]+$"
                }
              }
            }
          },
          "persistence_reason": { "type": "string", "minLength": 1 }
        }
      }
    },
    "new": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern_id_current", "title", "emergence_reason", "affected_findings_count", "severity_range"],
        "properties": {
          "pattern_id_current": {
            "type": "string",
            "pattern": "^p\\d+$"
          },
          "title": { "type": "string", "minLength": 1 },
          "emergence_reason": { "type": "string", "minLength": 1 },
          "affected_findings_count": { "type": "integer", "minimum": 1 },
          "severity_range": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "enum": ["Critical", "Important", "Minor"]
            }
          }
        }
      }
    },
    "insights": {
      "type": "object",
      "required": ["progress_summary", "systemic_changes"],
      "properties": {
        "progress_summary": { "type": "string", "minLength": 1 },
        "systemic_changes": {
          "type": "object",
          "properties": {
            "v2_systemic_issue": { "type": "string" },
            "v3_systemic_issue": { "type": "string" },
            "interpretation": { "type": "string", "minLength": 1 }
          }
        }
      }
    }
  }
}
```

**Step 2: Commit**

```bash
git add schemas/delta-detection-v1.0.0.schema.json
git commit -m "feat(schemas): add delta detection JSON Schema v1.0.0

Implements validation for:
- Resolved patterns (no longer appear)
- Persisting patterns (semantic matching across iterations)
- New patterns (newly emerged)
- Cross-iteration insights

Supports FR10.2 (delta detection), FR5.2 (cross-iteration tracking).

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Create Validation Script

**Files:**
- Create: `scripts/validate-schemas.py`
- Create: `scripts/requirements.txt`

**Step 1: Create scripts directory and requirements**

```bash
mkdir -p scripts
```

Create `scripts/requirements.txt`:

```
jsonschema==4.21.1
```

**Step 2: Write validation script**

Create `scripts/validate-schemas.py`:

```python
#!/usr/bin/env python3
"""
Validate JSONL/JSON files against parallax schemas.

Usage:
    python3 scripts/validate-schemas.py docs/reviews/parallax-review-v1/
    python3 scripts/validate-schemas.py --file assumption-hunter.jsonl --schema reviewer-findings
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import jsonschema
from jsonschema import Draft202012Validator


SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
SCHEMA_MAPPING = {
    "reviewer-findings": "reviewer-findings-v1.0.0.schema.json",
    "run-metadata": "run-metadata-v1.0.0.schema.json",
    "pattern-extraction": "pattern-extraction-v1.0.0.schema.json",
    "delta-detection": "delta-detection-v1.0.0.schema.json",
}


def load_schema(schema_name: str) -> dict:
    """Load JSON Schema from schemas/ directory."""
    schema_file = SCHEMA_DIR / SCHEMA_MAPPING[schema_name]
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema not found: {schema_file}")

    with open(schema_file) as f:
        return json.load(f)


def validate_jsonl_line(line_num: int, line: str, schema: dict) -> Tuple[bool, str]:
    """Validate a single JSONL line against schema."""
    try:
        obj = json.loads(line)
    except json.JSONDecodeError as e:
        return False, f"Line {line_num}: Invalid JSON: {e}"

    try:
        Draft202012Validator(schema).validate(obj)
        return True, ""
    except jsonschema.ValidationError as e:
        return False, f"Line {line_num}: Validation error: {e.message}"


def validate_jsonl_file(file_path: Path, schema_name: str) -> Tuple[bool, List[str]]:
    """Validate entire JSONL file."""
    schema = load_schema(schema_name)
    errors = []

    with open(file_path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            valid, error = validate_jsonl_line(line_num, line, schema)
            if not valid:
                errors.append(error)

    return len(errors) == 0, errors


def validate_json_file(file_path: Path, schema_name: str) -> Tuple[bool, List[str]]:
    """Validate entire JSON file."""
    schema = load_schema(schema_name)
    errors = []

    with open(file_path) as f:
        try:
            obj = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]

    try:
        Draft202012Validator(schema).validate(obj)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [f"Validation error: {e.message}"]


def detect_schema_type(file_path: Path) -> str:
    """Auto-detect schema type from filename."""
    name = file_path.name

    if name == "run_metadata.jsonl":
        return "run-metadata"
    elif name.startswith("patterns-v") and name.endswith(".json"):
        return "pattern-extraction"
    elif name.startswith("delta-v") and name.endswith(".json"):
        return "delta-detection"
    elif name.endswith(".jsonl"):
        return "reviewer-findings"
    else:
        raise ValueError(f"Cannot detect schema type for: {name}")


def validate_directory(dir_path: Path) -> Tuple[int, int]:
    """Validate all files in a review directory."""
    total = 0
    passed = 0

    for file_path in sorted(dir_path.glob("*.jsonl")) + sorted(dir_path.glob("*.json")):
        # Skip markdown files
        if file_path.suffix == ".md":
            continue

        try:
            schema_name = detect_schema_type(file_path)
        except ValueError as e:
            print(f"⚠️  SKIP {file_path.name}: {e}")
            continue

        total += 1

        if file_path.suffix == ".jsonl":
            valid, errors = validate_jsonl_file(file_path, schema_name)
        else:
            valid, errors = validate_json_file(file_path, schema_name)

        if valid:
            print(f"✅ PASS {file_path.name} ({schema_name})")
            passed += 1
        else:
            print(f"❌ FAIL {file_path.name} ({schema_name})")
            for error in errors:
                print(f"   {error}")

    return total, passed


def main():
    parser = argparse.ArgumentParser(description="Validate parallax schema files")
    parser.add_argument("path", help="Directory or file to validate")
    parser.add_argument("--file", action="store_true", help="Treat path as single file")
    parser.add_argument("--schema", choices=SCHEMA_MAPPING.keys(), help="Schema type (for single file)")

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)

    if args.file:
        # Single file validation
        schema_name = args.schema or detect_schema_type(path)

        if path.suffix == ".jsonl":
            valid, errors = validate_jsonl_file(path, schema_name)
        else:
            valid, errors = validate_json_file(path, schema_name)

        if valid:
            print(f"✅ PASS {path.name} ({schema_name})")
            sys.exit(0)
        else:
            print(f"❌ FAIL {path.name} ({schema_name})")
            for error in errors:
                print(f"   {error}")
            sys.exit(1)
    else:
        # Directory validation
        if not path.is_dir():
            print(f"Error: Not a directory: {path}")
            sys.exit(1)

        print(f"Validating directory: {path}\n")
        total, passed = validate_directory(path)

        print(f"\n{'='*60}")
        print(f"Results: {passed}/{total} files passed")
        print(f"{'='*60}")

        sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
```

**Step 3: Make script executable**

```bash
chmod +x scripts/validate-schemas.py
```

**Step 4: Test script on itself (should fail gracefully)**

```bash
python3 scripts/validate-schemas.py scripts/
```

Expected: "SKIP" messages (no .jsonl/.json files in scripts/)

**Step 5: Commit**

```bash
git add scripts/validate-schemas.py scripts/requirements.txt
git commit -m "feat(scripts): add schema validation script

Implements:
- JSONL line-by-line validation
- JSON file validation
- Auto-detection of schema type from filename
- Directory batch validation

Unblocks FR7.5 (schema validation before synthesis).

Usage:
  python3 scripts/validate-schemas.py docs/reviews/<topic>/
  python3 scripts/validate-schemas.py --file <file> --schema <type>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Test with Existing Review Output

**Files:**
- Test: `docs/reviews/parallax-review-v1/*.md` (convert to JSONL for testing)

**Step 1: Install dependencies**

```bash
pip3 install -r scripts/requirements.txt
```

**Step 2: Create test fixture (minimal valid finding)**

Create `tests/fixtures/valid-finding.jsonl`:

```bash
mkdir -p tests/fixtures
cat > tests/fixtures/valid-finding.jsonl << 'EOF'
{"type": "finding", "id": "v3-assumption-hunter-001", "title": "Test Finding", "severity": "Critical", "phase": {"primary": "design", "contributing": null}, "section": "Test Section", "issue": "This is a test issue", "why_it_matters": "Testing", "suggestion": "Fix it"}
{"type": "blind_spot_check", "content": "I may have missed implementation details."}
EOF
```

**Step 3: Test validation script**

```bash
python3 scripts/validate-schemas.py --file tests/fixtures/valid-finding.jsonl --schema reviewer-findings
```

Expected output:
```
✅ PASS valid-finding.jsonl (reviewer-findings)
```

**Step 4: Create invalid test fixture**

Create `tests/fixtures/invalid-finding.jsonl`:

```bash
cat > tests/fixtures/invalid-finding.jsonl << 'EOF'
{"type": "finding", "id": "invalid-id-format", "title": "Bad Finding", "severity": "VeryBad", "phase": {"primary": "design"}, "section": "Test"}
EOF
```

**Step 5: Test validation failure**

```bash
python3 scripts/validate-schemas.py --file tests/fixtures/invalid-finding.jsonl --schema reviewer-findings
```

Expected output (should fail):
```
❌ FAIL invalid-finding.jsonl (reviewer-findings)
   Line 1: Validation error: ...
```

**Step 6: Commit test fixtures**

```bash
git add tests/fixtures/
git commit -m "test: add schema validation test fixtures

Valid and invalid JSONL examples for:
- Reviewer findings (finding + blind spot)
- Invalid ID format
- Invalid severity enum

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Document Usage

**Files:**
- Create: `schemas/README.md`

**Step 1: Write schema documentation**

Create `schemas/README.md`:

```markdown
# Parallax JSONL Schemas

JSON Schema specifications for parallax:review output artifacts.

## Schema Files

| Schema | Version | File | Description |
|--------|---------|------|-------------|
| Reviewer Findings | 1.0.0 | `reviewer-findings-v1.0.0.schema.json` | Per-reviewer findings JSONL |
| Run Metadata | 1.0.0 | `run-metadata-v1.0.0.schema.json` | Run-level + per-reviewer tracking |
| Pattern Extraction | 1.0.0 | `pattern-extraction-v1.0.0.schema.json` | Post-synthesis pattern grouping |
| Delta Detection | 1.0.0 | `delta-detection-v1.0.0.schema.json` | Cross-iteration comparison |

## Validation

**Validate entire review directory:**
```bash
python3 scripts/validate-schemas.py docs/reviews/parallax-review-v1/
```

**Validate single file:**
```bash
python3 scripts/validate-schemas.py --file assumption-hunter.jsonl --schema reviewer-findings
```

**Auto-detection:**
Schema type is auto-detected from filename:
- `run_metadata.jsonl` → run-metadata
- `patterns-v3.json` → pattern-extraction
- `delta-v2-v3.json` → delta-detection
- `*.jsonl` → reviewer-findings

## Schema Evolution

Schemas use semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR:** Breaking changes (field removal, type changes)
- **MINOR:** Additive changes (new optional fields)
- **PATCH:** Documentation only

Current version: **1.0.0**

## Requirements Traceability

| Requirement | Schema | Implementation |
|-------------|--------|----------------|
| FR6.1 (JSONL canonical format) | Reviewer Findings | ✅ |
| FR4.3 (disposition tracking) | Reviewer Findings | ✅ (inline fields) |
| FR5.1 (finding ID format) | Reviewer Findings | ✅ (pattern validation) |
| NFR2.4 (per-reviewer tracking) | Run Metadata | ✅ (reviewers[] array) |
| NFR2.5 (run-level metadata) | Run Metadata | ✅ (run, prompts, model) |
| FR10.1 (pattern extraction) | Pattern Extraction | ✅ (15 pattern cap) |
| FR10.2 (delta detection) | Delta Detection | ✅ (semantic matching) |
| FR7.5 (schema validation) | All | ✅ **UNBLOCKED** |

## Design Reference

Full schema design documentation: `docs/plans/2026-02-16-jsonl-schema-design.md`
```

**Step 2: Commit**

```bash
git add schemas/README.md
git commit -m "docs: add schema validation README

Documents:
- Schema file mapping
- Validation usage
- Schema evolution strategy
- Requirements traceability

FR7.5 now unblocked.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Update Requirements Doc

**Files:**
- Modify: `docs/requirements/parallax-review-requirements-v1.md`

**Step 1: Remove FR7.5 blocker note**

Find and update this line (around line 226):

```diff
-**FR7.5:** Validate reviewer JSONL output before synthesis (schema check, retry on malformed JSON)
-- **Dependency:** Blocked on JSONL schema definition (Next Steps #5)
+**FR7.5:** Validate reviewer JSONL output before synthesis (schema check, retry on malformed JSON)
+- **Schema:** `schemas/reviewer-findings-v1.0.0.schema.json`
+- **Validator:** `scripts/validate-schemas.py`
```

**Step 2: Mark Next Steps #5 complete**

Find Next Steps section (around line 601) and update:

```diff
-5. **JSONL schema implementation** — Define exact structure (blocks FR7.5 validation)
+5. ✅ **JSONL schema implementation** — Define exact structure (blocks FR7.5 validation)
    - Reviewer output schema (findings JSONL)
    - Run metadata schema (cost tracking, prompt versions)
    - Pattern extraction schema (patterns-v{N}.json)
    - Delta detection schema (delta-v{N-1}-v{N}.json)
+   - **Status:** Complete. Schemas implemented in `schemas/` directory.
```

**Step 3: Commit**

```bash
git add docs/requirements/parallax-review-requirements-v1.md
git commit -m "docs: mark FR7.5 unblocked, Next Steps #5 complete

FR7.5 schema validation now implementable:
- JSON Schema files created (v1.0.0)
- Validation script implemented
- Test fixtures added

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Testing Checklist

Before marking complete:

- [ ] All 4 schema files validate as proper JSON Schema
- [ ] Validation script runs without errors
- [ ] Valid test fixture passes validation
- [ ] Invalid test fixture fails validation (expected)
- [ ] Requirements doc updated (FR7.5 unblocked)
- [ ] 8 commits made (one per task)

**Run full test:**
```bash
# Validate schemas are valid JSON
for f in schemas/*.schema.json; do
  python3 -c "import json; json.load(open('$f'))"
done

# Test validation script
python3 scripts/validate-schemas.py tests/fixtures/
```

---

## Next Steps (Post-Implementation)

After schemas are validated:

1. **Convert existing v1 review** - Convert markdown to JSONL to test against real data
2. **Implement parsers** - Python/TS parsers for each schema type
3. **Implement renderers** - JSONL → markdown rendering
4. **Integration** - Update synthesizer to output JSONL instead of markdown
5. **Pattern extraction prototype** - Test FR10 workflow with v3 review data

These are tracked separately in implementation planning.

---

## Notes

- **No runtime code yet** - This task creates validation artifacts only
- **Schemas block implementation** - Future review pipeline will use these schemas
- **Test early** - Validate with real review output (v1, v2, v3) once schemas are stable
- **Schema evolution** - When adding fields, bump MINOR version and update schema_version in files
