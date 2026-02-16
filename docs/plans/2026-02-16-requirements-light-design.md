# parallax:requirements --light Design

**Date:** 2026-02-16
**Status:** Approved
**Related:** Issue #31, requirements-review-resolution.md

---

## Overview

A lightweight requirements review skill that catches requirement gaps after brainstorming, before heavy design investment. Part of the two-checkpoint requirements review model (light + deep modes).

**This design covers --light mode only.** Deep mode deferred until light mode proves valuable.

---

## Goals

**Purpose:** Quick post-brainstorm checkpoint that validates problem framing, scope, and constraints.

**What --light does:**
- Reads design doc from brainstorming
- Runs 5 reviewer personas against it
- Finds requirement gaps: unclear scope, missing constraints, undefined success criteria
- Outputs JSONL findings for user to address

**What --light does NOT do:**
- Generate requirements (brainstorming does that)
- Refine requirements (user does that based on findings)
- Replace design review (that's `parallax:review`)
- Create requirements files (eval later whether it adds value)

**Success criteria:**
- Catches 3-5 real requirement gaps that would cause rework if missed
- Takes <30 min to run
- Findings are actionable, not philosophical debates
- Users naturally remember to invoke after brainstorming (workflow fit)

---

## Workflow Integration

**Manual workflow (MVP):**
```
1. User invokes brainstorming skill
2. Brainstorming writes design doc to docs/plans/YYYY-MM-DD-<topic>-design.md
3. User manually invokes: /requirements --light
4. --light reads design doc, runs 5 personas
5. Outputs findings to docs/reviews/<topic>-requirements-light/
6. User addresses findings (refines design doc)
7. [Later] Design review with parallax:review
```

**Input artifact:** `docs/plans/YYYY-MM-DD-<topic>-design.md` (pure brainstorming output)
**Output artifacts:**
- `docs/reviews/<topic>-requirements-light/findings-v1-<persona>.jsonl` (per-persona findings)
- `docs/reviews/<topic>-requirements-light/summary.md` (human-readable synthesis)

**No auto-integration yet.** Prove value manually before modifying upstream brainstorming skill.

---

## Reviewer Personas

**5 personas** review the design doc for requirement gaps:

### 1. Problem Framer
**Focus:** "Are we solving the right problem? Is this root cause or symptom?"

**Looks for:**
- Problem statement clarity and completeness
- Root cause vs symptom framing
- Why this problem matters (impact/value)
- Whether the problem is well-scoped

**Blind spot check:** "What assumptions am I making about problem understanding?"

---

### 2. Scope Guardian
**Focus:** "Is scope clear? What's in/out? Where's the MVP boundary?"

**Looks for:**
- Explicit scope boundaries (what's included)
- What's explicitly out of scope
- MVP vs future work distinction
- Scope creep risks

**Blind spot check:** "What scope ambiguities might I have missed?"

---

### 3. Constraint Finder
**Focus:** "What limits exist? Time, budget, technical, regulatory?"

**Looks for:**
- Documented constraints (time, budget, technical, regulatory)
- Unstated limitations that could block implementation
- Feasibility concerns
- Resource availability

**Blind spot check:** "What constraints might not be obvious from the design doc?"

---

### 4. Assumption Hunter
**Focus:** "What unstated assumptions exist? What constraints are missing?"

**Looks for:**
- Implicit assumptions (things taken for granted)
- Missing context that implementers would need
- Assumptions about user behavior, system capabilities, environment
- Dependencies on external systems or decisions

**Blind spot check:** "What am I assuming is 'obvious' that isn't stated?"

---

### 5. Success Validator
**Focus:** "How do we know if this succeeded? What are acceptance criteria?"

**Looks for:**
- Measurable success criteria
- Definition of done
- How to test if the solution works
- Specific, concrete acceptance criteria (not vague goals)

**Blind spot check:** "What success dimensions might I have overlooked?"

---

## Output Format

### JSONL Findings

Reuses existing `reviewer-findings-v1.0.0.schema.json`:

```json
{
  "type": "finding",
  "id": "v1-problem-framer-001",
  "title": "Success criteria undefined",
  "severity": "Critical",
  "phase": {
    "primary": "calibrate",
    "contributing": null
  },
  "section": "Goals",
  "issue": "Problem statement defines what to build but not how to measure success",
  "why_it_matters": "Without success metrics, can't validate if solution works",
  "suggestion": "Add 3-5 concrete acceptance criteria with measurable outcomes"
}
```

**Phase classification:**
- `primary`: Always `"calibrate"` (requirements stage)
- `contributing`: `"survey"` if research gap caused it, `null` otherwise

**Severity levels:**
- `Critical`: Blocks implementation (e.g., scope undefined, success criteria missing)
- `Important`: Causes rework if not addressed (e.g., unstated assumptions, vague constraints)
- `Minor`: Polish issues (e.g., clarity improvements, documentation gaps)

### Output Location

```
docs/reviews/<topic>-requirements-light/
├── findings-v1-problem-framer.jsonl
├── findings-v1-scope-guardian.jsonl
├── findings-v1-constraint-finder.jsonl
├── findings-v1-assumption-hunter.jsonl
├── findings-v1-success-validator.jsonl
└── summary.md
```

**Separate folder** prevents collision with design review outputs (`<topic>-review-v1/`).

### Summary Output

Human-readable markdown summary (similar to existing review summaries):
- Finding counts by severity
- Key themes across personas
- Actionable next steps

---

## MVP Scope

### Build First

1. **Light mode only** - validate checkpoint-after-brainstorm workflow
2. **5 personas** - Problem Framer, Scope Guardian, Constraint Finder, Assumption Hunter, Success Validator
3. **Manual workflow** - document when to invoke, not auto-integrated
4. **JSONL output** - reuse existing schema and synthesis logic
5. **Design doc input** - no requirements file creation (eval later whether it adds value)

### Test Cases

**Test on 3-5 past brainstorms:**
- Parallax v1/v2 problem statements
- Parallax's own design doc (dogfooding)
- claude-ai-customize brainstorm (if accessible)
- Other openclaw design sessions (if accessible)

**Validation approach:**
- Run --light on each test case
- Manually review findings: Are they real gaps? Would they have caused rework?
- Measure: finding count, severity distribution, time to run
- User feedback: Are findings actionable? Is workflow natural?

### Success Criteria for MVP Validation

**Quality:**
- Catches 3-5 real requirement gaps per test case that would have caused rework

**Performance:**
- Takes <30 min to run (including synthesis)

**Actionability:**
- Findings are specific and actionable (not philosophical debates)
- Suggestions are concrete (not "think more about X")

**Workflow fit:**
- Users naturally remember to invoke after brainstorming
- Feels like a natural checkpoint, not forced process

### Defer to Post-MVP

- **Deep mode** - build after light mode proves valuable
- **Auto-integration** - modify brainstorming skill to auto-invoke --light
- **Requirements file extraction** - eval whether extracting requirements into separate file adds value
- **Pattern analysis tooling** - manual analysis first, automate if patterns emerge
- **Learning loop** - analyze findings across runs to improve personas

---

## Design Decisions

### Why design doc input instead of requirements file?

**Decision:** Use design doc directly as input. Don't force requirements file creation.

**Rationale:**
- Not all projects need formal requirements docs
- For simple projects, design doc might be sufficient
- Requirements file extraction is extra step that might not add value
- YAGNI: don't build until we know it's needed

**Evaluation plan:**
- After 5-10 runs, evaluate: "Does extracting requirements into separate file improve review quality?"
- Test on simple vs complex projects
- Measure: finding quality, review time, user preference
- If evals show value, add `--extract` flag or separate mode

### Why 5 personas instead of 6 (like design review)?

**Decision:** 5 personas for light mode (Problem Framer, Scope Guardian, Constraint Finder, Assumption Hunter, Success Validator).

**Rationale:**
- Design review has 6 personas because it reviews detailed designs
- Requirements review needs different focus: problem framing, scope, constraints
- 5 personas cover the key requirement gaps at brainstorm stage
- Keeps review time <30 min

**Note:** Deep mode (post-design) will have different personas focused on specification completeness.

### Why manual workflow instead of auto-integration?

**Decision:** Manual invocation for MVP. User explicitly calls `/requirements --light`.

**Rationale:**
- Prove value before modifying upstream brainstorming skill (from superpowers plugin)
- Let users build muscle memory for when to invoke
- Avoid forcing process on projects that don't need it
- Easier to test and validate workflow fit

**Future:** If MVP validates value, consider auto-integration or prompt in brainstorming.

---

## Implementation Notes

### Skill Structure

```
parallax/
└── skills/
    └── requirements/
        └── SKILL.md
```

**Skill invocation:**
- `/requirements --light` (light mode, MVP)
- `/requirements --deep` (deep mode, post-MVP)
- `/requirements` (defaults to --light)

### Reusable Components

**From parallax:review:**
- JSONL schema (`reviewer-findings-v1.0.0.schema.json`)
- Synthesis logic (if we build a synthesizer)
- Output directory structure pattern

**From existing reviews:**
- Persona prompt patterns
- Blind spot check pattern
- Summary markdown format

### Testing Strategy

**Black-box validation:**
1. Run --light on 3-5 past brainstorming outputs
2. Manually review findings: real gaps vs false positives
3. Compare to actual rework that happened (ground truth)
4. Measure precision: % of findings that are real gaps
5. Measure recall: % of known gaps that were caught

**Success threshold:**
- Precision >70% (most findings are real gaps)
- Recall >60% (catches most gaps)
- <5 false positives per run

---

## Next Steps

1. **Write implementation plan** (invoke writing-plans skill)
2. **Implement --light mode** - 5 personas, JSONL output, manual workflow
3. **Test on past brainstorms** - 3-5 test cases
4. **Validate success criteria** - catches 3-5 real gaps, <30 min, actionable findings
5. **If validated:** Consider deep mode
6. **If not validated:** Revise personas or defer (requirements review may not be as high-leverage as hypothesized)

**Related work:**
- Issue #31: Calibrate phase systemic failure (resolved by this design)
- Issue #22: Prior art evaluation (Inspect AI, LangGraph) - 8-10 hour spike
- Issue #14: Parallax self-test validation

---

## Appendix: Example Finding

**Input:** Design doc with "Goals: Build a fast search feature"

**Problem Framer finding:**
```json
{
  "type": "finding",
  "id": "v1-problem-framer-001",
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

This finding is:
- **Actionable:** Specific suggestion for what to add
- **High-value:** Prevents architecture mismatch (would cause rework)
- **Scoped:** Focused on one missing requirement, not a philosophical debate
