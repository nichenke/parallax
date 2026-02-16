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
