# Finding 2: Voice & Tone for Pipeline Output

**Source:** claude-ai-customize repo — Lever 3 (Style/Tone Controls), Custom Styles from writing samples
**Applies to:** All human-facing output — checkpoint summaries, review findings, calibrate output, plan summaries
**Priority:** High (quick win)
**Decision:** Likely adopt — inline instructions for portability (not custom style). Define baseline voice in plugin-level CLAUDE.md; per-skill overrides only where a phase genuinely needs a different tone.

## Finding

Claude supports custom styles derived from writing samples (upload 3-5 docs representing your voice). For parallax, every human checkpoint produces output that a senior+ engineer needs to read and act on quickly. The default AI voice — hedging, verbose, diplomatic — directly works against this.

The claude-ai-customize research identifies this as the gap between "median user" output and expert-targeted output. The fix is encoding voice corrections into the system rather than making them repeatedly.

## Why It Matters

Parallax has 3 human checkpoints (after requirements, after design review, after plan review). At each one, the engineer reads output and makes a go/no-go decision. Every second spent parsing verbose or hedging language is waste. Every "it might be worth considering..." that should have been "This will break under load" is a missed signal.

The CLAUDE.md already calls for SRE-influenced thinking (premortem, blast radius, error budgets). The output voice should match.

## In Practice

Target voice characteristics:
- Lead with the verdict, not the analysis
- Severity + one-sentence finding + evidence location (file:line)
- No hedging language ("it might be worth considering...", "you may want to...")
- SRE-style framing: blast radius, rollback path, confidence level
- Short sentences, short paragraphs
- Technical precision over diplomatic softening

Two approaches to implement:
1. **Custom style** — Upload 3-5 writing samples (incident reports, design review comments, code review feedback) and let Claude generate a style profile. Reference this style in skill prompts.
2. **Inline instructions** — Encode voice rules directly in each skill's system prompt. More portable, no dependency on Claude's style feature.

## Tradeoffs

| For | Against |
|-----|---------|
| Measurable reduction in checkpoint decision time | Style tuning takes real writing samples |
| Consistent voice across all pipeline phases | Custom styles are Claude-specific (not portable to Codex) |
| Quick to implement (15 min for custom style setup) | Risk of over-constraining — some phases may need different voices |
| The Correction Compounder pattern prevents drift | Inline instructions are more portable but more verbose |

## Alternative

Don't set a global voice. Let each skill's prompt handle tone independently. Risk: inconsistent output quality across phases, repeated voice corrections.

## Action

Define target voice with examples (good output vs bad output). Decide between custom style vs inline instructions based on portability needs (Claude-only vs multi-model).

## Reference

- `~/src/claude-ai-customize/resources/setup-guide.md` — Claude custom style setup walkthrough
- `~/src/claude-ai-customize/resources/prompt-kit.md` — Prompt 3 (Correction Compounder) for encoding voice corrections
