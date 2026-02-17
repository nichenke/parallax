# Dataset Document Snapshots Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Store frozen document snapshots in each eval dataset directory so evals always run against the exact content that was reviewed, not the live file.

**Architecture:** Each dataset directory gains a snapshot file using the original document filename. `dataset_loader.py` learns a new path resolution rule: a `design_doc_path` with no path separator (`/`) is resolved relative to the dataset directory (snapshot). Legacy absolute paths and repo-relative paths (containing `/`) continue to work unchanged.

**Tech Stack:** Python 3.11+, pytest. All commands run from repo root: `/Users/nic/src/design-parallax/parallax/`. Active branch: `feat/dataset-document-snapshots`.

---

## Pre-flight

Confirm you are on the right branch and tests are green:

```bash
git branch --show-current
# Expected: feat/dataset-document-snapshots

.venv-evals/bin/pytest tests/ -v --tb=short 2>&1 | tail -5
# Expected: 52 passed
```

---

## Task 1: Update dataset_loader.py path resolution (TDD)

**Files:**
- Modify: `evals/utils/dataset_loader.py:48-51`
- Modify: `tests/evals/utils/test_dataset_loader.py`

**Context:** Current resolution (lines 48-51) always treats relative paths as repo-root-relative. New rule: if `design_doc_path` has no `/` → it's a local filename, resolve against the dataset directory.

**Step 1: Write the failing test**

Add to the end of `tests/evals/utils/test_dataset_loader.py`:

```python
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
```

**Step 2: Run tests to verify they fail**

```bash
.venv-evals/bin/pytest tests/evals/utils/test_dataset_loader.py::test_load_validated_findings_local_snapshot_resolution -v
```

Expected: `FAILED` — `FileNotFoundError` because `my-requirements.md` is being resolved against the repo root instead of `tmp_path`.

**Step 3: Update dataset_loader.py path resolution**

Replace lines 48-51 in `evals/utils/dataset_loader.py`:

```python
    doc_path = Path(metadata["design_doc_path"])
    if not doc_path.is_absolute():
        doc_path = Path(__file__).parent.parent.parent / doc_path
    doc_content = doc_path.read_text()
```

With:

```python
    doc_path_str = metadata["design_doc_path"]
    doc_path = Path(doc_path_str)
    if doc_path.is_absolute():
        pass  # use as-is
    elif "/" in doc_path_str or "\\" in doc_path_str:
        # repo-relative path (legacy) — resolve from repo root
        doc_path = Path(__file__).parent.parent.parent / doc_path
    else:
        # bare filename — resolve against dataset directory (frozen snapshot)
        doc_path = base / doc_path
    doc_content = doc_path.read_text()
```

**Step 4: Run tests to verify they pass**

```bash
.venv-evals/bin/pytest tests/evals/utils/test_dataset_loader.py -v
```

Expected: all tests pass.

**Step 5: Run full suite**

```bash
.venv-evals/bin/pytest tests/ -v --tb=short 2>&1 | tail -5
```

Expected: 54 passed.

**Step 6: Commit**

```bash
git add evals/utils/dataset_loader.py tests/evals/utils/test_dataset_loader.py
git commit -m "feat: resolve bare filename design_doc_path against dataset directory (snapshot support)"
```

---

## Task 2: Add frozen snapshot for inspect-ai-integration-requirements-v2

**Files:**
- Create: `datasets/inspect-ai-integration-requirements-v2/inspect-ai-integration-requirements-v2.md`
- Modify: `datasets/inspect-ai-integration-requirements-v2/metadata.json`

**Context:** The pre-fix content of requirements-v2.md is at `bad05de~1`. Its sha256 is `e0930d4615ef53b7ca32468ac30cf5608398e6790ef4ce8da2df162967721e90` — which already matches `design_doc_hash` in the current metadata. We're making the implicit explicit.

**Step 1: Extract the pre-fix snapshot**

```bash
git show bad05de~1:docs/requirements/inspect-ai-integration-requirements-v2.md \
  > datasets/inspect-ai-integration-requirements-v2/inspect-ai-integration-requirements-v2.md
```

**Step 2: Verify the hash matches metadata**

```bash
shasum -a 256 datasets/inspect-ai-integration-requirements-v2/inspect-ai-integration-requirements-v2.md
```

Expected: `e0930d4615ef53b7ca32468ac30cf5608398e6790ef4ce8da2df162967721e90  datasets/...`

This must match `design_doc_hash` in `metadata.json`. If it doesn't match, stop and investigate.

**Step 3: Update metadata.json design_doc_path**

Edit `datasets/inspect-ai-integration-requirements-v2/metadata.json`. Change:

```json
"design_doc_path": "docs/requirements/inspect-ai-integration-requirements-v2.md",
```

To:

```json
"design_doc_path": "inspect-ai-integration-requirements-v2.md",
```

Leave all other fields unchanged.

**Step 4: Run the ground truth load test**

```bash
.venv-evals/bin/pytest tests/evals/utils/test_dataset_loader.py -v -k "real_ground_truth"
```

Expected: passes (the test already uses a file-relative path to the dataset dir).

**Step 5: Run full suite**

```bash
.venv-evals/bin/pytest tests/ -v --tb=short 2>&1 | tail -5
```

Expected: 54 passed.

**Step 6: Commit**

```bash
git add datasets/inspect-ai-integration-requirements-v2/
git commit -m "feat: add frozen document snapshot to requirements-v2 dataset (pre-fix, bad05de~1)"
```

---

## Task 3: Add frozen snapshot for inspect-ai-integration-requirements-light

**Files:**
- Create: `datasets/inspect-ai-integration-requirements-light/inspect-ai-integration-requirements-v1.md`
- Modify: `datasets/inspect-ai-integration-requirements-light/metadata.json`

**Context:** The requirements-light ground truth was captured from a review of requirements-v1.md during Session 18 (commit `44965c9`). The metadata incorrectly pointed to v2 with a `PLACEHOLDER` hash. We fix both.

**Step 1: Extract the v1 snapshot**

```bash
git show 44965c9:docs/requirements/inspect-ai-integration-requirements-v1.md \
  > datasets/inspect-ai-integration-requirements-light/inspect-ai-integration-requirements-v1.md
```

**Step 2: Verify the hash**

```bash
shasum -a 256 datasets/inspect-ai-integration-requirements-light/inspect-ai-integration-requirements-v1.md
```

Expected: `4fa1356ead5b1757406eac3b10d7d70b511898df70eac11aaddf836761869316  datasets/...`

Note this hash. It replaces `PLACEHOLDER` in metadata.

**Step 3: Update metadata.json**

Edit `datasets/inspect-ai-integration-requirements-light/metadata.json`. Make two changes:

1. `design_doc_path`: `"docs/requirements/inspect-ai-integration-requirements-v2.md"` → `"inspect-ai-integration-requirements-v1.md"`
2. `design_doc_hash`: `"PLACEHOLDER"` → `"4fa1356ead5b1757406eac3b10d7d70b511898df70eac11aaddf836761869316"`

**Step 4: Update the ground truth count test**

The existing test `test_real_ground_truth_loads_correctly` in `tests/evals/utils/test_dataset_loader.py` loads this dataset. It currently expects the doc content to come from requirements-v2.md. After this change, it loads requirements-v1.md content instead — the assertion `len(findings) == 10` and severity/status checks are unaffected (they test the JSONL, not the doc content).

Run it to confirm:

```bash
.venv-evals/bin/pytest tests/evals/utils/test_dataset_loader.py::test_real_ground_truth_loads_correctly -v
```

Expected: passes.

**Step 5: Run full suite**

```bash
.venv-evals/bin/pytest tests/ -v --tb=short 2>&1 | tail -5
```

Expected: 54 passed.

**Step 6: Commit**

```bash
git add datasets/inspect-ai-integration-requirements-light/
git commit -m "feat: add frozen v1 snapshot to requirements-light dataset, fix PLACEHOLDER hash"
```

---

## Task 4: Smoke test — run reviewer-eval and verify non-zero accuracy

**Purpose:** Confirm the end-to-end pipeline now loads the correct frozen content and returns non-zero accuracy for at least one reviewer.

**Step 1: Run a single-task smoke test (cheapest reviewer)**

```bash
. .venv-evals/bin/activate && inspect eval evals/reviewer_eval.py@scope_guardian_eval \
    --model anthropic/claude-haiku-4-5 \
    --log-dir logs/ \
    --limit 1
```

**Step 2: Check the result**

Expected: `accuracy` is non-zero (scope-guardian should detect `scope-guardian-004` from the pre-fix v2 doc).

If still 0.000, diagnose:

```bash
python3 -c "
import json, zipfile
log = sorted(__import__('pathlib').Path('logs').glob('*scope*'))[-1]
with zipfile.ZipFile(log) as z:
    s = json.loads(z.read('samples/1_epoch_1.json'))
print('OUTPUT:', s['output']['choices'][0]['message']['content'][:500])
print('SCORER:', json.dumps(s['scores']['severity_calibration']['metadata'], indent=2))
"
```

**Step 3: Push and open PR**

```bash
git push -u origin feat/dataset-document-snapshots
gh pr create --title "feat: frozen document snapshots in eval datasets" --body "$(cat <<'EOF'
Fixes the root cause of \`accuracy: 0.000\` across all reviewer-eval tasks (issue #63).

## Changes
- \`dataset_loader.py\`: bare filename in \`design_doc_path\` now resolves to dataset directory (snapshot)
- \`datasets/inspect-ai-integration-requirements-v2/\`: frozen pre-fix snapshot added (\`bad05de~1\`)
- \`datasets/inspect-ai-integration-requirements-light/\`: frozen v1 snapshot added, PLACEHOLDER hash fixed
- 2 new tests for path resolution behavior

## Why
Ground truth was captured against specific document versions. Without frozen snapshots, any doc edit silently changes what the eval measures. See design doc: \`docs/plans/2026-02-17-dataset-document-snapshots-design.md\`

Closes #63

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
