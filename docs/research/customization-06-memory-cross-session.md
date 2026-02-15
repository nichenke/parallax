# Finding 6: Memory Across Sessions

**Source:** claude-ai-customize repo — Lever 1 (Memory), cross-conversation persistence
**Applies to:** Pipeline state, design iteration history, reviewer calibration data
**Priority:** Low (for pipeline use); Medium (for development workflow)
**Decision:** Defer — pipeline agents stay stateless. Curated reference docs (common findings per codebase) are a separate concern from session memory, handled by Finding 4 (correction compounding).

## Finding

The claude-ai-customize repo identifies memory as a key customization lever — AI retaining information across conversations without re-explaining context. For parallax, the pipeline is designed to be self-contained per run (git-tracked iterations provide the history). Cross-session memory is less critical for the pipeline itself than for the development workflow building it.

## Why It Matters

**For the pipeline:** Each design review run should be stateless and reproducible. Memory introduces non-determinism — if the reviewer "remembers" a previous design, it may bias the review. For eval purposes, deterministic runs are essential.

**For development:** When iterating on reviewer prompts, calibration rules, and pipeline architecture across sessions, memory helps maintain continuity. This is already handled by CLAUDE.md + git + memory files.

## In Practice

**Pipeline (defer):** No cross-session memory for review agents. Each run gets the full context via the design document + system prompt. History is in git, not in memory.

**Development (already doing):**
- CLAUDE.md for project context (travels with git)
- `.claude/projects/.../memory/MEMORY.md` for local session state
- Git commits for iteration tracking

The existing approach already implements the "active curation" practice that claude-ai-customize recommends.

## Tradeoffs

| For | Against |
|-----|---------|
| Memory could help reviewers learn domain-specific patterns | Non-determinism breaks eval reproducibility |
| Could reduce prompt size (offload context to memory) | Memory curation overhead |
| Already solved for dev workflow via CLAUDE.md | Pipeline should be stateless for reliability |

## Action

No action needed. The existing CLAUDE.md + memory file pattern covers development workflow. Pipeline agents should remain stateless.

## Reference

- `~/src/claude-ai-customize/resources/article-why-your-ai-output-feels-generic.md` — Memory lever
- `~/src/claude-ai-customize/resources/setup-guide.md` — Claude memory setup
- CLAUDE.md context management section (portable vs machine-local)
