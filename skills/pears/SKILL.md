---
name: pears
description: Use when generating or restructuring requirements into PEARS format — "write PEARS requirements", "structure requirements", "PEARS format", "parallax:pears", or when converting existing requirements/specs into structured EARS/BDD hybrid format.
version: 0.1.0
---

# PEARS — Parallax EARS Requirements

Generate structured requirements for systems with both deterministic and probabilistic behavior. PEARS combines EARS syntax for deterministic components, BDD Given/When/Then for LLM/skill behavior, JTBD for intent, and RFC 2119 SHALL/SHOULD/MAY for constraint tiers.

## When to Use

- Starting a new feature and need structured requirements
- Restructuring existing requirements/specs into a reviewable format
- Before feeding requirements into OpenSpec or any SDD pipeline
- When requirements need to distinguish deterministic from probabilistic behavior
- Before running `parallax:review` or `parallax:requirements` — PEARS-structured input produces better review findings

## Process

### Phase 1: Gather Input

Collect from the user:
- **Existing requirements or feature description** — could be a doc path, prose description, issue list, or brainstorm output
- **Feature name** — short label for the requirements document

If the user provides a document path, read it. If they provide a description, use it as-is.

### Phase 2: Pre-Generation Analysis

Before writing any requirements, systematically decompose the feature:

1. **Enumerate system components** — what are the distinct parts of this system?
2. **Map user interactions** — what does the user do, and what does the system do in response?
3. **List system states and transitions** — what states can the system be in, and what triggers transitions?
4. **Identify failure modes** — what can go wrong at each interaction point?
5. **Classify behavior type** — for each component/interaction, is the behavior deterministic (EARS) or probabilistic (BDD)?

Present this decomposition to the user for validation before proceeding. This surfaces gaps early — missing components, overlooked interactions, unconsidered failure modes.

### Phase 3: Generate PEARS Document

Using the analysis from Phase 2, generate the requirements document following the template below. Apply the format selection rules and writing rules throughout.

#### Format Selection Rules

| What you're specifying | Format | Why |
|---|---|---|
| Deterministic behavior (hooks, CLI tools, linters, API contracts) | Pure EARS | Trigger → response is guaranteed; testable with assertions |
| Forbidden behavior (security boundaries, invariants) | EARS SHALL NOT | Explicit negative specification; gives reviewers boundaries to probe |
| LLM skill behavior (agent responses, review output, synthesis) | BDD Given/When/Then | Observable outcomes; acceptance-testable but not deterministic |
| Design intent and motivation | JTBD statement | Captures *why* before *what*; prevents solving the wrong problem |
| Hard constraints vs. guidance | RFC 2119 SHALL/SHOULD/MAY | Distinguishes non-negotiable from preferred from optional |
| Error and failure behavior | EARS WHEN [failure] or BDD GIVEN [error state] | Failure modes as requirements, not afterthoughts |

#### The Category Error to Avoid

> **"THE skill SHALL respond with X"** is a category error for LLM-based components.

EARS `SHALL` implies a guarantee. LLMs don't guarantee. Forcing probabilistic behavior into EARS syntax produces either:
- Vague requirements that defeat EARS's purpose ("THE skill SHALL provide helpful output")
- False precision that can't be tested ("THE skill SHALL include exactly 3 findings")

**Rule:** Use EARS for the deterministic parts of the system. Use BDD for the parts where you're specifying *observable outcomes* of probabilistic behavior. Use SHALL/SHOULD/MAY for constraint tiers on anything.

#### Document Template

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

### Phase 4: Completeness Sweep

After generating the initial document, walk through each PEARS category and confirm coverage:

1. **EARS deterministic requirements** — are all trigger → response behaviors specified? Any CLI commands, API endpoints, hooks, or tool integrations missing?
2. **BDD probabilistic requirements** — are all LLM/skill/agent behaviors specified as observable outcomes? Any skill interactions missing Given/When/Then scenarios?
3. **SHALL NOT boundaries** — are security invariants, forbidden behaviors, and scope fences explicitly stated? What must this system never do?
4. **Error handling** — does every requirement with a happy-path have a failure-path? What happens when dependencies are unavailable, input is invalid, or upstream times out?
5. **NFRs with concrete numbers** — are all performance, latency, throughput, and scale constraints quantified? Any vague qualifiers ("fast", "scalable") remaining?
6. **Anti-goals** — is the "won't do" list explicit enough to prevent scope creep?
7. **Open questions** — are unresolved decisions captured, or have they been silently assumed?

Surface any gaps found and add them to the document. Present the completeness sweep results to the user.

### Phase 5: Output

Save the PEARS requirements document. If restructuring from an existing document, also save a restructuring delta noting:
- Gaps surfaced by the PEARS process (new information the template forced)
- Information restructured (already present, reformatted)
- Completeness sweep findings

## Writing Rules

**Structure rules:**
1. Every requirement gets a unique ID (REQ-001, NFR-001)
2. One requirement per section — don't bundle multiple behaviors
3. EARS blocks use WHEN/IF/SHALL keywords in caps
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
15. Every requirement with a happy-path behavior SHOULD have an error-handling block
16. Every NFR constraint involving performance, latency, throughput, or scale MUST include a concrete number. No vague qualifiers
17. Use SHALL NOT for security boundaries, invariants, and scope fences — distinct from constraints

## Anti-Patterns

| Anti-pattern | Example | Fix |
|---|---|---|
| SHALL for probabilistic behavior | "THE skill SHALL generate 3-5 findings" | BDD: "THEN findings are generated" + SHOULD: "typically 3-5 findings" |
| Vague EARS | "WHEN the user requests help THE system SHALL help" | Make specific ("SHALL display help text") or use BDD |
| Implementation in BDD | "THEN the function calls the API" | Describe outcome: "THEN the data is available in the store" |
| Missing JTBD | Jump straight to REQ-001 | Write the job statement first — it's the "why" |
| Bundled requirements | REQ-001 covers auth, logging, and error handling | Split: REQ-001 (auth), REQ-002 (logging), REQ-003 (error handling) |
| No anti-goals | Feature scope is implied but not stated | Write explicit anti-goals — what you won't do |
| SHALL/SHOULD confusion | "The system SHOULD authenticate users" | If auth is required, it's SHALL. SHOULD means degraded-but-functional without it |
| Missing open questions | No open questions section | Always include — "None identified" forces the acknowledgment |
| Vague NFR | "The system SHALL be fast" | Quantify: "P95 response time SHALL be < 500ms under 100 concurrent requests" |
| Happy-path only | REQ-001 specifies success, no error handling | Add error block: WHEN [failure] THE [component] SHALL [error behavior] |
| Missing SHALL NOT | Security boundary implied but not stated | Explicit: "THE component SHALL NOT expose credentials in logs" |
| Negative as constraint | Constraints: "SHALL: must not leak data" | Use SHALL NOT block — distinct requirement type, not a constraint modifier |
