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

## Branch Discipline

**Never commit directly to `main`.** Always use feature branches + pull requests.

- A pre-commit hook enforces this (see `hooks/pre-commit`)
- New clones: Run `git config core.hooksPath hooks` to enable the hook

## Worktree Workflow

Always `cd` to the worktree first via a full absolute path (`cd /full/path && ...`) so all subsequent commands run in the correct context. Never use `make -C` or relative paths like `.worktrees/...` — they fail when shell CWD doesn't match.

**Venv setup in worktrees:** When a worktree needs Python dependencies, run `make install` from the worktree directory — do not run separate `python3 -m venv` + pip commands. The `make install` target creates `.venv-evals/`, installs `.[dev]`, and sets up required directories in one step. (Doc-only or config-only worktrees that need no Python can skip this.)

## Subagent Tool Discipline

Subagents inherit these rules. **Use dedicated tools, not bash equivalents:**
- **Read files:** Use `Read` tool — never `cat`, `head`, `tail`
- **Edit files:** Use `Edit` tool — never `sed`, `awk`
- **Search file content:** Use `Grep` tool — never `grep`, `rg`
- **Find files:** Use `Glob` tool — never `find`, `ls`
- **Write files:** Use `Write` tool — never `echo >`, heredocs

**Bash is only for commands that have no dedicated tool equivalent:** `git show`, `git diff`, `git log`, `npm`, `docker`, etc.

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

## Model Tiering Strategy

- **`opusplan` mode:** Opus for planning/analysis, Sonnet for execution. Default for this repo.
- **Planning phases** (Opus): Brainstorming, requirements review, design review, architecture decisions, finding synthesis
- **Execution phases** (Sonnet): Code edits, file operations, mechanical subagent tasks, formatting
- **Subagents:** Default to Sonnet (`model: "sonnet"` in Task tool) unless the task requires deep analysis
- **Superpowers integration:** The `using-superpowers` skill intercepts `EnterPlanMode` and routes through brainstorming. Plan mode = Opus engagement for complex analysis.

<!-- TODO: Investigate Codex equivalent of opusplan model tiering. Codex CLI may have different model routing. Track in Issue #4. -->

## Eval Design Guardrails

Rules that protect the precision metric from well-intentioned corruption.

### The genuineness gate is binary

The reverse judge scores each finding GENUINE or NOT_GENUINE. Do not introduce partial credit, confidence weighting, or "valuable ambiguity" exceptions. Once you allow NOT_GENUINE findings to score positively because they seem humanly useful, every false positive gets a defense and the precision metric becomes meaningless.

**The right answer for humanly-useful NOT_GENUINE findings:** surface them in the review notes tier (Issue #83) with the judge's reasoning, clearly separated from actionable findings. Keep the gate binary; make the output richer.

### Must_find reconciliation after document freeze

After freezing the source document for an eval dataset, validate every `must_find.jsonl` entry against the frozen document. Any entry the judge calls NOT_GENUINE on the frozen doc must be investigated — the finding may have been valid against an earlier document version but addressed by the time of freeze. Do not assume must_find entries remain valid across document revisions.

**Workflow:** ground truth creation → document freeze → must_find reconciliation pass (judge all entries against frozen doc) → dataset finalized.

### Experiment corpus size

Do not run comparative experiments (prompt A vs. prompt B) with fewer than 10 samples per class. Differences in small-N rates (2/4 vs 0/4) are not statistically distinguishable from noise. Label runs below this threshold as "exploratory" in the write-up and do not derive ADR decisions from accuracy comparisons alone — cost and latency differences remain valid evidence regardless of N.

## Workflow Preferences

- **Local-first development** — create files locally, test, then commit
- **Security-conscious** — tokens never in LLM context, credential separation between agents
- **Pragmatic** — build to learn, YAGNI ruthlessly
- **Prototype-first** — working code over design docs when exploring unknowns
- **Timezone:** Mountain Time (America/Denver)
