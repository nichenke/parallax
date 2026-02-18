# ADR-008: Eval Prior Art Sweep — Scorer Techniques and Platform Choice

**Date:** 2026-02-17
**Status:** Accepted
**Deciders:** @nichenke
**Related:** Issues #74, #75, #76, #78, #79; ADR-005 (Inspect AI); ADR-007 (two-tier scoring)

---

## Context

ADR-007 defined the two-tier eval scoring strategy (`reverse_judge_precision` + `must_find_recall`). Before implementing it (Issue #71), a prior art sweep evaluated four alternatives — two scorer techniques and two platforms — to check whether existing tools could replace or substantially reduce the custom work, and to validate that ADR-005's choice of Inspect AI remains correct.

**Research question:** Are we on the golden path? Does any alternative technique or platform natively support parallax's two-tier scoring needs, or does it reduce the custom scorer work required?

**Research artifacts:**
- `docs/research/prior-art-ragas-geval-2026-02-17.md` — Issues #74 (RAGAS), #75 (G-Eval)
- `docs/research/prior-art-braintrust-vercel-2026-02-17.md` — Issues #76 (Braintrust), #78 (Vercel)

---

## Decision Summary

### 1. RAGAS Faithfulness: Skip (Issue #74)

**Decision:** Do not integrate RAGAS faithfulness scorer.

**Rationale:**

RAGAS faithfulness checks *entailment*: "can this claim be inferred from the context?" It is designed for RAG pipelines where retrieved chunks should support generated answers.

Parallax is doing *genuineness checking*: "is this finding a real, document-visible problem — not hallucinated, not a style preference, not an implementation detail?"

These are structurally different problems. Design review findings are predominantly *absence-detection* — "the document does not specify X, which is a risk." An absence is by definition not entailed by the document. RAGAS would score every absence-detection finding as unfaithful, producing systematic false positives on the majority of valid review output.

Additionally, RAGAS requires a claim decomposition step before scoring. Parallax findings are already structured atomic units (JSONL with `title`, `issue`, `severity`, `evidence`). The decomposition step is wasted work.

The per-item verification pattern that makes RAGAS useful is already embedded in `reverse_judge_precision`. There is nothing to adopt.

**Disposition:** Issue #74 closed — not applicable.

---

### 2. G-Eval Chain-of-Thought: Defer — evaluate empirically after Issue #71 (Issue #75)

**Decision:** Adapt G-Eval's reasoning-first pattern to the `reverse_judge_precision` judge prompt, but defer implementation until after Issue #71 ships and establishes a baseline.

**Rationale:**

G-Eval's core insight is forcing the judge to reason through structured evaluation steps *before* rendering a verdict. This directly addresses the Haiku calibration concern (Issue #73): a systematically lenient judge giving shallow YES answers gets caught when it must justify each reasoning step.

The adaptation for parallax is a prompt restructure, not an architecture change:
- Replace "Answer YES/NO, then explain" with four explicit reasoning steps derived from ADR-007's genuineness criteria and false positive list
- Judge reasons through each step, then gives `GENUINE` / `NOT_GENUINE`
- Skip auto-CoT step generation (ADR-007's steps are already defined)
- Skip token probability weighting (adds API complexity for marginal benefit on binary classification)

**Why defer:** If reasoning-first is baked into Issue #71's initial judge prompt, there is no baseline. The eval framework cannot evaluate itself if the improvement ships at the same time as the scorer. The correct sequence:

1. Ship #71 with a simple judge prompt → run evals → establish baseline `reverse_judge_precision` scores
2. Add G-Eval reasoning-first as an isolated change → measure the delta
3. If precision improves meaningfully, the 3x token cost is justified. If not, skip.

This is the "measure before you change" principle ADR-007 itself establishes for reviewer quality — applied recursively to the eval infrastructure.

**Disposition:** Issue #75 deferred. Implement after Issue #71 baseline is established.

---

### 3. Braintrust Platform: Skip (Issue #76)

**Decision:** Do not adopt Braintrust as the eval platform. ADR-005 (Inspect AI) stands.

**Rationale:**

Parallax's two-tier scoring needs (`reverse_judge_precision` + `must_find_recall`) are domain-specific enough that no platform provides them natively. The custom scorer code is the same amount of work regardless of platform. The decision therefore rests on surrounding infrastructure.

Inspect AI wins on every dimension that matters for parallax:

| Dimension | Inspect AI | Braintrust |
|-----------|-----------|------------|
| **Cost model** | Open source MIT; pay API tokens only | $0–249/mo platform fee |
| **Batch API** | Native Anthropic batch support (50% off) | No batch discount |
| **Agent eval depth** | Built for multi-turn, tool use, sandboxing | Explicitly weaker; designed for RAG/chat |
| **Run-to-run variance** | Custom N-run logic (Phase 2) | No built-in N-run aggregation |
| **Existing investment** | Phase 1 implemented, 65 tests, scorer prototype validated | Zero |
| **OSS / local-first** | Full MIT stack, no SaaS dependency | SaaS-first |

Braintrust's strongest genuine differentiator — the experiment comparison UI for score diffs across prompt/model changes — is not parallax's primary need. Per-run quality scoring is the need. When cross-experiment comparison matters later, a lightweight script will suffice.

**Notable exception — `autoevals` Factuality scorer:** Braintrust's scorer library is MIT-licensed and installable standalone (`pip install autoevals`) with no platform dependency. The Factuality scorer could serve as a supplementary cross-check alongside `reverse_judge_precision`. This is low priority and cannot be meaningfully evaluated until Issue #71 and #72 are complete. Tracked in Issue #79.

**Disposition:** Issue #76 closed — Inspect AI confirmed. `autoevals` deferred to Issue #79 (blocked on #71, #72).

---

### 4. Vercel AI SDK Testing Patterns: Not Applicable (Issue #78)

**Decision:** No patterns from Vercel AI SDK testing apply to parallax.

**Rationale:**

Vercel's testing approach (mock providers, `vitest-evals`, "evals as tests" patterns) solves *application integration testing*: does your code correctly handle LLM responses? It tests the application layer, not LLM output quality.

Parallax needs *LLM output quality evaluation*: are the findings the reviewer produced genuine and comprehensive? These are different problems at different layers.

Vercel's mock providers are specifically designed to test code paths — they deterministically return canned LLM responses to verify that application logic handles them correctly. They have no mechanism to evaluate the quality of what an LLM actually produces. Inspect AI already handles parallax's problem with its Dataset/Solver/Scorer pattern.

**One indirect contribution:** The "evals as tests" framing (Sentry's approach: run evals in CI, fail builds on regression) validates the parallax direction. The pattern reinforces the value of the eval framework — it does not change the implementation approach.

**Disposition:** Issue #78 closed — not applicable. No follow-up actions.

---

## Overarching Finding

**No platform or technique natively provides parallax's two-tier scoring.** Custom scorer code is required regardless of platform choice. The key insight surfaced by comparing all four alternatives simultaneously: ADR-007's N-run per-finding recall statistics (Phase 2) are genuinely novel — no existing tool addresses run-to-run variance at the per-finding level. Inspect AI's custom scorer pattern is the right substrate.

**ADR-005 stands. Inspect AI remains the correct platform choice.**

---

## Implementation Sequence

Based on this sweep and the ordering analysis from 2026-02-17:

```
#71 (two-tier scorer)
  → #75 (G-Eval reasoning-first, conditional on precision baseline)
    → #72 (reviewer confidence: confidence field + FP list)
      → #79 (autoevals Factuality, supplementary signal)
```

Issue #73 (Haiku calibration gate) runs alongside #75 — G-Eval reasoning-first is one of two candidate solutions to the calibration problem.

---

## Consequences

### Positive

1. **ADR-005 validated:** No migration cost. Existing Phase 1 investment preserved.
2. **Scorer technique clarity:** RAGAS eliminated early (semantic mismatch), G-Eval deferred with a concrete empirical gate (baseline first), `autoevals` tracked without commitment.
3. **Novel ground confirmed:** N-run variance handling is custom work. No existing tool solves this — validates the research project's scope.
4. **Eval-driven development enforced:** G-Eval deferral establishes the pattern: use the scorer to validate scorer improvements.

### Negative

1. **No shortcut found:** All four alternatives require the same custom scorer work. The sweep found no 80%-solution.
2. **G-Eval benefit unknown until #71 ships:** Accepting some delay before the reasoning-first improvement is measurable.

### Neutral

1. **`autoevals` opportunity:** Standalone MIT library worth revisiting post-#72, but not on the critical path.
2. **Vercel patterns confirm direction:** "Evals as tests" framing validates the approach without changing it.

---

## Alternatives Considered

### Alternative: Adopt Braintrust Platform

Rejected. Platform fee + no batch discount + weaker agent eval depth. Custom scorer work is identical either way. See Section 3.

### Alternative: Integrate RAGAS as Primary Precision Scorer

Rejected. Entailment ≠ genuineness. Systematic false positives on absence-detection findings. See Section 1.

### Alternative: Adopt G-Eval Immediately in Issue #71

Rejected. Destroys baseline. Cannot measure improvement without a comparison point. See Section 2.

---

## References

**Research artifacts:**
- `docs/research/prior-art-ragas-geval-2026-02-17.md`
- `docs/research/prior-art-braintrust-vercel-2026-02-17.md`

**Prior ADRs:**
- ADR-005: Inspect AI integration decision
- ADR-007: Two-tier eval scoring strategy

**Issues:**
- #74: RAGAS (closed — not applicable)
- #75: G-Eval (deferred — evaluate after #71 baseline)
- #76: Braintrust (closed — Inspect AI confirmed)
- #78: Vercel AI SDK (closed — not applicable)
- #79: autoevals Factuality (deferred — blocked on #71, #72)
- #71: Two-tier scorer implementation
- #72: Reviewer confidence upgrade
- #73: Haiku judge calibration gate

---

## Revision History

- **2026-02-17:** Initial version — prior art sweep across four alternatives
