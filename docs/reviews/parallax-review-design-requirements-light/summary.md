# Requirements Review Summary — parallax-review-design (Light Mode)

**Review Date:** 2026-02-16
**Design Document:** `docs/plans/2026-02-15-parallax-review-design.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 3 | 5 | 2 | 10 |
| scope-guardian | 2 | 7 | 8 | 17 |
| constraint-finder | 4 | 16 | 5 | 25 |
| assumption-hunter | 3 | 11 | 6 | 20 |
| success-validator | 3 | 8 | 8 | 19 |
| **Total** | **15** | **47** | **30** | **92** |

---

## Key Themes

The requirements review reveals **fundamental problem framing gaps** and **severe scope ambiguity** in the parallax:review design. The design addresses a symptom (late-discovered design flaws) rather than the root cause (inadequate upstream review checkpoints). Multiple reviewers flagged critical contradictions between stated scope ("review skill only") and actual feature set (pattern extraction, delta detection, auto-fix, JSONL infrastructure).

**Problem Framing:**
The design document lacks an explicit problem statement. It jumps directly to solution description ("what parallax:review does") without establishing the pain point being solved. The core hypothesis conflates two distinct problems: (1) perspective diversity catching design gaps, and (2) pipeline phase routing of findings. Most critically, the phase routing mechanism treats symptoms (findings discovered late) rather than root causes (checkpoints lack adversarial review). Three reviewers independently flagged this inversion: **the real problem is that requirements/design/plan phases aren't being reviewed adversarially in the first place**—building elaborate routing infrastructure optimizes the wrong problem.

The design assumes design-stage review is the primary use case, but the stated pain points suggest requirements review would deliver higher leverage (preventing downstream issues entirely). Finding classification to pipeline phases is positioned as a "novel contribution" but doesn't map to any stated Job-to-Be-Done.

**Scope & Boundaries:**
Severe contradiction between claimed MVP scope ("review skill only, phase 1") and the actual "Build now" list. The design includes pattern extraction (with LLM semantic grouping, 15-pattern cap, JSON output), delta detection (cross-iteration semantic matching), auto-fix workflow (separate git commits, re-review), and full JSONL infrastructure—none of which appear in requirements v1.2. This represents **at minimum 3x scope expansion** beyond stated boundaries.

Auto-fix is particularly problematic: marked "deferred to post-MVP" in requirements Q2 resolution but described in detail in UX Flow Step 4. The design claims v4 is "synced with requirements v1.2" but this section wasn't updated. Cross-iteration tracking (pattern extraction + delta detection) adds major complexity, runs in critical path, and has independent failure modes not addressed in the design.

**Constraints & Feasibility:**
Four **Critical constraint gaps** block implementation:
1. **No cost constraints** - Design uses 4-9 parallel LLM agents with full document context but no per-review budget or cost ceiling
2. **No document size limits** - Unbounded input could exceed context windows or make reviews prohibitively expensive
3. **Auto-fix scope unbounded** - Dangerous without strict change type whitelist and blast radius limits
4. **Schema validation circular dependency** - Auto-fix blocked on undefined JSONL schema (though MEMORY.md indicates FR7.5 complete)

Additionally, 16 **Important** constraints are missing or arbitrary: timeout values (60-120s) lack performance justification, minimum reviewer threshold (4/6) lacks rationale for partial results, systemic detection threshold (30%) lacks empirical basis, pattern extraction cap (15) is arbitrary, 50-finding interactive processing threshold unjustified. Many operational constraints unstated: concurrency limits, retry budgets, git dependency assumptions, multi-file design support.

**Assumptions:**
Three **Critical** unstated assumptions could block implementation:
1. **Claude Code API capabilities** - Multi-agent dispatch with tool access controls assumed without validation
2. **Reviewer isolation mechanism** - Independence requirement (FR1.3) has no specified technical implementation
3. **Synthesizer capacity** - Assumes Claude can reliably process 100+ findings without hallucination, dropping findings, or context overflow

Eleven **Important** assumptions risk incorrect design: WebFetch tool existence not validated, pattern extraction timeout/context handling undefined, git state assumptions (clean working directory), prompt caching effectiveness (90% savings) not empirically validated, interactive processing assumes synchronous human availability (contradicts "async-first" claim), JSONL schema validation assumed to catch all malformed outputs but only checks format not semantics.

The design exhibits **systematic assumption pattern**: technical capabilities taken for granted without API validation, numeric thresholds selected arbitrarily without empirical basis, and optimization strategies (prompt caching, clean reviews) assumed effective without measurement plans.

**Success Criteria:**
Three **Critical** gaps make the design unvalidatable:
1. **No measurable success criteria** - Core hypothesis ("multiple perspectives catch gaps") stated but not measurable
2. **No acceptance criteria for prototype** - "Build now" features have no exit conditions or pass/fail thresholds
3. **No quality definition for synthesis** - Deduplication accuracy, phase classification correctness, contradiction detection all unspecified

Eight **Important** validation gaps: verdict accuracy not measurable (no ground truth), 30% systemic threshold lacks justification, auto-fix success criteria undefined, cost targets missing despite cost logging commitment, no user satisfaction or usability metrics, reviewer quality baselines not specified, pattern extraction success criteria missing, delta detection accuracy not measurable.

The design is **thorough on mechanism but silent on measurement**. It specifies *what* to build in detail but lacks *how to validate it worked*.

---

## Critical Findings

### Problem Framing (3 Critical)

1. **v1-problem-framer-001**: Problem statement missing from design document
   - Design jumps to solution without establishing pain point
   - Requirements have JTBD but design doesn't reference them
   - **Suggestion:** Add Problem Statement section before Overview

2. **v1-problem-framer-003**: Pipeline phase routing solves symptom not root cause
   - Phase routing treats late discovery (symptom) not inadequate upstream review (root cause)
   - If requirements were properly reviewed, design findings wouldn't trace back to calibrate gaps
   - **Suggestion:** Reframe as "Apply parallax:review at ALL checkpoints, phase routing becomes diagnostic signal"

3. **v1-problem-framer-008**: Root cause framing inverted—tool problem or process problem?
   - If teams lack adversarial review discipline, automating it doesn't teach the skill
   - May be solving wrong layer of problem
   - **Suggestion:** Validate whether root cause is tooling overhead or lack of review framework

### Scope Boundaries (2 Critical)

4. **v1-scope-guardian-001**: MVP boundary contradicts prototype scope claim
   - States "review skill only" but includes pattern extraction, delta detection, auto-fix, JSONL infrastructure
   - Implementation team cannot plan work without knowing actual MVP scope
   - **Suggestion:** Explicitly reconcile requirements v1.2 with design v4 "Build now" list

5. **v1-scope-guardian-005**: Cross-iteration tracking adds significant complexity to stated MVP
   - Pattern extraction + delta detection represent major feature additions beyond "review skill only"
   - Runs in critical path, adds LLM cost, requires semantic grouping logic
   - **Suggestion:** Move cross-iteration tracking to post-MVP unless explicit requirements added

### Constraints (4 Critical)

6. **v1-constraint-finder-003**: Cost constraints missing entirely
   - No per-review budget despite 4-9 parallel LLM agents
   - Single review could cost $5-20 depending on document size
   - **Suggestion:** Document per-review cost ceiling, model tiering strategy, cost estimation with approval gate

7. **v1-constraint-finder-004**: Document size limits unstated
   - No maximum token count, file size, or section limits
   - Large documents break design (exceed context windows)
   - **Suggestion:** Define max document size (e.g., 10k tokens), chunking strategy for oversize docs

8. **v1-constraint-finder-011**: Auto-fix scope unbounded
   - Vague criteria ("typos, missing file extensions") without whitelist
   - Unbounded auto-fix is dangerous—surprise commits users didn't review
   - **Suggestion:** Define strict whitelist, max-changes-per-auto-fix limit, require user confirmation with diff preview

9. **v1-constraint-finder-016**: Schema validation blocks auto-fix but schema undefined
   - Auto-fix depends on structured finding classification but schema not defined in design
   - Circular dependency blocks implementation
   - **Suggestion:** Reference FR7.5 completion (MEMORY.md: schemas exist) or defer auto-fix to post-schema milestone

### Assumptions (3 Critical)

10. **v1-assumption-hunter-001**: Claude Code API availability assumed without fallback
    - Assumes multi-agent dispatch with tool access controls exists
    - Entire architecture depends on unvalidated API capabilities
    - **Suggestion:** Validate API before finalizing design, define fallback approach

11. **v1-assumption-hunter-002**: Reviewer agent isolation mechanism unspecified
    - FR1.3 requires independence but doesn't specify HOW (separate sessions? API calls? threads?)
    - Cannot validate FR1.3 achievable without knowing mechanism
    - **Suggestion:** Specify technical isolation mechanism, document environment requirements

12. **v1-assumption-hunter-006**: Synthesizer agent capability assumptions unstated
    - Assumes Claude can deduplicate, classify, surface contradictions for 100+ findings reliably
    - NFR1.2 claims this works but not validated
    - **Suggestion:** Validate with realistic test (process v3's 87 findings), define maximum capacity, specify fallback

### Success Criteria (3 Critical)

13. **v1-success-validator-001**: No measurable success criteria defined
    - Core hypothesis ("multiple perspectives catch gaps") not measurable
    - Cannot validate whether skill solves the problem
    - **Suggestion:** Add measurable outcomes: finding recall/precision, completion time, cost per review, reviewer agreement thresholds

14. **v1-success-validator-002**: Acceptance criteria missing for prototype scope
    - "Build now" features lack exit conditions or pass/fail criteria
    - Impossible to determine when prototype is complete
    - **Suggestion:** Define specific acceptance criteria per feature with test case pass/fail thresholds

15. **v1-success-validator-003**: No definition of done for review quality
    - No thresholds for deduplication accuracy, phase classification correctness, contradiction detection
    - Cannot validate synthesizer output quality
    - **Suggestion:** Define measurable quality thresholds (≥90% deduplication, ≥80% phase classification agreement)

---

## Important Findings

### Problem Framing (5 Important)

- **v1-problem-framer-002**: Core hypothesis conflates two distinct problems (perspective diversity vs phase routing)
- **v1-problem-framer-004**: Implicit assumption that design review is primary use case, but requirements review likely higher leverage
- **v1-problem-framer-005**: Success criteria missing for problem validation (no baseline metrics)
- **v1-problem-framer-006**: Problem scope unclear (skill vs pipeline vs orchestration)
- **v1-problem-framer-009**: Finding classification doesn't map to any stated JTBD

### Scope Boundaries (7 Important)

- **v1-scope-guardian-002**: Auto-fix scope undefined with conservative promise but no criteria
- **v1-scope-guardian-004**: JSONL output in MVP conflicts with markdown-first strategy, schema missing
- **v1-scope-guardian-006**: Systemic issue detection logic defined but action unspecified
- **v1-scope-guardian-007**: Reviewer tool capabilities deferred to eval without MVP baseline
- **v1-scope-guardian-009**: Git integration assumed but non-git scenarios not handled
- **v1-scope-guardian-013**: Reviewer count "open question" but fixed at 6 for MVP (cost planning blocked)
- **v1-scope-guardian-014**: Contradiction resolution vs synthesizer judgment boundary ambiguous

### Constraints (16 Important)

- **v1-constraint-finder-001**: Timeout values arbitrary without performance justification (60-120s)
- **v1-constraint-finder-002**: Minimum reviewer threshold lacks rationale (4/6 threshold)
- **v1-constraint-finder-005**: Pattern extraction cap lacks justification (15 patterns)
- **v1-constraint-finder-006**: 50-finding threshold for interactive processing arbitrary
- **v1-constraint-finder-007**: Systemic issue detection threshold lacks empirical basis (30%)
- **v1-constraint-finder-008**: Retry strategy incomplete (exponential backoff with 1 retry contradictory)
- **v1-constraint-finder-009**: Concurrency limits unstated (API rate limits)
- **v1-constraint-finder-010**: Git dependency assumption unstated (non-git workflows unsupported)
- **v1-constraint-finder-012**: Pattern extraction in critical path without timeout
- **v1-constraint-finder-013**: Reviewer tool access unspecified (which tools per persona)
- **v1-constraint-finder-014**: Prompt caching savings assumption unvalidated (90% reduction)
- **v1-constraint-finder-015**: Multi-file design support claimed but unspecified
- **v1-constraint-finder-017**: Authenticated document sources deferred without workaround
- **v1-constraint-finder-020**: Selective re-run requires state tracking mechanism undefined
- **v1-constraint-finder-022**: Contradiction resolution blocks proceed verdict
- **v1-constraint-finder-023**: No fallback when LLM semantic matching fails

### Assumptions (11 Important)

- **v1-assumption-hunter-003**: WebFetch tool assumed available without validation
- **v1-assumption-hunter-004**: Pattern extraction assumed to complete within session context
- **v1-assumption-hunter-005**: Git repository assumed to be in clean state
- **v1-assumption-hunter-007**: Prompt caching effectiveness assumed without empirical validation (90% savings)
- **v1-assumption-hunter-009**: Interactive finding processing assumes synchronous human availability (conflicts with "async-first")
- **v1-assumption-hunter-010**: JSONL schema validation assumed to catch all malformed outputs (only format, not semantics)
- **v1-assumption-hunter-011**: Reviewer token budget unspecified (large docs could exhaust context)
- **v1-assumption-hunter-012**: Severity classification assumed consistent across reviewers
- **v1-assumption-hunter-016**: Clean reviews assumption conflicts with efficiency goal
- **v1-assumption-hunter-018**: LLM semantic matching for pattern delta assumed reliable
- **v1-assumption-hunter-020**: Verdict escalation assumes upstream phases are idempotent

### Success Criteria (8 Important)

- **v1-success-validator-004**: Verdict accuracy not measurable (no ground truth comparison)
- **v1-success-validator-005**: 30% systemic issue threshold lacks empirical justification
- **v1-success-validator-006**: Auto-fix success criteria undefined
- **v1-success-validator-007**: Cost targets missing despite cost logging commitment
- **v1-success-validator-008**: No user satisfaction or usability metrics
- **v1-success-validator-009**: Reviewer quality baselines not specified
- **v1-success-validator-010**: Pattern extraction success criteria missing
- **v1-success-validator-011**: Delta detection accuracy not measurable

---

## Next Steps

1. **Address Critical problem framing issues** (findings 1, 2, 3)
   - Add explicit problem statement to design
   - Reframe phase routing as diagnostic, not primary feature
   - Validate root cause: tool overhead vs process/skill gap

2. **Resolve MVP scope contradiction** (findings 4, 5)
   - Reconcile "review skill only" claim with actual feature list
   - Move pattern extraction + delta detection to post-MVP OR add to requirements v1.2
   - Remove/defer auto-fix (already deferred in requirements but still in design)

3. **Define blocking constraints** (findings 6, 7, 8, 9)
   - Document per-review cost ceiling and model tiering strategy
   - Define maximum document size limits
   - Remove auto-fix or define strict whitelist
   - Reference existing JSONL schema (FR7.5 complete per MEMORY.md)

4. **Validate critical assumptions** (findings 10, 11, 12)
   - Validate Claude Code API multi-agent capabilities before implementation
   - Specify reviewer isolation mechanism
   - Test synthesizer capacity with v3's 87 findings

5. **Add measurable success criteria** (findings 13, 14, 15)
   - Define finding recall/precision targets
   - Specify acceptance criteria per prototype feature
   - Define quality thresholds for synthesis (deduplication, phase classification)

6. **Review Important findings** (47 total)
   - Address arbitrary thresholds with empirical justification
   - Specify missing operational constraints
   - Validate unstated assumptions
   - Define measurement plans for optimization strategies

7. **Consider Minor findings** (30 total)
   - Documentation gaps and edge case handling
   - Process metrics and iteration limits
   - Blind spot checks and meta-concerns
