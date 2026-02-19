# Issues #73 / #79 — Synthesis & Findings

**Date:** 2026-02-18
**Session:** feat/confidence-eval worktree, first precision/recall baseline run
**Sources:** docs/issue-73-plan.md, docs/issue-79-plan.md, docs/adversarial-73-79-review.md

---

## Issue #79 — autoevals Factuality

### Decision: REJECT (confirmed)

The desk rejection in the plan is correct, but the arguments used were weak. The ADR-quality
argument is:

**Absence-detection is the fundamental mismatch.** Reviewer findings identify what is *not* in
the document ("the document fails to specify X"). Factuality measures whether a claim is
*consistent with* a reference text. It cannot evaluate an absence claim — the same reason RAGAS
was rejected in ADR-008. This is the correct rejection argument.

### Arguments to drop

- **"No natural question exists"** — wrong. The frozen document can be `expected`, the finding
  can be `output`. The mapping is awkward but not nonexistent. The real problem is absence-detection,
  not input mapping.

- **"Requires Braintrust proxy or LiteLLM"** — trivially solvable. Project has Codex access and
  $50-100/month OpenAI budget. This is a convenience objection masquerading as an architectural
  one.

- **"Binary gate violation"** — necessary context but insufficient as a standalone argument.
  Any scoring system can be thresholded. The real problem is that Factuality's category semantics
  (category B: superset scores 0.6; category E: unrelated topics scores 1.0) are designed for
  answer comparison, not claim verification. The wrong ontology is the problem, not the partial
  credit per se.

### Missed opportunity

Even after rejecting Factuality as a primary scorer, running it as a **cross-model calibration
check** was not considered. 12 findings × ~$0.04/call = ~$0.50 to see if gpt-4o and Haiku agree
on verdicts. If agreement is 90%, that's evidence Haiku is well-calibrated. If agreement is 50%,
that's a red flag worth investigating. This experiment is cheap enough to run before or alongside
#73. Not blocking, but worth noting.

### ADR-008 status

The "maybe — evaluate Factuality" open item from ADR-008 is now resolved. Prior art sweep is
complete:
- RAGAS: skip (entailment mismatch)
- G-Eval: reject (same FN rate, 10x latency, session 32)
- Braintrust platform: skip (keep Inspect AI)
- autoevals Factuality: reject (absence-detection mismatch, binary gate ontology)

---

## Issue #73 — Judge Calibration Gate

### The gate as designed is statistically uninformative

N=12 (6 per partition) gives a **42% probability of passing a genuinely miscalibrated judge**
at 70% true specificity.

```
P(5 or 6 correct | true_specificity=0.70)
  = C(6,5) × 0.70^5 × 0.30^1 + C(6,6) × 0.70^6
  = 0.303 + 0.118
  = 0.42
```

A gate with 42% false-pass probability does not validate anything — it generates false confidence.
The plan's claim of "acceptable for MVP" is inconsistent with "validate the metric before trusting
it." Those goals require different N.

**Resolution options:**
1. Increase to ~25-30 examples per partition for meaningful statistical power (detects 70% vs 90%
   true accuracy at ~80% power)
2. Reframe explicitly as a **smoke test for catastrophic failures only** (catches judge that accepts
   everything or rejects everything) — N=12 is fine for this narrower purpose

The current plan should not ship without choosing one of these options and stating it clearly.

### Thresholds should be asymmetric

The plan sets both specificity and sensitivity thresholds at 83% (5/6). This treats leniency
errors and strictness errors as equally harmful. They are not.

With 72–93% of findings being NOT_GENUINE:
- A specificity error (judge accepts a false positive) inflates precision significantly.
  With ~40 NOT_GENUINE findings across all reviewers, 17% leniency = ~7 leaked FPs.
  Precision inflates by ~7/(7+10) ≈ 41% relative error.
- A sensitivity error (judge rejects a true positive) deflates precision modestly.
  With ~10 GENUINE findings total, 17% strictness = ~2 dropped TPs.

**Specificity threshold should be higher than sensitivity threshold.** At minimum, the plan
must justify symmetric thresholds against the observed base rate.

Recommendation: specificity ≥ 6/6 (100%) or 5/6 with explicit acknowledgment of leniency risk;
sensitivity ≥ 4/6 (67%) — one miss is low-cost given the base rate.

### The GENUINE partition relies on author-subjective validation

The plan uses the 6 `real_flaw` entries from `critical_findings.jsonl` as the known-GENUINE
partition. These were human-validated — the Haiku judge was NOT used to validate them. No
circularity.

But: they were validated by the same person who wrote the requirements document, reviewer agent
prompts, and judge prompt. The calibration set defines "genuine" as "the author says so." If
the judge disagrees with the author, the plan assumes the judge is wrong. This assumption should
be stated explicitly.

What the gate cannot detect: systematic bias shared between author and judge. An external expert
might disagree with both. Not a reason to abandon the approach — the author is the ground truth
authority — but the limitation should be documented.

### Standalone script output format is unspecified

The plan recommends a standalone Python script over an Inspect AI task. Technically correct —
calibration has no generation step. But the operational cost is real: Inspect AI produces
structured JSON logs that are comparable across runs. A standalone script produces... what?

The plan must specify: output format, output location, and how calibration regression is detected
when the judge model updates (Haiku version bump, swap to Sonnet). If the output is not
comparable across runs, the gate is a one-shot check, not a regression test.

Alternative: wrap calibration as an Inspect AI task where the solver is a no-op (passes the
finding as-is) and the scorer runs the judge. Inelegant but keeps everything in one log format.

### Narrower scope with #79 closed

The original plan sequence was: #73 calibrates judge → #79 compares Factuality against calibrated
judge. With #79 rejected, calibration stands alone. The value proposition weakens:

- **Gate passes:** "judge is not catastrophically broken, proceed." Low-information.
- **Gate fails:** "judge is miscalibrated, fix before trusting precision." High-information.

The gate is only high-value if there is a plausible path to failing. Given the G-Eval experiment
showed the direct judge at 84.6% accuracy on clean ground truth, the gate will likely pass. The
plan should acknowledge this and state what a pass means operationally.

---

## The Calibration Inversion — Root Cause

### Rubric-task mismatch, not judge error

The confidence rubric anchor at 75 reads: *"directly supported by document evidence."*

**Requirements-focused reviewers** (problem-framer, scope-guardian, success-validator): their
job is to find missing sections, undefined criteria, unresolved questions. The document either
has the section or it doesn't. High confidence = "I checked, the section is absent." The rubric
fits. Calibration direction is correct (high-conf precision > low-conf precision).

**Absence-detection reviewers** (assumption-hunter, constraint-finder): their job is to find
what is NOT stated. An unstated assumption is by definition not evidenced in the document. When
these reviewers assign confidence 85, they mean "I am very confident this assumption exists" —
but the evidence is inferential, not direct. The judge looks for document support, finds none,
calls it NOT_GENUINE. The calibration inversion is **mechanical and expected** given the rubric.

Additionally, quantity effects matter. Assumption-hunter and constraint-finder produce 13 findings
each vs 7-10 for other reviewers. More findings = more marginal findings = mechanically lower
per-finding precision. "Per-finding quality is lower" and "more findings means more chances for
NOT_GENUINE" are different failure modes with different fixes. The plans do not separate them.

### Fix

Update the 75-confidence anchor for absence-detection reviewers. Instead of:

> 75: Highly confident — double-checked, directly supported by document evidence, will impact
> design validity

Use something like:

> 75: Highly confident — the absence is clearly relevant to the document's stated scope and
> purpose; the document creates a context in which this gap would be expected to be addressed

This preserves the intent (high confidence = well-grounded) while fitting the inference-based
nature of absence detection.

---

## The Critical Missing Question: What If the Judge Is Right?

Neither the #73 plan nor the #79 plan addresses the most important scenario: **precision is
genuinely 7–28%, and the judge is correct.**

The evidence supports this more than either plan acknowledges:
- The judge reasoning on NOT_GENUINE calls is described in the #73 plan as "largely correct"
- G-Eval experiment showed the direct judge at 84.6% accuracy on clean ground truth
- The `quality_failures/` directory documents real hallucination patterns: implementation details
  as Critical findings, duplications of resolved issues, requirements/design confusion

**If the judge is right, the implications are:**

1. **The calibration gate will pass.** The plan has no "judge is correct, now what" branch.

2. **Reviewer agents need fundamental redesign.** Five reviewers producing 7-13 findings each
   at 72-93% hallucination rate means ~50 total findings of which ~5-10 are genuine. Signal-to-noise
   ≈ 1:9.

3. **The confidence feature (#72) is addressing the wrong layer.** If reviewers cannot
   distinguish genuine from hallucinated (the calibration inversion shows assumption-hunter and
   constraint-finder cannot, under the current rubric), then confidence is a metacognitive signal
   applied to hallucinated findings. The rubric fix (see above) is necessary before confidence
   filtering is meaningful.

4. **The synthesizer becomes the critical component.** If individual reviewers have 7-28%
   precision, the synthesizer must achieve far higher precision through cross-referencing and
   filtering. That is a harder problem than the current plan scopes.

**This should be explicit in the #73 plan:** if the calibration gate passes and precision remains
low, the next action is reviewer prompt redesign — not more eval infrastructure.

---

## Impact on the feat/confidence-eval Branch

### What's working

- `confidence` field emitted consistently on all 5 reviewers ✓
- Schema validation passes (required field, 0-100 integer) ✓
- `confidence_stratified` metadata in scorer output ✓
- Synthesizer filter at threshold 80 ✓ (but see below)

### Why the branch should not land yet

1. **Synthesizer filter is backwards for absence-detection reviewers.** The filter removes
   findings with `confidence < 80`. For assumption-hunter and constraint-finder, the
   low-confidence findings have *higher* genuine precision (0.125/0.143 vs 0.000 for
   high-confidence). The filter is removing the relatively more-genuine findings for those two
   reviewers.

2. **Calibration inversion documented in eval results.** Merging with inverted calibration
   makes the confidence feature actively misleading in production — users would see high-confidence
   findings from assumption-hunter that are systematically worse than low-confidence ones.

### Path to landing

1. **Fix the confidence rubric** for assumption-hunter and constraint-finder (absence-detection
   anchor language). Single-file edits to `agents/assumption-hunter.md` and
   `agents/constraint-finder.md`.

2. **Re-run `make reviewer-eval`** to verify calibration inversion disappears for those two
   reviewers. If high-conf precision > low-conf precision for all five reviewers, the branch
   is ready.

3. **Update eval results doc** with the re-run data.

4. **Proceed with #73** as a smoke test (reframe scope, adjust N or explicitly label as
   catastrophic-failure detector, add "judge is correct" contingency, fix threshold asymmetry).

5. **Close #79** with corrected reasoning in the issue comment.

---

## Next Session Start Point

- Worktree: `feat/confidence-eval`
- First action: fix absence-detection anchor in assumption-hunter.md and constraint-finder.md
- Second action: `make reviewer-eval`, check calibration direction
- If calibration fixes: update eval results doc, update MEMORY.md, proceed toward merge
- If calibration persists: deeper investigation of reviewer prompts before landing
