# Test Case: FR0 Grouping Failure

**Date:** 2026-02-16
**Category:** Requirements quality - grouping/consolidation
**Severity:** Important (confusing but not blocking)

## Failure Description

Problem-framer agent created FR0.1, FR0.2, FR0.3 as separate sub-requirements when they're all steps of the same process (validate ground truth). Should have been single FR0 with consolidated acceptance criteria.

## Reproduction Steps

1. **Input document:** `docs/requirements/inspect-ai-integration-requirements-v1.md` at commit `0f8f090`
2. **Review findings:** `docs/reviews/inspect-ai-integration-requirements-light/findings-v1-problem-framer.jsonl`
3. **Applied fixes:** Suggestions from findings `v1-problem-framer-006` and `v1-problem-framer-008`
4. **Result:** Created three redundant sub-requirements:
   - FR0.1: Human expert validation
   - FR0.2: Document validation process
   - FR0.3: Create validated dataset

   All three describe the same workflow with overlapping acceptance criteria.

## Expected Behavior

Reviewer should have suggested single FR0 with consolidated acceptance criteria:

```markdown
### FR0: Ground Truth Validation (Prerequisite)

**FR0:** Establish validated ground truth via human expert review
- **Acceptance Criteria:**
  - Human examines each finding
  - Classification into real/false-positive/ambiguous
  - Only real findings used as ground truth
  - Process documented
  - Dataset created with metadata
  - Inter-rater reliability measured (if multiple reviewers)
  - Target: ≥15 validated findings
```

## Detection Criteria for Eval Framework

**finding_quality_scorer.py** should flag:
- Requirements with >80% overlapping acceptance criteria
- Sub-requirements (FR0.1, FR0.2, FR0.3) that describe sequential steps of single process
- Redundant rationale statements across related requirements

**Scoring:**
- Precision: Are flagged grouping failures actually redundant? (Target: ≥80%)
- Recall: How many grouping failures are caught? (Target: ≥70%)

## Root Cause Hypothesis

LLM suggestion followed finding structure (one finding → one FR) instead of semantic grouping. The three findings addressed related aspects of ground truth validation, but solution should consolidate rather than multiply requirements.

## Mitigation

Post-processing step: After applying review findings, check for:
1. Sequential sub-requirements (FR0.1, FR0.2, FR0.3)
2. Similar rationale text across requirements
3. Acceptance criteria that reference each other

Suggest consolidation when patterns detected.

## Files

- **Original requirements:** `0f8f090:docs/requirements/inspect-ai-integration-requirements-v1.md`
- **Review findings:** `docs/reviews/inspect-ai-integration-requirements-light/findings-v1-problem-framer.jsonl`
- **Consolidated version:** Current HEAD (after manual fix)

## Test Dataset Entry

```json
{
  "input": "Requirements document with ground truth validation issue",
  "expected_finding": {
    "type": "quality_issue",
    "category": "redundant_grouping",
    "severity": "Important",
    "issue": "FR0.1, FR0.2, FR0.3 are sequential steps of single process, not separate requirements",
    "suggestion": "Consolidate into single FR0 with all acceptance criteria"
  }
}
```
