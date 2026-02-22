# Parallax vs. OpenSpec vs. Spec Kit: Ecosystem Analysis (v2)

**Date:** 2026-02-21
**Status:** Revised with SDD research report context and EARS/BDD hybrid model
**Supersedes:** v1 (same filename, prior commit)

## Summary

Parallax was built as a standalone skill + eval framework for adversarial multi-perspective design review. Two ecosystems — OpenSpec and Spec Kit — address overlapping territory in specification-driven development. A separate SDD research report (`sdd-research-report.md`) independently arrived at a three-layer architecture: custom EARS/BDD requirements elicitation → OpenSpec lifecycle → execution. This analysis integrates that research, maps what's durable in parallax, what's replaceable, and critically evaluates two migration strategies.

**Revised bottom line:** The original v1 recommendation ("adopt OpenSpec, inject parallax:review as a gate") was directionally correct but undervalued two things: (1) the EARS/BDD hybrid requirements model fills a gap that *neither* ecosystem nor parallax currently addresses well, and (2) parallax's requirements-stage agents are more valuable than v1 suggested — they're not redundant with OpenSpec's specify phase, they're *complementary* as automated validation of EARS/BDD-structured requirements. The better architecture is the SDD report's three-layer stack with parallax providing both the review gate (Layer 2) AND requirements validation (Layer 1 quality check).

---

## Key Input: The SDD Research Report

The SDD research report (`sdd-research-report.md`) was written from a different angle — evaluating SDD tooling for Splunk Cloud skill development. Its conclusions are independently relevant:

**Four failure modes identified:**
1. Requirements drift / scope creep → spec-anchored artifacts (OpenSpec)
2. Context loss across sessions → AGENTS.md + `.claude/skills/` persistence
3. No review gate → enforced proposal → review → apply lifecycle
4. Lack of rigor → EARS/BDD hybrid with automated gap detection

**Three-layer architecture proposed:**
- **Layer 1:** Requirements elicitation (custom skill) — JTBD → impact mapping → MoSCoW/YAGNI → EARS/BDD hybrid → gap check
- **Layer 2:** SDD lifecycle (OpenSpec OPSX) — proposal → specs → design → tasks → archive, with review gate
- **Layer 3:** Execution (Claude Code + Codex)

**Critical insight on EARS:** Pure EARS (`SHALL`/`WHEN`/`IF`) is a category error for LLM-based skills because skill behavior is probabilistic, not deterministic. The hybrid model uses EARS for hooks/tools/linters (deterministic), BDD Given/When/Then for skill behavioral contracts (observable), and RFC 2119 SHALL/SHOULD/MAY for non-functional properties.

**OpenSpec's review gate gap is called out explicitly** as "High severity" in the SDD report's gap analysis. This is precisely what parallax:review was built to fill.

---

## Ecosystem Profiles

### OpenSpec

Spec-driven development framework from Fission AI ([github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec), ~25k stars). Universal planning layer for AI coding assistants.

**Core concepts:**
- Proposal → spec → design → tasks pipeline via slash commands (`/openspec:proposal`, `/openspec:ff`, `/openspec:apply`)
- Living specs as first-class git artifacts in `openspec/specs/`; change deltas in `openspec/changes/` with `ADDED`/`MODIFIED`/`REMOVED` markers
- Custom schemas in YAML + markdown templates, version-controlled in `openspec/schemas/`
- Three-layer AI instructions: context, rules, templates — assembled dynamically
- Intent-focused review — reviewers examine proposals and spec deltas, not raw code
- Agent-agnostic (30+ platforms including Claude Code, Cursor, Copilot)
- Brownfield-native via two-folder model (specs/ + changes/)

**Known gaps (from SDD report):**
- Hardcoded spec parser (issue #666) — affects EARS heading customization
- No review gate native — key failure mode
- No PM-layer elicitation (JTBD, impact mapping, MoSCoW)
- No cross-repo spec composition

### Spec Kit

Constitutional specification-driven development — a methodology pattern implemented by multiple repos (plaesy/spec-kit, specpulse/specpulse, IBM/iac-spec-kit, others).

**Core concepts:**
- Constitutional governance (project principles as guardrails for agent behavior)
- 8-phase workflow: constitute → specify → plan → tasks → implement → analyze → clarify → validate
- Multi-artifact consistency validation (constitution ↔ spec ↔ plan ↔ code)
- Zero-ambiguity protocol with anti-hallucination mechanisms

**Assessment from SDD report:** "Remains experimental with known brownfield weaknesses and review overload reported in practitioner reviews. Not recommended as primary tool."

---

## Durability Assessment (Revised)

### DURABLE — Genuinely Novel

#### Adversarial multi-agent review

**Unchanged from v1.** Neither ecosystem dispatches specialized reviewer agents in parallel with distinct critical lenses. This remains parallax's core differentiator.

The 11 reviewer agents, synthesizer, JSONL finding schema, phase classification, and SRE-style finding format are all durable. Three completed review cycles (v1: 44 findings, v2: 55 findings, v3: confidence baseline) demonstrate real output with no equivalent in either ecosystem.

#### Two-tier eval scoring

**Unchanged from v1.** Reverse judge precision + must-find recall, with falsity criteria, confidence stratification, absence-detection framing, and frozen document snapshots. Neither ecosystem measures output quality.

#### Finding classification by pipeline phase

**Unchanged from v1.** Routing findings to survey/calibrate/design/plan phases. Both ecosystems group by feature or workflow step, not by which development phase produced the flaw.

### REVISED: Requirements-Stage Agents (Upgraded from REPLACEABLE to AUGMENTABLE)

**v1 said:** Replace `requirements/SKILL.md` with OpenSpec's specify phase.

**v2 revision:** This was wrong. The SDD report's EARS/BDD hybrid model reveals that OpenSpec's specify phase captures requirements but doesn't *validate their rigor*. OpenSpec generates specs — it doesn't check whether those specs have gaps, unstated assumptions, missing acceptance criteria, or category errors (using EARS SHALL for probabilistic behavior).

Parallax's requirements-stage agents (Problem Framer, Scope Guardian, Constraint Finder, Success Validator, Assumption Hunter) are precisely the automated gap-detection mechanism the SDD report calls for in Layer 1 Phase 5 ("Gap check: failure mode analysis, edge cases, implied non-functional requirements").

**Revised classification:** AUGMENTABLE — keep the requirements-stage agents, retarget them to validate EARS/BDD-structured requirements generated by the elicitation skill or OpenSpec's specify phase. They become the quality gate on Layer 1 output.

### REPLACEABLE — Solved Better by Ecosystem Tooling

#### Pipeline orchestration (`parallax:orchestrate`, Issue #52)

**Unchanged from v1.** Both the SDD report and v1 agree: adopt OpenSpec's orchestration rather than building custom. The novel parts — adversarial review and requirements validation — are gates *within* the pipeline, not the pipeline itself.

#### Context persistence

**Unchanged from v1.** OpenSpec's two-folder model (specs/ + changes/) with git-based persistence is more robust than CLAUDE.md + memory files for feature-level context. CLAUDE.md remains correct for project-level config.

#### Specification capture (as standalone)

**Unchanged from v1.** OpenSpec's specify phase is a superset. But see the upgrade on requirements-stage agents above — validation of specs is different from generation of specs.

---

## Architecture: Two Strategies Compared

### Strategy A: Original v1 — OpenSpec + Parallax Review Gate

```
/openspec:proposal → /openspec:ff → parallax:review → /openspec:apply
```

Parallax is a single injection point: review the design before implementation.

### Strategy B: SDD Three-Layer — OpenSpec + EARS/BDD + Parallax at Two Points

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 1: Requirements Elicitation   (custom skill)              │
│  JTBD → Impact Map → MoSCoW/YAGNI → EARS/BDD hybrid → Gap check │
│  Output: pre-proposal.md                                         │
│                                                                  │
│  ◆ PARALLAX INJECTION #1: Requirements-stage agents validate     │
│    EARS/BDD output for gaps, assumptions, scope issues            │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│  LAYER 2: SDD Lifecycle   (OpenSpec OPSX)                        │
│  proposal (from pre-proposal.md) → specs → design → tasks       │
│  Custom schema enforcing EARS/BDD structure                      │
│                                                                  │
│  ◆ PARALLAX INJECTION #2: Design-stage agents review design      │
│    before apply (same as Strategy A)                             │
│                                                                  │
│  → archive to spec source of truth                               │
└──────────────────────────────┬───────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│  LAYER 3: Execution   (Claude Code + Codex)                      │
│  Skill implementation via .claude/skills/                        │
│  AGENTS.md as cross-session context anchor                       │
└──────────────────────────────────────────────────────────────────┘
```

Parallax injects at two points: requirements validation AND design review.

---

## Critical Comparison: Strategy A vs. Strategy B

### Where Strategy B is stronger

**Requirements rigor.** Strategy A skips requirements elicitation entirely — it assumes the user arrives at OpenSpec with well-formed requirements. The SDD report's four failure modes show this assumption fails in practice. Strategy B's EARS/BDD layer with parallax validation catches problems before they enter the spec lifecycle. Fixing requirements is cheaper than fixing designs.

**Full use of parallax assets.** Strategy A retires the 5 requirements-stage agents. Strategy B repurposes them as EARS/BDD validators — they validate completeness of requirements before spec generation. This preserves the tuning investment and the eval framework's applicability to both stages.

**EARS/BDD type safety.** The SDD report's insight that pure EARS is a category error for probabilistic skill behavior is significant. Without the hybrid model, OpenSpec's specs will contain SHALL statements for LLM behavior that can't be tested deterministically. Strategy B prevents this class of error; Strategy A doesn't address it.

**Org scalability.** Strategy B has a path for non-engineers (PMs do Layer 1 via Claude.ai conversation → pre-proposal.md) and for tiered adoption (SREs skip Layer 1, use Layers 2+3). Strategy A is engineer-only.

### Where Strategy B is weaker

**Complexity.** Strategy B has three layers, two injection points, a custom EARS/BDD elicitation skill to build, and OpenSpec schema customization. Strategy A is one injection point. For an R&D project exploring adversarial review quality, the additional machinery is overhead that doesn't help answer the core research question: "does multi-agent adversarial review produce genuinely useful findings?"

**Build scope.** Strategy B requires building: (1) requirements-elicit skill with 5-phase elicitation, (2) EARS validator as a linter hook, (3) OpenSpec schema customization for EARS/BDD, (4) review gate skill, (5) cross-repo context design. Strategy A requires building: (1) review gate skill, (2) input parser adaptation. That's a 5:2 ratio of new work.

**Research focus dilution.** Parallax's current eval metrics (9-27% precision, 72-75% judge accuracy) show the adversarial review component itself needs significant improvement. Adding a requirements elicitation layer, EARS/BDD enforcement, and schema customization diverts effort from the core problem: making the review agents produce higher-precision findings.

**Dependency risk.** Strategy B couples parallax to OpenSpec + a custom EARS/BDD skill + a custom schema. If any piece breaks, the full pipeline stalls. Strategy A couples only to OpenSpec's design artifacts.

### Self-challenge: Was v1 actually right?

The strongest argument for v1 over v2 is **focus**. Parallax is an R&D project investigating whether automated adversarial review works. The answer isn't in yet — precision is low, N is small, the eval framework needs more corpus. Adding EARS/BDD elicitation and multi-layer orchestration is *correct architecture* for a production system, but it's premature optimization for a research project that hasn't validated its core hypothesis.

The counterargument: requirements rigor directly affects review quality. If the document being reviewed is vaguely specified, reviewers will produce vague findings (the "garbage in, garbage out" problem). Improving input quality via EARS/BDD may improve precision more than prompt tuning on the reviewers themselves. This is a testable hypothesis, not an obvious truth.

---

## Revised Recommendation

**Phased approach: Strategy A now, Strategy B elements when validated.**

1. **Now (R&D phase):** Adopt OpenSpec as orchestration layer. Inject parallax:review as design gate (Strategy A). Focus on improving review precision and expanding the eval corpus. This is the minimum viable integration.

2. **When precision improves (>50% on N>=10):** Experiment with EARS/BDD-structured input documents. Test whether structured requirements produce higher-precision review findings than unstructured ones. This is a controlled experiment, not a migration.

3. **When moving to production use:** Build the full three-layer stack (Strategy B). The requirements elicitation skill, EARS/BDD hybrid model, and requirements-stage agent repurposing become justified when the system is serving real users, not when it's still proving its hypothesis.

**Why this ordering:**
- Phase 1 gets OpenSpec integration tested with minimal investment
- Phase 2 tests the EARS/BDD hypothesis before building the full layer
- Phase 3 only triggers if parallax proves viable as a production tool

**What changes from v1:**
- Requirements-stage agents are NOT retired — they're held in reserve for Phase 3 and used as experimental validators in Phase 2
- The EARS/BDD hybrid model is acknowledged as the right requirements format for the production system, but deferred until the core review mechanism is validated
- The three-layer architecture from the SDD report is adopted as the target state, not the immediate state

---

## Risk Assessment (Revised)

### Risks from v1 (unchanged)

- **Pipeline control:** OpenSpec owns orchestration; interface changes break injection
- **Eval ground truth:** Existing datasets invalidated by new artifact format
- **Artifact format independence:** Tight coupling reduces generality
- **Development velocity:** External dependency adds friction

### New risks from the EARS/BDD model

**Category error propagation.** If the EARS/BDD distinction isn't enforced, SHALL statements for probabilistic behavior will enter specs and produce unfalsifiable requirements. The review agents may then flag these as genuine findings (they technically violate EARS semantics) or miss real gaps masked by pseudo-precise SHALL language. Either outcome degrades precision. Mitigation: the EARS validator linter (SDD report step 4) must exist before EARS-structured specs are reviewed.

**Elicitation skill quality.** The SDD report acknowledges "custom elicitation skill produces inconsistent output quality" as a Medium likelihood / High impact risk. If the elicitation skill generates poor EARS/BDD requirements, the review agents validate garbage — same precision problem, different source. Mitigation: eval harness for elicitation output quality, not just review output quality.

**Schema coupling to OpenSpec parser.** OpenSpec issue #666 (hardcoded spec parser) affects EARS heading customization. The SDD report suggests using EARS content inside standard headings as a workaround. If the workaround produces artifacts the review agents can't parse consistently, both injection points break.

### The case for NOT migrating (revised)

The v1 case for not migrating remains valid and is *strengthened* by the EARS/BDD analysis. If the core research question is "does multi-agent adversarial review produce genuinely useful findings?", then:

- OpenSpec integration tests whether the review gate works in a real pipeline (useful)
- EARS/BDD requirements structuring tests whether input format affects output quality (useful but secondary)
- Building a full three-layer stack with custom elicitation tests whether the *production system* works (premature)

The right question to ask is: **what's the minimum integration that lets you test the next hypothesis?** For review quality: Strategy A. For input format effects: a controlled experiment with EARS-structured vs. unstructured documents, no OpenSpec required. For production viability: Strategy B, but only after the first two questions are answered.

---

## Concrete Next Steps (Revised)

### Phase 0: Validate OpenSpec integration (unchanged from v1)

1. Install OpenSpec locally, run on a small feature in this repo
2. Examine generated design artifact format
3. Run existing reviewer agents against an OpenSpec-generated design (manual)
4. Evaluate: do agents produce useful findings on OpenSpec artifacts?

**Decision gate:** Comparable precision/recall on OpenSpec artifacts vs. standalone docs.

### Phase 1: Lightweight integration (unchanged from v1)

5. Modify `review/SKILL.md` to accept OpenSpec artifact paths
6. Create one new dataset with frozen OpenSpec-generated design + curated ground truth
7. Run eval framework against new dataset — compare to existing baselines
8. Document in ADR-009

### Phase 1.5: EARS/BDD experiment (NEW)

9. Write one requirements document in EARS/BDD hybrid format (manually, no elicitation skill)
10. Write an equivalent unstructured requirements document covering the same feature
11. Run all 11 reviewer agents against both documents
12. Compare precision/recall: does structured input improve review output?
13. Document in ADR-010

**Decision gate:** If EARS/BDD input shows measurably higher precision at N>=10, proceed to Phase 2. If comparable or worse, defer Layer 1 construction.

### Phase 2: Requirements validation (conditional on Phase 1.5)

14. Retarget requirements-stage agents to validate EARS/BDD-structured specs
15. Build EARS validator as pre-proposal linter
16. Create eval dataset for requirements validation quality
17. Establish baselines for requirements-stage agent precision

### Phase 3: Full three-layer stack (conditional on Phases 1 + 2)

18. Build requirements-elicit skill (5-phase sequence from SDD report)
19. Customize OpenSpec schema for EARS/BDD enforcement
20. Close Issue #52 with "use OpenSpec + three-layer stack" rationale
21. Update CLAUDE.md to reflect new workflow

**Dependencies:**
- Phase 1 depends on Phase 0 decision gate
- Phase 1.5 can run in parallel with Phase 1 (independent experiment)
- Phase 2 depends on Phase 1.5 decision gate
- Phase 3 depends on Phases 1 + 2 both passing

---

## Appendix: Detailed Ecosystem Comparison

| Dimension | Parallax | OpenSpec | Spec Kit | Three-Layer (SDD Report) |
|-----------|----------|----------|----------|--------------------------|
| **Primary value** | Adversarial review | Spec capture + orchestration | Constitutional governance | Structured requirements + lifecycle + review |
| **Review model** | 6 automated agents, parallel | Human intent review | Consistency analysis | Review gate (must be custom-built) |
| **Requirements rigor** | 5 validation agents | None native | None native | EARS/BDD hybrid + elicitation skill |
| **Eval framework** | Inspect AI, 2-tier scoring | None | None | None (parallax fills this) |
| **Spec persistence** | Git + CLAUDE.md | Git + `openspec/specs/` | Git + `.specify/` | Git + OpenSpec + AGENTS.md |
| **Orchestration** | Unbuilt (Issue #52) | Slash commands | 8-phase workflow | OpenSpec + custom layers |
| **Agent support** | Claude Code only | 30+ platforms | 8+ platforms | Claude Code + Codex |
| **Maturity** | R&D, 55 commits | Production, 25k stars | Fragmented | Proposed architecture |
| **Brownfield** | Document-agnostic | Two-folder model | Varies | OpenSpec native |
| **Build effort** | Agents + evals exist | Install + schema | Constitutional setup | 5 new components |

## Appendix: Reusable Prompt

See standalone file: `2026-02-21-ecosystem-analysis-prompt.md`
