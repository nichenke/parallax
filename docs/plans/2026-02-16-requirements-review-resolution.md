# Requirements Review Resolution — Two-Checkpoint Requirements Review

**Date:** 2026-02-16
**Status:** Approved
**Related:** Issue #31 (Calibrate Phase Systemic Failure), ADR-003

---

## Problem Statement

Pattern extraction from 87 v3 findings revealed calibrate phase systemic failure (32.2% of findings trace to requirements/planning gaps). Pattern p8 "Problem Framing & Priority Inversion" identified that requirements doc states requirement refinement is the highest leverage intervention, but prototype builds design review first and defers requirements review.

Initial framing assumed this was a priority inversion requiring a flip in build order. Requirements review session revealed the actual workflow reality.

---

## Workflow Insight

**Initial assumption:** Requirements come before design, so requirements review should be built first.

**Actual workflow:**
```
brainstorm → initial design → requirements crystallize → requirements review → design refinement
```

**Key insight:** Requirements aren't known up-front; they **emerge through design exploration**. People don't know what they want until there's design to challenge and think about. Up-front requirements generation is tricky without design context.

**Resolution:** Requirements review isn't deferred—it happens at **two checkpoints** where requirements can actually be evaluated:

1. **After brainstorming** (light check): Problem statement, scope, constraints clear?
2. **After design** (deep review): Specifications complete, acceptance criteria defined?

This matches real workflow and resolves the "priority inversion" concern.

---

## Design: parallax:requirements

### Scope & Goals

Two-checkpoint requirements review skill:
- **Light mode** (post-brainstorm): Quick check on problem statement, scope, constraints — "Are we solving the right problem?"
- **Deep mode** (post-design): Thorough review of specifications — "Did we define everything needed for implementation?"

**Not:**
- Generating requirements (brainstorming does that)
- Refining requirements (user does that based on findings)
- Replacing design review (that's still `parallax:review`)

**Success criteria:**
- Catches 3-5 real requirement gaps that would cause rework if missed
- Takes <30 min for light mode
- Findings are actionable, not philosophical debates

---

### Architecture & Workflow Integration

**Manual workflow** (MVP):
```
1. User invokes brainstorming (or auto-triggered)
2. Brainstorming explores idea (questions, approaches)
3. User manually invokes: /requirements --light
4. Present requirements findings
5. User addresses findings (adds constraints, clarifies scope)
6. Brainstorming continues to design phase
7. Brainstorming writes design doc
8. [Later] User invokes: /requirements --deep on design doc
9. User refines specifications based on findings
10. Then: /review for design review
```

**Future integration:** TBD. Options include parallax orchestrator wrapper or modifying brainstorming skill once value is proven. Not modifying upstream superpowers plugin yet.

---

### Reviewer Personas

**Light mode** (5 personas, 15-30 min):
Reviews problem statement, scope, and constraints

1. **Problem Framer** — "Are we solving the right problem? Is this root cause or symptom?"
2. **Scope Guardian** — "Is scope clear? What's in/out? Where's the MVP boundary?"
3. **Constraint Finder** — "What limits exist? Time, budget, technical, regulatory?"
4. **Assumption Hunter** — "What unstated assumptions exist? What constraints are missing?"
5. **Success Validator** — "How do we know if this succeeded? What are acceptance criteria?"

**Deep mode** (5 personas, 30-60 min):
Reviews design doc for specification gaps

1. **Requirement Auditor** — "Are all requirements specified? What's vague or undefined?"
2. **Acceptance Validator** — "Can we test this? Are success criteria measurable?"
3. **Edge Case Finder** — "What happens when X? Are failure modes defined?"
4. **Assumption Hunter** (reused) — "What new assumptions did the design introduce?"
5. **First Principles** — "Does this design actually solve the stated requirements? Any gaps?"

**Reuse from parallax:review:**
- Assumption Hunter appears in both modes (tracks assumptions through workflow)
- Requirement Auditor already exists in design review (promoted to requirements)
- First Principles reused for requirements-to-design alignment check

---

### Output Format

**JSONL findings structure** (reuses `reviewer-findings-v1.0.0.schema.json`):

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
- **primary phase**: Always `"calibrate"` (requirements stage)
- **contributing phase**: `"survey"` if research gap caused it, `null` otherwise

**Output location:**
- Light mode: `docs/reviews/<topic>-requirements-light/findings-v1-*.jsonl`
- Deep mode: `docs/reviews/<topic>-requirements-deep/findings-v1-*.jsonl`
- Separate folders prevent collision with design review outputs

**Blind spot checks:**
Each reviewer includes: "What might I have missed by focusing on X?"

**Learning loop:**
After 3-5 deep mode runs, analyze findings for patterns:
- Question: "What do we consistently miss in light mode / brainstorming?"
- Use patterns to:
  - Improve light mode personas (add prompts for common gaps)
  - Feed back to brainstorming skill (update question templates)
  - Create requirement checklists for common domains (API design, UI features, data pipelines)

This makes `parallax:requirements` self-improving based on actual usage patterns.

---

### MVP Scope

**Build first:**
1. **Light mode only** — validate checkpoint-after-brainstorm workflow catches real issues
2. **5 personas** — Problem Framer, Scope Guardian, Constraint Finder, Assumption Hunter, Success Validator
3. **Manual workflow** — document when to invoke, not auto-integrated
4. **JSONL output** — reuse existing schema and synthesis logic
5. **Test on 3-5 past brainstorms** — validate before building deep mode

**Defer to post-MVP:**
- Deep mode (build after light mode proves valuable)
- Auto-integration with brainstorming skill
- Pattern analysis tooling (manual analysis first)
- Orchestrator wrapper (`parallax:orchestrate`)

**Success criteria for MVP validation:**
- Catches 3-5 real requirement gaps in test cases that would have caused rework
- Takes <30 min to run
- Findings are actionable (not philosophical debates)
- Users naturally remember to invoke after brainstorming (workflow fit)

---

## Resolution of Calibrate Phase Systemic Failure

**Issue #31 concerns:**
1. ✅ Architectural specifications undefined — **Resolved in ADR-003** (specs documented or explicitly deferred)
2. ✅ Problem framing inversion — **Resolved in this design** (two-checkpoint model matches real workflow)
3. ⏳ Prior art evaluation deferred — **Tracked in Issue #22** (separate spike work)
4. ✅ Model tiering unspecified — **Resolved in ADR-003** (Sonnet baseline, eval-driven optimization)
5. ⏳ Second Brain test case not run — **Deferred to parallax self-test** (Issue #14 approach changed based on test case evaluation)

**Calibrate phase gaps addressed:**
- Requirements review now has **two checkpoints** (light + deep)
- Not a priority inversion—requirements emerge through design, so checkpoints fit natural workflow
- MVP validates light mode first (highest ROI: catch issues before heavy design investment)
- Deep mode built once light mode proves value

**Systemic threshold (32.2%):**
- Many findings were about **deferred architectural specs** (resolved in ADR-003)
- Remaining findings about **requirements review missing** (resolved in this design)
- Post-resolution, expect calibrate phase percentage to drop below 30% threshold in future reviews

---

## Next Steps

1. **Implement parallax:requirements light mode** — 5 personas, manual workflow
2. **Test on 3-5 past brainstorms** — openclaw sessions, parallax v1/v2 problem statements, claude-ai-customize brainstorm
3. **Validate success criteria** — catches 3-5 real gaps, <30 min, actionable findings
4. **If validated:** Build deep mode
5. **If not validated:** Revise personas or defer entirely (requirements review may not be as high-leverage as hypothesized)

**Related work:**
- Issue #22: Prior art evaluation (Inspect AI, LangGraph) — 8-10 hour spike
- Issue #14: Parallax self-test validation (using parallax design doc as test case)
- ADR-003: Architectural specification status (scope reductions documented)

---

## Decision

**Approved:** Two-checkpoint requirements review model with `parallax:requirements` skill

**Rationale:** Matches real workflow (requirements emerge through design), resolves "priority inversion" concern without requiring build-order flip, provides two natural checkpoints where requirements can actually be evaluated.

**MVP:** Light mode only, 5 personas, manual workflow, test on past sessions before building deep mode.
