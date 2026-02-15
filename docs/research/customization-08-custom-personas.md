# Finding 8: Custom Personas (ChatGPT Custom GPTs Pattern)

**Source:** claude-ai-customize repo — Custom GPTs concept, persona-as-product pattern
**Applies to:** Review agents conceptually; not directly implementable
**Priority:** Low
**Decision:** Defer — the reviewer agents *are* this pattern, implemented as skills

## Finding

ChatGPT's Custom GPTs allow creating complete personas with knowledge bases, instructions, and capabilities bundled together. This is effectively what parallax's reviewer agents are — but built as Claude Code skills/agents rather than as a product feature.

The insight from claude-ai-customize is that the persona bundle (identity + knowledge + voice + tools) is what makes the output useful, not any single component. Parallax's architecture already captures this — each reviewer agent is a persona with a specific identity, review methodology, output format, and tool access.

## Why It Matters

This is a validation that the architectural approach is sound, not a new feature to add. The parallax reviewer agents are purpose-built Custom GPTs for design review. The value is in recognizing this equivalence so that lessons from Custom GPT best practices (knowledge base curation, persona testing, version management) can inform reviewer agent development.

## In Practice

**Already planned:**
- `agents/design-reviewer/` — adversarial design critic persona
- `agents/security-reviewer/` — security-focused review persona
- `agents/consistency-checker/` — design-to-plan alignment persona
- `agents/eval-grader/` — test result evaluation persona

Each is a persona bundle: system prompt (identity + methodology) + output format + tool access.

**Applicable lessons from Custom GPT practices:**
- Version your persona prompts (git-tracked, already planned)
- Test personas against known inputs before deploying (eval framework)
- Iterate persona instructions based on user feedback (correction compounding, Finding 4)
- Keep knowledge bases focused — don't dump everything into every persona

## Tradeoffs

| For | Against |
|-----|---------|
| Validates architectural direction | No new action items — already planned |
| Imports Custom GPT best practices | Custom GPT ecosystem lessons may not all transfer |
| Frames reviewer agents in familiar terms | Naming overlap could cause confusion |

## Action

No action needed. Architecture already implements this pattern. Use Custom GPT best practices (versioning, testing, focused knowledge) as a checklist during reviewer agent development.

## Reference

- `~/src/claude-ai-customize/resources/setup-guide.md` — Custom GPTs section
- `~/src/claude-ai-customize/resources/article-why-your-ai-output-feels-generic.md` — persona bundling concept
- CLAUDE.md architecture: `agents/` directory structure
