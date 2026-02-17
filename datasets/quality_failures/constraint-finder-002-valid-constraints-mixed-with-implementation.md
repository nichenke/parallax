# Test Case: Valid Constraints Mixed With Implementation Details (constraint-finder-002)

**Date:** 2026-02-16
**Category:** Requirements quality - valid constraints + implementation details mixed
**Severity:** Critical (correct severity, but needs separation)

## Failure Description

Constraint-finder flagged "API key security and multi-environment access patterns undefined" (v1-constraint-finder-002) as Critical. Unlike previous findings, this one contains **valid security constraints** but mixes them with **implementation details**.

**The mix:**
- ✅ Valid: Keys never in git, work/personal separation, rotation policy
- ❌ Implementation: Where to store keys (`~/.bashrc`), CI/CD tool (GitHub Actions), specific fallback mechanism

## What's Valid vs What's Implementation

| Item | Type | Why |
|------|------|-----|
| "Keys never committed to git" | ✅ Valid constraint | Security requirement, non-negotiable |
| "Work/personal key separation" | ✅ Valid constraint | Audit compliance, billing attribution |
| "Key rotation policy" | ✅ Valid constraint | Security requirement |
| "Store in ~/.bashrc" | ❌ Implementation | One of many valid approaches (.env, .envrc, etc) |
| "GitHub Actions secrets" | ❌ Implementation | CI/CD tool choice (could be CircleCI, GitLab, etc) |
| "Bedrock → API fallback" | ❌ Implementation | Specific fallback mechanism (design decision) |

## Correct Separation

**Requirements (NFR - Security):**
```markdown
### NFR1: API Key Security

**NFR1.1:** API keys never committed to version control
- Keys stored in environment variables or gitignored config files
- Pre-commit hook blocks commits containing API key patterns

**NFR1.2:** Work/personal key separation for audit compliance
- Personal dev uses personal API keys
- Work context uses separate Bedrock IAM roles
- Key rotation procedure documented
```

**Implementation (Phase 1 Design):**
- Where to store keys: `~/.bashrc` vs `.env` vs `.envrc` (choose during setup)
- CI/CD secrets: GitHub Actions vs CircleCI (choose based on repo platform)
- Bedrock fallback: Implement in eval runner logic (design decision)

## Detection Criteria for Eval Framework

**finding_quality_scorer.py** should flag:
- Findings that mix valid constraints with specific tooling choices
- Findings that suggest "use [specific tool/location]" for security (implementation leak)
- Findings that could be split: constraint section + implementation section

**Heuristics:**
- If finding contains both "never do X" (constraint) and "use Y tool" (implementation) → mixed
- If finding references specific files/tools (`~/.bashrc`, GitHub Actions) → likely implementation detail
- If finding can be rewritten as "must prevent X" without mentioning how → extract constraint

## Quality Improvement

**Better reviewer output:**
```json
{
  "id": "v1-constraint-finder-002",
  "title": "API key security constraints undefined",
  "severity": "Critical",
  "issue": "No security constraints for API key handling. Must prevent: keys in git, work/personal mixing, unauthorized access.",
  "suggestion": "Add NFR: Keys never in git (pre-commit hook), work/personal separation (separate credentials), rotation policy documented. Implementation details (storage location, CI/CD setup) deferred to Phase 1."
}
```

**Separation achieved:**
- Constraint: "Keys never in git"
- Implementation: "Pre-commit hook checks for patterns" (how we enforce)

## This is NOT a False Positive

Unlike findings #3 (schema) and #5 (Python env), this finding **correctly identifies Critical gaps**:
- Missing security constraints ARE blocking requirements
- Severity=Critical is justified (security violations block deployment)

**The issue:** Valid constraints buried in implementation suggestions. Reviewer should have:
1. Extracted constraints as requirements
2. Noted implementation details separately
3. Let Phase 1 design choose specific mechanisms

## Root Cause Hypothesis

Reviewer (constraint-finder) correctly identified missing security constraints but over-specified solutions. Instead of:
- "Must prevent keys in git" (constraint)
- Suggested: "Store in ~/.bashrc, never in git" (constraint + implementation)

## Mitigation

**Reviewer training:**
- Separate "what must be prevented" (constraint) from "how to prevent it" (implementation)
- If suggestion includes specific tools/files → extract the underlying constraint
- Security constraints are requirements, security mechanisms are implementation

**Post-processing:**
- If finding mixes "never/always/must" (constraint language) with specific tools → split
- Extract constraints into NFR section
- Note implementation suggestions for Phase 1 design

## Files

- **Review finding:** `docs/reviews/inspect-ai-integration-requirements-light/findings-v1-constraint-finder.jsonl` (finding v1-constraint-finder-002)
- **Resolution:** Added NFR1 (API Key Security) with constraints only, implementation deferred

## Test Dataset Entry

```json
{
  "input": "Requirements document with no API key security mentioned",
  "expected_finding": {
    "type": "valid_constraint_with_implementation_leak",
    "category": "requirements_quality",
    "severity": "Important",
    "issue": "Finding v1-constraint-finder-002 correctly identifies Critical security gaps but mixes valid constraints (keys never in git) with implementation details (store in ~/.bashrc, GitHub Actions).",
    "suggestion": "Extract constraints into NFR section (keys never in git, work/personal separation, rotation policy). Defer implementation details (where to store, CI/CD setup) to Phase 1 design."
  }
}
```

## Related Test Cases

- **scope-guardian-004:** Pure implementation detail as requirement (schema)
- **constraint-finder-001:** Pure implementation detail as requirement (Python env)
- **FR0 grouping failure:** Redundant sub-requirements

## Pattern Summary

**4 quality failure modes identified:**

1. **Redundant grouping** (FR0): Same requirement split into sub-requirements
2. **Pure implementation detail** (findings #3, #5): Design decisions flagged as requirements
3. **Mixed constraints + implementation** (finding #6): Valid requirements buried in implementation
4. (More patterns likely in remaining findings)

**Severity of failure:**
- Findings #3, #5: False positives (not actual requirement gaps)
- Finding #6: True positive (real gaps) but needs refinement (separate constraint from implementation)
