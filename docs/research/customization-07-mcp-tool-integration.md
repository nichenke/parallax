# Finding 7: MCP & Tool Integration

**Source:** claude-ai-customize repo — Lever 4 (Tools/MCP), tool configuration as steering
**Applies to:** `parallax:survey` (research phase), eval framework data collection
**Priority:** Low-medium (useful later, not the bottleneck now)
**Decision:** Prefer CLI tools over MCP. Adopt available CLI tools immediately; investigate structured tools where CLI gaps exist. Defer MCP to Phase 2+ only where no CLI equivalent exists.

## Finding

The claude-ai-customize research observes that tool configuration changes the *character* of output, not just its capabilities. What tools an agent has access to determines what kind of analysis it produces. For parallax, the survey phase and eval framework would both benefit from MCP integrations — but these are enhancements to an already-functional pipeline, not prerequisites.

## Why It Matters

**Survey phase:** Currently spec'd to "explore codebase, check docs, web search, identify constraints." MCP servers for GitHub (repo analysis), filesystem (dependency scanning), and web search would make this phase more thorough. But the survey phase can work with Claude Code's built-in tools first.

**Eval framework:** MCP could connect to Braintrust/LangSmith for trace analysis, or to a database for storing eval results. Useful for scale, but not needed for initial prototyping.

**Review agents:** MCP for codebase access during review would let reviewers verify claims in the design against actual code. High value but adds complexity.

## In Practice

**Phase 1 (now):** Use Claude Code's built-in tools (Bash, Read, Glob, Grep). Sufficient for prototyping.

**Phase 2 (after pipeline works):** Add MCP servers for:
- GitHub (PR context, issue history, repo structure)
- Filesystem (dependency graphs, import analysis)
- Web search (external constraint discovery)

**Phase 3 (at scale):** Add MCP servers for:
- Eval data stores (Braintrust, custom databases)
- CI/CD integration (automated review on PR)
- Notification (Slack alerts for fatal findings)

## Tradeoffs

| For | Against |
|-----|---------|
| Richer context for survey and review phases | Adds setup complexity and dependencies |
| Tool access changes output character (per research) | Built-in tools sufficient for prototyping |
| Enables automation (CI/CD triggered reviews) | MCP server reliability becomes a dependency |
| Aligns with long-term automation goals (Issue #6) | Premature optimization before pipeline works |

## CLI Tools Available Now

| Tool | What it gives us | Install |
|------|-----------------|---------|
| `gh` | GitHub PRs, issues, repo metadata, API access, actions | Already installed (standard) |
| `jq` | JSON parsing for API responses, eval result processing | Already installed (standard) |
| `git` | Diff, log, blame — design iteration tracking is already git-native | Already installed |
| `curl` | Direct API calls to Claude/Anthropic batch API, webhooks | Already installed |
| `npx promptfoo` | Prompt testing, red-teaming (10k probes/month free) | `npm install -g promptfoo` |
| `inspect` | Inspect AI eval runner | `pip install inspect-ai` |

## CLI Tools to Investigate

| Tool | Potential use | Notes |
|------|--------------|-------|
| `langchain` / `langgraph` CLI | Pipeline orchestration from terminal | Check if CLI exists or if it's Python-only |
| `braintrust` CLI | Eval logging, LLM-as-judge scoring | Has CLI — check capabilities vs web UI |
| `anthropic` CLI | Batch API submission, prompt caching management | Official SDK has CLI utils |
| `tree-sitter` CLI | Codebase structure analysis for survey phase | Fast AST parsing, language-agnostic |
| `semgrep` | Security pattern scanning (feeds security-reviewer) | Free for CLI, 20k findings/month |
| `tokcount` / `ttok` | Token counting for cost estimation and budget tracking | Various options, check accuracy per model |

## Action

Adopt CLI tools immediately — they work today with no infrastructure. Investigate the "to investigate" list during survey/eval framework buildout. Reserve MCP for cases where CLI has no equivalent (e.g., real-time bidirectional communication with external services).

## Reference

- `~/src/claude-ai-customize/resources/article-why-your-ai-output-feels-generic.md` — Tools lever
- `~/src/claude-ai-customize/resources/setup-guide.md` — Claude MCP server setup
- CLAUDE.md: Issue #6 (Claude-native background automation — Agent SDK + MCP + cron)
