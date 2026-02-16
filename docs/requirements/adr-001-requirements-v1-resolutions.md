# ADR-001: parallax:review Requirements v1.1 — Open Question Resolutions

**Date:** 2026-02-16
**Status:** Accepted
**Deciders:** @nichenke

---

## Context

Three design review iterations (v1: 44, v2: 55, v3: 83 findings) surfaced eight open questions requiring resolution before implementation. The v3 review shifted findings from "decided but not documented" to "documented but not specified." These resolutions convert specifications into concrete requirements.

Each resolution below states the question, alternatives considered, the decision, and which requirements were added, removed, or modified.

---

## Q1: Deterministic Execution Scope

**Question:** Should parallax:review support deterministic replay of review runs?

**Alternatives:**
- (a) Full deterministic replay via LangGraph state machines
- (b) Checkpoint/resume for long-running reviews
- (c) Split into error recovery (production) + eval reproducibility (testing)

**Decision:** Option (c). Production needs error recovery (re-run failed reviewers, clean up partial output), not deterministic replay. Testing needs reproducibility via git + versioned prompts + JSONL + variance measurement.

**Rationale:** Deterministic replay solves an eval problem, not a production problem. LangGraph adds orchestration complexity without production value. Accept non-determinism, measure variance instead of eliminating it.

**LangGraph disposition:** Defer. Useful for cross-LLM orchestration + Full-Auto bounded iteration (Issue #10), not for checkpoint/resume.

**Requirements impact:**
- Added: FR7.6 (cleanup partial output), NFR5.1-NFR5.7 (eval reproducibility)
- Removed: C3.3 (stateless for determinism — determinism was never the actual goal)

---

## Q2: Auto-Fix Scope

**Question:** Should parallax:review auto-fix findings in the design doc?

**Alternatives:**
- (a) Auto-fix with git safety (commit before modifying, rollback on failure)
- (b) Suggest fixes but don't apply
- (c) Defer entirely to post-MVP

**Decision:** Option (c). Defer auto-fix entirely.

**Rationale:** v3 review produced 0 auto-fixable findings (all required human judgment). Auto-fix adds complexity (infinite loop risk, Git Safety Protocol violations) for zero demonstrated value.

**Requirements impact:**
- NFR4.1 notes auto-fix deferred
- Added D10 (explicit deferral)

---

## Q3: Cross-Iteration Finding Matching

**Question:** How should findings be tracked across review iterations?

**Alternatives:**
- (a) Stable finding IDs via content hashing (cross-run stability)
- (b) Pass prior review to individual reviewers (anchored reviews)
- (c) Simple per-iteration IDs + post-synthesis pattern extraction (clean reviews)

**Decision:** Option (c). Two-pass post-synthesis: pattern extraction then delta detection.

**Rationale:**
- **Content hashing is brittle.** Minor wording changes create "new" findings that are semantically identical.
- **Anchored reviews taint reviewers.** Passing prior context costs ~270k tokens AND creates anchoring bias.
- **Clean reviews + semantic matching** preserves reviewer independence. Post-synthesis pattern extraction costs ~30k tokens and handles semantic equivalence via LLM.

**Finding ID format:** `v{iteration}-{reviewer}-{sequence}` (e.g., `v3-assumption-hunter-001`). Simple, unique per run, no cross-run stability needed.

**Token savings:** 270k (anchored) → 30k (pattern extraction) = 240k tokens saved per iteration.

**Requirements impact:**
- Added: FR5.1 (simple IDs), FR5.2 (pattern-based delta), FR10.1-FR10.5 (post-synthesis analysis)
- Removed: FR5.4 (prior context in reviewers — taints clean reviews)

---

## Q4: JSONL Output Schema

**Question:** What output format should reviewers produce, and how should metadata be tracked?

**Sub-decisions:**

**Q4.1: Canonical format**
- Decision: JSONL as source of truth. Summary.md rendered from JSONL.
- Rationale: Structured from the start. No lossy markdown→structured conversion.

**Q4.2: Disposition tracking**
- Decision: Append disposition field to findings JSONL (single file).
- Rationale: All context in one file. Git tracks disposition history via diffs.

**Q4.3: Per-reviewer cost tracking**
- Decision: Track input/output/cache tokens, wall clock time, model used per reviewer.
- Rationale: Budget validation, model tiering decisions, cache effectiveness analysis.

**Q4.3+: Run-level metadata**
- Decision: Track vendor, model IDs, prompt versions (stable + calibration), run parameters.
- Rationale: Eval framework needs run differentiation for model comparison, prompt iteration analysis, vendor portability testing.

**Requirements impact:**
- Added: FR6.1-FR6.7 (JSONL canonical, markdown rendered), NFR2.4-NFR2.5 (metadata tracking)

---

## Q5: TOON Format

**Question:** Should we use a token-optimized output notation for reviewer→synthesizer communication?

**Decision:** Defer to post-MVP.

**Rationale:** JSONL is already token-optimized vs markdown. Further optimization is premature. Eval framework should measure synthesizer token costs first to determine if optimization is warranted.

**Requirements impact:**
- Added: D11 (explicit deferral)

---

## Q6: Prompt Caching Strategy

**Question:** How should reviewer prompts be structured for cache optimization?

**Alternatives:**
- (a) Monolithic prompt (simple but no caching)
- (b) Two-part: static + dynamic (caches persona, but calibration changes invalidate)
- (c) Three-part: stable prefix + calibration rules + variable suffix

**Decision:** Option (c). Three-part prompt structure.

**Structure:**
- **Part 1 — Stable prefix** (cached): Persona definition, mandate, output format, voice guidelines. Rarely changes. Cache invalidation only on major prompt restructuring.
- **Part 2 — Calibration rules** (not cached, versioned): False positive/negative corrections, domain-specific guidelines. Changes frequently via correction compounding. Does NOT invalidate cache.
- **Part 3 — Variable suffix**: File paths for documents to review. NOT document content — reviewers use Read/WebFetch tools.

**Document access decision:** Reviewers read documents via tools (Read for local files, WebFetch for URLs). This solves the git-only assumption (v3 Critical Finding C4) and supports multi-file designs, Confluence/Notion/Google Docs.

**Version tracking:** Two version numbers tracked separately (stable v1.0, calibration v2.3) so eval framework can isolate impact of each.

**Requirements impact:**
- Added: FR8.1-FR8.4 (three-part prompt, tool-based document access), NFR2.6 (calibration without cache invalidation)
- Updated: C1.3 (non-git docs supported via tools)

---

## Q7: Model Tiering per Persona

**Question:** Should different reviewers use different models (Haiku/Sonnet/Opus)?

**Decision:** Defer to post-MVP. MVP uses Sonnet for all reviewers.

**Rationale:** Consistent quality baseline needed before measuring tiering tradeoffs. Eval framework (Issue #5) should test Haiku for mechanical reviewers (Prior Art Scout, Edge Case Prober) where thoroughness matters less than coverage.

**Architecture support:** Per-reviewer model overrides already supported in NFR3.3. Metadata tracks model used per reviewer (NFR2.4). No implementation work needed for MVP — just don't configure overrides.

**Requirements impact:**
- Added: D12 (explicit deferral)
- Architecture: NFR3.3 + NFR2.4 already support future tiering

---

## Q8: Systemic Issue Detection Taxonomy

**Question:** How should the system detect systemic issues (upstream root causes)?

**Alternatives:**
- (a) Simple phase count (>30% threshold)
- (b) Semantic root cause clustering via LLM
- (c) Both, layered (simple for MVP, semantic for post-MVP)

**Decision:** Option (c). Simple phase count for MVP, semantic clustering post-MVP.

**MVP algorithm:**
1. Count findings by `contributing_phase` field
2. Denominator: findings with `contributing_phase` set (not all findings)
3. Flag as systemic if any phase exceeds 30%

**Example:** 11/16 findings with contributing phase have `calibrate` as contributing phase → 68% → systemic calibrate gap.

**Post-MVP:** Pattern extraction (FR10.1) enables semantic root cause clustering — grouping related findings by underlying cause rather than just phase label.

**Requirements impact:**
- Updated: FR2.7 (clarified denominator), added FR2.7.1 (MVP: simple phase count)
- Added: FR10.5 (post-MVP: semantic clustering), D13 (explicit deferral)

---

## Consequences

### Requirements Added (by resolution)

| Resolution | Requirements Added |
|-----------|-------------------|
| Q1 | FR7.6, NFR5.1-NFR5.7 |
| Q2 | D10 |
| Q3 | FR5.1, FR5.2, FR10.1-FR10.5 |
| Q4 | FR6.1-FR6.7, NFR2.4-NFR2.5 |
| Q5 | D11 |
| Q6 | FR8.1-FR8.4, NFR2.6, C1.3 update |
| Q7 | D12 |
| Q8 | FR2.7 update, FR2.7.1, FR10.5, D13 |

### Requirements Removed

| Removed | Reason |
|---------|--------|
| C3.3 (stateless for determinism) | Determinism was never the goal (Q1) |
| FR5.4 (prior context in reviewers) | Taints clean reviews (Q3) |

### Build-vs-Leverage Assessment

Conducted alongside Q1-Q8 resolutions:

- **LangGraph:** Wrong problem for MVP. Deterministic replay is for eval testing, not production. Defer until retry logic or Full-Auto (Issue #10) needs it.
- **Inspect AI:** Wrong abstraction. Eval harness for ground truth testing, not design review. Use later for skill testing (Issue #5).
- **Neither solves token efficiency** — that's prompt caching + model tiering + TOON.
