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
