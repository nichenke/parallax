# Test Case: Requirements vs Design Confusion (scope-guardian-004)

**Date:** 2026-02-16
**Category:** Requirements quality - outcome vs implementation confusion
**Severity:** Critical (misclassified as requirement gap, but actually design work)

## Failure Description

Scope-guardian flagged "Ground truth dataset format not specified" (v1-scope-guardian-004) as **Critical** requirements gap. However, this is actually:
1. **Not a requirements issue** - it's an implementation/design detail
2. **Not Critical severity** - it's normal Phase 1 research/design work
3. **Confused "what" with "how"** - confused outcome (Inspect AI compatibility) with implementation (specific schema)

## Actual Requirement (Outcome-Based)

**What we need:** Dataset format compatible with Inspect AI

**How we achieve it:** Use Inspect AI Sample format with input/target/metadata fields ← This is design work

## Reviewer Error

**Finding title:** "Ground truth dataset format not specified - Inspect AI Dataset schema unknown"

**Issue text:** "Acceptance criteria says 'Dataset format' but doesn't specify Inspect AI's Dataset schema. Does it require specific JSON structure? What fields are mandatory?"

**Why this is wrong:**
- Schema structure is **implementation detail**, not requirement
- Requirement is: "Can Inspect AI read the dataset?" (yes/no outcome)
- Schema research is **Phase 1 design work**, not requirements gap
- Severity should be **Minor** (missing design detail) not **Critical** (blocking requirement)

## Correct Review Finding

**Should have been:**

```json
{
  "id": "v1-scope-guardian-004",
  "title": "Dataset compatibility requirement needs clarification",
  "severity": "Minor",
  "issue": "FR3.1 says 'Inspect AI Dataset format' but doesn't specify compatibility requirement. Suggest: 'Dataset format must be readable by Inspect AI eval tasks without errors.'",
  "suggestion": "Reframe as outcome: 'Dataset compatible with Inspect AI' (requirement). Schema research is Phase 1 design work, not requirements gap."
}
```

## Detection Criteria for Eval Framework

**finding_quality_scorer.py** should flag:
- Findings that specify implementation details (JSON schemas, field names, data structures) as requirements
- Findings marked Critical that describe normal design/research work
- Findings that confuse "what" (outcome) with "how" (implementation)

**Heuristics:**
- Keywords suggesting implementation: "schema", "format", "fields", "structure", "JSON", "API"
- If finding suggests "research X during implementation" → likely design work, not requirement
- If finding would be resolved by Phase 1 design research → not a requirement gap

## Litmus Test for Requirements vs Design

**Question:** Would this information change **what we're trying to achieve** or **how we achieve it**?

- **What** (requirement): "Dataset must be Inspect AI compatible"
- **How** (design): "Use Sample format with input/target/metadata fields"

**When schema invalidates requirements:**
- Inspect AI requires proprietary format we can't produce → **Change requirement** (use different tool)
- Inspect AI uses standard JSON → **Design detail** (implement conversion)

## Root Cause Hypothesis

Reviewer (scope-guardian) focused on "undefined specification" as blocker, without asking:
1. Is this an outcome requirement or implementation detail?
2. Would this be resolved by normal Phase 1 design/research work?
3. Does this actually block requirements validation?

## Mitigation

**Reviewer training:**
- Distinguish requirements (outcomes) from design (implementation)
- Flag "research needed" as Minor/Important, not Critical
- Use litmus test: "What vs How"

**Post-processing check:**
- Findings with severity=Critical should block requirements approval
- If finding is resolved by "research during Phase 1" → downgrade to Minor
- If finding specifies schemas/formats/APIs → likely design detail

## Files

- **Review finding:** `docs/reviews/inspect-ai-integration-requirements-light/findings-v1-scope-guardian.jsonl` (finding v1-scope-guardian-004)
- **Original requirements:** `0f8f090:docs/requirements/inspect-ai-integration-requirements-v1.md` (FR3.1)
- **Corrected version:** Current HEAD (reframed as outcome-based)

## Test Dataset Entry

```json
{
  "input": "Requirements document with 'Dataset format TBD (research Phase 1)'",
  "expected_finding": {
    "type": "quality_issue",
    "category": "requirements_vs_design_confusion",
    "severity": "Important",
    "issue": "Finding v1-scope-guardian-004 marked Critical but describes normal design research work, not missing requirement",
    "suggestion": "Downgrade to Minor. Schema research is Phase 1 design work. Requirement should be outcome-based: 'Dataset compatible with Inspect AI.'"
  }
}
```

## Related Test Cases

- **FR0 grouping failure:** Redundant sub-requirements (same session)
- **Issue #38:** Sub-design references (related workflow issue)
- **Task #9:** Research gaps workflow (UX improvement)
