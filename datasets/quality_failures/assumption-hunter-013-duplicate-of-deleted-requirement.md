# Test Case: Duplicate of Deleted Requirement (assumption-hunter-013)

**Date:** 2026-02-16
**Category:** Review quality - duplicate detection after deletion
**Severity:** Important (duplicate, but interesting pattern)

## Description

Finding v1-assumption-hunter-013 ("Assumes <95% confidence threshold is achievable without defining how confidence is measured") is a **duplicate** of finding v1-scope-guardian-013, which we already addressed by **deleting FR2.3**.

**Timeline:**
1. scope-guardian flagged "confidence measurement undefined" (FR2.3)
2. We deleted FR2.3 as redundant with FR0
3. assumption-hunter independently flagged the same issue
4. But FR2.3 no longer exists - it's a duplicate of a resolved finding

## The Pattern

**Two reviewers flagged same missing definition:**
- scope-guardian-013: "FR2.3 requires <95% confidence findings flagged but doesn't define how confidence is measured"
- assumption-hunter-013: "Requirements reference 95% confidence threshold but never define how it's calculated"

**Same root cause:** Confidence measurement undefined

**Same sections referenced:**
- FR2.3 (deleted during fixing)
- FR3.3 (never existed in final version)
- Open Question #1 (also deleted during fixing)

**Resolution:** FR2.3 deleted as redundant, Open Question #1 deleted as obsolete

## Why This Is Interesting

**Not just a simple duplicate:**
- scope-guardian found it first → we deleted FR2.3
- assumption-hunter found it second → but requirement already gone
- This is a "duplicate of deleted requirement"

**Synthesizer challenge:**
- If synthesizer runs after fixes applied, finding becomes "references non-existent requirement"
- If synthesizer runs before fixes, it's a normal duplicate
- Timing matters for duplicate detection

## Detection Complexity

**Simple duplicate detection:**
```
if finding1.section == finding2.section and finding1.issue == finding2.issue:
    flag_as_duplicate()
```

**Cross-reference validation needed:**
```
if finding.references_requirement(X) and not requirement_exists(X):
    flag_as_obsolete("Requirement already deleted/fixed")
```

**Synthesizer needs to:**
1. Detect duplicates across reviewers
2. Track which findings already addressed
3. Mark obsolete findings when requirements change

## Stale Finding Detection

**This finding became stale because:**
- FR2.3 deleted (requirement removed)
- Open Question #1 deleted (question resolved)
- FR3.3 never existed (false reference)

**Signs of staleness:**
- References non-existent requirement IDs
- Suggests fixes already applied
- Multiple references to deleted content

## Value for Eval Framework

**Phase 1 (MVP):**
- Accept that some findings may be duplicates or stale
- Manual review can catch these
- Focus on catching real issues, tolerate some redundancy

**Phase 2 (Advanced):**
- Track which findings have been addressed
- Mark findings as "duplicate" or "stale" automatically
- Prevent re-raising fixed issues

**Phase 3 (Production):**
- Cross-reference validation (finding references exist)
- Temporal tracking (finding X already fixed by change Y)
- Incremental reviews (only review changed sections)

## Test Dataset Entry

```json
{
  "input": "Review findings generated before requirements changes applied",
  "scenario": "FR2.3 deleted while addressing finding A, finding B still references FR2.3",
  "expected_behavior": {
    "phase_1": "Accept both findings (manual review catches duplicate)",
    "phase_2": "Mark finding B as duplicate/stale (references deleted requirement)",
    "phase_3": "Suppress finding B (requirement already addressed)"
  }
}
```

## Related Patterns

- **Finding #4** (scope-guardian-013): Original finding about confidence measurement
- **Finding #9** (assumption-hunter-013): Duplicate after original was fixed
- **Confidence references:** FR2.3 (deleted), FR3.3 (never existed), Open Question #1 (deleted)
- **Pattern:** Multiple reviewers discover same gap, but gap gets fixed between reviews

## Recommendation

**For requirements review workflow:**
- When fixing findings, check if other findings reference same requirement
- Delete/update related findings together
- Or accept that synthesizer will catch duplicates

**For eval framework:**
- Phase 1: Tolerate duplicates and stale findings (manual review acceptable)
- Phase 2: Add staleness detection (references to non-existent requirements)
- Phase 3: Add temporal tracking (finding already addressed)

## Lessons

**Good:**
- Multiple reviewers catching same issue = high confidence it's real
- Independent discovery validates finding importance

**Challenge:**
- Fixing findings one-by-one can create stale references
- Synthesizer needs to understand temporal ordering
- "Duplicate" vs "stale" distinction matters for different reasons
