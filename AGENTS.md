# Parallax — Project Context

> See CLAUDE.md for full project context. This file adds Codex-specific guidance.

**Design looks different depending on where you stand. Parallax makes you look from everywhere.**

A skill and eval framework for multi-perspective design orchestration in AI-assisted software development.

## What This Repo Is

A public R&D repo exploring how to automate the multi-phase design process:
brainstorm -> requirement refinement -> design -> adversarial review -> plan -> execution

The name comes from parallax — the apparent shift in an object's position when observed from different vantage points. The difference between views reveals truth. One-perspective design review is parallax error.

## Current State

- **Working prototype:** `parallax:review` — adversarial multi-agent design review skill
- **Three full review cycles complete** against our own design doc (v1: 44, v2: 55, v3: 83 findings)
- **6 reviewer agents** with distinct critical lenses, plus a synthesizer agent
- **Core novel contribution:** Finding classification routes errors back to the pipeline phase that failed (survey/calibrate/design/plan)
- **Branch:** `feature/sync-design-doc-v1-dispositions` — v3 review artifacts on disk, not yet committed

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full project context, decisions, architecture |
| `skills/review/SKILL.md` | Review skill orchestration instructions |
| `agents/*.md` | Individual reviewer agent prompts (6 reviewers + 1 synthesizer) |
| `docs/plans/2026-02-15-parallax-review-design.md` | Design doc for the review skill |
| `docs/problem-statements/design-orchestrator.md` | Requirements/problem statement |
| `docs/reviews/parallax-review-v1/` | Review outputs (v3, latest) |
| `docs/reviews/parallax-review-v1/summary.md` | Synthesized findings with dispositions |

## Running the Review Skill

The review skill (`skills/review/SKILL.md`) was built for Claude Code's plugin system. To run it on any LLM agent:

### Inputs
- **Design artifact:** `docs/plans/2026-02-15-parallax-review-design.md`
- **Requirements:** `docs/problem-statements/design-orchestrator.md`
- **Topic label:** e.g., `parallax-review-v1`

### Agent Prompts
Each file in `agents/` contains a reviewer prompt with YAML frontmatter (metadata — ignore) and a system prompt (the actual instructions). The reviewers are:

| Agent | File | Focus |
|-------|------|-------|
| Assumption Hunter | `agents/assumption-hunter.md` | Implicit assumptions, unstated dependencies |
| Edge Case Prober | `agents/edge-case-prober.md` | Boundary conditions, failure modes |
| Requirement Auditor | `agents/requirement-auditor.md` | Requirements coverage, gaps |
| Feasibility Skeptic | `agents/feasibility-skeptic.md` | Implementation viability, cost |
| First Principles | `agents/first-principles.md` | Fundamental approach validity |
| Prior Art Scout | `agents/prior-art-scout.md` | Existing solutions, prior work |
| Review Synthesizer | `agents/review-synthesizer.md` | Consolidation, deduplication, verdict |

### Process
1. Read both input documents
2. For each reviewer: apply the agent prompt to the design+requirements, write output to `docs/reviews/<topic>/<agent-name>.md`
3. After all reviewers: apply the synthesizer prompt to all reviewer outputs, write `docs/reviews/<topic>/summary.md`
4. Present the verdict and findings

### Adaptation Notes
- **Claude Code dispatches reviewers in parallel** via its `Task` tool. Without parallel dispatch, run sequentially — the prompts are independent.
- **Agent YAML frontmatter** (`name`, `model`, `color`, `tools`) is Claude Code metadata. The system prompt content after the `---` delimiter is what matters.
- **Tool names** (`Read`, `Grep`, `Glob`, `Write`) are Claude Code tools. Map to your agent's equivalents.

## Development Philosophy

- **Quality bar:** Senior+ engineer audience. Think clearly, articulate tradeoffs, justify decisions.
- **Prototype-first:** Build to understand, not design to death.
- **YAGNI ruthlessly:** Build what's needed now, defer what isn't.
- **SRE-influenced:** Premortem thinking, error budgets, blast radius scoping.

## Open Design Questions

1. **Workflow guardrails:** Should parallax embed a "check for relevant skills before acting" hook (like the `using-superpowers` pattern in Claude Code plugins), or should the `orchestrate` skill enforce ordering? Tradeoff: hooks are always-on but add friction; orchestrate skill is explicit but only works when invoked.

2. **JSONL output format:** 4-reviewer consensus across v2+v3 that findings need a machine-readable format. Schema not yet defined.

3. **Cross-iteration tracking:** Finding IDs for linking across review cycles. Currently done by synthesizer matching, not by stable IDs.

4. **Build vs leverage:** Adversarial review is novel (BUILD). Orchestration/eval may be better served by LangGraph + Inspect AI (LEVERAGE). Evaluation deferred to empirical testing.

## Architecture

Pipeline of independently useful skills:
```
parallax:survey     -> research and brainstorming
parallax:calibrate  -> requirement refinement (MoSCoW, anti-goals)
parallax:review     -> adversarial multi-agent review [IMPLEMENTED]
parallax:orchestrate -> full pipeline orchestration
parallax:eval       -> skill testing framework
```

Only `review` is implemented. Others are planned.
