# Eval Strategy Synthesis — 2026-02-17

> **Purpose:** Capture current understanding of eval architecture, open decisions, and design gaps for re-synthesizing eval requirements and design in the next iteration. Written after reviewing `docs/research/inspect-ai-eval-patterns.md` and the subagent analysis on workflow automation and directory co-location.

---

## Current State

- Branch: `feat/inspect-ai-integration-design`, PR #46 open
- 33 tests passing
- `make eval` runs end-to-end (8,462 input tokens) but accuracy: 0.000
- Ground truth: 10 validated Critical findings in `datasets/inspect-ai-integration-requirements-light/`
- Root cause of 0.000: two-layer mismatch (see below)

---

## The Two-Layer Mismatch

**Layer 1 (orchestration):** `skills/requirements/SKILL.md` is an orchestration workflow. Step 1 asks "What should I call this review folder?" and Step 3 dispatches 5 parallel agents via Task tool. In eval context, no interactive input, no Task tool. Model produces ~100 tokens of interactive prompts and stops.

**Layer 2 (output format):** Even with decomposed per-reviewer tasks, reviewer agents output structured markdown (`agents/assumption-hunter.md`: "Write your findings as structured markdown"). Scorer in `evals/utils/output_parser.py` expects JSONL. Zero findings parsed from markdown output.

**Fix for both:** Decompose to per-reviewer eval tasks (`evals/reviewer_eval.py`) + add JSONL output instruction to reviewer agent prompts in eval context.

---

## Eval Architecture: Three Tiers

### Tier 1 — Solver Chains (current, broken)
`system_message(skill) + generate()`. Works for single-turn tasks. Does not work for orchestration skills.

### Tier 2 — Agents with Tools (Phase 1 target)
Individual reviewer agents (`assumption-hunter`, `scope-guardian`, etc.) as system prompts. Document content in `Sample.input`. Per-reviewer `@task` functions with per-reviewer ground truth filtering. No tools needed for Phase 1 — reviewers receive full doc in prompt.

Phase 2: add mock tools (`mock_read()`, `mock_grep()`) for richer behavior testing.

### Tier 3 — Agent Bridge / inspect_swe (Phase 3+, reframed)
**Reframe from research report:** This is not an "alternative to decompose" — it is a different test type. Agent bridge runs the full skill inside a Docker sandbox to confirm skills work correctly inside each target runtime (Claude Code, Codex). Different system prompts, different tool availability, different ambient context per runtime. Use for system/integration testing, not unit-level quality testing. Phase 3+ is still the right timing.

---

## Test Philosophy

Write tests for what you want to protect or have encountered quality issues with. Not everything. Stop at good functional + manual testing coverage. Specific criteria:
- Detection: did the reviewer find the known ground truth findings?
- Output format compliance: is the output parseable?
- Skill loading: does the correct skill path resolve?
- Dataset integrity: is ground truth non-empty and valid?

**Don't test:** Every possible edge case, orchestration mechanics, internal skill formatting choices.

---

## Output Format Strategy

**Current:** JSONL — required for Phase 1 eval scorer compatibility.

**Phase 4+ question (filed as issue):** Test speed/quality/cost for switching back to markdown as default human-readable format, with JSONL serialization as a scorer pipeline step. Hypothesis: markdown may produce richer findings. JSONL stays until eval pipeline is stable and quality baseline exists for comparison.

**Immediate action:** Align all reviewer agent prompts on JSONL output format for eval context. This is the fix for Layer 2.

---

## Quality Bar Problem (Never Resolved)

Provisional thresholds from requirements v1.1: 90% detection, 80% precision. These are numbers without a definition of what "quality" means at the individual finding level.

**LLM-as-judge (Phase 2) as the fix:** Score each finding on a rubric:
1. Specific and actionable (1-5)
2. Severity appropriate (1-5)
3. Suggestion helpful (1-5)
4. "Why it matters" convincing (1-5)

This gives a concrete number to optimize against, a regression signal for quality (not just detection), and a comparison baseline across reviewer agents and prompt changes.

**Design and requirements gap:** The quality bar must be defined before Phase 2 implementation. The rubric above is a starting point; it needs validation against the ground truth findings.

---

## Multi-Turn Eval — react() Agent (Education Track)

Inspect AI's `react()` runs a tool loop until the model stops calling tools, then produces final output. This is closer to how reviewers work in production. Deferred to a dedicated education + evaluation track (filed as issue). Prerequisite: Phase 1 detection baseline established first. Key questions:
- Does multi-turn produce better findings? (quality, not just detection)
- Cost scaling with turns?
- Does it change how reviewer prompts should be written?

---

## Multi-Model Comparison

Free via Inspect AI `--model` flag. No code changes needed. Prerequisites:
- Google account + Gemini API setup
- Cost tracking infrastructure (see below)

Phase 1.5 target: after per-reviewer tasks are green on Anthropic.

---

## Batch API

50% cost reduction via `--batch` flag. No code changes. Enable for all non-interactive eval runs. Free win once Phase 1 works.

---

## Cost Tracking (Missing Infrastructure)

No current mechanism to track API cost across eval runs. Needed because:
- Codex experiments (Pro account — need burn rate visibility)
- Multi-model runs are 3x cost of single-model
- LLM-as-judge adds grader cost on top of reviewer cost
- Batch API savings should be visible to confirm it's working

Proposed: `make cost-report` target that reads `logs/` and aggregates: model, tokens in, tokens out, estimated cost per run.

---

## Codex Compatibility

**Timing:** After basic Anthropic tests work. Sequence: green on Anthropic → run same evals on Codex → measure delta → assess compatibility effort.

**Existing assets:** Branches from previous design/requirements work have a now-obsolete deterministic test runner with Claude/Codex smoothing. Worth checking before assuming clean start. Gate: must not break Claude tests.

**Dependency risk:** If the orchestrate wrapper (see below) composes superpowers skills, need to verify Codex supports the same invocation patterns before committing to that dependency.

---

## Orchestrate Wrapper (Open Decision)

**Status:** Explicitly deferred since Session 1. Eval framework is now built — the original blocker is resolved. Time to decide.

**UX pain evidence:** Users don't remember magic phrases, don't know the trigger sequence, have no pipeline visibility (ux-friction-log.md).

**Current state:** Skills are manually triggered. `parallax:orchestrate` namespace is planned but not started.

**Recommended shape:** Thin prompted router — not auto-trigger. After brainstorming, ask "Ready to run requirements review? [y/n]". Artifact paths auto-detected from previous step. No analytical content in the orchestrate layer (keeps eval attribution clean).

**Prerequisite:** Per-reviewer eval tasks (Phase 1) working first — need detection baseline to measure whether the wrapper changes analytical quality.

**Open sub-questions (filed as issue):**
- Trigger detection without modifying superpowers plugin
- Superpowers dependency isolation for eval attribution
- Codex compatibility

---

## Directory Co-location (Deferred, Principled Reason)

Current layout (`datasets/`, `docs/`, `skills/` as separate trees) is functionally correct and Inspect AI-compatible. The co-location question is really a plugin distribution question: **datasets are developer artifacts, not plugin content.** Each team generates their own ground truth for their own codebase — datasets should not travel with a published plugin.

Action: enrich `metadata.json` schema (`source_skill`, `review_folder` fields) to make artifact family relationships explicit without moving files. Revisit layout before first published plugin release.

---

## Blind Spot Concern (Phase 3+, Don't Lose This)

As we tune down Important findings (reduce noise), we risk hiding systematic coverage gaps. The eval framework could be optimizing for a narrow band of "known findable" issues while missing categories we've never seen. Need a mechanism to detect this — possibly:
- Deliberate blind spot injection (run with a design that has known Category X flaw, verify it's detected)
- Cross-reviewer coverage analysis (if 0 reviewers flag a finding type, is that because it's absent or because no reviewer has that lens?)

This is Phase 3+. Related to Issue #34 (blind spot checks). Flag and don't forget.

---

## Phase Map

| Phase | What | Key blocking issue |
|-------|------|-------------------|
| **1** | Per-reviewer eval tasks, JSONL output fix, detection baseline | Output format alignment |
| **1.5** | Codex eval, multi-model comparison | Google account, cost tracking |
| **2** | LLM-as-judge quality scoring, mock tools (Tier 2) | Quality rubric definition |
| **2.5** | Multi-model LLM grading, synthesis eval | Multi-model setup |
| **3** | End-to-end orchestration (Tier 3, agent bridge) | Phase 1-2 stable |
| **4+** | Markdown vs JSONL output experiment, blind spot detection | Detection + quality baselines |

---

## Issues Filed This Session

| # | Title |
|---|-------|
| #47 | Research: What made the Opus research prompt work? (prompt-context experiment) |
| #48 | Experiment: Markdown vs JSONL output format — speed/quality/cost tradeoff |
| #49 | Design: Use LLM-as-judge to establish concrete quality bar |
| #50 | Educate + evaluate: multi-turn eval with react() agent loop |
| #51 | Multi-model comparison + cost tracking infrastructure |
| #52 | Decision: parallax:orchestrate wrapper |

---

## For Next Iteration: Requirements/Design Questions

When re-synthesizing eval requirements and design, address these gaps:

1. **Quality bar definition:** What does a 5/5 finding look like on each rubric dimension? Get human-annotated examples before implementing LLM-as-judge.

2. **Output format spec:** JSONL field schema must be documented as a requirement, not an implementation detail. Reviewer agents must be required to emit compliant JSONL (not just markdown with a conversion step).

3. **Eval-compatible interface requirement:** Requirements must specify that each reviewer agent must have an eval-compatible interface (single-turn, JSONL output, no tool dependency) distinct from its production interface (multi-turn, markdown, full tool set). These are two different artifacts.

4. **Cost budget per eval run:** Requirements should specify acceptable cost per full eval suite run. Without this, there's no constraint on multi-model + LLM-as-judge + epochs combinations.

5. **Ground truth refresh cadence:** Requirements should specify when ground truth must be refreshed (e.g., after any reviewer prompt change, after any design doc change that affects the reviewed artifact).
