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

### Variables

- **Independent variable:** Requirements document format (unstructured vs. EARS/BDD hybrid)
- **Dependent variables:** Finding precision (reverse judge), finding actionability (qualitative), finding distribution (severity, phase, false positive rate)
- **Controlled:** Same feature scope, same agents, same reviewer temperature, same judge configuration

### Method

1. Select a real feature you're planning to build (not a synthetic example)
2. Write the requirements document twice:
   - **Version A:** Unstructured markdown — the way you'd naturally describe it in a CLAUDE.md or design doc
   - **Version B:** EARS/BDD hybrid format following the scaffolding below
3. Both documents must cover the same scope, constraints, and acceptance criteria — the information content should be equivalent, only the structure differs
4. Run all 6 design-stage agents against Version A, collect JSONL findings
5. Run all 6 design-stage agents against Version B, collect JSONL findings
6. Run reverse judge on both finding sets
7. Compare precision, severity distribution, and qualitative actionability

### What "success" looks like

- **Clear signal:** EARS/BDD findings have measurably higher precision (>10 percentage points) and/or fewer false positives in the same severity class
- **Marginal signal:** Precision is comparable but findings reference specific requirements by ID, making them more actionable for the author
- **No signal:** Precision is comparable and findings are qualitatively similar
- **Negative signal:** EARS/BDD structure causes agents to generate more false positives (e.g., flagging EARS syntax issues instead of real gaps)

### Limitations

This is N=1 per format. It produces directional signal, not statistical proof. Label results as "exploratory." If directionally positive, design a larger experiment (N>=10 per format) before committing to tooling investment.

---

## EARS/BDD Hybrid Format: Scaffolding

### When to use which format

| What you're specifying | Format | Why |
|---|---|---|
| Deterministic behavior (hooks, CLI tools, linters, API contracts) | Pure EARS | Trigger → response is guaranteed; testable with assertions |
| LLM skill behavior (agent responses, review output, synthesis) | BDD Given/When/Then | Observable outcomes; acceptance-testable but not deterministic |
| Design intent and motivation | JTBD statement | Captures *why* before *what*; prevents solving the wrong problem |
| Hard constraints vs. guidance | RFC 2119 SHALL/SHOULD/MAY | Distinguishes non-negotiable from preferred from optional |

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

### REQ-002 — [Next requirement]
[Same structure. One requirement per section. Number sequentially.]

---

## Non-Functional Requirements

### NFR-001 — [Title]

- SHALL: [Hard constraint — e.g., "respond within 500ms"]
- SHOULD: [Target — e.g., "log latency at INFO level"]
- MAY: [Aspiration — e.g., "support batch mode"]

---

## Acceptance Criteria

[BDD scenarios that validate the feature works end-to-end.
These are integration-level, not per-requirement.]

GIVEN [system state]
WHEN [user action or trigger sequence]
THEN [end-to-end observable outcome]

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

### Step 1: Select project, write Version A (unstructured)

Write the requirements the way you naturally would — prose, bullet lists, whatever structure you'd put in a CLAUDE.md or design doc. Don't artificially make it worse; write it the way you'd actually write it.

Save as `docs/experiments/ears-bdd/version-a-unstructured.md`.

### Step 2: Write Version B (EARS/BDD hybrid)

Using the template and rules above, restructure the same requirements into EARS/BDD format. The information content should be equivalent — same scope, same constraints, same acceptance criteria. The structure is the only variable.

This step will surface gaps: the template forces JTBD, anti-goals, and open questions that the unstructured version may not have. **That's signal, not contamination.** Note which information is *new* (forced by the template) vs. *restructured* (present in Version A but differently organized). If the template forces you to add significant new content, that itself is a finding about the format's value.

Save as `docs/experiments/ears-bdd/version-b-structured.md`.

### Step 3: Run design-stage agents against Version A

Run all 6 design-stage agents (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout) against Version A. Collect JSONL output.

Save findings as `docs/experiments/ears-bdd/findings-version-a.jsonl`.

### Step 4: Run design-stage agents against Version B

Same agents, same configuration, against Version B.

Save findings as `docs/experiments/ears-bdd/findings-version-b.jsonl`.

### Step 5: Run reverse judge on both finding sets

Use the existing eval framework's reverse judge (Haiku, T=0.0) to score each finding as GENUINE or NOT_GENUINE against its respective source document.

### Step 6: Compare and document

| Metric | Version A | Version B |
|---|---|---|
| Total findings | | |
| Genuine findings | | |
| Not genuine findings | | |
| Precision (genuine / total) | | |
| Severity distribution (Critical / Important / Minor) | | |
| Phase distribution (survey / calibrate / design / plan) | | |
| New information surfaced by template (Version B only) | N/A | |

Qualitative comparison:
- Are Version B findings more specific (reference requirement IDs)?
- Are Version B findings more actionable (clearer remediation)?
- Does Version B produce fewer "vague concern" findings?
- Did the template itself surface gaps before the agents ran?

### Step 7: Decision

| Result | Action |
|---|---|
| Clear signal (>10pp precision improvement) | Design larger experiment (N>=10). Consider EARS/BDD tooling investment. |
| Marginal signal (comparable precision, better actionability) | The format helps humans more than it helps agents. Consider lightweight adoption without tooling. |
| No signal | Defer EARS/BDD tooling. Focus on agent prompt improvement instead. |
| Negative signal | EARS/BDD structure confuses agents. Investigate whether prompt adaptation fixes it before abandoning. |

---

## Cautions

**Separate the variables.** This experiment tests whether structured input improves design-stage review quality. It does NOT test whether the requirements-stage agents are useful as EARS/BDD validators — that's a different experiment, only worth running if this one shows positive signal.

**Don't refactor parallax first.** The agents consume raw markdown. An EARS/BDD document is raw markdown. No pipeline changes needed for this experiment. If the experiment succeeds, *then* consider tooling.

**Watch for confirmation bias.** You're invested in the three-layer architecture. Pre-commit to what "not worth pursuing" looks like (the decision table above) so you have an exit ramp.

**N=1 produces direction, not proof.** Label results as "exploratory." Don't make ADR decisions from a single comparison.

**The template is the minimal scaffolding.** Don't build an elicitation skill, an EARS linter, or an OpenSpec schema customization before running this experiment. The template and writing rules above are enough to produce a properly structured document by hand.
