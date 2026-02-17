# Test Case: Implementation Detail Flagged as Critical Requirement (constraint-finder-001)

**Date:** 2026-02-16
**Category:** Requirements quality - implementation detail vs requirement
**Severity:** Critical (incorrectly) → Should be Minor or deferred to Phase 1

## Failure Description

Constraint-finder flagged "Python environment and dependency management constraints unstated" (v1-constraint-finder-001) as **Critical** blocker. However, this is **Phase 1 implementation detail**, not a requirements gap.

**The confusion:**
- **Requirement:** "Inspect AI must be installable and operational"
- **Implementation:** "Use Python 3.11, poetry, dedicated venv, requirements.txt with pinned versions"

Reviewer flagged missing implementation details (venv strategy, dependency resolution) as Critical requirement gaps.

## Actual Requirement (Outcome-Based)

**What we need:** Inspect AI installed and working, no conflicts with existing tools

**How we achieve it:** Python 3.11+, poetry/uv/pipenv, dedicated venv, pinned dependencies ← This is Phase 1 setup work

## Reviewer Error

**Finding title:** "Python environment and dependency management constraints unstated"

**Issue text:** "Requirements mandate Inspect AI installation but don't specify Python version requirements, virtual environment strategy, or dependency conflict resolution."

**Suggested fix:** "Add NFR section 'Development Environment': Python 3.11+ required, pyenv for version management, dedicated venv..."

**Why this is wrong:**
- Python tooling choices (venv vs poetry vs uv) are **implementation decisions**, not requirements
- This is "very solvable" with standard Python tooling (user's words)
- Requirement is: "Can we install Inspect AI without breaking existing tools?" (yes/no)
- Setup details are **Phase 1 design/implementation work**
- Severity should be **Minor** (note for implementer) not **Critical** (blocks requirements)

## Pattern: Same as Finding #3 (Schema)

Both findings confuse requirements with implementation:

| Finding | Requirement (What) | Implementation (How) | Flagged As | Should Be |
|---------|-------------------|---------------------|------------|-----------|
| v1-scope-guardian-004 | Dataset compatible with Inspect AI | Use Sample schema with input/target/metadata | Critical requirement gap | Minor (design work) |
| v1-constraint-finder-001 | Inspect AI installable without conflicts | Python 3.11, poetry, venv, pinned deps | Critical requirement gap | Deferred to Phase 1 |

## Detection Criteria for Eval Framework

**finding_quality_scorer.py** should flag:
- Findings marked Critical that describe tooling choices (venv, poetry, pip, conda)
- Findings that list specific versions/tools in requirements (implementation detail)
- Findings resolved by "standard tooling" → not blocking requirements
- Findings about "how to install/configure" → implementation, not requirement

**Heuristics:**
- Keywords: "version", "venv", "dependency", "package manager", "requirements.txt"
- Suggests specific tools (pyenv, poetry, pipenv) → implementation choice
- Describes "strategy" or "approach" → design work, not requirement
- User says "very solvable with [tool]" → not a blocker, just setup

## Litmus Test

**Question:** Is this a **constraint** (limits what's possible) or **implementation detail** (how we do it)?

- **Constraint:** "Inspect AI requires Python 3.10+" (hard limit, must be documented)
- **Implementation:** "Use pyenv for version management" (one of many valid approaches)

**When environment becomes requirement:**
- Inspect AI only works on Linux → **Requirements change** (deploy differently or choose different tool)
- Inspect AI works on macOS with standard Python tooling → **Implementation detail** (set up venv in Phase 1)

## Correct Review Finding

**Should have been:**

```json
{
  "id": "v1-constraint-finder-001",
  "title": "Note Python 3.10+ requirement for Inspect AI",
  "severity": "Minor",
  "issue": "FR1.1 should note Inspect AI requires Python 3.10+. Environment setup (venv, dependencies) is Phase 1 design work.",
  "suggestion": "Add to FR1.1: 'Requires Python 3.10+'. Defer venv strategy and dependency management to Phase 1 implementation."
}
```

## Root Cause Hypothesis

Reviewer (constraint-finder) focused on "unstated constraints" without distinguishing:
1. Hard constraints that limit what's possible (Python 3.10+ minimum)
2. Implementation choices that have multiple valid solutions (venv vs poetry vs uv)

Flagged all missing details as Critical, even when solutions are standard/obvious.

## Mitigation

**Reviewer training:**
- Distinguish hard constraints (limits) from implementation choices (how)
- If problem is "very solvable with standard tooling" → not Critical
- Critical = blocks requirements validation, Minor = note for implementer

**Post-processing check:**
- Findings about tooling choices (venv, package managers, version pinning) → likely Phase 1 work
- If finding suggests "use [specific tool]" → implementation detail, not requirement
- Downgrade to Minor or defer to Phase 1 design

## Files

- **Review finding:** `docs/reviews/inspect-ai-integration-requirements-light/findings-v1-constraint-finder.jsonl` (finding v1-constraint-finder-001)
- **Original requirements:** FR1.1 (Inspect AI integration)
- **Resolution:** Deferred to Phase 1 implementation

## Test Dataset Entry

```json
{
  "input": "Requirements document with 'Install Inspect AI' but no venv/dependency details",
  "expected_finding": {
    "type": "quality_issue",
    "category": "implementation_detail_as_requirement",
    "severity": "Important",
    "issue": "Finding v1-constraint-finder-001 marked Critical but describes Phase 1 setup work, not requirements gap. Python environment setup is solvable with standard tooling.",
    "suggestion": "Downgrade to Minor. Note 'Python 3.10+ required' in FR1.1, defer venv/dependency strategy to Phase 1 design."
  }
}
```

## Related Test Cases

- **scope-guardian-004:** Requirements vs design confusion (dataset schema)
- **FR0 grouping failure:** Redundant sub-requirements
- **Task #9:** Research gaps workflow (UX improvement)

## Pattern Summary

**3 findings so far with same root cause: Implementation details flagged as Critical requirements**

1. Dataset schema specification (scope-guardian-004)
2. Python environment setup (constraint-finder-001)
3. (Likely more in remaining findings)

Reviewers need better distinction between:
- **Requirements:** Outcomes, constraints, capabilities
- **Design:** How we achieve those outcomes
- **Implementation:** Specific tools, versions, configurations
