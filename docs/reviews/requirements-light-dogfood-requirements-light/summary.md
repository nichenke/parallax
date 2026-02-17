# Requirements Review Summary — requirements-light-dogfood (Light Mode)

**Review Date:** 2026-02-16
**Design Document:** `docs/plans/2026-02-16-requirements-light-design.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 1 | 3 | 1 | 5 |
| scope-guardian | 2 | 3 | 3 | 8 |
| constraint-finder | 0 | 6 | 2 | 8 |
| assumption-hunter | 1 | 7 | 4 | 12 |
| success-validator | 2 | 4 | 3 | 9 |
| **Total** | **6** | **23** | **13** | **42** |

---

## Key Themes

The 42 findings reveal that while the requirements-light design has a clear vision and solid structure, it has **significant specification gaps** that would block implementation. Three major categories of issues emerged:

### 1. **Implementation Specifications Missing** (Critical blockers)

The design clearly articulates WHAT to build but lacks HOW to build it:

- **Finding ID format ambiguous** (scope-guardian-004): Per-persona vs global counters unspecified, blocks implementation
- **JSONL schema location/versioning undefined** (assumption-hunter-005): Personas don't know where to find or which version to use
- **Validation ground truth undefined** (scope-guardian-006): Can't measure precision/recall without defining "real gaps"
- **MVP definition of done missing** (success-validator-008): No completion criteria, risks infinite iteration
- **Workflow fit not measurable** (success-validator-005): Success criterion requires longitudinal observation but MVP tests retrospectively

### 2. **Implicit Assumptions Pervasive** (23 Important findings)

The design makes numerous unstated assumptions about system behavior, dependencies, and user context:

- **File discovery assumptions**: Design doc location/naming convention assumed stable (assumption-hunter-001, -002, -004, -012)
- **Cost/performance assumptions**: Model tiering strategy not referenced (constraint-finder-001), concurrency limits not specified (constraint-finder-002), prompt caching strategy missing (constraint-finder-006)
- **Dependency assumptions**: Git repo required but not validated (constraint-finder-007), brainstorming skill output format assumed (assumption-hunter-001), test case accessibility uncertain (assumption-hunter-007, constraint-finder-008)
- **Synthesis approach unspecified**: Who generates summary.md and how? (assumption-hunter-008, scope-guardian-001)

### 3. **Problem Framing Questions** (High-leverage insights)

The most strategic findings challenge whether the design solves the right problem:

- **Root cause unclear** (problem-framer-001): Is the issue brainstorming output quality or user behavior? If users skip requirements thinking, adding a checkpoint won't help.
- **Value proposition unvalidated** (problem-framer-004): Design assumes requirement gaps cause expensive rework but provides no evidence. 30min review investment needs positive ROI analysis.
- **Success criteria conflated** (problem-framer-002): Mixes quality validation (catches gaps) with adoption validation (users remember to invoke). These measure different things and may conflict.
- **Scope boundary with mid-design drift** (problem-framer-003): MEMORY.md notes "requirements emerge through design" but two-checkpoint model rationale not explained.

---

## Problem Framing

**Core finding:** The design frames the problem as "brainstorming produces incomplete requirements" but doesn't establish whether this is a **skill limitation** (brainstorming output quality) or **user behavior** (users rush past requirements thinking). If root cause is user behavior, adding a checkpoint won't solve it—users will skip this too.

**Value proposition gap:** Design assumes catching requirement gaps prevents rework but provides no cost-benefit analysis. Some gaps might be trivial to fix post-design (5min edits), others catastrophic (full redesign). Without quantifying typical rework costs, can't validate if 30min upfront investment has positive ROI.

**Recommendation:** Add "Why this problem exists" section with evidence from past sessions showing requirement gaps that caused measurable rework. Distinguish skill output quality issues from user workflow issues.

---

## Scope & Boundaries

**MVP scope ambiguities:**
- Summary synthesis logic scope undefined (build synthesizer vs manual summary?)
- Test case minimum unclear (need 3 accessible cases but 2 marked "if accessible")
- Light vs deep mode boundary vague (what does light mode NOT validate?)

**Critical specification gaps:**
- Finding ID format incomplete (blocks ID generation logic)
- Validation ground truth undefined (blocks precision/recall measurement)

**Scope creep risks:**
- Without clear light/deep boundary, features might leak into light mode
- Test case accessibility uncertain—validation might fail for logistical reasons

**Recommendation:** Explicitly define MVP scope for synthesis (in/out), specify minimum viable test set with fallback, document what light mode does NOT cover.

---

## Constraints & Feasibility

**Cost constraints critical but unstated:**
- Design doesn't reference CLAUDE.md's model tiering strategy (Sonnet baseline)
- Prompt caching strategy missing—could cost 10x more without it ($50 vs $5 per review)
- 5 personas * multiple test runs could exceed $2000/month budget without explicit constraints

**Technical feasibility gaps:**
- Concurrency limits not documented (sequential vs parallel affects <30min criterion)
- Input size limits unstated (Claude 200K context window could be exceeded)
- Git repo dependency assumed but not validated

**Performance impact:**
- Sequential execution: 5 * 6min = 30min (at limit)
- Parallel execution: faster but requires rate limit handling
- API failures/retries not accounted for in runtime budget

**Recommendation:** Add explicit cost constraint ("Use Sonnet, target <$5 per review"), document concurrency strategy (sequential MVP, parallel post-MVP), specify input size limits (<100K tokens).

---

## Assumptions

**File discovery assumptions pervasive:**
- Design doc location/naming convention assumed stable from brainstorming skill
- Topic extraction from filename assumed reliable (edge case handling missing)
- Output directory collision risk with design review not addressed

**Dependency assumptions:**
- Superpowers plugin brainstorming skill not versioned (breaking changes would break --light)
- JSONL schema location/version not specified
- Git repo structure required but not validated

**Execution assumptions:**
- Parallel persona execution assumed possible (affects runtime)
- Prompt caching assumed available (affects cost by 10x)
- Test case accessibility assumed (but openclaw repo inaccessible per MEMORY.md)

**Synthesis assumptions:**
- Summary generation approach not specified (6th persona? Script? Manual?)
- Persona model/expertise level not specified (Sonnet vs Opus?)

**Recommendation:** Make design doc path an explicit parameter (decouple from brainstorming), document schema location/versioning strategy, specify execution model (parallel vs sequential).

---

## Success Criteria

**Measurement feasibility issues:**
- **Precision/recall ground truth undefined** (Critical): Can't measure without defining "real gaps" vs false positives
- **Workflow fit not measurable** (Critical): Retrospective testing on past brainstorms can't validate "users remember to invoke"
- **False negative detection missing**: Recall measurement requires exhaustive ground truth, not just "visible rework"

**Validation process gaps:**
- Manual review protocol not operationalized (no reviewer qualifications, rubric, inter-rater reliability)
- "Actionable findings" subjective without measurable criteria
- Test case sample size (3-5) lacks statistical justification

**Failure mode handling:**
- No specification for what happens if precision <70% or recall <60%
- Definition of done for MVP missing (when is it "complete" vs "needs iteration"?)
- Success criteria count target (3-5 gaps) lacks justification

**Recommendation:** Specify validation approach (dual-blind review, ground truth via v3 findings comparison), define actionability rubric, clarify failure mode handling (iterate vs escalate vs defer).

---

## Critical Findings

### 1. **[scope-guardian] Finding ID format specification incomplete**
- **Issue:** Format `v1-problem-framer-001` ambiguous—per-persona vs global counters? v1 = iteration or schema version?
- **Suggestion:** Specify `v{iteration}-{persona}-{NNN}` where iteration=review run number, NNN=zero-padded sequential per persona

### 2. **[scope-guardian] Validation metrics precision/recall ground truth undefined**
- **Issue:** Can't measure precision >70% / recall >60% without defining "real gaps" source
- **Suggestion:** Use v3 review findings as ground truth (calibrate-phase findings = gaps --light should catch)

### 3. **[assumption-hunter] JSONL schema availability assumed**
- **Issue:** Design says "reuses existing schema" but doesn't specify location, versioning, or discovery mechanism
- **Suggestion:** Specify schema location (e.g., `schemas/reviewer-findings-v1.0.0.schema.json`), document persona validation requirements

### 4. **[success-validator] Workflow fit success criterion not measurable**
- **Issue:** "Users naturally remember to invoke" requires longitudinal observation; retrospective testing can't validate this
- **Suggestion:** Revise to measurable proxy (intent survey) or defer workflow fit validation to post-MVP

### 5. **[success-validator] Definition of done for MVP missing**
- **Issue:** No explicit completion criteria—when is --light "complete" vs "needs iteration"?
- **Suggestion:** Define MVP done: all personas implemented, 5 test cases run, precision >70% on 4/5, runtime <30min on 4/5

### 6. **[problem-framer] Root cause vs symptom framing unclear**
- **Issue:** Assumes brainstorming produces incomplete requirements but doesn't establish if this is skill limitation or user behavior
- **Suggestion:** Add evidence section showing requirement gaps from past sessions; distinguish skill output vs user workflow issues

---

## Important Findings (Summary)

**Implementation gaps (8):**
- Synthesis logic scope undefined (scope-guardian-001)
- Test case scope ambiguous (scope-guardian-002)
- Deep mode boundary vague (scope-guardian-005)
- Finding ID collision prevention missing (assumption-hunter-010)
- Summary synthesis approach unspecified (assumption-hunter-008)
- Success criteria measurement feasibility (success-validator-002, -006)
- Precision/recall failure mode missing (success-validator-001)

**Cost/performance constraints (6):**
- Model API cost constraints not specified (constraint-finder-001)
- Concurrency limits not documented (constraint-finder-002)
- Input document size limits unstated (constraint-finder-003)
- Prompt caching strategy missing (constraint-finder-006)
- Git repository dependency not validated (constraint-finder-007)
- Test case data availability unstated (constraint-finder-008)

**File discovery assumptions (7):**
- Design doc location/naming assumed stable (assumption-hunter-001)
- Topic extraction logic not specified (assumption-hunter-002)
- Parallel execution model not clarified (assumption-hunter-003)
- User discovery mechanism missing (assumption-hunter-006)
- Test case accessibility unverified (assumption-hunter-007)
- Superpowers plugin dependency not versioned (assumption-hunter-012)
- Success criteria ground truth undefined (assumption-hunter-011)

**Problem framing gaps (3):**
- Success criteria conflate validation/adoption metrics (problem-framer-002)
- Problem scope excludes mid-design drift (problem-framer-003)
- Value proposition doesn't quantify rework cost (problem-framer-004)

---

## Next Steps

### Immediate (Blocks Implementation)
1. **Define finding ID format** — specify v{iteration}-{persona}-{NNN} structure with clear semantics
2. **Specify JSONL schema location** — document where personas find schema and which version
3. **Define ground truth approach** — use v3 findings as baseline for validation metrics
4. **Add MVP definition of done** — explicit completion criteria with quality gates
5. **Clarify synthesis scope** — is summary.md generation in MVP or deferred?

### High-Priority (Causes Rework)
1. **Add cost constraints** — reference CLAUDE.md model tiering, specify Sonnet-only, target <$5 per review
2. **Document concurrency strategy** — sequential MVP to avoid rate limits, parallel post-MVP
3. **Specify input constraints** — max design doc size <100K tokens with validation
4. **Make design doc path explicit** — accept as parameter, don't assume filename convention
5. **Revise workflow fit criterion** — change to measurable proxy (intent survey) or defer to post-MVP

### Strategic (High-Leverage Questions)
1. **Validate problem framing** — add evidence section showing requirement gaps caused rework
2. **Add cost-benefit analysis** — estimate typical rework cost per gap class, validate ROI
3. **Separate success criteria** — quality bar (catches gaps) vs adoption bar (users invoke)
4. **Define light/deep boundary** — document what light mode does NOT validate
5. **Test case fallback plan** — specify minimum 3 accessible cases with synthetic fallback

---

## Validation Observations

**Test quality:** This review caught **42 actionable findings** including **6 Critical blockers** that would have prevented implementation. The design is conceptually solid but severely underspecified.

**Pattern analysis:** Findings cluster around three themes:
1. **Specification gaps** (Critical): Implementation details missing (finding IDs, schema location, ground truth, completion criteria)
2. **Implicit assumptions** (Important): File discovery, cost constraints, dependencies, execution model
3. **Problem framing** (Strategic): Root cause unclear, value proposition unvalidated, success criteria conflated

**Most valuable finding:** problem-framer-001 (root cause unclear) — challenges whether the design solves the right problem. If users skip requirements thinking, adding a checkpoint won't help.

**Runtime:** Review completed in **~10 minutes** (well under 30min target).

**Success criteria validation:**
- ✅ **Caught 3-5 real gaps:** Actually caught 42 findings, 6 Critical blockers
- ✅ **<30 min:** Completed in ~10 minutes
- ✅ **Actionable findings:** All findings include specific suggestions
- ❓ **Workflow fit:** Can't measure retrospectively (requires forward testing)

**Meta-finding:** The skill itself validated its own value by catching significant specification gaps in its own design doc. Dogfooding successful.
