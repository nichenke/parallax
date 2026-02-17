# Inspect AI Integration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the Inspect AI eval framework for parallax: dataset loader, severity scorer, eval tasks, ablation tests, regression detection, and Makefile-driven developer workflow.

**Architecture:** Inspect AI conventional patterns (Dataset/Sample/Task/Scorer). Skills loaded from disk at eval runtime. Ground truth stored as validated JSONL in `datasets/`. All workflows wrapped in Makefile targets.

**Tech Stack:** Python 3.14, Inspect AI ≥0.3, pytest, Flask (validation UI — handled in separate worktree)

**Context:** Branch `feat/inspect-ai-integration-design`. Design doc at `docs/plans/2026-02-16-inspect-ai-integration-design.md`. Validation UI being built in `.worktrees/validation-ui` (parallel session — not part of this plan).

---

## Task 1: Python Environment Setup

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `evals/__init__.py`
- Create: `evals/utils/__init__.py`
- Create: `scorers/__init__.py`

**Step 1: Create `.python-version`**

```
3.14
```

**Step 2: Create `pyproject.toml`**

```toml
[project]
name = "parallax-evals"
requires-python = ">=3.11"

[project.dependencies]
inspect-ai = ">=0.3"

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 3: Create package `__init__.py` files**

Create empty `evals/__init__.py`, `evals/utils/__init__.py`, `scorers/__init__.py`.

**Step 4: Create venv and install**

```bash
python3 -m venv .venv-evals
source .venv-evals/bin/activate
pip install -e ".[dev]"
```

Expected: `inspect-ai` package installed, `inspect` CLI available.

**Step 5: Verify Inspect AI CLI works**

```bash
source .venv-evals/bin/activate
inspect --version
```

Expected: version string printed (e.g., `inspect-ai 0.3.x`)

**Step 6: Create `datasets/v3_review_validated/` directory structure**

```bash
mkdir -p datasets/v3_review_validated
```

Create `datasets/v3_review_validated/metadata.json` template:

```json
{
  "source_review": "parallax-review-v1",
  "design_doc_path": "docs/plans/parallax-design-v4.md",
  "design_doc_hash": "PLACEHOLDER",
  "review_date": "2026-02-16",
  "validation_date": "",
  "validator": "nic",
  "total_findings": 0,
  "severity_distribution": {"Critical": 0, "Important": 0, "Minor": 0},
  "false_positive_rate": 0.0,
  "skill_version": ""
}
```

Create empty `datasets/v3_review_validated/critical_findings.jsonl`.

**Step 7: Add `.gitignore` entries**

Append to `.gitignore`:

```
.venv-evals/
logs/
evals/baselines/
__pycache__/
*.pyc
.pytest_cache/
```

**Step 8: Commit**

```bash
git add pyproject.toml .python-version evals/ scorers/ datasets/ .gitignore
git commit -m "feat: Python environment setup for Inspect AI integration"
```

---

## Task 2: Dataset Loader

**Files:**
- Create: `evals/utils/dataset_loader.py`
- Create: `tests/evals/utils/test_dataset_loader.py`

**The finding schema** (from `schemas/reviewer-findings-v1.0.0.schema.json`) has required fields: `type`, `id`, `title`, `severity`, `phase`, `section`, `issue`, `why_it_matters`, `suggestion`. Validated findings add: `validated`, `validation_status`, `validation_notes`, `validator_id`, `validation_date`.

**Step 1: Write the failing tests**

Create `tests/evals/__init__.py` and `tests/evals/utils/__init__.py` (empty).

Create `tests/evals/utils/test_dataset_loader.py`:

```python
import json
import pytest
from pathlib import Path
from inspect_ai.dataset import Dataset

from evals.utils.dataset_loader import load_validated_findings, count_by_severity


FIXTURES = Path("tests/fixtures")


def test_count_by_severity_empty():
    assert count_by_severity([]) == {"Critical": 0, "Important": 0, "Minor": 0}


def test_count_by_severity_mixed():
    findings = [
        {"severity": "Critical"},
        {"severity": "Critical"},
        {"severity": "Important"},
        {"severity": "Minor"},
    ]
    assert count_by_severity(findings) == {"Critical": 2, "Important": 1, "Minor": 1}


def test_load_validated_findings_returns_dataset(tmp_path):
    # Create minimal valid dataset
    findings = [
        {
            "type": "finding",
            "id": "v3-assumption-hunter-001",
            "title": "Ground truth validity assumed",
            "severity": "Critical",
            "phase": {"primary": "design", "contributing": None},
            "section": "Architecture",
            "issue": "No validation",
            "why_it_matters": "Circular dependency",
            "suggestion": "Validate first",
            "validated": True,
            "validation_status": "real_flaw",
            "validation_notes": "Confirmed",
            "validator_id": "nic",
            "validation_date": "2026-02-16"
        }
    ]
    metadata = {
        "source_review": "parallax-review-v1",
        "design_doc_path": "docs/plans/parallax-design-v4.md",
        "design_doc_hash": "abc123",
        "review_date": "2026-02-16",
        "validation_date": "2026-02-16",
        "validator": "nic",
        "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0,
        "skill_version": "git:abc123"
    }

    (tmp_path / "critical_findings.jsonl").write_text(
        json.dumps(findings[0]) + "\n"
    )
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))

    assert isinstance(dataset, Dataset)
    assert len(dataset) == 1


def test_load_validated_findings_sample_structure(tmp_path):
    finding = {
        "type": "finding",
        "id": "v3-assumption-hunter-001",
        "title": "Test finding",
        "severity": "Critical",
        "phase": {"primary": "design", "contributing": None},
        "section": "Architecture",
        "issue": "Issue text",
        "why_it_matters": "Matters",
        "suggestion": "Fix it",
        "validated": True,
        "validation_status": "real_flaw",
        "validation_notes": "Notes",
        "validator_id": "nic",
        "validation_date": "2026-02-16"
    }
    metadata = {
        "source_review": "test",
        "design_doc_path": "docs/test.md",
        "design_doc_hash": "abc",
        "review_date": "2026-02-16",
        "validation_date": "2026-02-16",
        "validator": "nic",
        "total_findings": 1,
        "severity_distribution": {"Critical": 1, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.0,
        "skill_version": "git:abc"
    }

    (tmp_path / "critical_findings.jsonl").write_text(json.dumps(finding) + "\n")
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    sample = dataset[0]

    assert "design_doc" in sample.input
    assert "expected_findings" in sample.target
    assert len(sample.target["expected_findings"]) == 1
    assert sample.target["expected_findings"][0]["id"] == "v3-assumption-hunter-001"


def test_load_validated_findings_filters_non_real_flaws(tmp_path):
    findings = [
        {
            "type": "finding", "id": "v3-test-001", "title": "Real",
            "severity": "Critical", "phase": {"primary": "design", "contributing": None},
            "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix",
            "validated": True, "validation_status": "real_flaw",
            "validation_notes": "N", "validator_id": "nic", "validation_date": "2026-02-16"
        },
        {
            "type": "finding", "id": "v3-test-002", "title": "False positive",
            "severity": "Critical", "phase": {"primary": "design", "contributing": None},
            "section": "S", "issue": "I", "why_it_matters": "W", "suggestion": "Fix",
            "validated": True, "validation_status": "false_positive",
            "validation_notes": "N", "validator_id": "nic", "validation_date": "2026-02-16"
        }
    ]
    metadata = {
        "source_review": "test", "design_doc_path": "d", "design_doc_hash": "h",
        "review_date": "2026-02-16", "validation_date": "2026-02-16",
        "validator": "nic", "total_findings": 2,
        "severity_distribution": {"Critical": 2, "Important": 0, "Minor": 0},
        "false_positive_rate": 0.5, "skill_version": "git:abc"
    }

    lines = "\n".join(json.dumps(f) for f in findings) + "\n"
    (tmp_path / "critical_findings.jsonl").write_text(lines)
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    dataset = load_validated_findings(str(tmp_path))
    sample = dataset[0]

    # Only real_flaw findings in ground truth
    assert len(sample.target["expected_findings"]) == 1
    assert sample.target["expected_findings"][0]["id"] == "v3-test-001"
```

**Step 2: Run tests to verify they fail**

```bash
source .venv-evals/bin/activate
pytest tests/evals/utils/test_dataset_loader.py -v
```

Expected: `ImportError` — `evals.utils.dataset_loader` not found.

**Step 3: Implement `evals/utils/dataset_loader.py`**

```python
import json
from pathlib import Path
from inspect_ai.dataset import Dataset, Sample


def count_by_severity(findings: list[dict]) -> dict:
    counts = {"Critical": 0, "Important": 0, "Minor": 0}
    for f in findings:
        sev = f.get("severity")
        if sev in counts:
            counts[sev] += 1
    return counts


def read_jsonl(path: Path) -> list[dict]:
    lines = path.read_text().strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_validated_findings(dataset_path: str) -> Dataset:
    """Convert parallax validated JSONL findings → Inspect AI Dataset."""
    base = Path(dataset_path)
    findings = read_jsonl(base / "critical_findings.jsonl")
    metadata = json.loads((base / "metadata.json").read_text())

    # Only use confirmed real flaws as ground truth
    real_flaws = [
        f for f in findings
        if f.get("type") == "finding" and f.get("validation_status") == "real_flaw"
    ]

    sample = Sample(
        input={
            "design_doc": metadata["design_doc_path"],
            "skill_version": metadata.get("skill_version", "current")
        },
        target={
            "expected_findings": real_flaws,
            "severity_distribution": count_by_severity(real_flaws)
        },
        metadata=metadata
    )

    return Dataset(samples=[sample])
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/evals/utils/test_dataset_loader.py -v
```

Expected: all 5 tests PASS.

**Step 5: Commit**

```bash
git add evals/utils/dataset_loader.py tests/evals/
git commit -m "feat: Inspect AI dataset loader for validated JSONL findings"
```

---

## Task 3: Severity Scorer

**Files:**
- Create: `scorers/severity_scorer.py`
- Create: `tests/scorers/test_severity_scorer.py`

**Step 1: Write failing tests**

Create `tests/scorers/__init__.py` (empty).

Create `tests/scorers/test_severity_scorer.py`:

```python
import pytest
from scorers.severity_scorer import match_findings, calculate_metrics


FINDING_A = {
    "id": "v3-test-001", "title": "Ground truth validity assumed",
    "severity": "Critical", "issue": "No validation of v3 findings"
}
FINDING_B = {
    "id": "v3-test-002", "title": "API key security undefined",
    "severity": "Critical", "issue": "No key rotation policy"
}
FINDING_C = {
    "id": "v3-test-003", "title": "Python environment constraints missing",
    "severity": "Critical", "issue": "No Python version specified"
}


def test_match_findings_exact_id():
    """Exact ID match takes priority."""
    detected = match_findings(actual=[FINDING_A], expected=[FINDING_A])
    assert len(detected) == 1
    assert detected[0]["id"] == "v3-test-001"


def test_match_findings_no_match():
    """Non-matching findings return empty list."""
    different = {"id": "v3-other-001", "title": "Something else", "severity": "Critical", "issue": "Unrelated"}
    detected = match_findings(actual=[different], expected=[FINDING_A])
    assert detected == []


def test_match_findings_fuzzy_title_overlap():
    """Fuzzy match on title when IDs differ."""
    # Same title, different ID (e.g., fresh review rephrased slightly)
    rephrased = {
        "id": "v1-new-001",
        "title": "Ground truth validity assumption",  # ~90% overlap
        "severity": "Critical",
        "issue": "v3 findings not validated"
    }
    detected = match_findings(actual=[rephrased], expected=[FINDING_A])
    assert len(detected) == 1


def test_match_findings_partial_set():
    """Detects subset of expected findings."""
    expected = [FINDING_A, FINDING_B, FINDING_C]
    actual = [FINDING_A, FINDING_C]  # missed FINDING_B
    detected = match_findings(actual=actual, expected=expected)
    assert len(detected) == 2
    ids = [d["id"] for d in detected]
    assert "v3-test-001" in ids
    assert "v3-test-003" in ids


def test_calculate_metrics_perfect():
    recall, precision, f1 = calculate_metrics(detected=3, actual=3, expected=3)
    assert recall == pytest.approx(1.0)
    assert precision == pytest.approx(1.0)
    assert f1 == pytest.approx(1.0)


def test_calculate_metrics_half_recall():
    recall, precision, f1 = calculate_metrics(detected=1, actual=1, expected=2)
    assert recall == pytest.approx(0.5)
    assert precision == pytest.approx(1.0)
    assert f1 == pytest.approx(2/3, rel=1e-3)


def test_calculate_metrics_with_false_positives():
    recall, precision, f1 = calculate_metrics(detected=2, actual=4, expected=2)
    assert recall == pytest.approx(1.0)
    assert precision == pytest.approx(0.5)


def test_calculate_metrics_zero_actual():
    """Handle edge case: model returned no findings."""
    recall, precision, f1 = calculate_metrics(detected=0, actual=0, expected=3)
    assert recall == 0.0
    assert precision == 0.0
    assert f1 == 0.0
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/scorers/test_severity_scorer.py -v
```

Expected: `ImportError` — `scorers.severity_scorer` not found.

**Step 3: Implement `scorers/severity_scorer.py`**

```python
from difflib import SequenceMatcher
from inspect_ai.scorer import Score, scorer, accuracy


def _title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def match_findings(actual: list[dict], expected: list[dict]) -> list[dict]:
    """
    Match actual review findings to expected ground truth findings.
    Strategy: exact ID match first, fuzzy title match fallback (≥0.8 similarity).
    """
    matched = []
    actual_ids = {f["id"] for f in actual}

    for exp in expected:
        # Exact ID match
        if exp["id"] in actual_ids:
            matched.append(exp)
            continue

        # Fuzzy title match fallback
        for act in actual:
            if (
                act.get("severity") == exp.get("severity")
                and _title_similarity(act.get("title", ""), exp.get("title", "")) >= 0.8
            ):
                matched.append(exp)
                break

    return matched


def calculate_metrics(detected: int, actual: int, expected: int) -> tuple[float, float, float]:
    """Calculate recall, precision, F1."""
    recall = detected / expected if expected > 0 else 0.0
    precision = detected / actual if actual > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return recall, precision, f1


@scorer(metrics=[accuracy()])
def severity_calibration(recall_threshold: float = 0.90, precision_threshold: float = 0.80):
    """
    Validates Critical finding detection against ground truth.
    Thresholds: recall ≥90%, precision ≥80% (provisional — tune after first runs).
    """
    async def score(state, target):
        from evals.utils.output_parser import parse_review_output

        actual_findings = parse_review_output(state.output.completion)
        expected_findings = target.target["expected_findings"]

        detected = match_findings(actual=actual_findings, expected=expected_findings)

        recall, precision, f1 = calculate_metrics(
            detected=len(detected),
            actual=len(actual_findings),
            expected=len(expected_findings)
        )

        passes = recall >= recall_threshold and precision >= precision_threshold

        missed = [f["id"] for f in expected_findings if f not in detected]
        false_positives = [f.get("id", f.get("title")) for f in actual_findings
                          if not any(d["id"] == f.get("id") for d in detected)]

        return Score(
            value=1.0 if passes else 0.0,
            answer=str([f["id"] for f in detected]),
            explanation=(
                f"Detected {len(detected)}/{len(expected_findings)} findings. "
                f"Recall: {recall:.2%}, Precision: {precision:.2%}, F1: {f1:.2%}. "
                f"{'PASS' if passes else 'FAIL'}"
            ),
            metadata={
                "recall": recall,
                "precision": precision,
                "f1": f1,
                "passes_threshold": passes,
                "missed_findings": missed,
                "false_positives": false_positives
            }
        )

    return score
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/scorers/test_severity_scorer.py -v
```

Expected: all 8 tests PASS. (Note: `parse_review_output` import is only called inside the scorer coroutine — not needed for unit tests of `match_findings` / `calculate_metrics`.)

**Step 5: Commit**

```bash
git add scorers/severity_scorer.py tests/scorers/
git commit -m "feat: severity calibration scorer with fuzzy finding matching"
```

---

## Task 4: Output Parser

**Files:**
- Create: `evals/utils/output_parser.py`
- Create: `tests/evals/utils/test_output_parser.py`

The scorer calls `parse_review_output(completion)` to extract findings from the model's raw text output. The model outputs JSONL-formatted findings (following the parallax reviewer schema).

**Step 1: Write failing tests**

Create `tests/evals/utils/test_output_parser.py`:

```python
import pytest
from evals.utils.output_parser import parse_review_output


def test_parse_single_finding():
    completion = '''
    {"type": "finding", "id": "v1-test-001", "title": "Test", "severity": "Critical",
     "phase": {"primary": "design", "contributing": null}, "section": "Architecture",
     "issue": "Missing validation", "why_it_matters": "Blocks eval", "suggestion": "Add validation"}
    '''
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
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/evals/utils/test_output_parser.py -v
```

Expected: `ImportError`.

**Step 3: Implement `evals/utils/output_parser.py`**

```python
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
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/evals/utils/test_output_parser.py -v
```

Expected: all 5 tests PASS.

**Step 5: Commit**

```bash
git add evals/utils/output_parser.py tests/evals/utils/test_output_parser.py
git commit -m "feat: output parser extracts findings from model JSONL completion"
```

---

## Task 5: Eval Task + Skill Loader

**Files:**
- Create: `evals/utils/skill_loader.py`
- Create: `evals/severity_calibration.py`
- Create: `tests/evals/test_severity_calibration.py`

**Step 1: Write failing tests**

Create `tests/evals/test_severity_calibration.py`:

```python
import pytest
from pathlib import Path
from evals.utils.skill_loader import load_skill_content, drop_section


def test_load_skill_content_returns_string(tmp_path):
    skill_dir = tmp_path / "parallax:requirements"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n\n## Personas\nAssume Hunter")

    content = load_skill_content("parallax:requirements", skills_root=str(tmp_path))
    assert "# Test Skill" in content


def test_load_skill_content_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_skill_content("nonexistent:skill", skills_root=str(tmp_path))


def test_drop_section_removes_target():
    content = "# Skill\n\n## Personas\nAssume Hunter\n\n## Verdict Logic\nIf critical..."
    result = drop_section(content, "## Personas")
    assert "## Personas" not in result
    assert "Assume Hunter" not in result
    assert "## Verdict Logic" in result


def test_drop_section_nonexistent_is_noop():
    content = "# Skill\n\n## Verdict Logic\nIf critical..."
    result = drop_section(content, "## Nonexistent Section")
    assert result == content
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/evals/test_severity_calibration.py -v
```

Expected: `ImportError`.

**Step 3: Implement `evals/utils/skill_loader.py`**

```python
import re
from pathlib import Path


def load_skill_content(skill_name: str, skills_root: str | None = None) -> str:
    """Load skill prompt from parallax skills directory."""
    if skills_root is None:
        skills_root = Path(__file__).parent.parent.parent / "skills"
    else:
        skills_root = Path(skills_root)

    skill_path = skills_root / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")
    return skill_path.read_text()


def drop_section(content: str, section_header: str) -> str:
    """
    Remove a markdown section (header + content until next same-level header).
    Used for ablation tests.
    """
    # Determine heading level from header
    level = len(section_header) - len(section_header.lstrip("#"))
    pattern = rf"(?m)^{re.escape(section_header)}.*?(?=^{'#' * level} |\Z)"
    return re.sub(pattern, "", content, flags=re.DOTALL).strip()
```

**Step 4: Implement `evals/severity_calibration.py`**

```python
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from evals.utils.dataset_loader import load_validated_findings
from evals.utils.skill_loader import load_skill_content
from scorers.severity_scorer import severity_calibration


DATASET_PATH = "datasets/v3_review_validated"


@task
def severity_calibration_eval() -> Task:
    """
    Evaluate Critical finding detection against validated ground truth.
    Loads actual skill content at runtime — skill changes flow through automatically.
    """
    return Task(
        dataset=load_validated_findings(DATASET_PATH),
        plan=[
            system_message(load_skill_content("parallax:requirements")),
            generate()
        ],
        scorer=severity_calibration(),
        max_tokens=16000
    )
```

**Step 5: Run tests to verify they pass**

```bash
pytest tests/evals/test_severity_calibration.py -v
```

Expected: all 4 tests PASS.

**Step 6: Commit**

```bash
git add evals/utils/skill_loader.py evals/severity_calibration.py tests/evals/test_severity_calibration.py
git commit -m "feat: eval task definition loads actual skill content at runtime"
```

---

## Task 6: Ablation Tests

**Files:**
- Create: `evals/ablation_tests.py`

No new tests needed — `drop_section` is fully tested in Task 5. Ablation tasks are thin wrappers using already-tested components.

**Step 1: Implement `evals/ablation_tests.py`**

```python
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from evals.utils.dataset_loader import load_validated_findings
from evals.utils.skill_loader import load_skill_content, drop_section
from scorers.severity_scorer import severity_calibration


DATASET_PATH = "datasets/v3_review_validated"


def _ablated_task(section_to_drop: str, task_name: str) -> Task:
    skill = load_skill_content("parallax:requirements")
    ablated = drop_section(skill, section_to_drop)
    return Task(
        dataset=load_validated_findings(DATASET_PATH),
        plan=[system_message(ablated), generate()],
        scorer=severity_calibration(),
        max_tokens=16000,
        metadata={"ablation": section_to_drop, "task": task_name}
    )


@task
def ablation_no_personas() -> Task:
    """Ablation: drop persona descriptions. Expect >50% detection rate drop."""
    return _ablated_task("## Personas", "ablation_no_personas")


@task
def ablation_no_verdict_logic() -> Task:
    """Ablation: drop verdict/severity logic. Expect >50% detection rate drop."""
    return _ablated_task("## Verdict Logic", "ablation_no_verdict_logic")


@task
def ablation_no_synthesis() -> Task:
    """Ablation: drop synthesis instructions. Expect >50% detection rate drop."""
    return _ablated_task("## Synthesis", "ablation_no_synthesis")
```

**Step 2: Commit**

```bash
git add evals/ablation_tests.py
git commit -m "feat: ablation test tasks for section-level skill content validation"
```

---

## Task 7: Regression Detection Script

**Files:**
- Create: `tools/compare_to_baseline.py`
- Create: `tests/tools/test_compare_to_baseline.py`

**Step 1: Write failing tests**

Create `tests/tools/__init__.py` (empty).

Create `tests/tools/test_compare_to_baseline.py`:

```python
import json
import pytest
from pathlib import Path
from tools.compare_to_baseline import compare_runs, RegressionStatus


def _make_result(recall: float, precision: float, f1: float) -> dict:
    return {
        "results": [{
            "scores": [{
                "metadata": {"recall": recall, "precision": precision, "f1": f1}
            }]
        }]
    }


def test_pass_within_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.91, 0.85, 0.88)
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.PASS


def test_warn_approaching_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.86, 0.80, 0.83)  # ~7% recall drop
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.WARN


def test_fail_exceeds_threshold():
    baseline = _make_result(0.93, 0.87, 0.90)
    current  = _make_result(0.80, 0.75, 0.77)  # >10% recall drop
    status, delta = compare_runs(baseline, current, threshold=0.10)
    assert status == RegressionStatus.FAIL


def test_delta_values_correct():
    baseline = _make_result(0.90, 0.80, 0.85)
    current  = _make_result(0.85, 0.75, 0.80)
    _, delta = compare_runs(baseline, current, threshold=0.10)
    assert delta["recall"] == pytest.approx(-0.05, abs=1e-4)
    assert delta["precision"] == pytest.approx(-0.05, abs=1e-4)
    assert delta["f1"] == pytest.approx(-0.05, abs=1e-4)
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/tools/test_compare_to_baseline.py -v
```

Expected: `ImportError`.

**Step 3: Implement `tools/compare_to_baseline.py`**

Create `tools/__init__.py` (empty).

```python
#!/usr/bin/env python3
"""
Compare latest eval run to stored baseline.
Usage: python tools/compare_to_baseline.py [baseline_path] [current_path]
"""
import json
import sys
from enum import Enum
from pathlib import Path


BASELINE_PATH = Path("evals/baselines/v3_critical_baseline.json")
LOGS_DIR = Path("logs")
WARN_THRESHOLD = 0.05
FAIL_THRESHOLD = 0.10


class RegressionStatus(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


def _extract_metrics(run: dict) -> dict:
    """Extract recall/precision/f1 from Inspect AI EvalLog JSON."""
    try:
        scores = run["results"][0]["scores"][0]["metadata"]
        return {
            "recall": scores["recall"],
            "precision": scores["precision"],
            "f1": scores["f1"]
        }
    except (KeyError, IndexError) as e:
        raise ValueError(f"Cannot extract metrics from run: {e}")


def compare_runs(
    baseline: dict,
    current: dict,
    threshold: float = FAIL_THRESHOLD
) -> tuple[RegressionStatus, dict]:
    b = _extract_metrics(baseline)
    c = _extract_metrics(current)

    delta = {k: c[k] - b[k] for k in b}
    worst_drop = min(delta.values())

    if worst_drop < -threshold:
        status = RegressionStatus.FAIL
    elif worst_drop < -(threshold / 2):
        status = RegressionStatus.WARN
    else:
        status = RegressionStatus.PASS

    return status, delta


def main():
    baseline_path = Path(sys.argv[1]) if len(sys.argv) > 1 else BASELINE_PATH
    if not baseline_path.exists():
        print(f"No baseline found at {baseline_path}. Run 'make baseline' first.")
        sys.exit(1)

    # Find most recent log
    logs = sorted(LOGS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        print(f"No eval logs found in {LOGS_DIR}/. Run 'make eval' first.")
        sys.exit(1)

    current_path = Path(sys.argv[2]) if len(sys.argv) > 2 else logs[0]

    baseline = json.loads(baseline_path.read_text())
    current = json.loads(current_path.read_text())

    b_metrics = _extract_metrics(baseline)
    c_metrics = _extract_metrics(current)
    status, delta = compare_runs(baseline, current)

    b_git = baseline.get("metadata", {}).get("git", "unknown")
    c_git = current.get("metadata", {}).get("git", "unknown")

    print(f"\nComparing to baseline: {baseline_path}")
    print(f"\n  Baseline (git:{b_git}):  recall={b_metrics['recall']:.2f}  precision={b_metrics['precision']:.2f}  f1={b_metrics['f1']:.2f}")
    print(f"  Current  (git:{c_git}):  recall={c_metrics['recall']:.2f}  precision={c_metrics['precision']:.2f}  f1={c_metrics['f1']:.2f}")
    print(f"\n  Delta: recall={delta['recall']:+.2f}  precision={delta['precision']:+.2f}  f1={delta['f1']:+.2f}")
    print(f"  Status: {status.value}")

    if status == RegressionStatus.FAIL:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/tools/test_compare_to_baseline.py -v
```

Expected: all 4 tests PASS.

**Step 5: Commit**

```bash
git add tools/ tests/tools/
git commit -m "feat: regression detection compares eval runs to baseline"
```

---

## Task 8: Makefile

**Files:**
- Create: `Makefile`

No tests — verify manually.

**Step 1: Create `Makefile`**

```makefile
DESIGN_DOC ?= docs/plans/parallax-design-v4.md
MODEL       ?= anthropic/claude-sonnet-4-5
LOG_DIR     ?= logs/
VENV        := .venv-evals/bin/activate

## ── Setup ──────────────────────────────────────────────────────────────────

setup:
	python3 -m venv .venv-evals
	. $(VENV) && pip install -e ".[dev]"
	mkdir -p logs/ evals/baselines/

## ── Ground truth (run after significant design changes) ────────────────────

review:
	@echo "Run: parallax:review $(DESIGN_DOC) in Claude Code"
	@echo "Then: make validate"

validate:
	. $(VENV) && python tools/validate_findings.py

## ── Eval loop ───────────────────────────────────────────────────────────────

eval:
	mkdir -p $(LOG_DIR)
	. $(VENV) && inspect eval evals/severity_calibration.py \
	    --model $(MODEL) \
	    --log-dir $(LOG_DIR) \
	    --tags "git=$(shell git rev-parse --short HEAD)"

ablation:
	mkdir -p $(LOG_DIR)
	. $(VENV) && inspect eval evals/ablation_tests.py \
	    --model $(MODEL) \
	    --log-dir $(LOG_DIR)

baseline:
	mkdir -p evals/baselines/
	cp $$(ls -t $(LOG_DIR)*.json | head -1) evals/baselines/v3_critical_baseline.json
	@echo "Baseline stored."

regression:
	. $(VENV) && python tools/compare_to_baseline.py

view:
	. $(VENV) && inspect view

## ── Full cycle ──────────────────────────────────────────────────────────────

cycle: eval regression view

## ── Tests ───────────────────────────────────────────────────────────────────

test:
	. $(VENV) && pytest tests/ -v

## ── Help ────────────────────────────────────────────────────────────────────

help:
	@echo "Ground truth creation:"
	@echo "  make review      Run fresh parallax review on design doc"
	@echo "  make validate    Open validation UI in browser (localhost:5000)"
	@echo ""
	@echo "Eval loop:"
	@echo "  make eval        Run severity calibration eval"
	@echo "  make ablation    Run ablation tests"
	@echo "  make baseline    Store latest run as baseline"
	@echo "  make regression  Compare latest run to baseline"
	@echo "  make view        Open Inspect View UI"
	@echo "  make cycle       eval + regression + view"
	@echo ""
	@echo "Other:"
	@echo "  make test        Run unit tests"
	@echo "  make setup       Create venv and install dependencies"

.PHONY: setup review validate eval ablation baseline regression view cycle test help
```

**Step 2: Verify make help works**

```bash
make help
```

Expected: formatted help output printed with no errors.

**Step 3: Verify make test runs**

```bash
make test
```

Expected: all tests PASS.

**Step 4: Commit**

```bash
git add Makefile
git commit -m "feat: Makefile with ground truth creation + eval loop targets"
```

---

## Task 9: README and PR

**Files:**
- Create: `README-evals.md`

**Step 1: Create `README-evals.md`**

```markdown
# Parallax Eval Framework

Systematic validation for parallax skills using [Inspect AI](https://inspect.aisi.org.uk/).

## Quick Start

```bash
make setup          # Create venv, install dependencies
make test           # Verify all unit tests pass
make eval           # Run severity calibration eval (requires ANTHROPIC_API_KEY)
make view           # Open Inspect View UI
```

## Workflow

### When the design changes significantly

```bash
make review         # Run fresh parallax review on design doc (in Claude Code)
make validate       # Classify findings in browser UI (localhost:5000)
# Ground truth is now current
```

### When iterating on skill prompts

```bash
# Edit skills/parallax:requirements/SKILL.md
make eval           # Did detection rate hold?
make regression     # Compare to baseline — nothing should drop
make view           # Inspect missed findings + false positives
make baseline       # Store when satisfied
```

### When fixing design issues

```bash
# Fix docs/plans/parallax-design-v4.md based on findings
make review         # Re-run review on updated design
make eval           # Confirmed findings should no longer appear
```

## Architecture

- `evals/` — Inspect AI task definitions (Python `@task`)
- `scorers/` — Custom scoring functions (Python `@scorer`)
- `datasets/v3_review_validated/` — Validated ground truth (JSONL)
- `tools/` — Supporting scripts (validation UI, regression detection)
- `evals/baselines/` — Stored baseline runs (gitignored, local only)
- `logs/` — Eval run outputs (gitignored, local only)

## Ground Truth Schema

Findings in `datasets/*/critical_findings.jsonl` extend the parallax JSONL schema with:

- `validated: true` — finding has been reviewed
- `validation_status: "real_flaw" | "false_positive" | "ambiguous"`
- `validation_notes: string` — why this classification
- `validator_id: string` — who validated
- `validation_date: string` — when validated

Only `real_flaw` findings are used as ground truth.

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-..."   # Personal key
# Work context: AWS credentials for Bedrock (see ADR-005)
```
```

**Step 2: Commit**

```bash
git add README-evals.md
git commit -m "docs: eval framework README with workflow guide"
```

**Step 3: Push and open PR**

```bash
git push -u origin feat/inspect-ai-integration-design
gh pr create \
  --title "feat: Inspect AI eval framework (Phase 1)" \
  --body "$(cat <<'EOF'
## Summary

- Inspect AI integration using conventional Dataset/Sample/Task/Scorer patterns
- Severity calibration eval against validated ground truth (v3 Critical findings)
- Ablation tests: section-level drop validates skill content contribution
- Regression detection: compare eval runs to baseline, PASS/WARN/FAIL thresholds
- Makefile-driven workflow: `make eval`, `make regression`, `make view`, `make cycle`
- Skill content loaded at eval runtime — prompt changes flow through automatically

## Test Plan

- [ ] `make setup` succeeds (venv created, inspect-ai installed)
- [ ] `make test` passes all unit tests
- [ ] `make eval` runs against empty dataset (0 findings, not error)
- [ ] `make help` prints formatted output

Closes #5
EOF
)"
```

---

## Phase 1 Complete

After this plan executes, the eval framework is operational. Ground truth dataset will be populated by the validation UI (built in parallel worktree).

**Next steps (Phase 2):**
- `finding_quality_scorer.py` — LLM-as-judge for finding actionability
- `pattern_extraction_scorer.py` — semantic clustering validation
- Multi-model comparison (Codex portability check)
- Expand datasets: requirements-light, pattern-extraction
