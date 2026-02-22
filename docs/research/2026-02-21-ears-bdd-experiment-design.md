# PEARS Experiment: Does Review Add Value on Top of Structured Requirements?

**Date:** 2026-02-21
**Status:** Experiment design — ready for execution
**Related:** `sdd-research-report.md`, `2026-02-21-ecosystem-comparison-openspec-speckit.md`

---

## PEARS: Parallax EARS

**PEARS** (Parallax EARS) is a hybrid requirements format for systems with both deterministic and probabilistic behavior. It combines EARS syntax for deterministic components, BDD Given/When/Then for LLM skill behavior, JTBD for intent, and RFC 2119 SHALL/SHOULD/MAY for constraint tiers.

The name distinguishes it from pure EARS (deterministic only), pure BDD (no trigger syntax), Kiro's format (IDE-locked), and cc-sdd's templates (no probabilistic/deterministic distinction).

---

## Hypothesis

Parallax adversarial review adds measurable value on top of PEARS-structured requirements fed through OpenSpec.

**Why this matters:** If well-structured requirements already capture most gaps, the review gate may not justify its cost. If the review gate catches real issues that good structure misses, parallax's core value proposition is validated in a realistic workflow.

**Null hypothesis:** PEARS-structured requirements + OpenSpec produce designs that parallax reviewers cannot meaningfully improve — the structure is sufficient, the review is redundant.

---

## Experiment Design

### What we're actually testing

The starting artifact is a real requirements document that already has JTBD, MoSCoW, assumptions, and pre-mortem analysis — it's not "naive." The experiment tests whether **parallax review catches things that good requirements + OpenSpec miss**, not whether structure beats no-structure.

This is closer to the production question: in the three-layer architecture, you'd always have structured requirements. The variable is whether the review gate adds value.

### Two-arm comparison

```
Arm A (no review):
  PEARS requirements → OpenSpec pipeline → build

Arm B (with review):
  Same PEARS requirements → OpenSpec pipeline → parallax review → address findings → build

Compare:
  1. Did parallax review surface genuine findings the structure missed?
  2. Did addressing findings change the OpenSpec design?
  3. Did downstream build quality differ?
```

### Variables

- **Independent variable:** Whether OpenSpec-generated design goes through parallax adversarial review before build
- **Dependent variables:** Findings surfaced by review (genuine vs. false positive), design changes prompted by review, downstream build quality
- **Controlled:** Same PEARS requirements, same OpenSpec schema, same agents, same reviewer temperature, same judge configuration

### Method

1. Take existing requirements document. Restructure into PEARS format using the template and writing rules below. Track the refinement delta — what gaps the structuring process surfaces.
2. **Arm A:** Feed PEARS requirements into OpenSpec (`/openspec:proposal` → `/openspec:ff`). Proceed directly to build.
3. **Arm B:** Feed the same PEARS requirements into OpenSpec. Run parallax design-stage agents against the generated design. Evaluate findings. Address genuine findings (update requirements or design). Then build.
4. Run reverse judge on Arm B findings.
5. Compare at each stage.

### What to measure

**Stage 0: PEARS structuring (both arms, before split)**

The reformatting pass itself produces signal:
- How many gaps did PEARS structuring surface vs. the original requirements?
- Were these real gaps (would they have caused problems downstream)?
- What new information was forced by the template (SHALL NOT boundaries, error scenarios, quantified NFRs)?
- How much effort did the restructuring take?

This stage is shared — both arms benefit from PEARS structure. It's not part of the A/B comparison, but it's valuable data about the format itself.

**Stage 1: Parallax review value (Arm B only)**

| Metric | Value |
|---|---|
| Total findings | |
| Genuine findings (reverse judge) | |
| Not genuine findings | |
| Precision (genuine / total) | |
| Severity distribution (Critical / Important / Minor) | |
| Findings referencing specific requirement IDs | |
| "Vague concern" findings (no specific remediation) | |
| Findings that prompted design changes | |

Key question: did the agents find real issues that the PEARS structure didn't already surface?

**Stage 2: Design impact**

- Did Arm B findings change the OpenSpec design? How many changes, how significant?
- Were changes to requirements (upstream) or design (downstream)?
- `diff arm-a-design.md arm-b-design.md` after findings addressed

**Stage 3: Downstream build (qualitative)**

- Did Arm A build encounter surprises that Arm B avoided?
- Requirements misunderstandings in Arm A that Arm B caught in review?
- Spec-to-build divergence in each arm?

### What "success" looks like

- **Clear signal:** Parallax review surfaces genuine findings (>50% precision) that PEARS structure missed, findings prompt meaningful design changes, Arm B build has fewer surprises.
- **Marginal signal:** Some genuine findings, but most are things the PEARS structure already implied — reviewers are restating what the format made obvious. Review adds confidence, not information.
- **No signal:** Findings are mostly false positives or vague concerns. PEARS structure was sufficient; review added overhead without value.
- **Negative signal:** Review findings prompt changes that make the design worse, or review overhead delays the build without improving it.

### Limitations

This is N=1. It produces directional signal, not statistical proof. Label results as "exploratory." The two-arm design compensates partially by producing qualitative signal during the build phase — even if finding precision is inconclusive at N=1, the build-phase comparison reveals whether review prevented real problems.

---

## PEARS Format: Scaffolding

### Prior art incorporated

Research into cc-sdd (Kiro-inspired SDD tools) and production EARS specs surfaced three patterns added to the base EARS/BDD hybrid:

1. **Unwanted behavior requirements (EARS pattern #4)** — `SHALL NOT` specifications are a distinct EARS pattern, not just a negated constraint. They give review agents explicit boundaries to probe.
2. **Quantified constraints** — Concrete numbers mandatory on every performance/scale/latency constraint. "Fast" is not a requirement; "P95 < 500ms" is.
3. **Error scenarios as first-class requirements** — Failure modes specified alongside happy-path behavior, not deferred to implementation.

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
# [Feature Name] — PEARS Requirements

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

## Execution Steps

### Step 1: Generate PEARS requirements from existing requirements

Use the PEARS skill to guide AI-assisted restructuring of the existing requirements document into PEARS format. The skill includes:

1. **Pre-generation analysis phase** — before filling the template, enumerate system components, user interactions, state transitions, and failure modes (adapted from cc-sdd's structured decomposition)
2. **Template + writing rules + anti-patterns** — the format scaffolding defined in this doc
3. **Pattern completeness sweep** — after initial generation, walk through each PEARS category (EARS deterministic, BDD probabilistic, SHALL NOT boundaries, error handling, NFRs) and confirm whether it applies; surface any skipped categories

Both arms use the same skill with all three phases. The analysis phase and completeness sweep are not experimental variables — they're baseline generation quality. Testing a deliberately weakened PEARS skill against parallax review would conflate "bad generation" with "review adds value."

**Track the restructuring delta:**
- List every gap, ambiguity, and missing constraint the PEARS structuring surfaces
- Note which information is *new* (forced by the template — SHALL NOT boundaries, error scenarios, quantified NFRs, anti-goals) vs. *restructured* (already present, reformatted)
- Record effort involved

Save as:
- `pears-requirements.md` (the PEARS document)
- `pears-restructuring-delta.md` (what the process surfaced)

### Step 2: Arm A — PEARS requirements → OpenSpec → build (no review)

Feed PEARS requirements into OpenSpec:
```
/openspec:proposal [paste PEARS requirements]
/openspec:ff
```

Proceed directly to build from the generated design. Do not run parallax review.

Save the OpenSpec design artifact for later comparison.

### Step 3: Arm B — PEARS requirements → OpenSpec → parallax review → build

Feed the same PEARS requirements into OpenSpec (same commands).

Run all 6 design-stage agents (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout) against the generated design.

Evaluate findings. Address genuine findings — update requirements or design as needed. Then build.

Save:
- OpenSpec design artifact (pre-review)
- Agent findings (JSONL)
- Changes made in response to findings
- OpenSpec design artifact (post-review, if changed)

### Step 4: Run reverse judge on Arm B findings

Use the eval framework's reverse judge (Haiku, T=0.0) to score each finding as GENUINE or NOT_GENUINE against the OpenSpec design document.

### Step 5: Compare at every stage

**Stage 0 — PEARS restructuring value (shared, pre-split):**
- Gaps surfaced by PEARS structuring: [count and list]
- Were these real gaps or template noise?
- New information forced by template: [list]

**Stage 1 — Parallax review value (Arm B only):**

| Metric | Value |
|---|---|
| Total findings | |
| Genuine findings | |
| Precision (genuine / total) | |
| Severity distribution (Crit / Imp / Min) | |
| Findings referencing requirement IDs | |
| Vague concern findings | |
| Findings that prompted design changes | |

**Stage 2 — Design impact:**
- Changes prompted by review findings: [count and description]
- Were changes to requirements (upstream) or design (downstream)?
- Diff of pre-review vs. post-review design

**Stage 3 — Downstream build (qualitative):**
- Surprises in Arm A build that Arm B avoided?
- Requirements misunderstandings?
- Spec-to-build divergence?

### Step 6: Decision

| Result | Action |
|---|---|
| Review finds genuine issues structure missed, build improves | Parallax review gate validated. Invest in integration tooling. |
| Review finds genuine issues but build quality is comparable | Review adds confidence, not information. Keep as optional gate. |
| Review mostly restates what PEARS made obvious | Structure is sufficient. Defer review integration, focus on harder problems. |
| Review produces mostly false positives | Agents need prompt improvement before integration is worthwhile. |
| Review findings make design worse | Investigate root cause — is it the agents, the artifact format, or the OpenSpec integration? |

---

## Cautions

**This tests the review gate, not the format.** Both arms use PEARS-structured requirements. The variable is whether parallax review adds value on top of good structure. Don't conflate PEARS restructuring signal (Stage 0) with review signal (Stage 1).

**Don't refactor parallax first.** The agents consume raw markdown. A PEARS document is raw markdown. An OpenSpec design artifact is raw markdown. No pipeline changes needed.

**Watch for confirmation bias.** You want the review gate to work — that's parallax's reason for existing. Pre-commit to what "not worth pursuing" looks like (the decision table above).

**N=1 produces direction, not proof.** Label results as "exploratory."

**PEARS documents are AI-assisted, not hand-written.** The minimum viable tooling is a skill that provides the template, writing rules, and anti-patterns to guide AI-assisted generation. The template and rules in this doc are that skill's content — package them before the experiment, not after.

---

## Appendix: cc-sdd Requirements Specialist — What It Would Do Differently

See `2026-02-21-cc-sdd-requirements-specialist-analysis.md` for full technical analysis with exact system prompts.

### What cc-sdd's Requirements Specialist is

A **requirements generator** — takes a feature description and produces EARS-formatted requirements using a 4-phase pipeline: analysis → EARS template application → document structure → quality gate validation. It's a single agent, not a review team. It generates, it doesn't critique.

### Two things cc-sdd's generation process encodes that PEARS currently doesn't

**1. Structured analysis phase before generation**

cc-sdd's Requirements Specialist walks through a systematic decomposition before writing any requirements:
- Identify key system components
- Determine user interactions
- List system states and transitions
- Consider error scenarios

PEARS has the output template but doesn't prescribe this analysis sequence. A PEARS skill could add a similar pre-generation phase: "Before filling the template, enumerate components, interactions, states, and failure modes." This is lightweight — a few prompts, not a separate agent.

**2. Pattern-driven completeness sweep**

cc-sdd systematically generates requirements in each EARS category:
1. Ubiquitous requirements (system fundamentals, always active)
2. Event-driven requirements (user actions → responses)
3. State-driven requirements (conditional on system state)
4. Optional feature requirements (feature-conditional behavior)
5. Unwanted behavior requirements (error handling, edge cases)

PEARS lists EARS/BDD/SHALL NOT as format options but doesn't force you through each category asking "do you have requirements of this type?" A completeness prompt — "walk through each PEARS category and confirm whether it applies" — would catch omissions without adding a separate agent.

### What cc-sdd's generation process does NOT do that PEARS does

| Capability | cc-sdd | PEARS |
|---|---|---|
| Deterministic vs. probabilistic distinction | No — all EARS, all SHALL | Yes — EARS for deterministic, BDD for probabilistic |
| JTBD / intent capture | No | Yes — mandatory overview section |
| Anti-goals | No | Yes — mandatory |
| Assumptions and risks | No | Yes — via template |
| Pre-mortem / failure modes | No | Encouraged via error handling blocks |
| SHALL NOT boundaries | Only as "unwanted behavior" pattern | Explicit distinct pattern |
| Quantified NFRs | "Non-functional requirements specified" (checklist) | Concrete numbers mandatory (rule 16) |
| Open questions | No | Mandatory section |

### Decision: Not a separate experiment arm

cc-sdd's Requirements Specialist and PEARS operate at different layers — generation vs. review. A bakeoff between them doesn't test the same thing. The useful elements from cc-sdd (analysis phase, completeness sweep) are small enough to fold into the PEARS skill as pre-generation prompts rather than testing as a separate arm.

### Future hypothesis: cc-sdd generation approach addresses naive PEARS defects

If the current experiment's review gate (Arm B) repeatedly catches the same class of generation gap — missing requirement categories, overlooked components, incomplete state enumeration — that's evidence the PEARS skill's generation phase needs strengthening. The cc-sdd Requirements Specialist's structured decomposition (components → interactions → states → errors) is a candidate fix.

**Future experiment design:** Compare PEARS skill with basic analysis phase vs. PEARS skill with cc-sdd-style systematic decomposition. Measure: does the deeper decomposition reduce the number of genuine findings the review gate produces? If review findings drop because the generator caught those issues upstream, the decomposition paid for itself.

This experiment only makes sense after the current one. If the review gate finds few genuine issues on current PEARS output, there's nothing for better generation to prevent.
