# Requirements: Inspect AI Integration — v2

**Date:** 2026-02-17
**Status:** Draft v2.0
**Scope:** Eval framework — Phase 1 implementation corrections and Phase 2 prerequisites
**Related:** Issue #5, ADR-005, ADR-006, eval-strategy-synthesis-2026-02-17.md

---

## Background

This document supersedes the v1 requirements (available in git history). v1 was written pre-implementation. Implementation revealed a fundamental architecture mismatch: the skill-as-system-prompt pattern fails because parallax skills are orchestration workflows, not single-turn reviewers. The scorer got 0 findings to match against because the model produced interactive prompts instead of JSONL.

v2 replaces the single combined eval task with per-reviewer eval tasks. Each reviewer agent has its own `@task` function that uses the agent's system prompt directly. This is not a workaround — it's the correct architecture for testing review quality at the agent level.

Five additional gaps discovered during implementation are addressed in this document. See ADR-006 for the full decision rationale.

---

## Problem Statement (unchanged from v1)

Parallax skills are developed iteratively with no systematic way to measure effectiveness. Changes to skill prompts may improve, degrade, or have no effect on finding quality — we cannot tell which. This blocks empirical improvement and risks shipping broken skills.

**v2 addition:** The eval framework itself must be testable at the component level. The unit of testing is the individual reviewer agent (assumption-hunter, scope-guardian, etc.), not the full orchestration skill.

---

## Functional Requirements — v2 Additions

These add to or supersede corresponding v1 requirements.

---

### FR-ARCH-1: Per-Reviewer Eval Task Decomposition

**Supersedes:** FR2.1 (single combined `severity_calibration` eval using full skill as system prompt)

**Requirement:** Each reviewer agent has its own `@task` function in `evals/reviewer_eval.py`. The task uses the agent's system prompt as `system_message()`, not the full skill.

**Rationale:** Parallax skills are orchestration workflows — they ask interactive questions, dispatch parallel agents via Task tool, and write findings to disk. A single-turn eval context provides none of these affordances. Loading the full skill as system prompt produces interactive prompts instead of findings (confirmed: 102 tokens of interactive output, accuracy 0.000).

Per-reviewer tasks provide:
- Attribution clarity: which agent found which ground truth finding?
- Granular regression detection: if assumption-hunter degrades, which specific task fails?
- Prompt tuning: A/B test individual agent prompts without noise from other agents

**Acceptance Criteria:**
- `evals/reviewer_eval.py` contains one `@task` function per reviewer agent
- Each task uses `system_message(load_agent_content(agent_name))` as the solver
- Each task filters ground truth to findings where `reviewer == agent_name`
- Ground truth filtering excludes post-review findings (discovered during implementation, not detectable from requirements doc alone)
- `make reviewer-eval` runs all per-reviewer tasks

---

### FR-ARCH-2: Eval-Compatible Agent Interface

**New requirement:** Each reviewer agent must function correctly in eval context without modifications to the agent file.

**Rationale:** The agent file serves two contexts: (1) production — dispatched by the skill with full Claude Code tool access, multi-turn; (2) eval — used as system prompt in single-turn Inspect AI task with no tools. Both must work from the same agent file.

**Acceptance Criteria:**
- Agent system prompts are self-contained (no "now use tool X to read the design doc" instructions that assume tool availability)
- Agent prompts instruct: "The design document content will be provided to you in this message. Review it thoroughly."
- Agents do not require tool calls to produce findings (document content delivered in `Sample.input`)
- Agent output format (JSONL) parseable by `evals/utils/output_parser.py`

---

### FR-ARCH-3: JSONL Output Format as Explicit Requirement

**New requirement:** All reviewer agents must output JSONL. The output format is a requirement, not an implementation choice.

**Rationale:** During v1 implementation, assumption-hunter was the only agent with markdown output format. The scorer (`output_parser.py`) expects JSONL. Output format inconsistency between agents blocks the eval framework entirely — one non-compliant agent produces 0 parsed findings.

**Required JSONL Schema (per finding):**
```json
{
  "type": "finding",
  "id": "<reviewer>-<NNN>",
  "title": "Brief finding title (≤80 chars)",
  "severity": "Critical|Important|Minor",
  "phase": {
    "primary": "survey|calibrate|design|plan",
    "contributing": null
  },
  "section": "Section name from the reviewed document",
  "issue": "Description of the gap or problem found",
  "why_it_matters": "Impact if this gap is not addressed",
  "suggestion": "Specific, actionable fix"
}
```

**Acceptance Criteria:**
- All 5 reviewer agents output valid JSONL (one finding per line)
- `parse_review_output()` successfully parses output from any reviewer agent
- Blind spot check meta-findings also use JSONL format (not prose)
- Zero findings parsed from any agent is treated as an output format failure, not zero findings found

---

### FR-ARCH-4: Ground Truth Refresh Cadence

**New requirement:** Ground truth datasets must be refreshed when the reviewed artifact or reviewer agents change significantly.

**Rationale:** Stale ground truth causes false negatives in the eval framework — findings that the design has since addressed appear as "not detected" because they no longer exist in the current document. Discovered during Session 19: stale findings from the design doc validation UI caused misleading eval results.

**Refresh triggers:**
- Any reviewer agent prompt changed (the agent may now detect different things)
- The reviewed requirements/design document updated substantially (findings may no longer apply)
- A new finding discovered during implementation that reviewers missed (post-review findings)
- Ablation baseline established from stale ground truth (FR4.1 prerequisite)

**Acceptance Criteria:**
- `metadata.json` includes `design_doc_hash` field (content hash of reviewed document)
- `make validate` re-runs if document hash differs from stored hash
- Ground truth refresh is documented as a required step after any reviewer prompt change
- Post-review findings (discovered during implementation) stored separately in dataset with `"discovery": "implementation"` field and excluded from per-reviewer task ground truth

---

### FR-ARCH-5: Cost Budget Per Eval Suite Run

**New requirement:** Maximum acceptable API cost per full eval suite run must be specified.

**Rationale:** Per-reviewer task decomposition increases eval run count (5 tasks instead of 1). Multi-model comparison (Phase 1.5), LLM-as-judge grading (Phase 2), and combined scorer pipelines each add cost. Without a budget constraint, there is no signal for when to optimize.

**Budget constraints:**
- Single-reviewer task (1 agent × N findings): <$0.10 per task
- Full reviewer eval suite (5 agents): <$0.50 per suite run
- Full suite + LLM-as-judge grading (Phase 2): <$2.00 per run
- Multi-model comparison (Phase 1.5, 3 models × 5 agents): <$1.50 per run

**Cost reduction levers (in order of preference):**
1. Batch API (50% discount, no code changes) — enable after Phase 1 validated
2. Haiku for mechanical scorers, Sonnet for reviewer tasks
3. Reduce sample count (prioritize highest-confidence ground truth findings)

**Acceptance Criteria:**
- `make cost-report` reads eval logs and reports: model, input tokens, output tokens, estimated cost per run
- Eval run cost logged in EvalLog metadata
- If single run exceeds budget, report flags for optimization

---

### FR-QUALITY-1: Quality Rubric Definition (Phase 2 Prerequisite)

**New requirement:** Define the LLM-as-judge quality rubric before implementing Phase 2 finding quality scorer.

**Rationale:** v1 requirements specified "90% detection rate, 80% precision" without defining what a "detected" finding means qualitatively. Detection (recall/precision) only measures whether a finding exists — not whether it's useful. A finding that IDs the right issue but provides a vague suggestion or wrong severity is technically "detected" but not useful.

**Required rubric dimensions (starting point — validate with ground truth examples):**
1. **Specific and actionable** (1–5): Is the finding specific enough to act on? (1 = vague, 5 = clear action with specific location)
2. **Severity appropriate** (1–5): Does the severity match the actual impact? (1 = clearly wrong tier, 5 = unambiguously correct)
3. **Suggestion helpful** (1–5): Does the suggestion actually resolve the gap? (1 = generic, 5 = directly addresses root cause)
4. **Why it matters convincing** (1–5): Does the explanation connect to real consequences? (1 = abstract, 5 = concrete failure scenario)

**5/5 example (ground truth):**
- Finding: v1-success-validator-001 ("Detection rate has no target thresholds")
- Specific: FR2.2 is cited, exact problem stated
- Severity: Critical — cannot determine pass/fail without thresholds
- Suggestion: Add explicit numeric thresholds (90% recall, 80% precision)
- Why it matters: Ablation tests cannot run without a baseline to compare against

**Acceptance Criteria:**
- Rubric documented with 1-example and 5-example for each dimension before Phase 2 implementation begins
- LLM-as-judge prompt references rubric explicitly (not "is this finding good?")
- Rubric validated against existing ground truth findings before scoring new findings
- Target aggregate quality score defined (e.g., ≥3.5/5.0 average across all dimensions)

---

## MVP Phase Map (updated from v1)

| Phase | What | Blocking issue | Status |
|-------|------|----------------|--------|
| **0** | Establish ground truth (human validation) | Circular dependency | ✅ Complete (requirements-light dataset) |
| **1** | Per-reviewer eval tasks, JSONL output fix, detection baseline | Output format alignment (FR-ARCH-1, FR-ARCH-3) | In progress |
| **1.5** | Multi-model comparison (Sonnet vs Haiku), cost tracking | Google account, cost budget spec (FR-ARCH-5) | Not started |
| **2** | LLM-as-judge quality scoring, mock tools (Tier 2) | Quality rubric definition (FR-QUALITY-1) | Not started |
| **2.5** | Multi-model LLM grading, synthesis eval | Multi-model + Phase 2 stable | Not started |
| **3** | Agent bridge / inspect_swe (system-level runtime testing) | Phase 1–2 stable | Not started |
| **4+** | Markdown vs JSONL output experiment, blind spot detection | Detection + quality baselines | Not started |

**Phase 1 is the immediate target.** Phases 2+ remain blocked until Phase 1 produces non-zero accuracy.

---

## Explicitly Out of Scope (v2)

Items that were already deferred in v1 remain deferred:
- Batch API integration (Phase 3+)
- Fine-grained ablation (per-persona, Phase 3+)
- Input corruption adversarial tests
- CI/CD automation
- Blind spot detection (Phase 4+)

**v2 additions to deferred list:**
- react() multi-turn eval loop (Phase 2, filed Issue #50)
- Codex compatibility eval (after Anthropic baseline, Phase 1.5)
- Orchestrate wrapper (decision pending, Issue #52)
- Markdown vs JSONL output format experiment (Phase 4+, Issue #48)

---

## Open Questions (v2)

1. **post-review finding handling:** v1-post-review-001 was discovered during implementation, not by a reviewer agent. It is excluded from per-reviewer task ground truth. Should it be added to a separate "implementation discovery" dataset to track future misses?

2. **Reviewer consensus threshold:** If 3/5 reviewers independently flag the same root cause (e.g., ground truth circular dependency), should duplicates be deduplicated to one ground truth finding or kept as separate findings for each reviewer?

3. **Ground truth size:** 10 validated Critical findings (requirements-light dataset) — sufficient for Phase 1 detection baseline? Or should Important findings be added before Phase 1 completes?

4. **Ablation tasks:** With per-reviewer decomposition, should ablation tests also be decomposed per-agent, or is a combined "drop all persona content" test sufficient for Phase 1?

---

## References

- **eval-strategy-synthesis-2026-02-17.md** — Primary input; captures learnings from Opus research report and Sessions 21–22 debugging
- **ADR-005** — Inspect AI integration decision
- **ADR-006** — Per-reviewer eval task decomposition (supersedes v1 FR2.1)
- **Issue #45** — TDD edge case discipline (from implementation review)
- **Issues #47–52** — Filed during synthesis phase, capture open questions
