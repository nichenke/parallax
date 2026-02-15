# Finding 4: CLAUDE.md as Reviewer Calibration (Correction Compounding)

**Source:** claude-ai-customize repo — Prompt 3 (Correction Compounder), compounding discipline
**Applies to:** Review agent prompts, eval framework feedback loop
**Priority:** High (process, not code)
**Decision:** Adopt — requires eval framework first. Same automation note as Finding 3: corrections that modify the cacheable prefix should be surfaced automatically.

## Finding

The claude-ai-customize repo's central behavioral insight: most people correct AI output in their head, get a better response, and move on. Next conversation starts fresh. The compounding practice encodes corrections as permanent rules, so the same mistake never happens twice.

Applied to parallax: every time a reviewer misses a real flaw (false negative) or flags a non-issue (false positive), that's calibration data. The Correction Compounder pattern converts these into prompt rules for the reviewer agent, permanently improving its accuracy.

## Why It Matters

Parallax's review agents will produce false positives and false negatives. Without a systematic correction loop, the same errors recur across every design review. The eval framework can detect these errors — but the correction needs to flow back into the reviewer prompts, not just sit in eval results.

This is the difference between "we know our security reviewer misses X" and "our security reviewer's prompt now explicitly checks for X."

## In Practice

**The loop:**
1. Run review agents against a design (or test case with planted flaws)
2. Eval framework identifies false negatives (missed real flaws) and false positives (flagged non-issues)
3. For each recurring pattern, run the Correction Compounder: "The security reviewer keeps missing [pattern]. Current prompt says [X]. What instruction would catch this?"
4. Add the sharpened instruction to the reviewer's system prompt
5. Re-run eval to confirm improvement, check for regression

**Example:**
- **Observation:** Design reviewer didn't flag that a caching layer has no invalidation strategy
- **Correction Compounder output:** "When reviewing any design that introduces caching, explicitly verify: cache invalidation strategy, TTL policy, cache stampede handling, and memory bounds. Flag missing invalidation as severity:high."
- **Result:** Added to design-reviewer persona prompt, verified via eval

## Tradeoffs

| For | Against |
|-----|---------|
| Systematic improvement — never repeat same miss | Prompt growth over time (longer = more tokens = more cost) |
| Already doing this for CLAUDE.md (extend pattern to agents) | Need eval framework running first to detect errors |
| Measurable improvement via before/after eval scores | Risk of overfitting to test cases if calibration data is narrow |
| Aligns with SRE postmortem culture | Requires discipline to run the loop consistently |

## Alternative

Skip formal correction compounding. Rely on intuitive prompt editing based on observed failures. Faster but unsystematic — same mistakes may recur if the editor forgets or a different person edits the prompt.

## Action

Establish correction compounding as a process convention once the eval framework is running. No code to build — this is a workflow discipline applied during prompt iteration. Document the loop in the project's contributing guidelines.

## Reference

- `~/src/claude-ai-customize/resources/prompt-kit.md` — Prompt 3 (Correction Compounder)
- `~/src/claude-ai-customize/resources/article-why-your-ai-output-feels-generic.md` — compounding thesis
- Boris Cherny team practice: "Anytime we see Claude do something incorrectly we add it to the CLAUDE.md"
