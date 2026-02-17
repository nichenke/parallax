# Design: Inspect AI Integration — v2

**Date:** 2026-02-17
**Status:** Draft
**Related:** Requirements v2 (`docs/requirements/inspect-ai-integration-requirements-v2.md`), ADR-006, eval-strategy-synthesis-2026-02-17.md

---

## Overview

This document supersedes the v1 design (available in git history). See ADR-006 for the full rationale.

**Architecture:** Per-reviewer eval tasks. Each reviewer agent (assumption-hunter, scope-guardian, etc.) has its own `@task` function. The agent's system prompt is loaded directly as `system_message()`. Document content is passed in `Sample.input`. No tools required — the reviewer reads the document from the prompt and produces JSONL findings.

---

## Revised Repository Structure

```
parallax/
├── evals/
│   ├── __init__.py
│   ├── severity_calibration.py        # Original combined task (keep for comparison)
│   ├── reviewer_eval.py               # NEW: per-reviewer @task functions
│   ├── ablation_tests.py              # Unchanged
│   └── utils/
│       ├── __init__.py
│       ├── dataset_loader.py          # Updated: reviewer_filter parameter
│       ├── output_parser.py           # Unchanged
│       ├── skill_loader.py            # Unchanged
│       └── agent_loader.py            # NEW: load agent prompts (strip frontmatter)
├── scorers/
│   └── severity_scorer.py             # Unchanged
├── agents/
│   ├── assumption-hunter.md           # Fixed: markdown → JSONL output format
│   ├── scope-guardian.md              # Already JSONL
│   ├── problem-framer.md              # Already JSONL
│   ├── constraint-finder.md           # Already JSONL
│   └── success-validator.md           # Already JSONL
├── datasets/
│   └── inspect-ai-integration-requirements-light/
│       ├── critical_findings.jsonl    # 10 validated findings (5 reviewers + 1 post-review)
│       └── metadata.json              # Dataset info, design doc hash
└── Makefile                           # Updated: reviewer-eval target
```

---

## Per-Reviewer Task Architecture

### Agent Loader (`evals/utils/agent_loader.py`)

Loads agent system prompt content from `agents/<name>.md`, stripping YAML frontmatter.

```python
def load_agent_content(agent_name: str) -> str:
    """Load agent system prompt, stripping YAML frontmatter."""
    path = agents_root / f"{agent_name}.md"
    content = path.read_text()
    # Strip frontmatter: content between first pair of "---" delimiters
    if content.startswith("---"):
        end = content.index("---", 3)
        return content[end + 3:].strip()
    return content
```

### Dataset Loader — Reviewer Filter

`load_validated_findings()` gains an optional `reviewer_filter` parameter. When provided, only findings with matching `reviewer` field are included in ground truth.

```python
def load_validated_findings(
    dataset_path: str,
    reviewer_filter: str | None = None
) -> Dataset:
    ...
    real_flaws = [
        f for f in findings
        if f.get("type") == "finding"
        and f.get("validation_status") == "real_flaw"
        and (reviewer_filter is None or f.get("reviewer") == reviewer_filter)
    ]
    ...
```

**Special case: `post-review` finding**
`v1-post-review-001` was discovered during implementation, not by any reviewer agent reviewing the requirements document. It is excluded from per-reviewer task ground truth via reviewer_filter (no agent is named "post-review"). This finding may be included in a future "implementation discovery" dataset for system-level testing.

### Per-Reviewer Tasks (`evals/reviewer_eval.py`)

One `@task` function per reviewer agent. Pattern:

```python
@task
def assumption_hunter_eval() -> Task:
    return Task(
        dataset=load_validated_findings(DATASET_PATH, reviewer_filter="assumption-hunter"),
        plan=[
            system_message(load_agent_content("assumption-hunter")),
            generate()
        ],
        scorer=severity_calibration(),
        max_tokens=4000
    )
```

**Reviewers with ground truth in current dataset:**
- `assumption_hunter_eval` — 2 findings (001, 013)
- `constraint_finder_eval` — 2 findings (002, 009)
- `problem_framer_eval` — 2 findings (006, 008)
- `scope_guardian_eval` — 1 finding (013)
- `success_validator_eval` — 2 findings (001, 002)

**Total testable:** 9 findings. `v1-post-review-001` excluded from all per-reviewer tasks.

---

## JSONL Output Alignment

**Problem:** `assumption-hunter.md` specified markdown output format. All other agents specify JSONL. The scorer only parses JSONL.

**Fix:** Update `assumption-hunter.md` output format section to match the JSONL schema from other agents. No change to the agent's analytical content — only the output format instruction changes.

**Required JSONL fields (all agents):**
```json
{
  "type": "finding",
  "id": "v1-<agent-name>-NNN",
  "title": "...",
  "severity": "Critical|Important|Minor",
  "phase": {"primary": "...", "contributing": null},
  "section": "...",
  "issue": "...",
  "why_it_matters": "...",
  "suggestion": "..."
}
```

The blind spot check meta-finding also uses JSONL format (consistent with scope-guardian pattern).

---

## Makefile Update

```makefile
reviewer-eval:
    mkdir -p $(LOG_DIR)
    . $(VENV) && inspect eval evals/reviewer_eval.py \
        --model $(MODEL) \
        --log-dir $(LOG_DIR) \
        --tags "git=$(shell git rev-parse --short HEAD)"
```

`make reviewer-eval` runs all 5 per-reviewer tasks. The original `make eval` (severity_calibration.py) remains for comparison.

---

## Ground Truth Management

### Current dataset
`datasets/inspect-ai-integration-requirements-light/` — 10 validated Critical findings:

| ID | Reviewer | Status |
|----|----------|--------|
| v1-problem-framer-006 | problem-framer | real_flaw |
| v1-problem-framer-008 | problem-framer | real_flaw |
| v1-constraint-finder-009 | constraint-finder | real_flaw |
| v1-assumption-hunter-001 | assumption-hunter | real_flaw |
| v1-scope-guardian-013 | scope-guardian | real_flaw |
| v1-constraint-finder-002 | constraint-finder | real_flaw |
| v1-assumption-hunter-013 | assumption-hunter | real_flaw |
| v1-success-validator-001 | success-validator | real_flaw |
| v1-success-validator-002 | success-validator | real_flaw |
| v1-post-review-001 | post-review | real_flaw (excluded from per-reviewer tasks) |

### Refresh triggers (FR-ARCH-4)
Ground truth must be refreshed when:
- Any reviewer agent prompt changes
- The reviewed document (requirements-v1.md) changes substantially
- New findings discovered during implementation that reviewers missed

### Refresh process
1. Run `parallax:requirements --light` on updated document
2. Validate findings in browser UI (`make validate`)
3. Update `critical_findings.jsonl` with new validated findings
4. Update `metadata.json` with new document hash and review date
5. Run `make reviewer-eval` to confirm new ground truth is detectable

---

## Phase 1 Test Plan

After implementation, Phase 1 is complete when:

1. **Output format compliance:** `make reviewer-eval` runs without parse errors — all 5 agents produce parseable JSONL
2. **Non-zero detection:** At least 1 reviewer task achieves recall > 0.0
3. **Target detection:** ≥1 reviewer task achieves recall ≥ 0.90 and precision ≥ 0.80
4. **All 5 tasks run:** No task crashes at instantiation time
5. **Tests pass:** `make test` passes with new tests for `agent_loader`, `reviewer_filter`, and per-reviewer task instantiation

**Debugging if detection is low:**
- Check `inspect view` for raw model output (is it JSONL or prose?)
- Check if IDs in model output match expected IDs (exact match vs fuzzy match)
- If fuzzy match needed: check title similarity score (threshold 0.8)
- If IDs differ by version prefix: check that agent prompt specifies correct ID format

---

## Phase 2 Design Prerequisites (not in Phase 1)

Before Phase 2 (LLM-as-judge quality scoring):
1. Phase 1 produces non-zero accuracy on at least one reviewer task
2. Quality rubric defined and documented (FR-QUALITY-1)
3. Rubric validated with ground truth examples (5/5 and 1/5 examples per dimension)
4. Grader model selected (Haiku for cost, Sonnet for quality — start with Sonnet, optimize later)

Before Phase 1.5 (multi-model comparison):
1. Phase 1 non-zero accuracy on Anthropic
2. Google/Gemini API key available
3. Cost tracking report implemented (`make cost-report`)

---

## Key Design Decisions

**Why agent prompts, not skill as system message?**
Skills are orchestration scripts (ask questions, dispatch agents, write to disk). Agent prompts are single-purpose reviewer instructions. Evals need reviewers, not orchestrators. This is also the correct test attribution: if assumption-hunter degrades, we want the assumption-hunter task to fail, not the combined task.

**Why JSONL output format for eval context?**
The scorer (`output_parser.py`) expects JSONL. Markdown requires a conversion step that introduces noise (section parsing, title extraction). JSONL is deterministic. The tradeoff (less readable for humans) is acceptable for eval context — Inspect View shows raw output alongside scores.

**Why keep severity_calibration.py?**
The original combined task remains for comparison. It's useful as a regression signal for the orchestration layer (if the skill ever produces parseable output in eval context, we'd want to know). It also keeps ablation_tests.py functional (which still references the combined task pattern).

**Why exclude post-review finding from per-reviewer tasks?**
`v1-post-review-001` (skill/eval interface mismatch) was discovered during implementation, not by any reviewer reading the requirements document. No reviewer agent would detect it by reading requirements-v1.md — it requires knowing how parallax skills actually work. Excluding it keeps per-reviewer ground truth honest: each task only tests what that agent could plausibly detect.
