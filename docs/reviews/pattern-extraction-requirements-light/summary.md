# Requirements Review Summary — Pattern Extraction (Light Mode)

**Review Date:** 2026-02-16
**Design Document:** `docs/plans/2026-02-16-pattern-extraction-design.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator
**Parent Requirements:** `docs/requirements/parallax-review-requirements-v1.md` (Job 4, FR10)

---

## Sub-Design Reference Issue

**Post-review analysis revealed a systematic issue:** This design doc is a **sub-design** (prototype of FR10 pattern extraction from parent requirements) but **does not reference the parent requirements document**. This caused reviewers to flag "missing problem statement" when the problem framing actually exists upstream in Job 4 and FR10.

**Classification:**
- **1 finding (v1-problem-framer-001) is a missing reference**, not a genuine gap — resolved by linking to parent requirements
- **1 finding (v1-assumption-hunter-007) is a confirmed specification bug** — design contradicts FR2.7 denominator definition
- **7 findings remain valid design-level gaps** — MVP scope, testing strategy, implementation constraints not addressed by parent requirements

**Effective Critical Count:** 8 (not 9)

**Root Cause:** Sub-designs created after brainstorming don't automatically reference parent requirements, causing false positives in requirements review.

**Tracked in:** Issue #38 — "Sub-design docs don't link to parent requirements"

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 1 | 3 | 2 | 6 |
| scope-guardian | 2 | 3 | 4 | 9 |
| constraint-finder | 2 | 3 | 4 | 9 |
| assumption-hunter | 2 | 3 | 5 | 10 |
| success-validator | 2 | 4 | 4 | 10 |
| **Total** | **9** | **16** | **19** | **44** |

---

## Key Themes

The pattern extraction design document presents a technically sound approach but has significant **design-level gaps** that could derail implementation. Post-review analysis confirms 8 of 9 Critical findings are valid, with 1 finding resolved by referencing parent requirements.

**Problem Framing:** The design lacks a reference to parent requirements (Job 4, FR10) which contain the problem statement: *"No way to know if issues from previous review were addressed without manual cross-reference."* Pattern extraction solves this via automated semantic comparison. The design should link to `docs/requirements/parallax-review-requirements-v1.md` rather than restate the problem. However, it also conflates two distinct problems—validating pattern extraction (FR10) and clarifying systemic detection semantics (FR2.7)—which creates scope creep risk.

**Scope & Boundaries:** MVP boundaries are undefined despite multiple references to "post-MVP" features. No explicit statement of what constitutes the deliverable, and no consolidated out-of-scope list. The design uses ambiguous terms ("handcrafted sample" vs "cherry-pick") that differ by 10x in effort. Success criteria allow unbounded iteration via vague "manual review" thresholds without objective rubrics.

**Constraints & Feasibility:** Multiple missing constraints pose implementation risks: no token/cost budget for LLM calls, no schema stability guarantees during prototype execution, no failure recovery strategy if extraction produces unexpected results. The design assumes 15-20 findings are representative without statistical justification and provides no context window analysis for full-scale conversion (83 findings).

**Assumptions:** Critical assumptions lack validation: LLM semantic grouping assumed to work without consistency checks, sample representativeness assumed without empirical basis, v3 JSONL data assumed to exist and be valid without verification. **CRITICAL BUG:** The design contradicts FR2.7 on systemic detection denominator—design uses "30% of total findings" but FR2.7 explicitly specifies "findings with contributing_phase." This would cause the prototype to test the wrong algorithm.

**Success Criteria:** Success is defined by absence of errors rather than presence of value. Criteria test mechanics (schema validates, extraction completes) but not outcomes (do patterns help users? does cross-iteration comparison work?). No definition of done for the prototype, no iteration plan if validation fails, and no measurable thresholds for pattern quality beyond "manual review."

---

## Critical Findings

### Problem Framing (Resolved by Parent Reference)

1. **v1-problem-framer-001** — ~~Problem statement absent~~ **→ EXISTS in parent requirements**
   - **Status:** Resolved by referencing `docs/requirements/parallax-review-requirements-v1.md` Job 4 + FR10
   - Issue: Design doesn't link to parent requirements where problem framing exists
   - Suggestion: Add section: **"Problem Statement: See [Job 4](../requirements/parallax-review-requirements-v1.md#jobs-to-be-done) — cross-iteration delta detection without manual cross-reference"**

### Scope Definition

2. **v1-scope-guardian-001** — MVP boundary undefined - no explicit statement of deliverable scope
   - Issue: References "MVP" and "post-MVP" throughout but never states what the MVP actually includes
   - Suggestion: Add MVP Definition section with explicit in-scope and out-of-scope lists

3. **v1-scope-guardian-005** — Schema dependency scope impact undefined - what if schemas are broken?
   - Issue: Assumes existing schemas work with v3 data; no contingency if schema fixes needed
   - Suggestion: Document that schema fixes are in-scope for prototype execution

### Constraints

4. **v1-constraint-finder-004** — Schema evolution could invalidate prototype work
   - Issue: No versioning constraints—if schemas change mid-prototype, all JSONL files become invalid
   - Suggestion: Freeze schemas during prototype execution (Issue #17 branch only)

5. **v1-constraint-finder-007** — No context window constraints for full v3 conversion
   - Issue: 83 findings may exceed Claude context limits; no chunking strategy documented
   - Suggestion: Add constraint: 83 findings estimated <50k tokens, document fallback if limits exceeded

### Assumptions

6. **v1-assumption-hunter-001** — LLM pattern extraction assumes semantic grouping succeeds without validation
   - Issue: No mechanism to verify patterns are stable across runs or semantically meaningful
   - Suggestion: Run extraction twice with different seeds; patterns should be >80% consistent

7. **v1-assumption-hunter-007** — **CONFIRMED BUG:** Systemic detection denominator contradicts FR2.7
   - **Status:** Design uses wrong denominator — "30% of total findings" vs FR2.7's "findings with contributing_phase"
   - Issue: Prototype would test incorrect algorithm, invalidating FR2.7 validation
   - Suggestion: **FIX:** Change line 123 to match FR2.7 exactly: "High: 4+ findings in pattern, OR >30% of findings with contributing_phase set"

### Success Criteria

8. **v1-success-validator-001** — Pattern quality validation relies on unmeasurable 'manual review'
   - Issue: "Patterns match expected themes" has no objective rubric—different reviewers could disagree
   - Suggestion: Define measurable: "≥75% of patterns map to v3 themes, each pattern contains 2+ findings"

9. **v1-success-validator-002** — Definition of done missing for prototype
   - Issue: "If validated" path unclear—which criteria must pass? Can we proceed with 5/6 passing?
   - Suggestion: Explicit DoD: all 6 criteria pass + manual review confirms 4/5 themes + 1+ systemic issue

---

## Important Findings

### Problem Framing (3)
- **v1-problem-framer-002** — Root cause unclear - why prototype separately from full pipeline?
- **v1-problem-framer-003** — Conflates two problems - pattern extraction validation AND systemic detection clarification
- **v1-problem-framer-004** — Success criteria validate mechanics, not value - no evidence solves user need

### Scope Definition (3)
- **v1-scope-guardian-002** — Sample creation scope ambiguous - handcrafted vs cherry-pick effort undefined
- **v1-scope-guardian-003** — Out-of-scope not explicitly stated
- **v1-scope-guardian-004** — Validation success criterion allows unbounded iteration

### Constraints (3)
- **v1-constraint-finder-001** — No token/cost budget for LLM-driven pattern extraction
- **v1-constraint-finder-003** — Manual JSONL conversion has unbounded effort
- **v1-constraint-finder-005** — No failure recovery or rollback constraints

### Assumptions (3)
- **v1-assumption-hunter-002** — Sample size representativeness not justified - assumes 20% captures distribution
- **v1-assumption-hunter-003** — Assumes v3 JSONL data exists and is valid - no verification step
- **v1-assumption-hunter-006** — Single-pass extraction assumes success - no validation-retry loop

### Success Criteria (4)
- **v1-success-validator-003** — Systemic detection validation lacks concrete success metrics
- **v1-success-validator-004** — Pattern extraction success defined by absence of errors, not quality
- **v1-success-validator-005** — Expected pattern count range lacks validation threshold
- **v1-success-validator-009** — Testing workflow lacks post-failure iteration plan

---

## Minor Findings

19 Minor findings identified across clarity improvements, documentation gaps, and blind spot checks. See individual JSONL files for details.

---

## Next Steps

### Immediate Actions (Block Implementation)

1. **Link to Parent Requirements** — Add reference to Job 4 + FR10 for problem framing (v1-problem-framer-001)
2. **FIX SPECIFICATION BUG** — Correct systemic detection denominator to match FR2.7 exactly (v1-assumption-hunter-007)
3. **Define MVP Scope** — Explicit deliverable list + out-of-scope consolidation (v1-scope-guardian-001, 003)
4. **Add Schema Stability Constraint** — Freeze schemas during prototype (v1-constraint-finder-004)
5. **Define Measurable Success Criteria** — Replace "manual review" with objective thresholds (v1-success-validator-001, 002)

### Validation Improvements (Reduce Risk)

6. **Add Pattern Consistency Check** — Run extraction twice, verify >80% stable (v1-assumption-hunter-001)
7. **Verify v3 Data Exists** — Prerequisite check before sample creation (v1-assumption-hunter-003)
8. **Document Failure Recovery** — Iteration plan if extraction/validation fails (v1-success-validator-009)
9. **Add Context Window Analysis** — Document chunking strategy for full conversion (v1-constraint-finder-007)

### Scope Clarifications (Prevent Confusion)

10. **Separate Two Problems** — Split pattern extraction prototype from FR2.7 clarification (v1-problem-framer-003)
11. **Define Sample Creation Process** — Cherry-pick vs handcraft effort estimate (v1-scope-guardian-002)
12. **Add Cost Constraint** — Token budget for LLM pattern extraction (v1-constraint-finder-001)

---

## Assessment

**Severity:** This design document cannot proceed to implementation without addressing 8 Critical findings (1 of 9 resolved by parent requirements reference).

**Confirmed Specification Bug:** Design contradicts FR2.7 on systemic detection denominator—must be fixed before implementation to avoid testing wrong algorithm.

**Recommendation:** **DO NOT IMPLEMENT** until design-level gaps are resolved:
- Add parent requirements reference (Job 4 + FR10)
- Fix systemic detection denominator bug (line 123)
- Define MVP scope boundaries
- Add measurable success criteria
- Document implementation constraints

**Estimated Remediation Effort:** 2-4 hours to address Critical findings. After remediation, consider re-running requirements review to confirm gaps resolved (though sub-design reference issue may trigger false positives again—see Issue #38).

**Lessons Learned:** Sub-designs need parent requirements links. This prevents requirements review from flagging "missing problem statement" when problem framing exists upstream. Consider enhancing brainstorming or requirements skill to inject parent references automatically.
