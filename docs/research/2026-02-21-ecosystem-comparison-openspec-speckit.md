# Parallax vs. OpenSpec vs. Spec Kit: Ecosystem Analysis

**Date:** 2026-02-21
**Status:** Initial analysis — parallax developed without knowledge of either ecosystem

## Summary

Parallax was built as a standalone skill + eval framework for adversarial multi-perspective design review. Two ecosystems — OpenSpec and Spec Kit — address overlapping territory in specification-driven development. This analysis maps what's durable in parallax, what's replaceable, and how migration could work.

**Bottom line:** Parallax's adversarial review and eval framework are genuinely novel and not addressed by either ecosystem. The specification capture, pipeline orchestration, and context persistence layers are solved better by OpenSpec. The recommended path is adopting OpenSpec as the primary workflow and injecting parallax's review gate into its pipeline.

---

## Ecosystem Profiles

### OpenSpec

Spec-driven development framework from Fission AI ([github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec), ~25k stars). Universal planning layer for AI coding assistants.

**Core concepts:**
- Proposal → spec → design → tasks pipeline via slash commands (`/openspec:proposal`, `/openspec:ff`, `/openspec:apply`)
- Living specs as first-class git artifacts in `openspec/specs/`
- Intent-focused review — reviewers examine proposals and spec deltas, not raw code
- Agent-agnostic (30+ platforms including Claude Code, Cursor, Copilot)
- Brownfield-ready, lightweight, iterative
- Persistent context across sessions via repo-stored specs

**Philosophy:** Fluid, not rigid. Iterative, not waterfall. Easy, not complex.

**Gap:** No adversarial review. Intent review is human-driven, not automated multi-agent.

### Spec Kit

Constitutional specification-driven development — a methodology pattern implemented by multiple repos (plaesy/spec-kit, specpulse/specpulse, IBM/iac-spec-kit, others).

**Core concepts:**
- Constitutional governance (project principles as guardrails for agent behavior)
- 8-phase workflow: constitute → specify → plan → tasks → implement → analyze → clarify → validate
- Multi-artifact consistency validation (constitution ↔ spec ↔ plan ↔ code)
- Zero-ambiguity protocol with anti-hallucination mechanisms
- File structure in `.specify/` directory
- Platform-agnostic (8+ AI coding tools)

**Philosophy:** Constitutional, structured, deterministic phases.

**Gap:** Analyze phase is consistency checking, not adversarial criticism. Ecosystem is fragmented across 5+ implementations with no clear winner.

---

## Durability Assessment

### DURABLE — Genuinely Novel

#### Adversarial multi-agent review

Neither ecosystem dispatches specialized reviewer agents in parallel with distinct critical lenses. OpenSpec's "intent-focused review" is human-driven. Spec Kit's "analyze" phase checks consistency between artifacts — it doesn't generate adversarial findings.

The 11 reviewer agents (6 design-stage, 5 requirements-stage) with explicit false-positive exclusion lists, confidence rubric anchors, and structured JSONL output represent significant tuning work that has no equivalent. The reviewer personas — Assumption Hunter, Edge Case Prober, Feasibility Skeptic, First Principles Challenger, Prior Art Scout, Requirement Auditor — each encode a distinct critical lens that produces findings the others miss.

The synthesizer agent's consolidation logic (dedup, severity classification, phase routing) is also novel. Neither ecosystem produces structured adversarial findings, let alone consolidates them.

**Evidence:** Three completed review cycles (v1: 44 findings, v2: 55 findings, v3: confidence baseline) demonstrate real output. No comparable artifacts exist in OpenSpec or Spec Kit documentation or examples.

#### Two-tier eval scoring

The reverse judge precision metric ("is this finding genuine?") + must-find recall (curated ground truth regression guard) is a real contribution to measuring review quality. Neither ecosystem has any mechanism for evaluating whether their outputs are correct.

Key innovations within this framework:
- **Falsity criteria** — explicit rules for what makes a finding NOT genuine (implementation details, hallucinated constraints, style preferences, external context, duplicates)
- **Confidence stratification** — comparing high-conf vs. low-conf precision as a calibration signal
- **Absence-detection framing** — reviewers look for what's NOT stated, requiring different eval rubrics than presence-detection
- **Frozen document snapshots** — ground truth tied to specific document versions to prevent drift

**Evidence:** ADR-005 through ADR-008 document the rigorous process of evaluating and rejecting alternatives (G-Eval, Factuality, RAGAS) with specific rationale. The eval framework runs on Inspect AI with reproducible results.

#### Finding classification by pipeline phase

Routing findings to survey/calibrate/design/plan phases answers "which phase failed" rather than just "what's wrong." This is architecturally sound and absent from both ecosystems — OpenSpec groups by feature, Spec Kit groups by workflow phase, but neither classifies findings by the development phase that produced the flaw.

#### SRE-style finding format

Blast radius, failure mode, mitigation framing in structured JSONL. Both ecosystems produce specs and plans; neither produces machine-readable adversarial findings with severity/confidence/phase metadata.

### REPLACEABLE — Solved Better by Ecosystem Tooling

#### Specification capture (`requirements/SKILL.md`)

Parallax's requirements skill dispatches 5 reviewers to validate requirements. OpenSpec's specify phase captures requirements as living artifacts with proposal context, design rationale, and task decomposition — a superset of what `requirements/SKILL.md` does.

OpenSpec's brownfield support (incremental spec creation for existing codebases) and multi-session persistence (specs survive chat sessions via git) are more mature than parallax's current approach of generating findings against a document snapshot.

**Migration path:** Replace `requirements/SKILL.md` invocations with `/openspec:proposal` + `/openspec:ff`. The requirements-stage reviewer agents (Problem Framer, Scope Guardian, etc.) could run against OpenSpec's generated spec artifacts instead.

#### Pipeline orchestration (`parallax:orchestrate`, Issue #52)

This is an unsolved design decision in parallax — Issue #52 is open with "thin router vs. auto-trigger" as the pending question. Both ecosystems have working orchestration:

- OpenSpec: `/openspec:proposal` → `/openspec:ff` (generates spec + design + tasks) → `/openspec:apply` (implements)
- Spec Kit: constitute → specify → plan → tasks → implement → validate (8-phase sequential)

Building custom orchestration when two mature implementations exist is not justified by any novel requirement. The novel part — adversarial review — is a gate *within* the pipeline, not the pipeline itself.

**Migration path:** Adopt OpenSpec's orchestration. Close Issue #52. Inject `parallax:review` between `/openspec:ff` and `/openspec:apply`.

#### Context persistence

Parallax relies on CLAUDE.md + `~/.claude/projects/.../memory/MEMORY.md` + git. OpenSpec stores specs as first-class git artifacts readable by any agent on any machine. Spec Kit uses `.specify/` directories with constitutional documents.

Both solve multi-session, multi-machine context more robustly than parallax's current approach.

**Migration path:** Continue using CLAUDE.md for project config and development workflow. Use OpenSpec specs for feature-level context persistence.

### AUGMENTABLE — Keep but Integrate

#### ADR process

Parallax's ADR discipline (8 decisions documented with full rationale) is complementary to OpenSpec's proposal model, not redundant. ADRs capture *why* architectural decisions were made; OpenSpec proposals capture *what* is being built. Keep both.

#### Dataset curation

The 2 curated datasets (19 ground truth findings) with frozen document snapshots are required for the eval framework regardless of orchestration layer. The datasets would need updating to reflect OpenSpec-generated artifacts instead of standalone requirement documents, but the curation methodology transfers.

#### Agent prompt engineering

The 11 reviewer agent prompts transfer to any framework — they're self-contained markdown with YAML frontmatter. The false-positive exclusion lists, confidence rubric anchors, and voice rules don't depend on parallax-specific infrastructure.

---

## Ecosystem Recommendation

**OpenSpec as primary workflow.** Rationale:

| Dimension | OpenSpec | Spec Kit | Winner |
|-----------|----------|----------|--------|
| Maturity | Single reference impl, 25k stars, active dev | 5+ fragmented impls, no clear leader | OpenSpec |
| Philosophy | Fluid, iterative (aligns with parallax) | Constitutional, rigid phases | OpenSpec |
| Agent support | 30+ platforms | 8+ platforms | OpenSpec |
| Migration effort | Slash commands, minimal ceremony | Requires constitutional setup | OpenSpec |
| Brownfield support | First-class | Varies by implementation | OpenSpec |
| Spec format | Markdown in `openspec/specs/` | Markdown in `.specify/` | Comparable |

**Counterarguments considered:**

1. *Spec Kit's constitutional model is more rigorous.* True — but parallax's ADR process already provides governance, and the constitutional model adds ceremony without clear benefit for a solo/small-team R&D project. If parallax scales to team use, constitutional governance could be added later.

2. *OpenSpec's review model is human-driven, which means integration friction.* True — there's no native hook point for automated review in OpenSpec's pipeline. The integration requires either forking OpenSpec to add a review gate, or wrapping the workflow in a thin orchestrator that calls OpenSpec commands + parallax review in sequence. This is the primary technical risk.

3. *Neither ecosystem is stable yet.* Fair — both are early-stage. OpenSpec at 25k stars has more community momentum, but API/command changes could break integrations. Mitigation: parallax's review components are self-contained and framework-independent.

---

## Migration Architecture

```
User intent
    │
    ▼
/openspec:proposal          ← OpenSpec captures intent + rationale
    │
    ▼
/openspec:ff                ← OpenSpec generates spec + design + tasks
    │
    ▼
┌─────────────────────────────────────────────┐
│  parallax:review (INJECTION POINT)          │
│                                             │
│  Input: OpenSpec-generated design artifact  │
│                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │Assump.  │ │Edge     │ │Require. │      │
│  │Hunter   │ │Case     │ │Auditor  │ ...  │
│  └────┬────┘ └────┬────┘ └────┬────┘      │
│       └───────────┼───────────┘            │
│                   ▼                         │
│           ┌──────────────┐                  │
│           │ Synthesizer  │                  │
│           └──────┬───────┘                  │
│                  ▼                           │
│  Verdict: PROCEED / REVISE / STOP           │
│                                             │
│  If REVISE → loop back to /openspec:ff      │
│  If STOP   → escalate to human              │
└─────────────────────────────────────────────┘
    │ (PROCEED)
    ▼
/openspec:apply             ← OpenSpec implements reviewed design
    │
    ▼
Eval framework              ← Inspect AI measures review quality
(offline, not in pipeline)    (precision/recall on review output)
```

### What Transfers As-Is

| Component | Location | Notes |
|-----------|----------|-------|
| 6 design reviewer agents | `agents/` | Self-contained prompts, no framework dependency |
| 5 requirements reviewer agents | `agents/` | May repurpose to review OpenSpec proposals |
| Synthesizer agent | `agents/` | Consolidation logic is framework-independent |
| Eval framework | `evals/`, `scorers/` | Inspect AI tasks, datasets, judge scorer |
| Datasets | `datasets/` | Need new datasets against OpenSpec artifacts |
| ADRs | `docs/requirements/` | Complementary to OpenSpec |
| JSONL schema | Throughout | Finding format is framework-independent |

### What Needs Adaptation

| Component | Change Required |
|-----------|----------------|
| `review/SKILL.md` | Modify input parsing to accept OpenSpec design artifacts instead of raw documents |
| `requirements/SKILL.md` | Retire or repurpose agents to review OpenSpec proposal/spec artifacts |
| Dataset documents | Create new frozen snapshots from OpenSpec-generated designs |
| Must-find entries | Curate against OpenSpec artifact format |
| Eval tasks | Update document loading to read from `openspec/specs/` |

### What Gets Deleted

| Component | Rationale |
|-----------|-----------|
| `parallax:orchestrate` (planned) | Replaced by OpenSpec pipeline |
| Issue #52 design decision | Moot — use OpenSpec orchestration |
| Custom context persistence logic | Replaced by OpenSpec specs |
| Requirements skill (as standalone) | Replaced by OpenSpec specify phase |

---

## Risk Assessment

### What parallax loses by migrating

**Pipeline control.** OpenSpec owns the orchestration. If OpenSpec's command interface changes, the review injection point breaks. Mitigation: parallax:review is self-contained — worst case, it runs standalone against any document, with or without OpenSpec.

**Eval ground truth.** Existing datasets are curated against standalone requirement documents. Migration to OpenSpec-generated artifacts invalidates current ground truth and requires new dataset curation. This is significant effort — the 19 validated findings and 2 frozen document snapshots represent multiple cycles of careful human validation.

**Artifact format independence.** Currently parallax reviews any markdown document. Tight coupling to OpenSpec's artifact format reduces generality. Mitigation: keep the review skill's input parser flexible — accept both raw documents and OpenSpec artifacts.

**Development velocity.** Adding a dependency on OpenSpec means tracking its releases, adapting to breaking changes, and debugging integration issues. For a solo R&D project, this friction may outweigh the benefit of not building orchestration.

### Architectural assumptions that may break

**Per-reviewer eval decomposition (ADR-006)** assumes reviewers receive a standalone document. If OpenSpec's design artifacts are split across multiple files (spec + design + tasks), the eval framework needs to handle multi-file input or concatenation. This is solvable but not trivial.

**Frozen document snapshots** assume a single document version. OpenSpec's iterative spec updates (spec deltas) may require freezing at a specific git commit rather than a file snapshot.

**Judge context window.** The reverse judge currently receives one document + one finding. If OpenSpec artifacts are larger (proposal + spec + design), judge accuracy may degrade from context dilution.

### The case for NOT migrating

If the primary goal remains R&D — understanding what makes adversarial review work, improving precision from 9-27% to a useful range, and validating the eval framework — then adding OpenSpec integration is a distraction from the core research questions. The orchestration layer is a convenience, not a research contribution. Building a thin `parallax:orchestrate` wrapper that calls existing skills is simpler than integrating with an external ecosystem.

**When migration makes sense:** When parallax moves from R&D to production use — when the review quality is high enough that the question shifts from "does this work?" to "how do people use this in their workflow?" At that point, plugging into an established workflow (OpenSpec) is clearly better than asking users to adopt a parallax-specific pipeline.

---

## Concrete Next Steps

### Phase 0: Validation (before committing to migration)

1. Install OpenSpec locally, run it on a small feature in this repo
2. Examine the generated design artifact format — what does `parallax:review` need to parse?
3. Run existing reviewer agents against an OpenSpec-generated design (manual, no integration code)
4. Evaluate: do the agents produce useful findings on OpenSpec artifacts, or do they need prompt adjustments?

**Decision gate:** If agents produce comparable precision/recall on OpenSpec artifacts vs. standalone docs, proceed. If quality degrades significantly, investigate prompt adaptation before continuing.

### Phase 1: Lightweight integration (if Phase 0 passes)

5. Modify `review/SKILL.md` to accept OpenSpec artifact paths as input
6. Create one new dataset with a frozen OpenSpec-generated design + curated ground truth
7. Run eval framework against new dataset — compare precision/recall to existing baselines
8. Document findings in ADR-009

### Phase 2: Orchestration migration (if Phase 1 shows parity)

9. Close Issue #52 (orchestrate design decision) with "use OpenSpec" rationale
10. Retire `requirements/SKILL.md` as standalone — repurpose agents if useful
11. Write integration wrapper: OpenSpec ff → parallax review → OpenSpec apply
12. Update CLAUDE.md to reflect new workflow

### Phase 3: Eval framework adaptation

13. Create second corpus using OpenSpec-generated artifacts (satisfies Issue #92)
14. Update eval tasks to handle multi-file input from `openspec/specs/`
15. Validate judge accuracy on new artifact format
16. Establish new baselines

**Dependencies:**
- Phase 1 depends on Phase 0 decision gate
- Phase 2 depends on Phase 1 showing precision/recall parity
- Phase 3 can run in parallel with Phase 2

---

## Appendix: Detailed Ecosystem Comparison

| Dimension | Parallax | OpenSpec | Spec Kit |
|-----------|----------|----------|----------|
| **Primary value** | Adversarial review | Spec capture + orchestration | Constitutional governance |
| **Review model** | 6 automated agents, parallel | Human intent review | Consistency analysis |
| **Eval framework** | Inspect AI, 2-tier scoring | None | None |
| **Spec persistence** | Git + CLAUDE.md | Git + `openspec/specs/` | Git + `.specify/` |
| **Orchestration** | Unbuilt (Issue #52) | Slash commands | 8-phase workflow |
| **Agent support** | Claude Code only | 30+ platforms | 8+ platforms |
| **Maturity** | R&D, 55 commits | Production, 25k stars | Fragmented |
| **Finding format** | Structured JSONL | N/A | N/A |
| **Ground truth** | 19 curated findings, 2 datasets | N/A | N/A |
| **Philosophy** | Multi-angle adversarial critique | Fluid spec-driven development | Constitutional determinism |

## Appendix: Reusable Prompt for Deep Analysis

The following prompt can be used in a fresh Claude Code session with full parallax repo context to re-run or extend this analysis:

```markdown
# Deep Analysis: Parallax vs. OpenSpec vs. Spec Kit

## Context

I maintain the `parallax` repo (github.com/nichenke/parallax) — a skill and eval
framework for multi-perspective adversarial design review in AI-assisted development.
It was started without knowledge of OpenSpec or Spec Kit. I need you to do a deep
comparative analysis and migration strategy.

## What Parallax Is (Current State)

Parallax explores automated multi-perspective design review orchestration. Core thesis:
design flaws survive review because review happens from one perspective.

**What exists (built, working):**
- 2 production skills: `review/SKILL.md` (6 parallel adversarial reviewers + synthesizer)
  and `requirements/SKILL.md` (5 parallel requirement validators)
- 11 reviewer agents with distinct critical lenses (Assumption Hunter, Edge Case Prober,
  Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout,
  plus 5 requirements-stage agents)
- Eval framework on Inspect AI: two-tier scoring with reverse judge precision
  (Haiku asks "is this finding genuine?") + must-find recall (curated ground truth)
- 2 curated datasets (19 ground truth findings) with frozen document snapshots
- 3 completed review cycles with full finding artifacts
- 8 ADRs documenting key architectural decisions
- JSONL finding schema with phase/severity/confidence metadata
- Finding classification by pipeline phase (survey/calibrate/design/plan)

**What's planned but unbuilt:**
- `parallax:orchestrate` — full pipeline controller (Issue #52, design decision pending)
- Second corpus for black-box validation (Issue #92)
- Quality rubric definition (FR-QUALITY-1)
- Multi-model comparison evals (deferred to Phase 3+)

**Current eval metrics (N=1, point samples):**
- Reviewer precision: 9-27% (constraint-finder weakest at 9%/0% recall)
- Judge accuracy: 72-75% (Haiku at T=0.0)
- Confidence stratification: generally correct direction (high-conf > low-conf precision)
- Statistical power insufficient at current N — need N=25-30 per Phase 2

**Key design decisions:**
- BUILD adversarial review (novel), LEVERAGE Inspect AI + Haiku judge
- Per-reviewer eval decomposition (not full-skill orchestration)
- Reverse judge for precision (solves context contamination in ground truth matching)
- Absence-detection framing (reviewers look for what's NOT stated)
- Git-as-audit-trail (every re-review is a diffable commit)
- SRE-style finding format (blast radius, failure mode, mitigation)

## What OpenSpec Is

Spec-driven development framework from Fission AI (github.com/Fission-AI/OpenSpec,
~25k stars). Universal planning layer for AI coding assistants.

**Core concepts:**
- Proposal → spec → design → tasks pipeline via slash commands
- Living specs as first-class git artifacts in `openspec/specs/`
- Intent-focused review (reviewers examine proposals and spec deltas, not code)
- Agent-agnostic (30+ platforms including Claude Code, Cursor, Copilot)
- Brownfield-ready, lightweight, iterative
- Persistent context across sessions via repo-stored specs

**Commands:** `/openspec:new`, `/openspec:proposal`, `/openspec:ff` (fast-forward),
`/openspec:apply`

**Gap:** No adversarial review. Intent review is human-driven, not automated multi-agent.

## What Spec Kit Is

Constitutional specification-driven development — a methodology pattern implemented
by multiple repos (plaesy/spec-kit, specpulse/specpulse, IBM/iac-spec-kit, others).

**Core concepts:**
- Constitutional governance (project principles as guardrails)
- 8-phase workflow: constitute → specify → plan → tasks → implement → analyze →
  clarify → validate
- Multi-artifact consistency validation (constitution ↔ spec ↔ plan ↔ code)
- Zero-ambiguity protocol with anti-hallucination mechanisms
- File structure in `.specify/` directory
- Platform-agnostic (8+ AI coding tools)

**Gap:** Analyze phase is consistency checking, not adversarial criticism.
Ecosystem is fragmented across 5+ implementations with no clear winner.

## Your Task

Read the full parallax repo deeply — every doc, every agent, every eval, every issue.
Then produce:

### 1. Durability Assessment
For each major parallax component, classify as:
- **DURABLE** — genuinely novel, not addressed by either ecosystem
- **REPLACEABLE** — solved better by OpenSpec or Spec Kit
- **AUGMENTABLE** — keep but integrate with ecosystem tooling

Justify each classification with specific evidence from all three systems.

### 2. Ecosystem Recommendation
Which ecosystem (OpenSpec or Spec Kit) should be the primary workflow, and why?
Consider: maturity, philosophical alignment, migration effort, what Parallax loses
vs. gains. Present tradeoffs explicitly.

### 3. Migration Architecture
Design how Parallax's durable components plug into the chosen ecosystem. Specifically:
- Where in the ecosystem's pipeline does adversarial review inject?
- What Parallax skills/agents/evals transfer as-is vs. need adaptation?
- What gets deleted from parallax?
- What new integration code is needed?

### 4. Risk Assessment
What does Parallax lose by migrating? What capabilities or design properties
of the current standalone approach don't survive integration? Are there
architectural assumptions in the eval framework that break under a different
orchestration model?

### 5. Concrete Next Steps
Ordered list of migration actions with dependencies. What do I do first,
second, third? What experiments validate the approach before full commitment?

## Constraints
- Be direct. This is for a principal SWE with 25 years experience.
- No scoring systems or letter grades. Use severity levels if needed.
- Stress-test your own recommendations — surface counterarguments.
- If you'd recommend NOT migrating, say so and explain why.
```
