# Deep Analysis: Parallax vs. OpenSpec vs. Spec Kit (v2 — with EARS/BDD Context)

## Context

I maintain the `parallax` repo (github.com/nichenke/parallax) — a skill and eval
framework for multi-perspective adversarial design review in AI-assisted development.
It was started without knowledge of OpenSpec or Spec Kit. Separately, an SDD research
report (`docs/research/sdd-research-report.md`) proposed a three-layer architecture
using OpenSpec + EARS/BDD hybrid requirements. I need you to do a deep comparative
analysis, evaluate two migration strategies, and critically challenge assumptions.

## What Parallax Is (Current State)

Parallax explores automated multi-perspective design review orchestration. Core thesis:
design flaws survive review because review happens from one perspective.

**What exists (built, working):**
- 2 production skills: `review/SKILL.md` (6 parallel adversarial reviewers + synthesizer)
  and `requirements/SKILL.md` (5 parallel requirement validators)
- 11 reviewer agents with distinct critical lenses (Assumption Hunter, Edge Case Prober,
  Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout,
  plus 5 requirements-stage: Problem Framer, Scope Guardian, Constraint Finder,
  Success Validator, Assumption Hunter)
- Eval framework on Inspect AI: two-tier scoring with reverse judge precision
  (Haiku asks "is this finding genuine?") + must-find recall (curated ground truth)
- 2 curated datasets (19 ground truth findings) with frozen document snapshots
- 3 completed review cycles with full finding artifacts (v1: 44, v2: 55, v3: confidence baseline)
- 8 ADRs documenting key architectural decisions (ADR-005 through ADR-008 cover
  eval framework choices: rejected G-Eval, Factuality, RAGAS with specific rationale)
- JSONL finding schema with phase/severity/confidence metadata
- Finding classification by pipeline phase (survey/calibrate/design/plan)
- Synthesizer agent for finding consolidation (dedup, severity classification, phase routing)

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
- Per-reviewer eval decomposition (ADR-006: test agents independently, not full skill)
- Reverse judge for precision (solves context contamination in ground truth matching)
- Absence-detection framing (reviewers look for what's NOT stated)
- Git-as-audit-trail (every re-review is a diffable commit)
- SRE-style finding format (blast radius, failure mode, mitigation)
- Genuineness gate is binary (no partial credit — protects precision metric)

## What OpenSpec Is

Spec-driven development framework from Fission AI (github.com/Fission-AI/OpenSpec,
~25k stars). Universal planning layer for AI coding assistants.

**Core concepts:**
- Proposal → spec → design → tasks pipeline via slash commands
- Living specs in `openspec/specs/`; change deltas in `openspec/changes/`
  with `ADDED`/`MODIFIED`/`REMOVED` markers
- Custom schemas in YAML + markdown templates in `openspec/schemas/`
- Three-layer AI instructions: context, rules, templates (assembled dynamically)
- Agent-agnostic (30+ platforms including Claude Code, Cursor, Copilot)
- Brownfield-native via two-folder model

**Known gaps (from SDD research):**
- Hardcoded spec parser (issue #666) — affects EARS heading customization
- No review gate native (High severity)
- No PM-layer elicitation (JTBD, impact mapping, MoSCoW)
- No cross-repo spec composition

## What Spec Kit Is

Constitutional specification-driven development — a methodology pattern implemented
by multiple repos (plaesy/spec-kit, specpulse/specpulse, IBM/iac-spec-kit, others).

**Core concepts:**
- Constitutional governance (project principles as guardrails)
- 8-phase workflow: constitute → specify → plan → tasks → implement → analyze →
  clarify → validate
- Multi-artifact consistency validation
- Zero-ambiguity protocol with anti-hallucination mechanisms

**Assessment:** Experimental, brownfield-weak, fragmented across 5+ implementations.
Not recommended as primary tool per SDD research.

## The EARS/BDD Hybrid Model (from SDD Research)

A key finding from separate SDD research: pure EARS (`SHALL`/`WHEN`/`IF`) is a
category error for LLM-based skills because skill behavior is probabilistic, not
deterministic. The hybrid model:

| Layer | Format | Rationale |
|---|---|---|
| Hook / tool / linter requirements | Pure EARS | Deterministic, event-driven, testable |
| Skill behavioral contracts | BDD Given/When/Then | Observable outcomes, acceptance-testable |
| Skill design intent | JTBD + SHALL/SHOULD/MAY tiers | Captures 'why' + constraint precision |
| Non-functional properties | RFC 2119 SHALL/SHOULD/MAY | Precision without false determinism |

The SDD report proposes a three-layer architecture:
- **Layer 1:** Requirements elicitation (custom skill) — JTBD → impact map →
  MoSCoW/YAGNI → EARS/BDD → gap check. Output: `pre-proposal.md`
- **Layer 2:** SDD lifecycle (OpenSpec) — proposal → specs → design → tasks →
  archive. Review gate blocks apply.
- **Layer 3:** Execution (Claude Code / Codex)

## Two Migration Strategies to Evaluate

### Strategy A: OpenSpec + Parallax Review Gate (Simple)

```
/openspec:proposal → /openspec:ff → parallax:review → /openspec:apply
```

Single injection point. Requirements-stage agents retired. Minimal build scope.

### Strategy B: Three-Layer + Parallax at Two Points (Full)

```
Layer 1: EARS/BDD elicitation → parallax requirements agents validate → pre-proposal.md
Layer 2: OpenSpec lifecycle → parallax design agents review → apply
Layer 3: Execution
```

Two injection points. All 11 agents used. Significant build scope (5 new components).

## Your Task

Read the full parallax repo deeply — every doc, every agent, every eval, every issue,
and especially `docs/research/sdd-research-report.md`. Then produce:

### 1. Durability Assessment
For each major parallax component, classify as:
- **DURABLE** — genuinely novel, not addressed by either ecosystem or EARS/BDD model
- **REPLACEABLE** — solved better by OpenSpec, Spec Kit, or EARS/BDD
- **AUGMENTABLE** — keep but integrate with ecosystem tooling

Pay special attention to the requirements-stage agents (Problem Framer, Scope
Guardian, Constraint Finder, Success Validator, Assumption Hunter). They have
9-27% precision on unstructured documents and have never been tested on
EARS/BDD-structured input. Evaluate their value based on demonstrated
effectiveness, not on the investment made in building them. Watch for sunk-cost
reasoning — "preserves the tuning investment" is not a valid justification.
The question is: would a purpose-built EARS linter be simpler and more effective
than repurposing these agents?

### 2. Strategy Comparison
Evaluate Strategy A vs Strategy B on:
- **Research value:** Which helps answer "does adversarial review work?" faster?
- **Build scope:** What's the effort difference?
- **Quality impact:** Does EARS/BDD-structured input measurably improve review output?
- **Premature optimization risk:** Is Strategy B building a production system before
  the core hypothesis is validated?
- **Garbage-in risk:** Does Strategy A skip input quality and suffer lower precision?

### 3. Ecosystem Recommendation
Which ecosystem should be primary, and when does the EARS/BDD layer justify its cost?
Challenge the SDD report's assumption that Layer 1 is necessary — is requirements
elicitation a distraction from review quality improvement?

### 4. Migration Architecture
Design how parallax components plug into the chosen strategy. Show injection points,
what transfers, what needs adaptation, what gets deleted.

### 5. Risk Assessment
What does parallax lose by migrating? What architectural assumptions break?
Specific risks to evaluate:
- Per-reviewer eval decomposition (ADR-006) with multi-file OpenSpec artifacts
- EARS category error propagation (SHALL for probabilistic behavior)
- Judge context dilution with larger OpenSpec artifacts
- Elicitation skill quality as a new failure mode

### 6. Concrete Next Steps
Ordered list with decision gates. Include the EARS/BDD controlled experiment:
structured vs. unstructured input documents, same reviewer agents, compare
precision/recall. This tests the "garbage in" hypothesis before committing to
Layer 1 construction.

## Constraints
- Be direct. This is for a principal SWE with 25 years experience.
- No scoring systems or letter grades. Use severity levels if needed.
- Stress-test your own recommendations — surface counterarguments.
- Challenge the SDD report's conclusions where evidence is thin.
- The core research question is still "does multi-agent adversarial review produce
  genuinely useful findings?" — don't lose that thread in architecture astronautics.
- If you'd recommend deferring ALL migration, say so and explain why.
- Watch for sunk-cost reasoning in your own analysis. "We built X, so let's find
  a use for X" is not the same as "X solves problem Y." Evaluate each component
  on demonstrated value, not development investment.
