# Build-vs-Leverage Spike: LangGraph + Inspect AI

**Date:** 2026-02-16
**Triggered by:** V3 review findings (3 reviewers flagged build-vs-leverage decision deferral)
**Spike goal:** Determine if LangGraph or Inspect AI replace custom parallax:review infrastructure

---

## TL;DR

**LangGraph:** Wrong problem. Deterministic replay is for eval reproducibility (testing), not production orchestration. MVP doesn't need it.

**Inspect AI:** Wrong abstraction. Built for "test against ground truth" (eval harness), not "find design problems" (adversarial review). Use it later for skill testing (Issue #5), not for parallax:review orchestration.

**Recommendation:** Build JSONL schema from first principles. Defer both frameworks until hitting actual limitations.

---

## LangGraph Analysis

### What It Offers
- **Parallel execution:** Scatter-gather pattern with parallel edges
- **Deterministic replay:** Checkpointing + skip completed steps on resume
- **State persistence:** SQLite/Postgres/in-memory checkpointers
- **Human-in-the-loop:** Built-in approval gates with conditional edges
- **Retry logic:** Conditional edges + checkpoint forking

### What parallax:review Currently Does
```
Main session:
├─ Dispatch 6 reviewers (Task tool, background=true)
├─ Wait for completion notifications
├─ Read outputs (6 × ~50k tokens each)
├─ Manual synthesis in main context
└─ Interactive finding processing (AskUserQuestion)
```

### Mapping to Requirements

| Capability | Your Implementation | LangGraph Native | Migration Value |
|------------|---------------------|------------------|-----------------|
| **Parallel dispatch** | `Task` tool × 6 with `run_in_background=true` | Parallel edges | Low — works fine |
| **Deterministic execution** | None — re-running is full re-execution | Checkpointing with replay | **Eval-only** — not in production requirements |
| **State persistence** | Files on disk (`docs/reviews/<topic>/`) | SQLite/Postgres checkpointers | Low — filesystem is fine |
| **Human-in-the-loop** | Manual — read outputs, AskUserQuestion | Built-in approval gates | Medium — could automate "escalate vs retry" |
| **Retry logic** | Manual — user decides, re-dispatch reviewers | Conditional edges + checkpoint forking | Medium — no infinite loop risk |
| **Cross-iteration tracking** | Git commits per iteration | Thread-based checkpoints | Low — git is better for diffs |

### Requirements Check: Where's Deterministic Replay?

**Only mention in requirements (design-orchestrator.md:165):**
> "Pipeline agents stay stateless — **deterministic runs are essential for eval reproducibility**."

This is about **testing** (run same eval twice, get comparable results), NOT production orchestration.

**Actual production requirements:**
- Human checkpoints at decision points ✓
- Async-first (artifacts to disk) ✓
- Git-tracked iteration history ✓
- Interactive finding processing ✓

**None of these need LangGraph's deterministic replay.**

### Adoption Barrier Analysis

| Concern | Reality |
|---------|---------|
| **Installation** | `pip install langgraph` — not worse than other deps |
| **Claude Code compatibility** | Python lib. Skills dispatch via `Task` tool. No conflict. |
| **User learning curve** | Users invoke `/review` — never see LangGraph (internal to skill) |
| **Deployment** | Skills are markdown + agents. LangGraph = dev-time only |

**Key insight:** LangGraph wouldn't be a *user* dependency — it would be a *skill developer* dependency (you). And only if it replaced enough custom code to justify the learning curve.

### What LangGraph DOESN'T Replace
- **Your reviewer agent prompts** — orchestration, not agents themselves
- **Finding consolidation logic** — still need synthesizer intelligence
- **Git-based iteration tracking** — checkpoints are operational state, not design history
- **JSONL schema** — still need to define finding format

### Token Efficiency Analysis

**Question:** Could LangGraph help with token efficiency for Claude or Codex parallel activities?

**Current token pain points (from v3 review findings):**

1. **Prior context accumulation** (Assumption Hunter Finding 3, Critical):
   - "After 5 iterations, token costs scale linearly with iteration count"
   - "Token budget and warn user if prior context exceeds threshold"

2. **Synthesizer overhead** (Session 9 learnings):
   - Reading 6 reviewer outputs × ~50k tokens each = 300k tokens
   - Main context consumed 40% before dispatching reviewers (prep work)

3. **Prompt caching conflicts** (Assumption Hunter Finding 10, Important):
   - Reviewer calibration requires prompt changes
   - Every calibration change invalidates cache (90% cost savings lost)

4. **Cross-iteration semantic matching** (Feasibility Skeptic Finding 2, Important):
   - N_new × N_prior comparisons for finding deduplication
   - "30 findings across 3 iterations = 900 semantic similarity evaluations"

**What LangGraph offers for token efficiency:**

| Token Problem | LangGraph Solution | Actual Value |
|---------------|-------------------|--------------|
| **Prior context pruning** | Checkpointing = store state externally, not in prompt | **Medium** — but files-on-disk already does this |
| **Synthesizer reads 300k tokens** | State graph nodes only receive relevant state slices | **Low** — you still need to read all reviewer outputs |
| **Prompt caching conflicts** | No built-in solution (LangGraph doesn't manage prompts) | **None** |
| **Semantic matching overhead** | No built-in solution (LangGraph is orchestration) | **None** |

**Key insight:** LangGraph's state management doesn't reduce tokens sent to LLMs — it just manages where state lives between calls. Your token costs are:
1. Reviewer prompts (stable, cacheable)
2. Design doc input (required every time)
3. Synthesizer reading all outputs (required for consolidation)

None of those change with LangGraph.

**What WOULD help token efficiency:**

1. **Prompt caching structure** (already in your design):
   - Stable prefix + variable suffix
   - 90% input cost reduction on cache hits
   - This is prompt design, not orchestration

2. **Model tiering** (Requirement Auditor Finding 5, Critical):
   - Haiku for mechanical reviewers (Edge Case Prober, Prior Art Scout)
   - 30-40% cost reduction if quality is acceptable
   - This is model selection, not orchestration

3. **TOON format** (MEMORY.md decision):
   - Token-optimized output for LLM-to-LLM hops
   - Reduce synthesizer input from 300k tokens to structured finding list
   - This is output format design, not orchestration

4. **Codex for mechanical tasks** (CLAUDE.md cost strategy):
   - "3x more token-efficient for code generation"
   - Use for survey phase (codebase exploration) and auto-fix
   - This is model routing, not orchestration

**Codex parallel activities:**

LangGraph is Python-native and works with any LLM API (Claude, Codex, GPT). If you wanted to:
- Run 3 reviewers on Claude Sonnet + 3 on Codex in parallel
- Route mechanical tasks (Prior Art Scout, survey) to Codex
- Route adversarial analysis (First Principles) to Claude Opus

LangGraph would handle the graph execution, but **you don't need a framework for that** — your current Task dispatch already does parallel execution. The model routing decision is orthogonal to orchestration.

### Verdict

**Defer LangGraph until hitting actual limitations.**

Current dispatch works (6 background agents → wait → synthesize). LangGraph doesn't solve token efficiency problems — those are solved by:
1. Prompt caching (design decision, already planned)
2. Model tiering (Haiku/Sonnet/Opus, eval-dependent)
3. TOON format (output optimization, post-JSONL)
4. Codex routing (model selection, independent of orchestration)

**LangGraph's value is orchestration complexity** (retry logic, human-in-the-loop gates, conditional branching), not token optimization.

Revisit when:
1. Retry logic becomes painful (manual re-dispatch is error-prone)
2. Eval framework needs reproducible test runs
3. Auto-retry workflow needs loop guards
4. Multi-model routing gets complex (Claude for review, Codex for survey, Opus for synthesis)

---

## Inspect AI Analysis

### What It Is
An **evaluation harness** for testing LLM capabilities against known-good answers.

**Core pattern:**
```python
Dataset (input + target)
  → Solver chain (agent scaffold, multi-turn, critique)
  → Scorer (compare output vs target, LLM-as-judge)
  → EvalLog (JSONL with metadata, scores, token usage)
```

Built for: "Here are 100 coding problems. Does GPT-4 solve them correctly?"

### What parallax:review Actually Does
**Design artifact review** — no "correct answer":

```python
Design doc (no target)
  → 6 adversarial reviewers (find problems, not score correctness)
  → Synthesize findings (consolidate, categorize)
  → Human disposition (accept/reject/discuss)
  → Optional: revise + re-review
```

### Force-Fit Attempt

| Inspect AI Component | parallax:review Mapping | Fit Quality |
|----------------------|-------------------------|-------------|
| **Dataset** | Single sample: design doc as input, target="N/A" | Awkward — datasets are for many samples |
| **Solver** | Dispatch 6 reviewer agents, return findings | **Possible** — multi-agent primitives exist |
| **Scorer** | LLM-as-judge grading finding quality? | **Wrong abstraction** — you don't grade findings, you disposition them |
| **EvalLog (JSONL)** | Structured output with metadata, token usage | **HIGH VALUE** — this is what you want |

### The Key Mismatch

**Inspect AI scorers expect:** "Is this output correct?"
**parallax:review needs:** "What problems exist in this design?"

You *could* abuse the scorer as a synthesizer ("grade" the 6 reviewer outputs by consolidating them), but you're fighting the framework's assumption (ground truth exists).

### What Inspect AI DOES Offer
1. **Structured JSONL logging** — EvalLog format with sample metadata, token usage, timing
2. **Multi-agent primitives** — compose agents together
3. **Built-in web viewer** — Inspect View for monitoring runs
4. **Header-only reads** — avoid loading full logs (useful for GB-scale outputs)

### What It DOESN'T Offer
- **Design review workflow** — no finding consolidation, severity categorization, disposition tracking
- **Human-in-the-loop for findings** — scorers are automatic, not interactive
- **Iteration management** — evals are one-shot (input → output → score), not iterative (review → revise → re-review)

### The JSONL Insight

**Inspect AI's EvalLog schema is the WRONG starting point for your JSONL format.**

Their schema (eval-focused):
```json
{
  "status": "success",
  "eval": {...},
  "plan": {...},
  "results": {...},
  "samples": [
    {"input": "...", "output": "...", "score": 0.8, "metadata": {...}}
  ]
}
```

Your needs (finding-focused):
```jsonl
{"finding_id": "C-ARCH-001", "severity": "Critical", "category": "Architecture", "title": "...", "description": "...", "reviewer": "assumption-hunter", "iteration": 3}
{"finding_id": "I-DOC-042", "severity": "Important", "category": "Documentation", ...}
```

One log per finding (JSONL stream), not one log per eval run.

### Decision Matrix

| Question | Answer |
|----------|--------|
| **Use Inspect AI for parallax:review orchestration?** | **No** — wrong abstraction (eval harness, not review workflow) |
| **Study Inspect AI's JSONL schema?** | **No** — it's eval-focused (samples/scores), not finding-focused |
| **Use Inspect AI for skill testing (Issue #5)?** | **YES** — this is exactly what it's for ("Does parallax:review find known issues in test cases?") |

### Verdict

**Don't adopt Inspect AI for parallax:review orchestration.**

Use it later for skill testing: "Given design doc X with planted flaws Y, does parallax:review surface them?"

---

## LangGraph vs Inspect AI: Not Competitors

They solve different problems:

- **LangGraph** = orchestration (state machine, checkpoints, human-in-the-loop) — could replace Task dispatch + retry logic
- **Inspect AI** = evaluation (ground truth testing, scoring, metrics) — tests whether parallax:review *works*

You might eventually use **both**:
- LangGraph orchestrates the review workflow
- Inspect AI tests the workflow against known-bad design docs

But neither replaces your need to **define a finding schema** for JSONL.

---

## Action Items

### 1. Requirements Rethink: Deterministic Execution Scope

**Current requirement (design-orchestrator.md:165):**
> "Pipeline agents stay stateless — **deterministic runs are essential for eval reproducibility**."

**Problem:** This conflates two different requirements:
1. **Eval testing:** "Run same eval twice, get comparable results" (testing infrastructure)
2. **Production orchestration:** "Resume failed runs, replay execution" (user-facing feature)

**Reality check:** Your actual production requirements are:
- Human checkpoints at decision points ✓
- Async-first (artifacts to disk) ✓
- Git-tracked iteration history ✓
- Interactive finding processing ✓

None of these need deterministic replay in the LangGraph sense.

**Recommendation:**
- **Before JSONL implementation:** Clarify whether deterministic replay is a production requirement or test-only requirement
- If test-only: Move to eval framework track (Issue #5), remove from production orchestration requirements
- If production: Document specific use cases (resume after crash? partial reviewer failure? iteration restart?) and add to requirements

**Impact on design:** If deterministic replay stays in requirements, it forces architectural decisions (checkpointing, state persistence) that add complexity. If it's test-only, you can defer until building eval framework.

---

## Next Steps

1. **Design JSONL schema from first principles** — what fields does a finding need? What operations do you want?
2. **Clarify deterministic replay scope** — production feature or test-only? Update requirements doc.
3. **Defer LangGraph** — current dispatch works, revisit when retry logic or eval reproducibility becomes painful
4. **Defer Inspect AI orchestration** — wrong abstraction for design review
5. **Plan Inspect AI for skill testing** — after you have a second test case (Issue #9 — Bill/Second Brain)

---

## References

- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Persistence & Checkpointing](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Parallel Execution in LangGraph](https://medium.com/codetodeploy/built-with-langgraph-11-parallelization-efa2ccdba2e0)
- [Human-in-the-Loop with LangGraph](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Inspect AI Overview](https://inspect.aisi.org.uk/)
- [Inspect AI Log Files](https://inspect.aisi.org.uk/eval-logs.html)
- [Inspect AI Review 2025](https://neurlcreators.substack.com/p/inspect-ai-evaluation-framework-review)
