# Parallax — Working Context

**Design looks different depending on where you stand. Parallax makes you look from everywhere.**

A skill and eval framework for multi-perspective design orchestration in AI-assisted software development.

## What This Repo Is

A public R&D repo exploring how to automate the multi-phase design process:
brainstorm → requirement refinement → design → adversarial review → plan → execution

The name comes from parallax — the apparent shift in an object's position when observed from different vantage points. The difference between views reveals truth. One-perspective design review is parallax error.

## Development Philosophy

- **Quality bar:** This should resonate with experienced senior+ engineers. Think clearly, articulate tradeoffs, justify decisions.
- **Prototype-first:** Exhaustive research matters, but not at the expense of building. We learn more from a working prototype than another design doc. Build to understand, not design to death.
- **YAGNI ruthlessly:** Don't over-engineer. Build what's needed now, defer what isn't.
- **SRE-influenced:** Premortem thinking, error budgets, blast radius scoping.

## Project Tracks (GitHub Issues)

Each track is an independent investigation area, suitable for a separate session:

1. **Competing skills & meta-skill landscape** — what exists, what could we leverage, periodic SOTA scanning
2. **Black-box testing framework** — validation criteria, test case design, outcome data collection
3. **Autonomous agent R&D architecture** — can an AI agent build and test skills autonomously? Security implications
4. **Agent teams & Codex evaluation** — multi-model review teams, performance/cost trade-offs
5. **Skill testing eval/grader framework** — unit/integration/smoke/perf/cost/ablation/adversarial testing for skills
6. **Claude-native background automation** — Agent SDK + MCP + cron for long-running research
7. **Test cases** — black-box validation using real design sessions

## Key Decisions

- **Name:** Parallax (parallax error = one-angle review, baseline = reviewer diversity, triangulation = finding consolidation)
- **Namespace:** `parallax:survey`, `parallax:calibrate`, `parallax:review`, `parallax:orchestrate`, `parallax:eval`
- **Architecture:** Pipeline of skills (not a monolithic single skill). Each namespace segment is independently useful.
- **Public repo:** Useful beyond personal infra, applicable to work contexts
- **Core differentiator:** Adversarial design review — no production tools exist for this (validated by Mitsubishi's Jan 2026 proprietary approach)
- **Build vs leverage:** BUILD adversarial review (novel), LEVERAGE LangGraph + Inspect AI + Claude Code Swarms (mature)
- **Iteration tracking:** Git commits per design iteration (full history, diffable)
- **Fatal review findings:** TBD during prototyping — test both "always escalate" and "attempt one redesign pass"
- **Calibrate skill:** Standalone (useful outside the pipeline)
- **Self-improvement:** DEFER to Phase 3+ (research-stage, not MVP-critical)
- **Review agent count:** Empirical — determine optimal N via eval framework

## Budget & Tooling

**Monthly budget:** $2000 (currently projects ~$200-500/month actual spend — most tools are free/OSS)

### Available Tools

| Tool | Access | Cost |
|------|--------|------|
| Claude (interactive) | MAX subscription | Covered |
| Claude API (evals) | Bedrock (work) + direct | ~$150-400/mo depending on model mix |
| Codex | OpenAI partnership (work) | Covered for interactive; API ~$50-100/mo for evals |
| Cursor | Work license | Covered |
| Inspect AI | Open source (MIT) | Free — eval runner, you pay API tokens |
| LangGraph | Open source (MIT) | Free — orchestration framework |
| Promptfoo | Open source | Free — prompt testing, 10k probes/month |
| Braintrust | Free tier | 1M spans, 10k scores — months of prototyping |
| LangSmith | Free tier | 5k traces/month — sufficient for early R&D |
| Claude Agent SDK | Free | Pay API token costs only |

### Cost Strategy
- **Batch API** for all non-interactive eval runs (50% discount)
- **Prompt caching** for repeated system prompts across evals (90% input cost reduction on cache hits)
- **Model tiering:** Haiku for simple evals, Sonnet for review agents, Opus sparingly for adversarial deep analysis
- Claude is the primary model. Codex for comparison evals and execution-phase experiments.
- **Codex portability checks:** Run skills on Codex CLI early to surface Claude-specific assumptions. Budget already allocated ($50-100/mo). Multi-LLM review (Claude + GPT + Gemini on same artifact) deferred to eval phase.

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

### Key Frameworks
- **Inspect AI** — agent evaluation, 100+ pre-built evals, supports Claude + Codex
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

## Test Cases

Four real design sessions identified for black-box validation. See `docs/brainstorm-2026-02-15.md` for full details.

| Test Case | Source | Best For |
|-----------|--------|----------|
| Second Brain Design | openclaw | Full review orchestration (3 reviews, 40+ findings) |
| Semantic Memory Search | openclaw | Iteration detection (artifact mismatch) |
| Phase 4 Plan | openclaw | Missing review detection |
| claude-ai-customize | local | Phase detection, continuation |

## Related Repos

| Repo | Relationship |
|------|-------------|
| `nichenke/openclaw` (private) | Origin — problem statement emerged from real OpenClaw design sessions |
| `~/src/claude-ai-customize` (local) | Test case candidate — partial (plan complete, execution pending) |

## Context Management

Context compaction is a known constraint. This repo may be worked on from multiple machines.

### Portable (travels with git)
- **CLAUDE.md** — authoritative project context, always loaded by Claude Code on any clone
- **docs/** — research, analysis, session captures, problem statements

### Machine-local (not in git)
- **`.claude/projects/.../memory/MEMORY.md`** — local paths, ephemeral session notes, current task state. Path-encoded to filesystem, won't exist on other machines.

### Session Discipline
- **Heavy subagent use** — delegate research and exploration to subagents to protect main context window
- **End of session** — promote any important decisions from memory to CLAUDE.md (so they travel with git)
- **Brainstorm capture** — raw session notes go in `docs/`, distilled decisions go in CLAUDE.md

## Workflow Preferences

- **Local-first development** — create files locally, test, then commit
- **Security-conscious** — tokens never in LLM context, credential separation between agents
- **Pragmatic** — build to learn, YAGNI ruthlessly
- **Prototype-first** — working code over design docs when exploring unknowns
- **Timezone:** Mountain Time (America/Denver)
