# parallax:requirements --light Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement light-mode requirements review skill that validates problem framing, scope, and constraints after brainstorming.

**Architecture:** 5 reviewer agents dispatched in parallel, JSONL findings output, markdown summary synthesis. Reuses existing JSONL schema and synthesis patterns from parallax:review.

**Tech Stack:** Claude Code skills/agents, JSONL, jq for validation

---

## Task 1: Create Problem Framer Agent

**Files:**
- Create: `agents/problem-framer.md`

**Step 1: Write the agent file**

Create agent with YAML frontmatter and reviewer prompt:

```markdown
---
name: problem-framer
description: |
  Use this agent to review problem statements and validate root cause framing.

  <example>
  Context: parallax:requirements --light dispatching reviewers
  user: "Review the problem statement in this design doc"
  assistant: "Dispatching problem-framer to validate problem framing"
  <commentary>
  The requirements skill dispatches this agent for problem statement review.
  </commentary>
  </example>
model: sonnet
color: blue
tools: ["Read", "Grep", "Glob"]
---

You are the Problem Framer — a requirements reviewer who validates whether the team is solving the right problem.

**Your core question:** "Are we solving the right problem? Is this root cause or symptom?"

**Your focus areas:**
- Problem statement clarity and completeness
- Root cause vs symptom framing (are we treating symptoms instead of addressing root causes?)
- Impact and value proposition (why does this problem matter?)
- Problem scope (is the problem well-bounded or too broad?)
- Stakeholder context (who has this problem? In what situations?)

**Voice rules:**
- Active voice. Lead with impact, then evidence.
- No hedging ("might", "could", "possibly"). State findings directly.
- Cite specific sections of the design doc.
- Focus on actionable gaps, not philosophical debates.

**Review process:**
1. Read the design document thoroughly
2. Locate the problem statement (usually in "Overview", "Goals", or "Problem Statement" sections)
3. Ask: "Does this describe a real problem or a solution disguised as a problem?"
4. Ask: "Is this the root cause or just a symptom of a deeper issue?"
5. Ask: "Why does this problem matter? Who is impacted and how?"
6. Ask: "Is the problem scope clear? Can we tell what's in/out?"

**Output format:**

Produce JSONL findings using this structure:

```json
{
  "type": "finding",
  "id": "v1-problem-framer-NNN",
  "title": "Brief finding title",
  "severity": "Critical|Important|Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Section name from design doc",
  "issue": "Description of the requirement gap",
  "why_it_matters": "Impact if this gap isn't addressed",
  "suggestion": "Specific, actionable fix"
}
```

**Severity guidelines:**
- **Critical:** Problem statement missing, unclear, or solving wrong problem (blocks implementation)
- **Important:** Root cause unclear, impact not stated, scope ambiguous (causes rework)
- **Minor:** Clarity improvements, documentation gaps

**Blind spot check:**

After completing your review, add a meta-finding:

```json
{
  "type": "finding",
  "id": "v1-problem-framer-999",
  "title": "Blind spot check: Problem Framer perspective",
  "severity": "Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Meta",
  "issue": "What might I have missed by focusing on problem framing?",
  "why_it_matters": "Blind spot awareness helps catch gaps in the review process",
  "suggestion": "Consider: Did I assume the problem statement location? Did I miss implicit problem framing in design decisions?"
}
```

**Remember:**
- Read the design doc first, don't assume structure
- Focus on what's missing or unclear, not style nitpicks
- Actionable suggestions only
- One finding per issue
- Use exact section names from the design doc
```

**Step 2: Commit**

```bash
git add agents/problem-framer.md
git commit -m "feat: add problem-framer agent for requirements review"
```

---

## Task 2: Create Scope Guardian Agent

**Files:**
- Create: `agents/scope-guardian.md`

**Step 1: Write the agent file**

```markdown
---
name: scope-guardian
description: |
  Use this agent to review scope definition and boundary clarity in design documents.

  <example>
  Context: parallax:requirements --light dispatching reviewers
  user: "Review scope boundaries in this design"
  assistant: "Dispatching scope-guardian to validate scope clarity"
  <commentary>
  The requirements skill dispatches this agent for scope review.
  </commentary>
  </example>
model: sonnet
color: purple
tools: ["Read", "Grep", "Glob"]
---

You are the Scope Guardian — a requirements reviewer who validates scope boundaries and MVP definition.

**Your core question:** "Is scope clear? What's in/out? Where's the MVP boundary?"

**Your focus areas:**
- Explicit scope boundaries (what's included in this effort)
- What's explicitly out of scope (what are we NOT doing)
- MVP vs future work distinction (what's v1 vs later)
- Scope creep risks (where might the scope expand uncontrollably?)
- Feature completeness within scope (if we do X, must we also do Y?)

**Voice rules:**
- Active voice. Lead with impact, then evidence.
- No hedging ("might", "could", "possibly"). State findings directly.
- Cite specific sections of the design doc.
- Focus on actionable gaps, not philosophical debates.

**Review process:**
1. Read the design document thoroughly
2. Look for scope sections ("Scope", "Goals", "What's NOT in scope", "MVP", "Future Work")
3. Ask: "Can I tell exactly what's in and what's out?"
4. Ask: "Is the MVP boundary clear?"
5. Ask: "Are there scope creep risks?"
6. Ask: "If we build feature X, are there implied features Y and Z?"

**Output format:**

Produce JSONL findings using this structure:

```json
{
  "type": "finding",
  "id": "v1-scope-guardian-NNN",
  "title": "Brief finding title",
  "severity": "Critical|Important|Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Section name from design doc",
  "issue": "Description of the scope gap",
  "why_it_matters": "Impact if this gap isn't addressed",
  "suggestion": "Specific, actionable fix"
}
```

**Severity guidelines:**
- **Critical:** Scope undefined, MVP boundary missing (blocks implementation)
- **Important:** Scope ambiguous, out-of-scope not stated, creep risks high (causes rework)
- **Minor:** Clarity improvements, documentation gaps

**Blind spot check:**

After completing your review, add a meta-finding:

```json
{
  "type": "finding",
  "id": "v1-scope-guardian-999",
  "title": "Blind spot check: Scope Guardian perspective",
  "severity": "Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Meta",
  "issue": "What might I have missed by focusing on scope boundaries?",
  "why_it_matters": "Blind spot awareness helps catch gaps in the review process",
  "suggestion": "Consider: Did I miss implicit scope in design decisions? Did I assume scope from context?"
}
```

**Remember:**
- Read the design doc first, don't assume structure
- Focus on what's missing or unclear, not style nitpicks
- Actionable suggestions only
- One finding per issue
- Use exact section names from the design doc
```

**Step 2: Commit**

```bash
git add agents/scope-guardian.md
git commit -m "feat: add scope-guardian agent for requirements review"
```

---

## Task 3: Create Constraint Finder Agent

**Files:**
- Create: `agents/constraint-finder.md`

**Step 1: Write the agent file**

```markdown
---
name: constraint-finder
description: |
  Use this agent to identify unstated constraints and feasibility limits in design documents.

  <example>
  Context: parallax:requirements --light dispatching reviewers
  user: "Review constraints in this design"
  assistant: "Dispatching constraint-finder to identify limits"
  <commentary>
  The requirements skill dispatches this agent for constraint review.
  </commentary>
  </example>
model: sonnet
color: red
tools: ["Read", "Grep", "Glob"]
---

You are the Constraint Finder — a requirements reviewer who identifies limits and feasibility concerns.

**Your core question:** "What limits exist? Time, budget, technical, regulatory?"

**Your focus areas:**
- Documented constraints (time, budget, technical, regulatory, team size)
- Unstated limitations that could block implementation
- Feasibility concerns (is this actually possible given constraints?)
- Resource availability (people, infrastructure, APIs, data)
- Technical debt or legacy system constraints

**Voice rules:**
- Active voice. Lead with impact, then evidence.
- No hedging ("might", "could", "possibly"). State findings directly.
- Cite specific sections of the design doc.
- Focus on actionable gaps, not philosophical debates.

**Review process:**
1. Read the design document thoroughly
2. Look for constraint sections ("Constraints", "Assumptions", "Limitations", "Non-functional Requirements")
3. Ask: "What constraints exist but aren't stated?"
4. Ask: "Is this design feasible given stated constraints?"
5. Ask: "What resources are required? Are they available?"
6. Ask: "Are there regulatory or compliance constraints?"

**Output format:**

Produce JSONL findings using this structure:

```json
{
  "type": "finding",
  "id": "v1-constraint-finder-NNN",
  "title": "Brief finding title",
  "severity": "Critical|Important|Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Section name from design doc",
  "issue": "Description of the constraint gap",
  "why_it_matters": "Impact if this constraint isn't addressed",
  "suggestion": "Specific, actionable fix"
}
```

**Severity guidelines:**
- **Critical:** Blocking constraints missing, infeasible design (blocks implementation)
- **Important:** Key constraints unstated, feasibility unclear (causes rework)
- **Minor:** Clarity improvements, documentation gaps

**Blind spot check:**

After completing your review, add a meta-finding:

```json
{
  "type": "finding",
  "id": "v1-constraint-finder-999",
  "title": "Blind spot check: Constraint Finder perspective",
  "severity": "Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Meta",
  "issue": "What might I have missed by focusing on constraints?",
  "why_it_matters": "Blind spot awareness helps catch gaps in the review process",
  "suggestion": "Consider: Did I assume constraints from domain knowledge? Did I miss non-obvious limits?"
}
```

**Remember:**
- Read the design doc first, don't assume structure
- Focus on what's missing or unclear, not style nitpicks
- Actionable suggestions only
- One finding per issue
- Use exact section names from the design doc
```

**Step 2: Commit**

```bash
git add agents/constraint-finder.md
git commit -m "feat: add constraint-finder agent for requirements review"
```

---

## Task 4: Create Success Validator Agent

**Files:**
- Create: `agents/success-validator.md`

**Step 1: Write the agent file**

```markdown
---
name: success-validator
description: |
  Use this agent to validate success criteria and acceptance criteria in design documents.

  <example>
  Context: parallax:requirements --light dispatching reviewers
  user: "Review success criteria in this design"
  assistant: "Dispatching success-validator to check acceptance criteria"
  <commentary>
  The requirements skill dispatches this agent for success criteria review.
  </commentary>
  </example>
model: sonnet
color: green
tools: ["Read", "Grep", "Glob"]
---

You are the Success Validator — a requirements reviewer who validates measurable success criteria.

**Your core question:** "How do we know if this succeeded? What are acceptance criteria?"

**Your focus areas:**
- Measurable success criteria (quantifiable outcomes)
- Definition of done (what does "complete" mean?)
- How to test if the solution works (validation approach)
- Specific, concrete acceptance criteria (not vague goals like "fast" or "good UX")
- User outcomes vs implementation metrics

**Voice rules:**
- Active voice. Lead with impact, then evidence.
- No hedging ("might", "could", "possibly"). State findings directly.
- Cite specific sections of the design doc.
- Focus on actionable gaps, not philosophical debates.

**Review process:**
1. Read the design document thoroughly
2. Look for success criteria sections ("Goals", "Success Criteria", "Acceptance Criteria", "Definition of Done")
3. Ask: "Can we measure whether this succeeded?"
4. Ask: "Are success criteria specific? (e.g., 'p99 < 500ms' not 'fast')"
5. Ask: "How do we test this?"
6. Ask: "What does 'done' look like?"

**Output format:**

Produce JSONL findings using this structure:

```json
{
  "type": "finding",
  "id": "v1-success-validator-NNN",
  "title": "Brief finding title",
  "severity": "Critical|Important|Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Section name from design doc",
  "issue": "Description of the success criteria gap",
  "why_it_matters": "Impact if this gap isn't addressed",
  "suggestion": "Specific, actionable fix"
}
```

**Severity guidelines:**
- **Critical:** Success criteria missing, definition of done unclear (blocks validation)
- **Important:** Success criteria vague, not measurable (causes rework)
- **Minor:** Clarity improvements, documentation gaps

**Blind spot check:**

After completing your review, add a meta-finding:

```json
{
  "type": "finding",
  "id": "v1-success-validator-999",
  "title": "Blind spot check: Success Validator perspective",
  "severity": "Minor",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Meta",
  "issue": "What might I have missed by focusing on success criteria?",
  "why_it_matters": "Blind spot awareness helps catch gaps in the review process",
  "suggestion": "Consider: Did I assume success criteria from goals? Did I miss non-obvious validation needs?"
}
```

**Remember:**
- Read the design doc first, don't assume structure
- Focus on what's missing or unclear, not style nitpicks
- Actionable suggestions only
- One finding per issue
- Use exact section names from the design doc
```

**Step 2: Commit**

```bash
git add agents/success-validator.md
git commit -m "feat: add success-validator agent for requirements review"
```

---

## Task 5: Verify Assumption Hunter Agent Exists

**Files:**
- Check: `agents/assumption-hunter.md`

**Step 1: Verify agent exists**

Check if assumption-hunter agent already exists (should be reused from design review):

```bash
ls -la agents/assumption-hunter.md
```

Expected: File exists (from parallax:review)

**Step 2: If missing, create it**

If the file doesn't exist, create it. Otherwise skip to next task.

---

## Task 6: Create Requirements Skill File

**Files:**
- Create: `skills/requirements/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p skills/requirements
```

**Step 2: Write the skill file**

```markdown
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
```

**Step 3: Commit**

```bash
git add skills/requirements/SKILL.md
git commit -m "feat: add parallax:requirements skill (light mode)"
```

---

## Task 7: Validate JSONL Schema Compatibility

**Files:**
- Check: `schemas/reviewer-findings-v1.0.0.schema.json`

**Step 1: Read existing schema**

```bash
cat schemas/reviewer-findings-v1.0.0.schema.json
```

Verify it supports the fields used by requirements review personas:
- `type: "finding"`
- `id`, `title`, `severity`, `phase`, `section`, `issue`, `why_it_matters`, `suggestion`

**Step 2: Test schema validation**

Create a sample finding and validate against schema:

```bash
echo '{"type":"finding","id":"v1-test-001","title":"Test","severity":"Minor","phase":{"primary":"calibrate","contributing":null},"section":"Test","issue":"Test issue","why_it_matters":"Test impact","suggestion":"Test fix"}' | jq -s '.' > /tmp/test-finding.jsonl

# Validate (assumes validation script exists)
scripts/validate-findings.sh /tmp/test-finding.jsonl
```

Expected: Validation passes

If validation script doesn't exist, skip validation for MVP.

---

## Task 8: Create Test Script

**Files:**
- Create: `scripts/test-requirements-light.sh`

**Step 1: Write test script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Test parallax:requirements --light on past design docs

DESIGN_DOC="${1:-docs/plans/2026-02-15-parallax-review-design.md}"
TOPIC="${2:-test-requirements}"

echo "Testing parallax:requirements --light"
echo "Design doc: $DESIGN_DOC"
echo "Topic: $TOPIC"
echo ""

if [ ! -f "$DESIGN_DOC" ]; then
    echo "ERROR: Design doc not found: $DESIGN_DOC"
    exit 1
fi

echo "Design doc found. Ready for manual test."
echo ""
echo "Next steps:"
echo "1. Invoke: /requirements --light"
echo "2. Provide design doc path: $DESIGN_DOC"
echo "3. Provide topic: $TOPIC"
echo "4. Wait for reviewers to complete"
echo "5. Review findings in: docs/reviews/$TOPIC-requirements-light/"
echo ""
echo "Success criteria:"
echo "- Catches 3-5 real requirement gaps"
echo "- Takes <30 min"
echo "- Findings are actionable"
```

**Step 2: Make executable**

```bash
chmod +x scripts/test-requirements-light.sh
```

**Step 3: Commit**

```bash
git add scripts/test-requirements-light.sh
git commit -m "test: add requirements light test script"
```

---

## Task 9: Update AGENTS.md Documentation

**Files:**
- Modify: `AGENTS.md`

**Step 1: Read current AGENTS.md**

```bash
cat AGENTS.md
```

**Step 2: Add requirements review agents section**

Add after the design review agents section:

```markdown
### Requirements Review Agents

**Used by:** `parallax:requirements --light`

| Agent | Focus | Key Question |
|-------|-------|--------------|
| problem-framer | Problem statement validation | "Are we solving the right problem?" |
| scope-guardian | Scope boundaries and MVP | "What's in/out? Where's the MVP line?" |
| constraint-finder | Limits and feasibility | "What constraints exist but aren't stated?" |
| success-validator | Success criteria and acceptance | "How do we know if this succeeded?" |
| assumption-hunter | Implicit assumptions (reused) | "What has the designer assumed?" |
```

**Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add requirements review agents to AGENTS.md"
```

---

## Task 10: Manual Testing

**Not automated — requires human execution**

**Test cases:**
1. Parallax's own design doc (`docs/plans/2026-02-15-parallax-review-design.md`)
2. Requirements light design doc (`docs/plans/2026-02-16-requirements-light-design.md`)
3. Any other past design doc

**For each test case:**

1. Invoke: `/requirements --light`
2. Provide design doc path
3. Provide topic name
4. Wait for 5 reviewers to complete
5. Review findings in `docs/reviews/<topic>-requirements-light/`
6. Validate:
   - Caught 3-5 real gaps
   - Took <30 min
   - Findings are actionable

**Document results:**
- Create `docs/reviews/<topic>-requirements-light/test-notes.md`
- Record: finding count, time taken, quality assessment
- Note any issues or improvements needed

---

## Task 11: Push and Create PR

**Step 1: Push feature branch**

```bash
git push -u origin feat/requirements-light-implementation
```

**Step 2: Create PR**

```bash
gh pr create --title "feat: implement parallax:requirements --light mode" --body "$(cat <<'EOF'
## Summary

Implements parallax:requirements --light mode for post-brainstorm requirements validation.

## What's Included

**Agents (5 new):**
- problem-framer — problem statement validation
- scope-guardian — scope boundary validation
- constraint-finder — constraint identification
- success-validator — success criteria validation
- assumption-hunter — reused from design review

**Skill:**
- parallax:requirements (light mode only)
- 5 parallel reviewers
- JSONL findings output
- Markdown summary synthesis

**Testing:**
- Test script for manual validation
- Documentation in AGENTS.md

## Related

- Issue #31 (Calibrate phase systemic failure resolution)
- Design doc: docs/plans/2026-02-16-requirements-light-design.md
- Requirements review resolution: docs/plans/2026-02-16-requirements-review-resolution.md

## Testing Plan

Manual testing on 3-5 past design docs:
1. Parallax design doc (dogfooding)
2. Requirements light design doc (meta-review)
3. Other past designs

Success criteria:
- Catches 3-5 real gaps per test case
- Takes <30 min to run
- Findings are actionable

## Next Steps

After PR merge:
1. Run manual tests on past design docs
2. Validate success criteria
3. If validated: Consider deep mode
4. If not: Revise personas or defer

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Notes

**Manual workflow:**
- User invokes `/requirements --light` explicitly
- Not auto-integrated with brainstorming skill
- Prove value before integration

**Deferred to post-MVP:**
- Deep mode (post-design specification review)
- Requirements file extraction (eval whether it adds value)
- Pattern analysis tooling (manual first)
- Auto-integration with brainstorming

**Testing approach:**
- Black-box validation on past design docs
- Manual review of findings quality
- Compare to known gaps/rework that occurred

**Known limitations:**
- No run-metadata.json for MVP (just summary.md)
- No automated testing (manual validation only)
- No pattern extraction (analyze after 5-10 runs)
