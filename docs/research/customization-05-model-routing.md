# Finding 5: Model Routing Per Phase

**Source:** claude-ai-customize repo — Lever 4 (Tools), cost optimization; CLAUDE.md cost strategy
**Applies to:** All pipeline phases — survey, calibrate, review, consolidation, eval
**Priority:** Medium-high (defer tuning until empirical data available)
**Decision:** Adopted — incorporated into problem statement (Agent Team Comparison). Configurable model parameter per phase from the start, default Sonnet everywhere, tune empirically via evals.

## Finding

Different pipeline phases have different reasoning requirements. The claude-ai-customize research on tool configuration notes that what model you use changes the character of output, not just the cost. Applied to parallax, this means each phase should use the cheapest model that meets its quality threshold — determined empirically, not assumed.

## Why It Matters

The budget is $2k/month with projected $200-500 actual spend. Opus is ~15x more expensive than Haiku per token. If every phase uses Sonnet by default, you're overpaying for mechanical tasks (consolidation, dedup) and underpaying for hard tasks (adversarial review of complex designs). Getting this right can 2-3x the number of eval iterations within the same budget.

## In Practice

**Hypothesized routing (needs empirical validation):**

| Phase | Candidate Model | Reasoning Need | Token Intensity |
|-------|----------------|----------------|-----------------|
| survey (research) | Haiku | Low — search, summarize | Medium |
| calibrate (requirements) | Sonnet | Medium — judgment, elicitation | Low |
| review (adversarial) | Sonnet; Opus for complex | High — find non-obvious flaws | High |
| consolidation (dedup/merge) | Haiku | Low — pattern matching | Medium |
| eval grading | Sonnet | Medium — score finding quality | Medium |
| auto-fix (trivial findings) | Haiku | Low — mechanical edits | Low |

**Validation approach:**
1. Run all phases with Sonnet (baseline)
2. Swap one phase at a time to Haiku, measure quality delta
3. For review phase, compare Sonnet vs Opus on the hardest test cases
4. Build a cost-quality Pareto frontier: for each phase, what's the cheapest model that stays within acceptable quality?

**Codex consideration:** CLAUDE.md mentions Codex for comparison evals and execution-phase experiments. Codex is ~3x more token-efficient than Claude for code generation tasks. Worth testing for the survey phase (codebase exploration) and auto-fix phase.

## Tradeoffs

| For | Against |
|-----|---------|
| 2-3x budget efficiency | Needs eval framework running first |
| Higher eval volume within same spend | Model quality differences are task-dependent (can't just assume) |
| Configurable — easy to change routing | Adds complexity to pipeline configuration |
| Empirical approach avoids over/under-spending | Different models may need different prompt styles |

## Alternative

Use Sonnet everywhere. Simple, consistent, no routing logic. Accept the cost premium for simplicity. Revisit if budget becomes a constraint.

## Action

Defer implementation until the eval framework can measure quality per phase. Design the pipeline with a model parameter per phase so routing is configurable from the start, even if initially set to Sonnet everywhere.

## Reference

- CLAUDE.md cost strategy: "Haiku for simple evals, Sonnet for review agents, Opus sparingly for adversarial deep analysis"
- CLAUDE.md budget: "Batch API for 50% discount, prompt caching for 90% input cost reduction"
- `~/src/claude-ai-customize/PLAN.md` — Phase 5 (Tools & MCP) cost impact analysis
