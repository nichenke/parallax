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
