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
│       ├── output_parser.py           # Updated: fence-stripping added
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
    import frontmatter  # python-frontmatter library (add to pyproject.toml)
    path = agents_root / f"{agent_name}.md"
    post = frontmatter.load(str(path))
    return post.content.strip()
```

**Dependency:** Add `python-frontmatter` to `pyproject.toml`. The custom `content.index("---", 3)` approach raises `ValueError` on malformed frontmatter (crashes all 5 tasks) and matches `---` horizontal rules in body text (silently truncates system prompt). `python-frontmatter` handles both edge cases natively.

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

**Pre-flight check (C-5):** Before writing `reviewer_eval.py`, open `critical_findings.jsonl` and print all unique `reviewer` field values. Confirm each matches the expected agent filename (without `.md`): `assumption-hunter`, `constraint-finder`, `problem-framer`, `scope-guardian`, `success-validator`. A typo (e.g., `assumption_hunter` with underscore) causes the reviewer filter to return zero findings, producing recall = 0.0 with no error — silent failure indistinguishable from the agent missing all findings. If the field is missing from any finding, add a data migration step before proceeding.

**Guard:** `reviewer_filter` that matches zero findings must raise `ValueError` listing available reviewer names, not return an empty dataset silently.

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

### Phase 1 Prerequisites (Audit Gate)

**Before writing a single line of `reviewer_eval.py`**, complete this checklist for all 5 agents:

| Agent | JSONL native | No fences | No "Read the file" | All required fields |
|-------|-------------|-----------|-------------------|---------------------|
| assumption-hunter | ❌ Fix required | verify | Fix required | verify |
| constraint-finder | verify | verify | verify | verify |
| problem-framer | verify | verify | verify | verify |
| scope-guardian | verify | verify | Fix required | verify |
| success-validator | verify | verify | Fix required | verify |

**Do not skip this gate.** The v1 `accuracy: 0.000` failure was caused by exactly this kind of format mismatch. Gate `make reviewer-eval` behind passing this checklist.

### Output Format Fix

**Problem 1 — Markdown output:** `assumption-hunter.md` specifies markdown output format. All other agents specify JSONL. The scorer only parses JSONL.

**Fix:** Update `assumption-hunter.md` output format section to produce raw JSONL. No change to analytical content — only the output format instruction changes.

**Problem 2 — Fence wrapping (C-2):** Claude wraps structured output in markdown code fences by default, even when instructed otherwise. A strict line-by-line JSONL parser returns zero findings for fenced-but-valid JSONL. This is an independent silent-zero path.

**Fix:** Add fence-stripping to `output_parser.py` as a preprocessing step before line-by-line JSON parsing:
```python
def strip_fences(text: str) -> str:
    """Strip leading/trailing markdown code fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0] if "```" in text else text
    return text.strip()
```
Add a test: provide fenced-but-valid JSONL, assert correct finding count. Add a distinct log message when zero findings are parsed (`"parse_result": "empty"`) to distinguish format failure from genuine zero.

Also update all agent system prompts to include: _"Output raw JSONL only. Do not wrap output in markdown code fences."_

**Problem 3 — Tool call instructions in body text (C-7):** `scope-guardian.md` and `success-validator.md` include "Read the design document thoroughly" as step 1 of their review process. In eval context, no tools are available — the model may attempt a tool call that fails, hallucinate a reading step, or skip it and produce fewer findings. FR-ARCH-2 acceptance criterion requires agents to contain "The design document content will be provided to you in this message."

**Fix:** For all 5 agents: remove or qualify "Read the [document]" instructions. Add explicit transition language: _"The document content is provided below. You do not need to use any tools."_

### Required JSONL Schema (all agents)

```json
{
  "type": "finding",
  "id": "v1-<agent-name>-NNN",
  "title": "...",
  "severity": "Critical|Important|Minor",
  "phase": {"primary": "survey|calibrate|design|plan", "contributing": null},
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
        --tags "git=$(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)"
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

**Phase 1 is a smoke test.** N=1-2 findings per reviewer makes recall measurements statistically meaningless — at N=2, a single missed finding is a 50-point recall drop; at N=1, recall is binary. Quantitative thresholds (recall ≥ 0.90, precision ≥ 0.80) are Phase 2 targets, after ground truth is expanded to N≥5 per reviewer. Eval output will display a disclaimer when N<5 per reviewer.

Phase 1 is complete when:

1. **No crashes:** `make reviewer-eval` runs to completion — all 5 tasks instantiate and complete without exceptions
2. **Parseable output:** All 5 agents produce at least some parseable JSONL (zero tasks return a parse error on every finding)
3. **Basic detection:** At least 3 of 5 reviewer tasks produce recall > 0.0 (agent is detecting something)
4. **Tests pass:** `make test` passes with new tests for `agent_loader`, `reviewer_filter`, and per-reviewer task instantiation

**What Phase 1 does not validate:** Recall accuracy, precision, or prompt quality. Those are Phase 2 after ground truth expansion.

**Debugging if output is empty:**
- Check `inspect view` for raw model output (is it JSONL or fenced JSONL or prose?)
- Confirm fence-stripping is working — paste raw output into `output_parser.py` manually
- Confirm reviewer field values in `critical_findings.jsonl` match filter strings exactly
- Run `make validate-dataset` to confirm per-reviewer finding counts before blaming the agent

---

## Phase 2 Design Prerequisites (not in Phase 1)

Before Phase 2 (LLM-as-judge quality scoring):
1. Phase 1 produces non-zero accuracy on at least one reviewer task
2. Quality rubric defined and documented (FR-QUALITY-1). Target aggregate quality score: ≥3.5/5.0 (provisional — adjust after Phase 2 baseline run)
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
