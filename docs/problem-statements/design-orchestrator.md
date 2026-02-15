# Design Orchestrator — Problem Statement

**Date:** 2026-02-15
**Status:** Problem statement (not yet designed)
**Origin:** Captured during a real design session where the manual orchestration overhead became the bottleneck

## The Problem

When building features with AI coding assistants (Claude Code, Codex, etc.), teams follow a multi-phase process:

1. **Brainstorming** — explore the idea, ask clarifying questions, propose approaches
2. **Design** — write a design doc with architecture, trade-offs, risks
3. **Adversarial review** — launch subagents to find flaws in the design
4. **Iterate** — fix findings, re-review if needed
5. **Implementation plan** — write a step-by-step plan with exact commands
6. **Plan review** — adversarial + security review of the plan
7. **Iterate** — fix plan findings
8. **Execute** — implement task-by-task

Today this is done manually: the user invokes each skill, manually launches review subagents, manually consolidates findings, and decides when to iterate vs proceed.

**What we want:** A skill (or pipeline of skills) that orchestrates this entire process, with human checkpoints at decision points.

## Observed Pain Points (from real sessions)

1. **Three separate review agents** were launched manually, their findings consolidated by hand, and cross-referenced against each other. This took multiple user prompts and ~15 minutes of orchestration.

2. **Review findings revealed design flaws** (dimension mismatch, wrong file paths, incorrect ownership claims) that should have been caught during the research phase before the design was written.

3. **The design and plan diverged** — the plan correctly used `secrets.env` while the design doc said `gateway.env`. No automated consistency check caught this.

4. **Open questions in the design doc** were carried forward unresolved into the plan, creating speculative tasks ("try Option A, then Option B").

5. **No structured requirement refinement** — we jumped from "interesting idea" to "write the design" without formally prioritizing must-have vs nice-to-have. A major feature was dropped late, after significant design work.

## Desired Workflow

```
User: "I want to add semantic search to the memory system"
                    │
                    ▼
        ┌─ Research Phase (survey) ──────┐
        │  - Explore codebase context    │
        │  - Check docs / web search     │
        │  - Identify constraints        │
        └──────────┬─────────────────────┘
                   │
                   ▼
    ┌─► ┌─ Requirement Refinement ───────┐
    │   │  (calibrate)                   │
    │   │  - MoSCoW prioritization       │
    │   │  - Anti-goals (what NOT)       │
    │   │  - Success criteria            │
    │   │  - Human checkpoint ✓          │
    │   └──────────┬─────────────────────┘
    │              │
    │              ▼
    │   ┌─ Design Phase ────────────────┐
    │   │  - Write design doc           │
    │   │  - Adversarial review (sub)   │
    │   │  - Security review (sub)      │
    │   │  - Consolidate findings       │
    │   │  - Iterate until clean        │
    │   │  - Human checkpoint ✓         │
    │   └──────────┬────────────────────┘
    │              │
    │              ▼
    │   ┌─ Plan Phase ─────────────────┐
    │   │  - Write implementation plan  │
    │   │  - Adversarial review (sub)   │
    │   │  - Consistency check vs       │
    │   │    design doc                 │
    │   │  - Iterate until clean        │
    │   │  - Human checkpoint ✓         │
    │   └──────────┬────────────────────┘
    │              │
    │              ▼
    │   ┌─ Execution ──────────────────┐
    │   │  - Delegate to existing tools │
    │   │  - Classify errors:          │
    │   │    bug → fix in place        │
    │   │    spec wrong → escalate ◄───┼─── self-error-detecting
    │   └──────────┬────────────────────┘
    │              │
    │   (spec wrong)
    └──────────────┘
```

## Key Design Considerations

### Subagent Orchestration
- Reviews should run in parallel (design review + security review + domain review simultaneously)
- Findings should be automatically consolidated and deduplicated
- Severity should be normalized across reviewers
- **Persona engineering:** Each reviewer agent needs sharp, specific prompts — not "be critical" but a defined position with non-overlapping blind spots. Use the Instruction Sharpener / Position Mapper approach during prompt authoring. The prompts *are* the product. (See customization-01)
- **Prompt structure for caching:** System prompts should be structured as stable cacheable prefix (persona + methodology + output format) + variable suffix (the design being reviewed + iteration context). This is an architectural convention, not a feature — 90% input cost reduction on cache hits. Decide before building skills. (See customization-03)

### Requirement Refinement
- **Outcome-focused** — define what success looks like before defining how to get there. This has been the single biggest design quality lever in practice: missing a critical angle during requirements means the design optimizes for the wrong thing.
- MoSCoW (Must / Should / Could / Won't) or similar prioritization framework
- Anti-goals should be explicit (what are we deliberately NOT doing?)
- Document key **assumptions and constraints** explicitly — these become the review checklist. Any review finding that challenges an assumption is high-value and likely triggers a cycle restart, not a patch.
- Consider PM-style frameworks (Jobs-to-be-Done, etc.) but always in service of outcomes, not process

### Iteration Loops
- After adversarial review, auto-fix trivial findings (typos, wrong file paths) and re-review
- Escalate non-trivial findings to human with recommendations
- Track which findings have been addressed across iterations
- **Findings that challenge key assumptions or constraints are a success** — they likely trigger a full design cycle restart rather than incremental fixes. Archive the current plan (often useful as reference), restart the design phase with updated assumptions.
- **ADR-style finding documentation** — each review cycle produces a record of what was found, what was decided, and why. This builds a decision history that future reviewers (human and AI) can reference. Changing a decision is fine — undocumented decisions are the problem.
- **Correction compounding:** When the eval framework identifies false negatives (missed real flaws) or false positives (flagged non-issues), those become permanent calibration rules in the reviewer's system prompt. This is the compound-engineering "learnings" concept applied to prompt engineering — solve a miss once, never repeat it. **Note:** Prompt changes invalidate the cache prefix — not a concern during early iteration (prompts are changing constantly anyway), but worth flagging when changes happen so we build intuition about what's stable vs volatile. Cache optimization matters later when prompts stabilize. (See customization-04)

### Document Chain as RFC
- The pipeline naturally produces a chain: problem statement → requirements → design → review findings → plan. This chain consolidates into something RFC-like — a detailed record of goals, tradeoffs, alternatives considered, and reasoning.
- This artifact serves both human reviewers ("why was this designed this way?") and AI reviewers (context for future review cycles).
- **Self-consuming:** Parallax should use its own document chain as input to its own review tasks. The artifacts are the context that makes adversarial review effective.

### Finding Classification (Self-Error-Detecting)
- Not all findings are created equal. The review system should classify findings by what they indicate about which phase failed:

| Finding Type | Example | Action |
|---|---|---|
| **Bug / style** | Typo, wrong variable name, style violation | Fix in implementation |
| **Design assumption violated** | "The design assumes X, but X isn't true" | Escalate to design — spec quality problem |
| **Requirement missing** | "Nothing addresses what happens when Y" | Escalate to requirements — calibration problem |
| **Fundamental incompatibility** | "A and B cannot both be true" | Full cycle restart with updated constraints |

- Implementation errors that reveal spec problems are a **success**, not a failure. They mean the review system is working. The correct response is to fix the spec, not patch around a broken design.
- Archive the current plan when restarting — it's often useful as reference for the next iteration.
- This classification is the key differentiator from existing tools: compound-engineering and adversarial-spec treat all findings as same-phase fixes. No existing tool routes findings back to the phase that actually failed.

### Agent Team Comparison
- Run multiple agents on the same review task with different prompts/models
- Compare quality and coverage across agents
- Use this to calibrate which agent configurations produce the best reviews
- **Model routing:** Configurable model parameter per pipeline phase from the start. Default Sonnet everywhere, tune empirically via evals. Hypothesized routing: Haiku for survey/consolidation/auto-fix (mechanical), Sonnet for calibrate/review/eval-grading (judgment), Opus sparingly for adversarial review of complex designs. Build the routing table, validate with data. (See customization-05)

### Output Voice
- All human-facing output should be direct and engineer-targeted. The audience is senior+ engineers making go/no-go decisions at checkpoints.
- Lead with the verdict, not the analysis. Severity + one-sentence finding + evidence location.
- No hedging language ("it might be worth considering..."). SRE-style framing: blast radius, rollback path, confidence level.
- **Inline instructions, not custom styles** — encode voice rules in skill prompts for model portability (works with Codex, not just Claude). Define baseline voice in plugin-level config; per-skill overrides only where a phase genuinely needs a different tone. (See customization-02)

### Tooling
- **CLI-first.** Adopt available CLI tools immediately: `gh`, `jq`, `git`, `curl`, `npx promptfoo`, `inspect`. These work today with no infrastructure.
- **Investigate:** `braintrust` CLI, `anthropic` CLI (batch API), `tree-sitter` (AST for survey), `semgrep` (security patterns for review), `tokcount`/`ttok` (cost estimation).
- **MCP deferred to Phase 2+.** Reserve for cases with no CLI equivalent (real-time bidirectional communication, CI/CD triggered reviews). Built-in Claude Code tools sufficient for prototyping. (See customization-07)

### Human Checkpoints
- After requirement refinement (before design starts)
- After design review converges (before plan starts)
- After plan review converges (before execution starts)
- Never auto-proceed past a checkpoint without human approval

## What This Is NOT

- Not a replacement for human judgment on architecture decisions
- Not an auto-coder — execution is still handled by existing tools
- Not a project manager — no timeline estimation, resource allocation, or sprint planning
- Not trying to eliminate human involvement — trying to make the human's review time more productive by pre-filtering through adversarial review

## Deferred Considerations

- **Cross-session memory (#6):** Pipeline agents stay stateless — deterministic runs are essential for eval reproducibility. Development workflow memory already handled by CLAUDE.md + git. No action.
- **Custom persona pattern (#8):** The reviewer agents *are* custom personas (identity + methodology + tools), implemented as skills. Architecture already covers this. Use Custom GPT best practices (versioning, testing, focused knowledge) as a checklist during agent development. No action.

## Resolved Questions

1. **Single skill or pipeline?** → Pipeline of skills. Each namespace segment (`survey`, `calibrate`, `review`, `orchestrate`, `eval`) is independently useful.
2. **Fatal review finding invalidates design?** → TBD during prototyping. Will test both "always escalate to human" and "attempt one automated redesign pass." Deferred to prototype phase.
3. **Right number of review agents?** → Empirical. Determine optimal N via eval framework (diminishing returns analysis).
4. **Requirement refinement standalone?** → Yes. `parallax:calibrate` is useful outside the pipeline (e.g., for any design session).
5. **Version/track design iterations?** → Git commits per iteration. Full history, diffable artifacts.

## Open Questions

1. **Superpowers as foundation vs clean-room?** — Should parallax build on top of the superpowers brainstorming/planning skills, or start from scratch? Risk: evaluating superpowers-based design orchestration using superpowers-built tooling is circular. See landscape-analysis.md and plugin-framework-landscape.md for context. Compound-engineering (EveryInc) and adversarial-spec (zscole) are the two most relevant alternatives discovered — see plugin-framework-landscape.md for analysis.

## Prior Art

### Claude Code Plugins (potential foundations — see Open Questions)
- **superpowers** (obra, 52k stars) — `brainstorming`, `writing-plans`, `executing-plans`, `dispatching-parallel-agents`, `requesting-code-review`. Execution-oriented. Largest community. Current working environment.
- **compound-engineering** (EveryInc, 8.9k stars) — 15 review agents in parallel, `/compound` learning loop, 80/20 planning-over-execution philosophy. All agents are implementation-focused, none review requirements or design. Closest architectural match for multi-agent review.
- **adversarial-spec** (zscole, 487 stars) — Multi-LLM adversarial debate for spec refinement. Skepticism of early consensus, focus modes, model personas. Validates the adversarial review hypothesis but narrow (specs only, no eval). Study before building parallax:review.

See `docs/research/plugin-framework-landscape.md` and `docs/research/review-agent-analysis.md` for detailed analysis.

### External Frameworks
- LangGraph — stateful graph workflows (natural fit for pipeline control)
- Inspect AI — agent evaluation framework (for testing orchestrator quality)
- Mitsubishi Electric adversarial debate AI (Jan 2026) — validates concept for manufacturing decisions

### What Parallax Adds
The novel contribution is the combination of: (1) design-phase orchestration (not just execution), (2) adversarial review with finding classification that routes back to the phase that failed, and (3) eval instrumentation to measure review quality. No existing tool does all three. Foundation choice (which plugin scaffolding to build on) is an open question — see landscape-analysis.md.
