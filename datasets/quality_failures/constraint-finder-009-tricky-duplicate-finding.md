# Test Case: Tricky Duplicate Finding (Multiple Ground Truth Findings)

**Date:** 2026-02-16
**Category:** Review quality - duplicate detection complexity
**Severity:** Not a quality failure, but interesting for eval framework
**Phase:** Not for initial eval (too complex), interesting for later phases

## Description

**Three findings identify the same root cause from different angles:**

1. **v1-problem-framer-006:** "Ground truth validation circular dependency"
2. **v1-constraint-finder-009:** "Ablation test ground truth dependency creates circular validation"
3. **v1-assumption-hunter-001:** "Assumes v3 review findings are valid ground truth without verification"

All three findings share the same root cause (unvalidated ground truth) but:

1. **Different framing:**
   - problem-framer: "v3 findings unvalidated, creates circular dependency"
   - constraint-finder: "ablation tests use unvalidated baseline"
   - assumption-hunter: "assumes v3 is valid without verification"

2. **Same root cause:** Ground truth must be validated before use

3. **Different sections:**
   - problem-framer: FR3 (test datasets)
   - constraint-finder: FR4 (ablation tests)
   - assumption-hunter: FR3 (test datasets)

4. **Different depth:**
   - problem-framer: Conceptual issue (circular validation)
   - constraint-finder: Practical impact (ablation tests invalidated)
   - assumption-hunter: Foundational assumption (garbage in, garbage out)

## Why This Is Tricky

**Not a simple duplicate:**
- Simple duplicate: "FR3.1 dataset schema undefined" flagged by two reviewers → exact same issue
- Tricky duplicate: Same root cause, different manifestations, different implications

**All three findings are correct:**
- problem-framer: "Ground truth validation is circular" ✅
- constraint-finder: "Ablation tests depend on validated ground truth" ✅
- assumption-hunter: "v3 findings assumed valid without verification" ✅

**Single solution resolves all three:**
- FR0 (Phase 0: Ground truth validation) addresses all findings
- But each finding highlighted different consequences of the same gap

**Different reviewers, same gap:**
- 3 independent reviewers (different personas)
- All discovered the same fundamental issue
- Each approached from their domain expertise (problem framing, constraints, assumptions)

## Detection Challenge

**Simple duplicate detection:**
```
if finding1.issue == finding2.issue:
    flag_as_duplicate()
```

**Tricky duplicate detection requires:**
- Semantic similarity of root cause
- Understanding that downstream issues trace to same upstream gap
- Recognizing when single fix resolves multiple findings

**Example:**
- Finding A: "No input validation" (security issue)
- Finding B: "SQL injection possible" (consequence of A)
- Finding C: "XSS attacks possible" (consequence of A)

Are B and C duplicates? Or are they different issues with common root cause?

## Value vs Redundancy

**Argument for keeping both findings:**
- problem-framer caught the conceptual issue (circular validation)
- constraint-finder caught the practical impact (ablation tests invalidated)
- Different perspectives valuable for completeness

**Argument for deduplication:**
- Both resolve with same fix (FR0)
- Redundant work processing both findings
- Could confuse: "Are these two separate issues or one?"

## Synthesis Challenge

**Ideal synthesizer behavior:**
1. Recognize all three findings share root cause
2. Consolidate into single finding with multiple impacts:
   ```
   Ground truth validation required (Critical)
   - Root cause: v3 findings not validated by human expert
   - Impact 1: Circular validation (eval framework optimizes against potentially wrong outputs)
   - Impact 2: Ablation tests validate against contaminated baseline
   - Impact 3: Detection rate metrics may be measuring false positives
   - Impact 4: Garbage in, garbage out at foundation of eval framework
   - Solution: FR0 (Phase 0 ground truth validation) addresses all impacts
   - Reviewers: problem-framer, constraint-finder, assumption-hunter (consensus finding)
   ```

3. Credit all three reviewers for discovering different facets
4. Note this is high-confidence finding (3/5 reviewers independently identified)

## Implications for Eval Framework

**Phase 1 (MVP):**
- Skip this complexity
- Simple duplicate detection only (exact match on issue text)
- Accept some redundant findings

**Phase 2 (Advanced):**
- Semantic duplicate detection
- Root cause clustering
- Synthesizer consolidates related findings

**Phase 3 (Production):**
- Causal chain analysis
- Upstream/downstream issue linking
- Single finding, multiple impacts

## Why This Is "Interesting" Not "Failure"

**Not a reviewer failure:**
- Both reviewers correctly identified real issues
- Different lenses revealed different consequences
- No false positives, no misclassification

**Synthesis opportunity:**
- Synthesizer could consolidate for efficiency
- But keeping separate is also valid (different perspectives)
- Tradeoff: completeness vs conciseness

**Complexity indicator:**
- When issues share root causes, duplicate detection becomes non-trivial
- Requires semantic understanding, not just text matching
- Good test case for advanced eval capabilities

## Test Dataset Entry

```json
{
  "input": "Review with 2+ findings that share root cause but describe different consequences",
  "expected_behavior": {
    "phase_1_mvp": "Flag as separate findings (simple duplicate detection)",
    "phase_2_advanced": "Cluster by root cause, note related findings",
    "phase_3_production": "Synthesize into single finding with multiple impacts, credit all reviewers"
  },
  "metrics": {
    "duplicate_detection_recall": "Did we identify they're related?",
    "synthesis_quality": "Did we consolidate clearly without losing information?"
  }
}
```

## Related Patterns

- **Finding #1** (problem-framer-006): Ground truth validation circular dependency
- **Finding #7** (constraint-finder-009): Ablation test dependency on unvalidated baseline
- **Finding #8** (assumption-hunter-001): Ground truth validity assumed without verification
- **Pattern:** 3/5 reviewers (60%) independently discovered same root cause via different reasoning paths
- **Consensus signal:** When multiple reviewers flag same issue, high confidence it's real and Critical

## Recommendation

**For Phase 1 eval framework:**
- Document as "known complexity, defer to later phases"
- Simple duplicate detection acceptable for MVP
- Manual review can catch tricky duplicates

**For future phases:**
- Build semantic similarity scorer
- Cluster findings by root cause
- Test synthesizer's consolidation quality

**Value of this test case:**
- Distinguishes simple eval (text matching) from advanced eval (semantic understanding)
- Validates that duplicate detection is hard problem worth solving well
- Shows when "redundancy" is actually "multiple valid perspectives"
