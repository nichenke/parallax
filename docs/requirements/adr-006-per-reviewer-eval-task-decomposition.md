# ADR-006: Per-Reviewer Eval Task Decomposition

**Date:** 2026-02-17
**Status:** Accepted
**Deciders:** @nichenke
**Related:** Issue #5 (Eval Framework), ADR-005 (Inspect AI integration), eval-strategy-synthesis-2026-02-17.md

---

## Context

Session 21 implemented the Phase 1 eval framework using the design from v1: load the full parallax skill as the Inspect AI `system_message()` and run `generate()`. On the first real eval run (`make eval`), accuracy was 0.000.

**Root cause — two-layer mismatch:**

**Layer 1 (orchestration):** `skills/requirements/SKILL.md` is an orchestration workflow. Step 1 asks "What should I call this review folder?", Step 3 dispatches 5 parallel agents via Task tool. In eval context, there is no interactive input and no Task tool. The model produced ~102 tokens of interactive prompts and stopped. No findings were generated.

**Layer 2 (output format):** Even if orchestration were solved, four of the five reviewer agents output JSONL — but `assumption-hunter.md` specified markdown output. The scorer in `output_parser.py` expects JSONL. Any agent outputting markdown produces 0 parsed findings.

Session 22 (Opus research report review) confirmed the correct fix: decompose to per-reviewer eval tasks using individual agent prompts, not the full skill.

---

## Decision

**Replace the single combined eval task with per-reviewer eval tasks.**

Each reviewer agent (`assumption-hunter`, `scope-guardian`, `problem-framer`, `constraint-finder`, `success-validator`) gets its own `@task` function in `evals/reviewer_eval.py`. The task uses `system_message(load_agent_content(agent_name))` — the agent's system prompt directly, not the skill. Document content is passed via `Sample.input`.

**Supporting changes:**
1. `evals/utils/agent_loader.py` — new utility: load agent content (strip YAML frontmatter)
2. `evals/utils/dataset_loader.py` — add `reviewer_filter` parameter (filter ground truth by `reviewer` field)
3. `agents/assumption-hunter.md` — fix output format from markdown to JSONL (consistent with all other agents)
4. `Makefile` — add `reviewer-eval` target

**The original `severity_calibration.py` (single combined task) is retained** for comparison and historical reference. It remains broken as a useful reference point — if/when the skill produces parseable output, we would know.

---

## Rationale

### Why not fix the skill to work in eval context?

The orchestration skill asks interactive questions by design — that's what makes it useful in Claude Code. Creating an "eval mode" flag would bifurcate the skill into two code paths, adding complexity and a new failure mode (wrong mode selected at runtime). The skill and the eval serve different purposes and should remain separate artifacts.

### Why per-reviewer tasks instead of one combined task?

Per-reviewer tasks provide:
- **Attribution clarity:** which agent found which ground truth finding?
- **Granular regression detection:** if assumption-hunter degrades, that specific task fails — not an undifferentiated combined task
- **Prompt tuning attribution:** A/B test individual agent prompts without noise from other agents
- **Correct unit of testing:** the eval tests reviewer quality, not orchestration mechanics

### Why exclude v1-post-review-001 from per-reviewer tasks?

This finding was discovered during implementation, not by any reviewer reading the requirements document. It requires knowledge of how parallax skills actually work in practice — domain depth no reviewer would have from the document alone. Including it would make every per-reviewer task fail unconditionally, obscuring real detection signal.

### Why fix assumption-hunter output format?

All other agents already output JSONL. The markdown format in assumption-hunter was an oversight from the initial implementation. Making all agents consistent means:
- The scorer can treat all agents uniformly
- No special-case parsing code required
- The format is now a requirement (FR-ARCH-3), not a convention

---

## Consequences

**Positive:**
- `make reviewer-eval` can achieve accuracy > 0.000 (Phase 1 unblocked)
- Reviewer-level regression detection (not just combined pass/fail)
- Consistent output format across all reviewer agents
- Agent prompts are self-contained (no implicit tool dependency)

**Negative:**
- The original `severity_calibration.py` task (which tested the full skill integration) now has no path to accuracy > 0 without a separate "eval-compatible skill" artifact
- Five tasks instead of one increases eval runtime (partially offset by per-reviewer parallelism in Inspect AI)

**Deferred:**
- Tier 3 (agent bridge / inspect_swe) remains Phase 3+. This is a system-level test that runs the full skill inside Docker — it is not a replacement for per-reviewer unit testing, it is a different test layer
- Phase 2 (LLM-as-judge quality scoring) remains blocked until Phase 1 produces non-zero accuracy and quality rubric is defined (FR-QUALITY-1)

---

## Supersedes

- **Design v1** (`docs/plans/2026-02-16-inspect-ai-integration-design.md`): Section "Eval Architecture" — single combined task using full skill as system prompt
- **Requirements v1 FR2.1** (`docs/requirements/inspect-ai-integration-requirements-v1.md`): "Build `severity_calibration_scorer.py` using full skill as system message"
