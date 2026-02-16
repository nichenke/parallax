# ADR-003: Architectural Specification Status — Implemented, Deferred, and Required Work

**Date:** 2026-02-16
**Status:** Accepted
**Deciders:** @nichenke
**Related:** Issue #31 (Calibrate Phase Systemic Failure)

---

## Context

Pattern extraction from 87 v3 findings revealed systemic failure in calibrate phase (32.2% of findings trace to requirements/planning gaps). Five reviewers independently flagged "architectural specifications undefined" as Critical findings. This ADR clarifies what's been specified, what's deferred, and what requires design work before implementation.

The v3 review summary noted: "Design doc sync addressed decisions (what to do) but not specifications (how it works)." This ADR converts that observation into actionable status tracking.

---

## Status Categories

### ✅ Specified (implementation-ready)

**1. JSONL Schema** (FR7.5)
- **Status:** Implemented in PR #12
- **Location:** `schemas/reviewer-findings-v1.0.0.schema.json`, `schemas/pattern-extraction-v1.0.0.schema.json`
- **Validation:** Python script + JSON Schema Draft 2020-12
- **Decision rationale:**
  - Machine-readable format enables CLI tools (jq) for mechanical tasks
  - Schema validation catches missing fields without LLM involvement
  - JSONL as canonical format, markdown as presentation layer
  - Reduces context window pressure (load findings on-demand vs full markdown slurp)

**2. Output Artifacts** (FR7.1-FR7.4)
- Per-reviewer JSONL findings
- Merged findings JSONL
- Pattern extraction JSON
- Summary markdown (human-readable view)
- All artifacts git-tracked in `docs/reviews/<topic>/`

**3. Async-First Architecture** (FR2.1-FR2.4)
- Write artifacts to disk as baseline
- Interactive mode reuses artifacts (not re-runs review)
- File system as single source of truth (MVP constraint: single-user, single-machine)

**4. Model Tiering Strategy** (NFR2.2)
- **Policy documented:** Haiku (mechanical), Sonnet (analysis), Opus (deep reasoning)
- **Per-reviewer assignment:** Not yet specified (see Required Work below)
- **Cost target:** <$1 per review run (NFR2.1)

---

### 🚫 Deferred (post-MVP)

**1. Auto-Fix Workflow** (ADR-001 Q2)
- **Decision:** Defer entirely to post-MVP
- **Rationale:** Zero auto-fixable findings in v3 review (all required human judgment)
- **Risk mitigation:** Complexity (infinite loops, git safety, classification subjectivity) without demonstrated value
- **Future work:** If eval shows 20%+ findings are mechanically fixable, revisit

**2. Prompt Caching Architecture** (NFR2.3)
- **Decision:** Defer specification to implementation phase
- **Rationale:** Caching is performance optimization, not functional requirement. Can implement incrementally as token costs become clear during testing.
- **Known:** System prompt + design doc should be cache boundary
- **Unknown:** Versioning strategy, invalidation triggers, cost/benefit tradeoff
- **Test first:** Measure token costs without caching, then evaluate 90% savings on cache hits

**3. LangGraph Orchestration** (ADR-001 Q1)
- **Decision:** Defer. Native Claude Code dispatch sufficient for MVP.
- **Rationale:** LangGraph useful for cross-LLM orchestration (not needed yet) and bounded iteration loops (auto-fix deferred)
- **Revisit:** When testing cross-LLM review teams (Claude + GPT + Gemini) or Full-Auto mode (Issue #10)

**4. External State Management** (LangSmith, external DB)
- **Decision:** Defer. File system sufficient for single-user MVP.
- **Rationale:** Adds infrastructure complexity without solving MVP use case
- **Revisit:** When multi-user collaboration or distributed workflows become requirements

---

### ⚠️ Required Work (blocks implementation)

**1. Finding ID Mechanism** (FR7.3)

**Problem:** Cross-iteration finding tracking requires stable IDs. Design specifies hash-based IDs (`v{iteration}-{reviewer}-{sequence}`) but semantic matching for iteration-to-iteration persistence is unspecified.

**Known issues:**
- Hash brittleness: Section refactoring orphans findings
- Semantic matching cost: LLM comparison of 1800 finding pairs = $1+ per iteration
- False positives: Similar findings from different reviewers incorrectly merged
- False negatives: Rephrased findings treated as new

**Decision required:**
- (a) Accept hash brittleness, manual ID mapping for critical findings
- (b) Implement LLM semantic matching, budget for comparison cost
- (c) Hybrid: hash first-pass, LLM disambiguation on collisions
- (d) Defer cross-iteration tracking to post-MVP (accept findings as one-shot per iteration)

**Recommendation:** Option (d) for MVP. Cross-iteration tracking is optimization, not core value. Focus on single-iteration review quality first. Revisit after Second Brain test validates baseline value.

**Requirements impact:** FR7.3 marked as post-MVP scope reduction if (d) accepted.

---

**2. Systemic Issue Detection Taxonomy** (FR6.1-FR6.4)

**Problem:** 30% threshold for systemic issue flagging is specified, but semantic grouping criteria undefined. "What counts as same contributing phase?" requires LLM judgment or explicit taxonomy.

**Known gaps:**
- Root cause taxonomy: Which phase categories exist? (survey, calibrate, design, plan — but subcategories?)
- Semantic clustering: "JSONL schema missing" and "auto-fix unspecified" both trace to calibrate, but are they same root cause?
- Pattern vs systemic issue: When does a pattern (5 findings, 3 reviewers) become a systemic issue (>30% threshold)?

**Decision required:**
- (a) Manual systemic detection by synthesizer (LLM judgment, documented in summary)
- (b) Automated detection via pattern extraction (use pattern contributing_phase counts)
- (c) Hybrid: automated flagging + synthesizer confirmation

**Recommendation:** Option (b). Pattern extraction already groups findings by contributing phase. Systemic detection becomes mechanical aggregation of pattern metadata. Synthesizer validates and explains, but threshold check is automated.

**Implementation:** Systemic issue detection runs after pattern extraction. Reads `patterns-v3-full.json`, counts findings by contributing phase, flags if >30%. Synthesizer receives flagged phases and writes explanation in summary.

**Requirements impact:** FR6.4 implementation approach specified.

---

**3. Model Assignment Per Reviewer** (NFR2.2)

**Problem:** Model tiering policy documented (Haiku/Sonnet/Opus), but per-reviewer assignment unspecified. Cost optimization and quality tradeoffs untested.

**Decision required:**
- Assumption Hunter: Sonnet or Opus? (reasoning-heavy)
- Edge Case Prober: Sonnet or Opus? (scenario exploration)
- Requirement Auditor: Sonnet or Haiku? (checklist matching)
- Feasibility Skeptic: Sonnet (complexity estimation)
- First Principles: Opus (deep reasoning)
- Prior Art Scout: Sonnet or Haiku? (search + summarization)

**Recommendation:** Start all reviewers on Sonnet (baseline). Measure cost and quality per reviewer. Ablation study: does Requirement Auditor quality degrade on Haiku? Does Assumption Hunter improve on Opus? Make model assignment data-driven via eval framework (Issue #5).

**Requirements impact:** NFR2.2 implementation approach: Sonnet baseline, eval-driven optimization.

---

**4. Minimum Viable Reviewer Set** (NFR3.1)

**Problem:** 6 reviewers specified, but minimum viable set untested. Can we get 80% value with 3 reviewers? Which personas are essential vs nice-to-have?

**Decision required:** Ablation study via eval framework
- Test 6-reviewer baseline (full coverage)
- Test 3-reviewer subsets (e.g., Assumption Hunter + Edge Case Prober + Requirement Auditor)
- Measure: finding coverage, severity distribution, false positive rate, cost per review
- Identify: which reviewers find unique issues vs redundant overlap?

**Recommendation:** Defer to eval phase (Issue #5). All 6 reviewers provide value in self-review. Test cost/quality tradeoffs empirically on Second Brain test case.

**Requirements impact:** NFR3.1 validation approach specified (empirical via ablation study).

---

## Architectural Debt Summary

**Calibrate phase systemic failure (32.2%)** traces to:
1. ✅ JSONL schema — RESOLVED (implemented)
2. 🚫 Auto-fix — DEFERRED (post-MVP per ADR-001)
3. 🚫 Prompt caching — DEFERRED (optimization, not functional requirement)
4. ⚠️ Finding ID mechanism — DECISION REQUIRED (recommend defer to post-MVP)
5. ⚠️ Systemic detection taxonomy — DECISION REQUIRED (recommend automated via pattern extraction)
6. ⚠️ Model assignment — DECISION REQUIRED (recommend Sonnet baseline + eval-driven optimization)
7. ⚠️ Minimum reviewer set — DECISION REQUIRED (recommend defer to eval)

**Path forward:**
1. Accept items 4, 7 as post-MVP scope reductions
2. Specify item 5 (systemic detection) as automated pattern aggregation
3. Specify item 6 (model assignment) as Sonnet baseline
4. Run Second Brain test case to validate MVP scope decisions
5. Requirements review session to confirm scope reductions acceptable

---

## Decision

**Accepted architectural specifications:**
- Finding ID: Sequential per reviewer per iteration (`v{iteration}-{reviewer}-{sequence}`), cross-iteration tracking deferred to post-MVP
- Systemic detection: Automated via pattern extraction contributing phase counts, synthesizer writes explanation
- Model assignment: All reviewers use Sonnet baseline, eval-driven optimization in Issue #5
- Minimum reviewer set: All 6 reviewers for MVP, ablation study in eval phase

**Scope reductions:**
- Cross-iteration finding tracking → post-MVP
- Model tier optimization → post-MVP (Sonnet baseline sufficient)
- Auto-fix workflow → post-MVP (already deferred in ADR-001)

**Rationale:** Focus on single-iteration review quality first. Optimizations and cross-iteration features add complexity without validating core value hypothesis. Second Brain test case (Issue #14) validates whether single-iteration adversarial review catches real design flaws. If baseline doesn't work, optimizations won't save it.

---

## Consequences

**Positive:**
- Clear implementation scope (no architectural blockers)
- Reduced MVP complexity (faster to working prototype)
- Empirical decision-making (test baseline before optimizing)

**Negative:**
- Cross-iteration tracking deferred (users manually track finding status across iterations)
- Model tier optimization deferred (may overpay for Sonnet on mechanical tasks)
- Longer iteration cycles (finding processing is manual, not auto-fixed)

**Mitigations:**
- JSONL format makes manual tracking tractable (jq queries, not markdown parsing)
- Sonnet cost acceptable if <$1 per review (NFR2.1) — validate via Second Brain test
- Manual finding processing captures design decisions in disposition notes (higher value than auto-fix)

---

## Related Decisions

- ADR-001 Q2: Auto-fix deferred to post-MVP
- ADR-001 Q1: LangGraph deferred, native dispatch sufficient
- ADR-002: Requirements review v2 applied (JSONL schema implemented)
- Issue #31: Calibrate phase systemic failure escalation
- Issue #5: Eval framework for model tier and reviewer set optimization
- Issue #14: Second Brain test case (MVP validation)
