# ADR-004: Pattern-Based Systemic Detection

**Status:** Accepted
**Date:** 2026-02-16
**Supersedes:** ADR-002 Decision 3 (Systemic Detection Denominator Rationale)

---

## Context

ADR-002 Decision 3 specified that systemic detection uses `>30% of findings with contributing_phase` as the denominator. This approach conflates detection (is this systemic?) with routing (where should we fix it?).

Pattern extraction design (FR10) revealed that `contributing_phase` should be used for **routing** (identifying where the systemic root cause originated) not **detection** (determining if clustering is systemic).

**Key insight:** Systemic issues are patterns with high clustering strength. Phase attribution tells WHERE to fix them, not WHETHER they exist.

---

## Decision

**Change systemic detection from phase-counting to pattern-based clustering:**

**Old approach (ADR-002):**
- Denominator: Findings with `contributing_phase` set
- Threshold: >30% of findings with contributing_phase share the same contributing phase
- Rationale: Systemic issues are upstream root causes (contributing phase)

**New approach:**
- Denominator: Total findings
- Threshold: 4+ findings in pattern OR >30% of total findings
- Rationale: Systemic severity is absolute clustering strength, not relative to phase-attributed findings
- Phase attribution: Used for routing/escalation after systemic detection

---

## Rationale

### Separation of Concerns

**Detection (clustering):**
- Pattern clustering strength indicates severity
- 4+ findings or >30% of total = high impact requiring escalation
- Independent of whether phase attribution exists

**Routing (phase attribution):**
- `contributing_phase` identifies where to fix the root cause
- Enables escalation to appropriate upstream phase
- Applied AFTER systemic detection

### Example

Pattern: "JSONL schema completely missing"
- 5 findings from 4 reviewers (30% of 17 total findings)
- **Systemic detection:** Yes (high clustering, >30% threshold)
- **contributing_phase:** calibrate (schema missing from requirements)
- **Action:** Escalate to requirements review to add schema specification

Under old approach: If none of the 5 findings had `contributing_phase` set, this wouldn't be flagged as systemic despite high clustering.

### Why Total Findings Denominator

**Absolute severity matters:**
- 5 findings on same theme = high impact regardless of phase attribution
- Users care about "30% of findings cluster around X" (absolute)
- Not "30% of phase-attributed findings cluster" (relative, context-dependent)

**Phase attribution is optional:**
- Not all systemic issues have clear upstream causes
- Design patterns can be systemic without phase attribution
- Detection shouldn't depend on attribution completeness

---

## Consequences

### Requirements Impact

**FR2.7 updated:**
- **Old:** Flag systemic issues when >30% of findings with a contributing phase share the same contributing phase
- **New:** Flag systemic issues when pattern clustering exceeds threshold (4+ findings OR >30% of total findings)
- Denominator changed from "findings with contributing_phase" to "total findings"
- `contributing_phase` purpose clarified: routing (where to fix), not detection

### Design Impact

**Pattern extraction design (FR10) validated:**
- Algorithm confirmed: Extract patterns → Compute clustering → Flag high-clustering as systemic → Identify contributing phase
- Design doc line 123 (`>30% of total findings`) is correct, not a bug

### Implementation Impact

**No changes to existing code:**
- FR2.7 was not yet implemented (deferred to pattern extraction prototype)
- This ADR prevents implementing the wrong algorithm

---

## Alternatives Considered

**A) Keep phase-counting approach (ADR-002):**
- Pro: Focuses on upstream root causes
- Con: Misses systemic patterns without phase attribution
- Con: Relative threshold depends on how many findings have phases

**B) Hybrid approach (both thresholds):**
- Pro: Catches both types of systemic issues
- Con: More complex, two different detection paths
- Con: Unclear which takes precedence

**C) Pattern-based only (CHOSEN):**
- Pro: Simple, absolute severity measure
- Pro: Phase-independent detection
- Pro: `contributing_phase` clearly for routing only
- Con: Must ensure phase attribution still captured

---

## References

- ADR-002 Decision 3: Original systemic detection denominator rationale
- Pattern extraction design: `docs/plans/2026-02-16-pattern-extraction-design.md` (lines 115-149)
- FR2.7 specification: `docs/requirements/parallax-review-requirements-v1.md`
- Requirements review finding: v1-assumption-hunter-007 (caught original approach as "bug")
