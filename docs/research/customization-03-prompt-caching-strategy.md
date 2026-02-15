# Finding 3: Prompt Caching Strategy

**Source:** claude-ai-customize repo — Lever 2 + Cost optimization; Anthropic prompt caching documentation
**Applies to:** All agent invocations, especially review agents running in parallel
**Priority:** High (architectural decision — make early)
**Decision:** Adopt — with automation requirement. Cache boundary must be enforced automatically (not manually), and the system must surface a clear notification when a prefix change invalidates the cache (e.g., hash comparison, CI check, or runtime log).

## Finding

Each reviewer agent has a substantial system prompt. If running 3 reviewers per design and evaluating across test cases, the same system prompts get sent repeatedly. Anthropic's prompt caching gives 90% input cost reduction on cache hits. But this only works if prompts are designed for cacheability — stable prefix, variable suffix.

This is an architectural decision that affects how skill prompts are structured. Easier to get right upfront than to retrofit.

## Why It Matters

The parallax budget projects $150-400/month on API costs. Review agents are the most token-intensive phase (long system prompts + full design documents as input). Without caching, running 3 reviewers × 4 test cases × multiple iterations = significant token spend. With caching, the system prompt cost drops to ~10% after the first call in a session.

For evals specifically (running the same reviewers against many test cases), caching is the difference between "I can run 50 eval iterations" and "I can run 500."

## In Practice

**Prompt structure for cacheability:**
```
[CACHEABLE PREFIX — stable across invocations]
- Reviewer persona definition
- Review methodology and checklist
- Output format specification
- Severity taxonomy
- Voice/tone instructions

[VARIABLE SUFFIX — changes per invocation]
- The actual design document being reviewed
- Context-specific constraints
- Previous review findings (if iterating)
```

**Key constraint:** The cacheable prefix must be identical byte-for-byte across calls. Any variation (even whitespace) breaks the cache. This means:
- Persona prompts should be finalized before heavy eval runs
- Template variables should only appear in the suffix
- Version the prefix explicitly (so you know when you've invalidated the cache)

## Tradeoffs

| For | Against |
|-----|---------|
| 90% input cost reduction on cache hits | Requires disciplined prompt structure |
| Enables higher eval volume within budget | Prefix changes invalidate cache (iteration friction) |
| Compounds with batch API (50% + 90% = ~95% cost reduction) | Adds complexity to prompt management |
| No quality impact — output is identical | Cache TTL means cold starts on new sessions |

## Alternative

Don't optimize for caching. Accept higher costs during prototyping, optimize later. Risk: may hit budget ceiling during eval-intensive phases, limiting iteration count.

## Action

Design reviewer system prompts with a clear cacheable-prefix / variable-suffix boundary from the start. Document the boundary in the skill template. This is a structural convention, not a feature to build.

## Reference

- Anthropic prompt caching documentation
- CLAUDE.md cost strategy section (already mentions prompt caching)
- `~/src/claude-ai-customize/PLAN.md` — Phase 5 (Tools & MCP) discusses tool-level cost optimization
