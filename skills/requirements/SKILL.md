---
name: requirements
description: This skill should be used when the user asks to "review requirements", "requirements review", "validate problem statement", "check scope", "requirements --light", "parallax:requirements", or mentions post-brainstorm requirements validation.
version: 0.1.0
---

# Requirements Review — Light Mode

Lightweight requirements review that validates problem framing, scope, and constraints after brainstorming.

## When to Use

**Light mode** (this skill):
- After completing brainstorming
- After design doc is written
- Before heavy design investment
- Quick checkpoint: "Are we solving the right problem?"

**Scope:** This skill implements light mode only. Deep mode (post-design specification review) is planned but not yet implemented.

## Process

### Step 1: Gather Inputs

Collect from the user:
- **Design document path** — the design doc from brainstorming (e.g., `docs/plans/2026-02-16-feature-design.md`)
- **Topic label** — name for the review folder (e.g., "auth-system", "parallax-requirements"). Validate: alphanumeric, hyphens, underscores only. Reject invalid characters.

Verify design doc exists and is readable before proceeding.

### Step 2: Create Review Folder

Create `docs/reviews/<topic>-requirements-light/` in the project root.

If the folder already exists, this is a re-review — the previous review will be overwritten (git tracks history).

### Step 3: Dispatch Reviewers

Using the Task tool, dispatch all 5 light mode reviewers **in parallel**:

1. **problem-framer** — validates problem statement and root cause framing
2. **scope-guardian** — validates scope boundaries and MVP definition
3. **constraint-finder** — identifies unstated constraints and feasibility limits
4. **assumption-hunter** — finds implicit assumptions (reused from design review)
5. **success-validator** — validates success criteria and acceptance criteria

Each reviewer receives:
- The full text of the design document
- The topic label
- Instructions to output JSONL findings to `docs/reviews/<topic>-requirements-light/findings-v1-<persona>.jsonl`

**Use Task tool with subagent_type="general-purpose" for each reviewer.**

### Step 4: Wait for Completion

Wait for all 5 reviewer agents to complete. Do NOT check with TaskOutput (huge transcripts). Wait for completion notifications.

### Step 5: Collect Findings

Read all 5 JSONL files:
- `docs/reviews/<topic>-requirements-light/findings-v1-problem-framer.jsonl`
- `docs/reviews/<topic>-requirements-light/findings-v1-scope-guardian.jsonl`
- `docs/reviews/<topic>-requirements-light/findings-v1-constraint-finder.jsonl`
- `docs/reviews/<topic>-requirements-light/findings-v1-assumption-hunter.jsonl`
- `docs/reviews/<topic>-requirements-light/findings-v1-success-validator.jsonl`

Validate JSONL format using:

```bash
jq -s '.' docs/reviews/<topic>-requirements-light/findings-v1-*.jsonl > /dev/null
```

If validation fails, report which file has invalid JSONL.

### Step 6: Synthesize Summary

Create a human-readable summary in `docs/reviews/<topic>-requirements-light/summary.md`:

**Summary structure:**

```markdown
# Requirements Review Summary — <Topic> (Light Mode)

**Review Date:** YYYY-MM-DD
**Design Document:** `path/to/design.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | X | Y | Z | N |
| scope-guardian | X | Y | Z | N |
| constraint-finder | X | Y | Z | N |
| assumption-hunter | X | Y | Z | N |
| success-validator | X | Y | Z | N |
| **Total** | **X** | **Y** | **Z** | **N** |

---

## Key Themes

[2-3 paragraph synthesis of major patterns across findings]

**Problem Framing:**
[What did problem-framer find? Are we solving the right problem?]

**Scope & Boundaries:**
[What did scope-guardian find? Is scope clear?]

**Constraints & Feasibility:**
[What did constraint-finder find? Are limits documented?]

**Assumptions:**
[What did assumption-hunter find? What's unstated?]

**Success Criteria:**
[What did success-validator find? Can we measure success?]

---

## Critical Findings

[List all Critical severity findings with brief description]

1. **[Persona] — Finding Title**
   - Issue: [description]
   - Suggestion: [fix]

---

## Important Findings

[List all Important severity findings with brief description]

---

## Next Steps

1. Address Critical findings (block implementation if unresolved)
2. Review Important findings (cause rework if ignored)
3. Consider Minor findings (polish)
4. Refine design doc based on findings
5. Re-run requirements review if major changes made
```

### Step 7: Present Findings to User

Present the summary interactively:

1. Show finding counts table
2. Highlight Critical findings
3. Ask which findings to explore in detail
4. For each finding, show full context from JSONL

**Do NOT overwhelm with all findings at once.** Let user guide which to review.

### Step 8: Document Review Metadata

No run-metadata.json for MVP. Track review date and reviewer list in summary.md only.

---

## Success Criteria

After running requirements review, validate:

**Quality:**
- Caught 3-5 real requirement gaps
- Findings are actionable (not philosophical debates)

**Performance:**
- Took <30 min to run (including synthesis)

**Workflow fit:**
- Feels like a natural checkpoint
- Not forced process

---

## Limitations

**Light mode only:**
- Reviews problem statement, scope, constraints
- Does NOT review detailed specifications (that's deep mode, post-MVP)

**No requirements file creation:**
- Reviews design doc directly
- Does NOT extract/create separate requirements file
- Evaluation deferred: test whether requirements extraction adds value

**Manual workflow:**
- User explicitly invokes `/requirements --light`
- NOT auto-integrated with brainstorming skill

**No pattern analysis:**
- Manual analysis only for MVP
- After 5-10 runs, analyze patterns across reviews

---

## Examples

**Example invocation:**

```
User: /requirements --light
Skill: What design document should I review?
User: docs/plans/2026-02-15-auth-system-design.md
Skill: What should I call this review? (e.g., "auth-system")
User: auth-system
Skill: Dispatching 5 reviewers...
[wait for completion]
Skill: Review complete. Summary:
[presents findings table]
```

**Example finding:**

```json
{
  "type": "finding",
  "id": "v1-success-validator-001",
  "title": "Success criteria undefined - 'fast' not quantified",
  "severity": "Critical",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Goals",
  "issue": "Goal states 'fast search' but doesn't define what 'fast' means (p50 latency? p99? acceptable threshold?)",
  "why_it_matters": "Without quantified success criteria, can't validate if implementation meets requirements or choose appropriate architecture",
  "suggestion": "Add specific latency targets: e.g., 'p50 < 100ms, p99 < 500ms for 1M record dataset'"
}
```
