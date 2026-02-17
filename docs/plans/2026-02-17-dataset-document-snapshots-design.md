# Dataset Document Snapshots Design

**Date:** 2026-02-17
**Status:** Approved
**Scope:** Eval dataset ground truth — frozen document inputs

## Problem

`metadata.json` stores `design_doc_path` as a path to the live document in the repo. When the document is updated after ground truth capture, the eval silently runs against a different version than was reviewed. The accuracy metric becomes meaningless — 0.000 not because reviewers are missing findings, but because the findings no longer exist in the document.

This was discovered when `make reviewer-eval` returned `accuracy: 0.000` across all 5 tasks after requirements-v2.md was fixed in commit `bad05de`.

## Design

### Dataset directory structure

Each dataset directory stores a frozen snapshot of the document at the time ground truth was captured, using the original filename:

```
datasets/<dataset-name>/
  critical_findings.jsonl        — ground truth findings
  metadata.json                  — metadata, design_doc_path is relative filename
  <original-filename>.md         — frozen document snapshot
```

Example:
```
datasets/inspect-ai-integration-requirements-v2/
  critical_findings.jsonl
  metadata.json                  — design_doc_path: "inspect-ai-integration-requirements-v2.md"
  inspect-ai-integration-requirements-v2.md
```

### metadata.json resolution rule

`design_doc_path` is a **relative filename** (no path separators, no leading `/`) when it refers to a snapshot in the dataset directory. Absolute paths and repo-relative paths (containing `/`) continue to work for backward compatibility.

Resolution logic in `dataset_loader.py`:
- If `design_doc_path` is absolute → use as-is
- If `design_doc_path` contains `/` → resolve relative to repo root (legacy behavior)
- Otherwise → resolve relative to the dataset directory (snapshot)

### Why original filename

The original filename is preserved rather than normalizing to `document.md`. Agent prompts sometimes infer document type from filename. Preserving it keeps the option to include filename context in `Sample.input` without a schema migration.

### Ground truth capture workflow (updated)

When running a fresh review and creating a new dataset:

1. Run `parallax:requirements --light` or `parallax:review` on the target doc
2. Validate findings via validation UI
3. Copy the doc to the dataset directory: `cp path/to/doc.md datasets/<name>/doc.md`
4. Set `design_doc_path` in `metadata.json` to the filename only (e.g., `"doc.md"`)
5. Commit the dataset directory as a unit

This makes each dataset a fully self-contained test fixture.

## Migration

### inspect-ai-integration-requirements-v2

- Snapshot source: `git show bad05de~1:docs/requirements/inspect-ai-integration-requirements-v2.md`
- This is the pre-fix state reviewed in Session 25 (before `bad05de` applied 6 Critical fixes)
- `metadata.json` `design_doc_path`: `"inspect-ai-integration-requirements-v2.md"`

### inspect-ai-integration-requirements-light

- Snapshot source: `git show 44965c9:docs/requirements/inspect-ai-integration-requirements-v1.md`
- This is requirements-v1 at the Session 18 review (metadata incorrectly pointed to v2 path)
- `metadata.json` `design_doc_path`: `"inspect-ai-integration-requirements-v1.md"`
- Note: the snapshot is named `v1` to reflect what was actually reviewed

## Files changed

| File | Change |
|------|--------|
| `evals/utils/dataset_loader.py` | Update path resolution: relative filename → dataset dir |
| `datasets/inspect-ai-integration-requirements-v2/inspect-ai-integration-requirements-v2.md` | New: pre-fix snapshot |
| `datasets/inspect-ai-integration-requirements-v2/metadata.json` | Update design_doc_path to relative filename |
| `datasets/inspect-ai-integration-requirements-light/inspect-ai-integration-requirements-v1.md` | New: v1 doc snapshot |
| `datasets/inspect-ai-integration-requirements-light/metadata.json` | Update design_doc_path to relative filename, fix PLACEHOLDER hash |
| `tests/evals/utils/test_dataset_loader.py` | Add test for relative-to-dataset resolution |

## Design flaw note

The original `design_doc_path` approach was flagged as a known risk (design review C-8: "hash check design") but deferred as a non-blocker. The hash field existed in `metadata.json` but was never used for validation. A pre-eval hash check comparing the live doc against the capture-time hash would have surfaced this immediately instead of silently returning 0.000. See GitHub issue filed alongside this design.
