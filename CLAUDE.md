# Parallax — Working Context

**Design looks different depending on where you stand. Parallax makes you look from everywhere.**

A skill and eval framework for multi-perspective design orchestration in AI-assisted software development.

## What This Repo Is

A public R&D repo exploring how to automate the multi-phase design process:
brainstorm → requirement refinement → design → adversarial review → plan → execution

The name comes from parallax — the apparent shift in an object's position when observed from different vantage points. The difference between views reveals truth. One-perspective design review is parallax error.

## Project Tracks (GitHub Issues)

Each track is an independent investigation area, suitable for a separate session:

1. **Competing skills & meta-skill landscape** — what exists, what could we leverage, periodic SOTA scanning
2. **Black-box testing framework** — validation criteria, test case design, outcome data collection
3. **Autonomous agent R&D architecture** — can an AI agent build and test skills autonomously? Security implications
4. **Agent teams & Codex evaluation** — multi-model review teams, performance/cost trade-offs
5. **Skill testing eval/grader framework** — unit/integration/smoke/perf/cost/ablation/adversarial testing for skills
6. **Claude-native background automation** — Agent SDK + MCP + cron for long-running research
7. **Test cases** — black-box validation using real design sessions

## Key Decisions Made

- **Name:** Parallax (parallax error = one-angle review, baseline = reviewer diversity, triangulation = finding consolidation)
- **Namespace:** `parallax:survey`, `parallax:calibrate`, `parallax:review`, `parallax:orchestrate`, `parallax:eval`
- **Public repo:** Useful beyond personal infra, helps at work too
- **Core differentiator:** Adversarial design review — no production tools exist for this (validated by Mitsubishi's Jan 2026 proprietary approach)
- **Build vs leverage:** BUILD adversarial review (novel), LEVERAGE LangGraph + Inspect AI + Claude Code Swarms (mature)
- **Self-improvement:** DEFER to Phase 3+ (research-stage, not MVP-critical)

## Architecture Notes

### Planned Plugin Structure
```
parallax/
├── plugin.json
├── skills/
│   ├── survey/SKILL.md        — research and brainstorming
│   ├── calibrate/SKILL.md     — requirement refinement (MoSCoW, anti-goals)
│   ├── review/SKILL.md        — adversarial multi-agent review
│   ├── orchestrate/SKILL.md   — full pipeline orchestration
│   └── eval/SKILL.md          — skill testing framework
├── agents/
│   ├── design-reviewer/       — adversarial design critic
│   ├── security-reviewer/     — security-focused review
│   ├── consistency-checker/   — design-to-plan alignment
│   └── eval-grader/           — test result evaluation
├── docs/
│   ├── problem-statements/
│   ├── research/
│   └── test-cases/
└── evals/                     — Inspect AI eval definitions
```

### Key Frameworks to Integrate
- **Inspect AI** (inspect.aisi.org.uk) — agent evaluation, 100+ pre-built evals, supports Claude + Codex
- **LangGraph** — stateful graph workflows for pipeline control
- **Claude Code Swarms** — native multi-agent via TeammateTool
- **Braintrust** — LLM-as-judge for design quality scoring
- **Promptfoo** — prompt iteration for individual agent tuning

### Existing Skills This Composes (superpowers plugin)
- `brainstorming` → parallax:survey extends this with structured research
- `writing-plans` → parallax:orchestrate invokes this after design approval
- `executing-plans` → downstream of parallax pipeline
- `dispatching-parallel-agents` → parallax:review uses this pattern
- `requesting-code-review` → parallax:review adapts this for design review

## Related Repos

| Repo | Relationship |
|------|-------------|
| `nichenke/openclaw` (private) | Origin — problem statement emerged from real OpenClaw design sessions |
| `~/src/claude-ai-customize` (local) | Test case candidate — partial (plan complete, execution pending) |

## Brainstorm Session Context (2026-02-15)

This repo was created during a brainstorming session that explored 7 topics:

0. **Competing skills landscape** — landscape analysis complete (docs/research/landscape-analysis.md)
1. **Black-box testing** — identified 3 real test cases from OpenClaw (Second Brain Design, Semantic Memory Search, Phase 4 Plan) + 1 partial (claude-ai-customize)
2. **Bill/Ryker agent architecture** — separate agent (Ryker) with isolated PAT, separate Docker network, Opus for research is worth the security trade-off
3. **Public repo strategy** — this repo
4. **Agent teams + Codex** — hybrid strategy: Claude for design phases, Codex for execution/eval
5. **Skill testing framework** — Inspect AI as foundation, need custom design evals
6. **Claude-native automation** — OpenClaw cron → Agent SDK → MCP → Slack checkpoints → GitHub Issues/PRs

### Test Case Inventory

| Test Case | Source | Phases Present | Review Artifacts | Best For |
|-----------|--------|---------------|-----------------|----------|
| Second Brain Design | openclaw | Design → 3 reviews → Rev 4 | 1000+ lines, 40+ findings | Full review orchestration |
| Semantic Memory Search | openclaw | Design → review → revised → plan | Referenced but missing | Iteration detection |
| Phase 4 Plan | openclaw | Options → plan (no review) | None | Missing review detection |
| claude-ai-customize | local | Plan complete, execution pending | None | Phase detection, continuation |

### Validation Criteria for Orchestrator
1. Correctly identifies project phase
2. Spawns appropriate parallel reviews, consolidates findings
3. Catches design-to-plan inconsistencies
4. Enforces review artifact existence when status claims review happened
5. Tracks finding resolution (accepted/mitigated/deferred)
6. Measurable: cost and time overhead vs manual orchestration

### Outcome Data Needed for Testing
- Session recordings (time, prompts, decisions)
- Finding counts and severity distributions
- Iteration counts before convergence
- Design-to-plan consistency scores
- Token usage per phase

## Workflow Preferences

- **Local-first development** — create files locally, test, then commit
- **Security-conscious** — tokens never in LLM context, credential separation between agents
- **Pragmatic** — don't over-engineer; YAGNI ruthlessly
- **SRE-influenced** — premortem thinking, error budgets, blast radius scoping
- **Timezone:** Mountain Time (America/Denver)
