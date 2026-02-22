# EARS/BDD Structured Input Experiment

**Date:** 2026-02-21
**Status:** Experiment design — ready for execution
**Related:** `sdd-research-report.md`, `2026-02-21-ecosystem-comparison-openspec-speckit.md`

---

## Hypothesis

Structuring requirements in EARS/BDD hybrid format produces higher-precision findings from parallax reviewer agents than equivalent unstructured requirements documents.

**Why this matters:** If true, investing in EARS/BDD tooling (elicitation skill, linter, OpenSpec schema) is justified by measurable review quality improvement. If false or marginal, the three-layer architecture is overhead that doesn't improve the core product.

**Null hypothesis:** Finding precision and actionability are comparable regardless of input format — the agents are limited by their prompt engineering, not by input structure.

---

## Experiment Design

### What we're actually testing

The interesting question isn't "does document format help agents?" — it's "does a review-and-refine pass on requirements improve the whole downstream pipeline?" The experiment should test the *process*, not just the *format*.

### Three-arm comparison

```
Arm A (baseline):
  Naive requirements → OpenSpec pipeline → build

Arm B (refined):
  Same naive requirements → EARS/BDD review + refinement → OpenSpec pipeline → build

Compare at every stage:
  1. What did the review/refinement step catch? (Arm B only)
  2. Did the OpenSpec output differ between arms?
  3. Did parallax reviewer findings differ in quality?
  4. Did downstream build quality differ?
```

### Variables

- **Independent variable:** Whether requirements go through EARS/BDD review/refinement before entering OpenSpec
- **Dependent variables:** Requirements gaps surfaced during refinement, OpenSpec artifact quality, parallax reviewer finding precision, downstream build quality
- **Controlled:** Same feature, same agents, same reviewer temperature, same judge configuration, same OpenSpec schema

### Method

1. Select a real feature you're planning to build (not synthetic)
2. Write naive requirements the way you naturally would — prose, bullet lists, whatever you'd put in a design doc. This is the starting point for both arms.
3. **Arm A:** Feed naive requirements directly into OpenSpec (`/openspec:proposal` → `/openspec:ff`). Run parallax design-stage agents against the generated design. Collect findings.
4. **Arm B:** Take the same naive requirements. Structure them using the EARS/BDD template below. Note every gap, ambiguity, and missing constraint the structuring process surfaces. Then feed the refined EARS/BDD requirements into OpenSpec. Run parallax design-stage agents against the generated design. Collect findings.
5. Run reverse judge on both finding sets.
6. Compare at each stage.

### What to measure at each stage

**Stage 1: Requirements refinement (Arm B only)**

This stage produces its own value signal independent of the agents:
- How many gaps did the EARS/BDD structuring process surface?
- Were these gaps real (would they have caused problems downstream)?
- How much new information was forced by the template (JTBD, anti-goals, open questions)?
- How long did refinement take? (effort cost of the process)

**Stage 2: OpenSpec artifact comparison**

- Are the OpenSpec-generated specs materially different between arms?
- Does the Arm B spec have more specific acceptance criteria?
- Does the Arm B spec have fewer ambiguous sections?

**Stage 3: Reviewer finding comparison**

| Metric | Arm A | Arm B |
|---|---|---|
| Total findings | | |
| Genuine findings (reverse judge) | | |
| Precision (genuine / total) | | |
| Severity distribution | | |
| Findings referencing specific requirement IDs | N/A | |
| "Vague concern" findings (no specific remediation) | | |

**Stage 4: Downstream build (qualitative)**

- Did the Arm B build encounter fewer surprises?
- Were there requirements misunderstandings that Arm A hit but Arm B avoided?
- Did the build diverge from spec, and if so, where?

### What "success" looks like

- **Clear signal:** The EARS/BDD refinement pass surfaces real gaps (Stage 1), OpenSpec artifacts are measurably more specific (Stage 2), AND reviewer precision improves (Stage 3). All three stages show improvement.
- **Process value, not agent value:** Refinement surfaces real gaps (Stage 1) and OpenSpec output improves (Stage 2), but reviewer precision is comparable (Stage 3). This means the format helps humans and OpenSpec, but not the review agents — still valuable, different investment case.
- **Agent value only:** Reviewer precision improves (Stage 3) but the refinement process didn't surface much (Stage 1). The format helps agents parse better, but the human effort of structuring isn't justified — consider a lighter-weight formatting pass instead.
- **No signal:** Comparable across all stages. The refinement process is overhead without measurable benefit.
- **Negative signal:** EARS/BDD structure causes agents to generate more false positives or OpenSpec produces worse output from over-specified input.

### Limitations

This is N=1. It produces directional signal, not statistical proof. Label results as "exploratory." The three-arm design partially compensates by producing signal at multiple stages — even if agent precision is inconclusive at N=1, the requirements refinement stage produces qualitative data that's useful regardless of sample size.

---

## EARS/BDD Hybrid Format: Scaffolding

### Prior art incorporated

Research into cc-sdd (Kiro-inspired SDD tools) and production EARS specs (Vibe Kanban) surfaced three patterns missing from the initial template:

1. **Unwanted behavior requirements (EARS pattern #4)** — `SHALL NOT` specifications are a distinct EARS pattern, not just a negated constraint. They give review agents explicit boundaries to probe and are particularly useful for Assumption Hunter and Edge Case Prober.
2. **Quantified constraints** — Production EARS specs enforce concrete numbers on every performance/scale/latency constraint (P95 latencies, throughput targets, batch sizes). "Fast" is not a requirement; "P95 < 500ms" is.
3. **Error scenarios as first-class requirements** — Failure modes and error handling specified alongside happy-path behavior, not deferred to implementation.

These are incorporated into the template and writing rules below.

### When to use which format

| What you're specifying | Format | Why |
|---|---|---|
| Deterministic behavior (hooks, CLI tools, linters, API contracts) | Pure EARS | Trigger → response is guaranteed; testable with assertions |
| Forbidden behavior (security boundaries, invariants) | EARS SHALL NOT | Explicit negative specification; gives reviewers boundaries to probe |
| LLM skill behavior (agent responses, review output, synthesis) | BDD Given/When/Then | Observable outcomes; acceptance-testable but not deterministic |
| Design intent and motivation | JTBD statement | Captures *why* before *what*; prevents solving the wrong problem |
| Hard constraints vs. guidance | RFC 2119 SHALL/SHOULD/MAY | Distinguishes non-negotiable from preferred from optional |
| Error and failure behavior | EARS WHEN [failure] or BDD GIVEN [error state] | Failure modes as requirements, not afterthoughts |

### The category error to avoid

> **"THE skill SHALL respond with X"** is a category error for LLM-based components.

EARS `SHALL` implies a guarantee. LLMs don't guarantee. Forcing probabilistic behavior into EARS syntax produces either:
- Vague requirements that defeat EARS's purpose ("THE skill SHALL provide helpful output")
- False precision that can't be tested ("THE skill SHALL include exactly 3 findings")

**Rule:** Use EARS for the deterministic parts of your system. Use BDD for the parts where you're specifying *observable outcomes* of probabilistic behavior. Use SHALL/SHOULD/MAY for constraint tiers on anything.

### Document template

```markdown
# [Feature Name] — Requirements

## Overview

**Job:** [JTBD statement — who is hiring this feature, to do what job,
so that what outcome?]

**Scope:** [One paragraph — what's in, what's explicitly out]

**Anti-goals:** [Bullet list — things this feature deliberately does NOT do]

---

## Functional Requirements

### REQ-001 — [Requirement title]

**EARS (deterministic behavior):**
[Use for hooks, tools, CLI, API contracts, infrastructure]

WHEN [trigger condition]
IF [guard condition, optional]
THE [component] SHALL [guaranteed behavior]

**BDD (observable skill behavior):**
[Use for LLM skills, agents, review output, synthesis]

GIVEN [precondition / context]
WHEN [action or trigger]
THEN [observable outcome]
AND [additional observable outcome, optional]

**Constraints:**
- SHALL: [Non-negotiable — system is broken without this]
- SHOULD: [Expected — deviation requires justification]
- MAY: [Optional — nice to have, defer if costly]

**Boundaries (what this component SHALL NOT do):**
[Use for security invariants, forbidden behaviors, scope fences]

WHEN [trigger condition]
THE [component] SHALL NOT [forbidden behavior]

**Error handling:**
[How does this requirement behave when things go wrong?]

WHEN [failure condition — e.g., upstream timeout, invalid input, missing dependency]
THE [component] SHALL [error behavior — e.g., return error code, retry with backoff, log and skip]

**BDD error scenario:**
GIVEN [error precondition — e.g., upstream service unavailable]
WHEN [the action is attempted]
THEN [observable error outcome — e.g., user sees error message within 2s]
AND [system state after error — e.g., no partial writes, queue entry preserved]

### REQ-002 — [Next requirement]
[Same structure. One requirement per section. Number sequentially.]

---

## Non-Functional Requirements

### NFR-001 — [Title]

- SHALL: [Hard constraint with concrete number — e.g., "P95 response time < 500ms"]
- SHOULD: [Target with concrete number — e.g., "log latency at INFO when > 200ms"]
- MAY: [Aspiration — e.g., "support batch mode for > 100 items"]

**Quantification rule:** Every performance, latency, throughput, or scale
constraint MUST include a concrete number. "Fast" is not a requirement.
"P95 < 500ms under 100 concurrent requests" is.

---

## Acceptance Criteria

[BDD scenarios that validate the feature works end-to-end.
These are integration-level, not per-requirement.]

**Happy path:**
GIVEN [system state]
WHEN [user action or trigger sequence]
THEN [end-to-end observable outcome]

**Error path:**
GIVEN [system state with failure condition]
WHEN [user action or trigger sequence]
THEN [graceful degradation outcome]
AND [no data loss / corruption]

---

## Open Questions

[Unresolved decisions. Each should state:
what the question is, what the options are, what's blocking resolution.]
```

### Writing rules

**Structure rules:**
1. Every requirement gets a unique ID (REQ-001, NFR-001)
2. One requirement per section — don't bundle multiple behaviors
3. EARS blocks use WHEN/IF/SHALL keywords in caps (parser convention)
4. BDD blocks use GIVEN/WHEN/THEN/AND keywords in caps
5. Every requirement has a constraints block with at least one SHALL

**Content rules:**
6. EARS blocks describe *deterministic trigger → response* only. If you can't write a pass/fail assertion, it's not EARS — use BDD
7. BDD blocks describe *observable outcomes*, not implementation. "THEN an alert exists in the event store" not "THEN the function calls createAlert()"
8. JTBD statement comes first — if you can't articulate the job, the requirements aren't ready
9. Anti-goals are mandatory. Stating what you won't do prevents scope creep and gives reviewers a boundary to check against
10. SHALL means the system is broken without it. If removing the requirement degrades but doesn't break the system, it's SHOULD

**Completeness rules:**
11. Every functional requirement needs at least one of: EARS block or BDD block (not both required — use whichever fits)
12. Every functional requirement needs a constraints block
13. Non-functional requirements use SHALL/SHOULD/MAY only (no EARS/BDD — these are properties, not behaviors)
14. Open questions section is mandatory even if empty — forces explicit acknowledgment of unknowns
15. Every requirement with a happy-path behavior SHOULD have an error-handling block — what happens when the trigger fails, the dependency is unavailable, or the input is invalid?
16. Every NFR constraint involving performance, latency, throughput, or scale MUST include a concrete number. No vague qualifiers ("fast", "scalable", "responsive")
17. Use SHALL NOT for security boundaries, invariants, and scope fences. These are distinct from constraints — they're explicit negative specifications that give reviewers boundaries to probe

### Anti-patterns

| Anti-pattern | Example | Fix |
|---|---|---|
| SHALL for probabilistic behavior | "THE skill SHALL generate 3-5 findings" | BDD: "THEN findings are generated" + SHOULD: "typically 3-5 findings" |
| Vague EARS | "WHEN the user requests help THE system SHALL help" | Either make it specific ("SHALL display help text") or use BDD |
| Implementation in BDD | "THEN the function calls the API" | Describe the outcome: "THEN the data is available in the store" |
| Missing JTBD | Jump straight to REQ-001 | Write the job statement first — it's the "why" |
| Bundled requirements | REQ-001 covers auth, logging, and error handling | Split into REQ-001 (auth), REQ-002 (logging), REQ-003 (error handling) |
| No anti-goals | Feature scope is implied but not stated | Write explicit anti-goals — what you won't do |
| SHALL/SHOULD confusion | "The system SHOULD authenticate users" | If auth is required, it's SHALL. SHOULD means degraded-but-functional without it |
| Missing open questions | No open questions section | Always include — even "None identified" forces the acknowledgment |
| Vague NFR | "The system SHALL be fast" | Quantify: "P95 response time SHALL be < 500ms under 100 concurrent requests" |
| Happy-path only | REQ-001 specifies success, no error handling | Add error block: WHEN [failure] THE [component] SHALL [error behavior] |
| Missing SHALL NOT | Security boundary implied but not stated | Explicit: "THE component SHALL NOT expose credentials in logs" |
| Negative as constraint | Constraints: "SHALL: must not leak data" | Use SHALL NOT block — it's a distinct requirement type, not a constraint modifier |

---

## Project Selection Criteria

The experiment project should be:

- **Real** — something you'd build anyway, not a synthetic exercise. Synthetic examples produce synthetic findings; the experiment needs realistic ambiguity and real gaps to find.
- **Skill-sized** — small enough that one requirements pass is feasible in a single session. A full service design is too much scope for N=1.
- **Mixed deterministic/probabilistic** — includes both hook/tool behavior (EARS-appropriate) and skill/agent behavior (BDD-appropriate). This exercises the hybrid model, not just one format.
- **Has natural gaps** — you know there are open questions or unstated assumptions. Perfect requirements produce no findings; the agents need something to find.

Good candidates: a Claude Code skill, a CLI hook, an MCP tool integration — anything with both a deterministic interface and LLM-driven behavior.

---

## Execution Steps

### Step 1: Select project, write naive requirements

Pick a real feature. Write requirements the way you naturally would — prose, bullet lists, whatever you'd put in a CLAUDE.md or design doc. Don't artificially make it worse; write it the way you'd actually write it.

Save as `docs/experiments/ears-bdd/naive-requirements.md`.

### Step 2: Arm A — Naive requirements → OpenSpec

Feed the naive requirements directly into OpenSpec:
```
/openspec:proposal [paste naive requirements]
/openspec:ff
```

Save the generated OpenSpec design artifact as `docs/experiments/ears-bdd/arm-a-openspec-design.md`.

### Step 3: Arm A — Run design-stage agents

Run all 6 design-stage agents (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout) against the Arm A OpenSpec design.

Save findings as `docs/experiments/ears-bdd/arm-a-findings.jsonl`.

### Step 4: Arm B — EARS/BDD refinement pass

Take the same naive requirements. Structure them using the EARS/BDD template above.

**Track the refinement delta:**
- List every gap, ambiguity, and missing constraint the structuring process surfaces
- Note which information is *new* (forced by the template) vs. *restructured* (already present)
- Record the effort involved (rough time, number of iterations)

Save as:
- `docs/experiments/ears-bdd/arm-b-refined-requirements.md` (the EARS/BDD document)
- `docs/experiments/ears-bdd/arm-b-refinement-delta.md` (what the process surfaced)

### Step 5: Arm B — Refined requirements → OpenSpec

Feed the EARS/BDD-structured requirements into OpenSpec:
```
/openspec:proposal [paste refined requirements]
/openspec:ff
```

Save as `docs/experiments/ears-bdd/arm-b-openspec-design.md`.

### Step 6: Arm B — Run design-stage agents

Same agents, same configuration, against the Arm B OpenSpec design.

Save findings as `docs/experiments/ears-bdd/arm-b-findings.jsonl`.

### Step 7: Run reverse judge on both finding sets

Use the existing eval framework's reverse judge (Haiku, T=0.0) to score each finding as GENUINE or NOT_GENUINE against its respective OpenSpec design document.

### Step 8: Compare at every stage

**Stage 1 — Refinement value (Arm B only):**
- Gaps surfaced by EARS/BDD structuring: [count and list]
- Were these real gaps or template noise?
- New information forced by template: [list]

**Stage 2 — OpenSpec artifact diff:**
- `diff arm-a-openspec-design.md arm-b-openspec-design.md`
- Material differences: [list]
- More specific acceptance criteria in Arm B? [yes/no + examples]

**Stage 3 — Reviewer findings:**

| Metric | Arm A | Arm B |
|---|---|---|
| Total findings | | |
| Genuine findings | | |
| Precision (genuine / total) | | |
| Severity distribution (Crit / Imp / Min) | | |
| Findings referencing requirement IDs | N/A | |
| Vague concern findings | | |

**Stage 4 — Qualitative (if you proceed to build):**
- Requirements misunderstandings hit during build
- Scope surprises
- Spec-to-build divergence

### Step 9: Decision

| Result | Action |
|---|---|
| All three stages show improvement | Design larger experiment (N>=10). Invest in EARS/BDD tooling. |
| Process value only (Stage 1-2 improve, Stage 3 comparable) | Adopt EARS/BDD as a human practice. Skip agent-specific tooling. |
| Agent value only (Stage 3 improves, Stage 1-2 marginal) | Investigate lighter formatting pass — maybe just section structure, not full EARS/BDD. |
| No signal across stages | Defer EARS/BDD investment. Focus on agent prompt improvement. |
| Negative signal | Investigate root cause before abandoning — is it the format or the OpenSpec integration? |

---

## Cautions

**Separate the variables.** This experiment tests whether structured input improves design-stage review quality. It does NOT test whether the requirements-stage agents are useful as EARS/BDD validators — that's a different experiment, only worth running if this one shows positive signal.

**Don't refactor parallax first.** The agents consume raw markdown. An EARS/BDD document is raw markdown. No pipeline changes needed for this experiment. If the experiment succeeds, *then* consider tooling.

**Watch for confirmation bias.** You're invested in the three-layer architecture. Pre-commit to what "not worth pursuing" looks like (the decision table above) so you have an exit ramp.

**N=1 produces direction, not proof.** Label results as "exploratory." Don't make ADR decisions from a single comparison.

**The template is the minimal scaffolding.** Don't build an elicitation skill, an EARS linter, or an OpenSpec schema customization before running this experiment. The template and writing rules above are enough to produce a properly structured document by hand.
