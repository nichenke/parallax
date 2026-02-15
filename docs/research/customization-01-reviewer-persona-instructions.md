# Finding 1: Reviewer Persona Instructions

**Source:** claude-ai-customize repo — Lever 2 (Instructions), Instruction Sharpener + Position Mapper meta-prompts
**Applies to:** `parallax:review` — adversarial review agents
**Priority:** High
**Decision:** Adopt — incorporated into problem statement (Subagent Orchestration). Use Instruction Sharpener / Position Mapper during prompt authoring. Wait for parallax design's own prompt engineering approach, then cross-reference.

## Finding

The claude-ai-customize repo's core thesis is that vague instructions produce generic output. The "Instruction Sharpener" meta-prompt transforms fuzzy preferences into specific steering. Applied to parallax, this means adversarial review agents need razor-sharp persona prompts — not "review this design critically" but specific instructions about what each reviewer looks for, how they think, and what they ignore.

## Why It Matters

The review agents *are* the product. The quality of their system prompts directly determines whether they catch real flaws or produce generic "have you considered..." noise. The research shows that specificity is what separates useful AI output from median output — and that's exactly the gap between a useful design review and a rubber-stamp one.

## In Practice

3-4 reviewer agents, each with a distinct "position" (in claude-ai-customize terminology):
- A **design-reviewer** who thinks like a staff engineer who's been burned by rewrites
- A **security-reviewer** who assumes every external input is hostile
- A **consistency-checker** who diffs the design against the plan and flags every divergence
- Non-overlapping blind spots by construction

Each persona uses the Position Mapper to define its "median vs. you" gap — what the default AI reviewer assumes vs. what this specific reviewer's perspective demands.

## Tradeoffs

| For | Against |
|-----|---------|
| Directly validated framework for producing sharper prompts | Adds upfront prompt design time |
| Produces measurably better output than vague prompts | Personas need calibration via eval framework before trustworthy |
| Fits eval-driven approach (A/B test sharp vs vague prompts) | May over-constrain if personas are too rigid early |

## Alternative

Skip the framework, write prompts intuitively, iterate purely via eval results. Faster start, but risks the "vague instructions → generic output" trap that claude-ai-customize specifically warns against.

## Action

Wait for the main parallax design to define its prompt engineering approach for review agents, then cross-reference with this finding. The Instruction Sharpener and Position Mapper are tools to apply during prompt authoring, not architectural constraints.

## Reference

- `~/src/claude-ai-customize/resources/prompt-kit.md` — Prompt 1 (Position Mapper), Prompt 2 (Instruction Sharpener)
- `~/src/claude-ai-customize/resources/article-why-your-ai-output-feels-generic.md` — specificity thesis
