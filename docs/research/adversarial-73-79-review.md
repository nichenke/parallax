# Adversarial review: issue #73 (judge calibration gate) and issue #79 (autoevals Factuality)

**Date:** 2026-02-18
**Reviewer:** Opus (adversarial)
**Scope:** Stress-test reasoning, surface weak assumptions, identify omissions

---

## Issue #79 (autoevals Factuality) -- REJECT decision

### 1. "No natural question exists" is wrong

The plan claims there is no natural mapping for the `input` slot. This is dismissive. The frozen document is the context. The finding is the claim. The natural question is: "Based on this document, is this finding identifying a real problem?"

This is exactly entailment-with-negation. Factuality's framing -- "is the output consistent with the expected given the input" -- maps to "is the finding consistent with what the document actually says." The plan waves this off as "no natural question" without trying the obvious mapping:

- `input`: "Evaluate whether this finding identifies a real, document-visible design flaw."
- `output`: The finding text (title + issue + severity).
- `expected`: The frozen document content.

This is not a clean fit -- `expected` is a reference corpus, not an expert answer -- but the plan never articulates why this specific mapping fails. It asserts difficulty and moves on.

The honest argument is: Factuality is designed for factual claims against reference text, not for absence-detection claims ("the document fails to specify X"). RAGAS was rejected for this exact reason in ADR-008. The #79 plan should have made this argument explicitly instead of the weaker "no natural question" framing.

**Verdict:** The rejection is probably correct, but for a reason the plan buries. The real killer is absence-detection, not input mapping.

### 2. The binary gate argument is weak standing alone

The plan says Factuality's partial credit (categories A-E) "directly violates" the binary gate. But thresholding is trivial: score >= 0.5 maps to GENUINE, score < 0.5 maps to NOT_GENUINE. Every classification system can be binarized.

The plan's counterargument -- "at that point you've built a custom scorer anyway" -- is undersold. The real problem is that Factuality's categories encode the wrong semantics:

- Category B (superset, consistent, 0.6): A finding that says more than the document states scores positively. But a finding that hallucinates extra constraints also says more than the document states. Category B cannot distinguish genuine inference from hallucination.
- Category E (unrelated subjects, 1.0): An irrelevant finding scores maximum. This is absurd for genuineness checking.
- Category A (subset, consistent, 0.4): A finding that is narrower than the expected answer scores below the binary threshold. A genuine finding that only partially captures a flaw would be classified NOT_GENUINE.

The category semantics are designed for answer comparison, not claim verification. The plan touches this but does not hammer it home. The binary gate is not the problem -- the wrong ontology is the problem.

**Verdict:** The binary gate argument is necessary context but insufficient as a standalone reason. Strengthen it or drop it.

### 3. Desk rejection without experiment is defensible -- barely

ADR-008 rejected G-Eval after an experiment. The #79 plan rejects Factuality at desk. The plan says the mismatch is "semantic, not calibration-related" to justify this.

The difference between G-Eval and Factuality: G-Eval is a prompting technique applied to the same judge (Haiku). It tests whether the judge prompt can be improved. Factuality is a different scoring framework with different semantics. The question for G-Eval was "does reasoning-first help?" -- you have to run it to know. The question for Factuality is "does this framework measure what we need?" -- which is answerable by analysis.

But there is one thing an experiment could reveal that desk analysis cannot: what does Factuality's agreement rate with the current Haiku judge look like? If Factuality (via gpt-4o) agrees with Haiku on 90% of verdicts, that is evidence the Haiku judge is well-calibrated. If it disagrees on 50%, that is evidence of systematic divergence worth investigating. The plan does not consider Factuality as a calibration cross-check even after rejecting it as a primary scorer.

This is a missed opportunity. The experiment would be cheap (12 findings, one API call each to gpt-4o, total cost under $0.50). The plan should either run it or explicitly argue why cross-model agreement data is not useful.

**Verdict:** Desk rejection is defensible for the primary scorer question but misses the cross-check opportunity.

### 4. gpt-4o dependency is not a real blocker

The plan lists "requires Braintrust proxy or LiteLLM translation" as infrastructure overhead. The project has Codex access, an explicit $50-100/month OpenAI budget, and gpt-4o is available via standard API. LiteLLM is `pip install litellm` and one environment variable.

This is a convenience objection masquerading as an architectural objection. If gpt-4o Factuality produced better calibration data than Haiku, the integration cost is one afternoon. The plan should not list this as a supporting argument for rejection.

**Verdict:** Drop this argument. It weakens the overall case by including a trivially solvable objection.

---

## Issue #73 (judge calibration gate) plan

### 5. Circularity in the GENUINE partition

The plan says: use the 6 `real_flaw` entries from `critical_findings.jsonl` as the GENUINE partition. These entries were manually validated -- but by whom, and against what standard?

Looking at the actual data: the `critical_findings.jsonl` entries have `"validation_status": "real_flaw"` set by the project author. The Haiku judge was NOT used to validate them originally -- they were human-validated. So the specific circularity of "using judge output to calibrate the judge" does not apply.

But there is a subtler problem. The entries were validated by the same person who wrote the requirements document, the reviewer agent prompts, and the judge prompt. If the author's understanding of "genuine" differs from the judge's understanding, the calibration set measures disagreement between author and judge -- not absolute accuracy.

This is not inherently wrong (the author is the ground truth authority), but the plan should state this explicitly: the calibration set's GENUINE partition defines "genuine" as "the author says so." If the judge disagrees with the author on a finding the author considers genuine, the plan assumes the judge is wrong. That assumption should be explicit because it constrains what the calibration gate can detect.

What it cannot detect: systematic bias the author shares with the judge. If both author and judge agree that a certain class of finding is genuine but an external expert would disagree, the calibration gate passes anyway.

**Verdict:** Not circular, but the limitation should be stated. The plan treats GENUINE as objective when it is author-subjective.

### 6. N=12 is not "acceptable for MVP" -- it is statistically uninformative for its stated purpose

The plan acknowledges "one wrong judgment shifts specificity/sensitivity by 17pp." This is not a minor caveat -- it is the central limitation.

Consider: the specificity threshold is 5/6 (83%). The judge must correctly reject 5 of 6 NOT_GENUINE examples. If the judge is actually 70% specific (genuinely miscalibrated), the probability of seeing 5/6 correct by chance is:

P(5 or 6 correct | true specificity = 0.70) = C(6,5) * 0.70^5 * 0.30^1 + C(6,6) * 0.70^6 = 6 * 0.168 * 0.30 + 0.118 = 0.303 + 0.118 = 0.42

A 42% chance of passing a genuinely miscalibrated judge. That is not a gate -- it is a coin flip.

For the sensitivity side, same math applies. A judge with true sensitivity of 0.70 has a 42% chance of passing the 5/6 threshold.

The plan says this is "acceptable for MVP." But the issue's stated purpose is "validate a metric before trusting it." An instrument with 42% probability of passing a broken metric does not validate anything. It generates false confidence.

The minimum useful calibration set for detecting a judge at 70% vs 90% with 80% power requires roughly 25-30 examples per partition. At 6 per partition, the gate is cosmetic.

**Verdict:** This is the plan's most serious problem. Either increase N substantially or reframe the gate's purpose from "validation" to "smoke test that catches only catastrophic failures (e.g., judge that accepts everything or rejects everything)." The current framing overpromises.

### 7. The 83% threshold is unprincipled

The plan says 83% because "one miss tolerable." This is convenience arithmetic, not a calibration decision.

The right question: what judge error rate makes the precision metric unreliable? If the judge has 83% specificity, then 17% of NOT_GENUINE findings leak through as GENUINE. With 5 reviewers producing ~10 findings each and 80% being NOT_GENUINE (the observed rate), that is 40 NOT_GENUINE findings, of which ~7 leak through. The precision metric inflates by roughly 7/(7+10) = ~41% relative error. Is that acceptable?

If the judge has 83% sensitivity, then 17% of GENUINE findings get rejected. With ~10 GENUINE findings across all reviewers, ~2 get dropped. Precision deflates slightly. This is less damaging.

The asymmetry matters: specificity errors (leniency) inflate precision more than sensitivity errors (strictness) deflate it, because NOT_GENUINE findings vastly outnumber GENUINE ones. The threshold for specificity should be higher than for sensitivity, not equal.

The plan sets them equal at 83%. This treats strictness errors and leniency errors as equally harmful when the observed data (72-93% NOT_GENUINE) makes leniency errors far more impactful.

**Verdict:** The threshold should be asymmetric. Specificity needs to be higher (5/6 minimum, ideally 6/6) while sensitivity can be lower. At minimum, the plan should justify symmetric thresholds against the observed base rate.

### 8. Standalone script vs Inspect AI task has a real cost

The plan argues that calibration has no generation step, so Inspect AI's generate-then-score pattern does not apply. This is technically correct.

But the cost is not architectural -- it is operational. Inspect AI logs produce structured JSON with timestamps, model names, scores, and metadata. The calibration script will produce... what? A print statement? A JSON file with ad hoc schema?

If calibration results are not in Inspect AI log format, they cannot be compared across runs using the same tooling. When the judge model changes (Haiku version bump, swap to Sonnet), re-running calibration and comparing to the previous run requires either writing comparison code or eyeballing output.

The plan should specify: what is the output format? Where do results go? How do you detect calibration regression when the judge model updates?

Also: the "no generation step" argument is weaker than presented. You could wrap the calibration check as an Inspect AI task where the "solver" is a no-op (returns the finding as-is) and the scorer runs the judge. This is inelegant but keeps everything in one log format. The plan dismisses this option without considering the operational cost of the alternative.

**Verdict:** Not blocking, but the plan has an operational gap. Specify the output format and regression detection workflow, or accept the Inspect AI wrapper's inelegance.

---

## Interaction between #73 and #79

### 9. #73 still has a purpose, but a narrower one

With #79 rejected, there is no second scorer to compare against. The calibration gate's purpose shrinks from "validate judge before comparing to alternatives" to "validate judge, period."

This is still useful, but the value proposition weakens. The original sequence (#73 calibrates judge, then #79 compares Factuality) had a clear payoff: calibration data fed into a comparison. Now calibration stands alone. The question becomes: what decision does calibration enable?

If the calibration gate passes: "the judge is not catastrophically broken, proceed." This is useful but low-information.

If the calibration gate fails: "the judge is miscalibrated, fix it before trusting precision." This is useful and high-information.

The asymmetry means the gate is only valuable if there is a plausible path to failing. Given that the direct judge already achieves 84.6% accuracy on clean ground truth (G-Eval experiment), the calibration gate probably passes. The plan should consider: is there enough prior evidence of miscalibration to justify building the gate? Or is the first precision baseline (7-28%) sufficient evidence that the problem is reviewer quality, not judge quality?

**Verdict:** #73 is still worth doing as a smoke test, but the plan should acknowledge the narrower scope and reduced expected value.

### 10. Factuality's semantic analysis is uninformative about the Haiku judge

The #79 plan says the mismatch is "semantic, not calibration-related." This is correct but the implication is underexplored.

The Haiku judge IS making semantic judgments. It is deciding whether a finding "identifies a real problem visible in the document" and whether the finding "references requirements not present in the document." These are entailment-adjacent decisions.

The fact that Factuality's entailment framing does not cleanly map to genuineness checking tells us that genuineness checking is more nuanced than entailment. It does not tell us whether the Haiku judge handles that nuance correctly. Specifically:

- Factuality would fail on absence-detection findings (as noted in ADR-008 for RAGAS).
- The Haiku judge also needs to handle absence-detection findings -- is "the document does not specify X" a genuine finding or a hallucinated constraint?

The #79 analysis identifies that Factuality cannot distinguish these cases. But neither plan asks: can Haiku? The G-Eval experiment showed Haiku has a 28.6% false negative rate, and the cases it misses are context-dependent findings that look genuine from the document alone. This is the same entailment ambiguity that makes Factuality unsuitable -- but it is also present in the current judge.

**Verdict:** The semantic analysis of Factuality's limitations should feed back into the judge prompt design. Both plans miss this connection.

---

## Broader situation

### 11. The calibration inversion has an unexplored alternative explanation

The plans frame the calibration inversion (high-confidence findings have lower precision for assumption-hunter and constraint-finder) as either a judge error or a reviewer error. There is a third option neither plan addresses: the confidence rubric interacts differently with different reviewer types.

Look at the agent prompts. All five reviewers use identical confidence rubric text:

> - 0: Not confident -- does not stand up to light scrutiny
> - 25: Somewhat confident -- might be real, could not fully verify from document alone
> - 50: Moderately confident -- verified present, but minor or low-frequency in practice
> - 75: Highly confident -- double-checked, directly supported by document evidence, will impact design validity
> - 100: Certain -- confirmed, will definitely cause problems if not addressed

The 75 anchor says "directly supported by document evidence." For problem-framer, scope-guardian, and success-validator, this maps naturally to their task: they look for missing sections, unclear criteria, and unresolved questions. The document either has the section or it does not. High confidence means "I checked and the section is missing."

For assumption-hunter and constraint-finder, "directly supported by document evidence" maps poorly. An unstated assumption is by definition NOT directly evidenced in the document. The assumption-hunter's job is to identify what is NOT there. When the assumption-hunter assigns 85 confidence, it means "I am very confident this assumption exists" -- but the supporting evidence is inferential, not direct. The judge then looks for direct document evidence, finds none (because the assumption is unstated), and calls it NOT_GENUINE.

The rubric creates a systematic mismatch for absence-detection reviewers. High confidence for these reviewers correlates with deeper inference, which correlates with less direct document evidence, which correlates with NOT_GENUINE verdicts. The inversion is a rubric-task interaction, not a judge error or a reviewer error.

Additionally, the quantity effect matters. Assumption-hunter and constraint-finder produce 13 findings each vs 7-10 for others. More findings means more marginal findings, which dilutes precision mechanically. The plans do not separate "per-finding quality is lower" from "more findings means more chances for NOT_GENUINE" -- these are different failure modes with different fixes.

**Verdict:** The confidence rubric needs reviewer-type-specific anchoring. Absence-detection reviewers need an anchor like "75: the absence is clearly relevant to the document's stated scope and purpose" instead of "directly supported by document evidence." Neither plan identifies this.

### 12. What if the judge is right?

Neither plan seriously considers the possibility that 7-28% precision is accurate. The framing throughout is "precision is low, find out why" with an implied "and fix it." But what if reviewers genuinely hallucinate 72-93% of their findings?

The evidence supports this more than either plan admits:

- The quality_failures directory documents real cases of reviewers producing implementation details as Critical findings, duplicating resolved issues, and confusing requirements with design.
- The G-Eval experiment found the direct judge achieves 84.6% accuracy on clean ground truth -- it is mostly right.
- The judge reasoning in NOT_GENUINE calls is described as "largely correct" in the #73 plan itself: "reviewers ARE producing hallucinated constraints, hypothetical concerns, and meta-reflections."

If the judge is right, then:

1. **The calibration gate (#73) will pass**, confirming the judge is working correctly. Then what? The plan has no "judge is correct, precision really is 7-28%" branch.

2. **The project's reviewer agents need fundamental redesign**, not better eval infrastructure. Five reviewers producing 7-13 findings each with 72-93% hallucination rate means the review panel generates ~50 findings of which ~5-10 are genuine. The signal-to-noise ratio is approximately 1:9.

3. **The confidence scoring feature (#72) is addressing the wrong problem.** If reviewers cannot distinguish genuine from hallucinated findings (the calibration inversion shows they cannot, at least for assumption-hunter and constraint-finder), then confidence is not a useful filter -- it is a hallucinated metacognitive signal applied to hallucinated findings.

4. **The synthesizer (review-synthesizer agent) becomes the critical component.** If individual reviewers have 7-28% precision, the synthesizer must achieve far higher precision by cross-referencing and filtering. This is a harder problem than either plan scopes.

The plans should include a "judge is correct" contingency. At minimum: if the calibration gate passes and precision remains 7-28%, what is the next action? Prompt engineering on reviewer agents? Reducing reviewer count? Raising the severity threshold? The current plan sequence (#73 then nothing) leaves a dead end if the judge validates.

**Verdict:** This is the most significant gap across both documents. The plans assume low precision is a measurement problem. If it is a production problem, the entire #73/#79 workstream is solving the wrong issue.

---

## Summary of findings by severity

**Critical (blocks the plan's purpose):**
- Point 6: N=12 calibration set has 42% probability of passing a genuinely miscalibrated judge. The gate does not validate what it claims to validate.
- Point 12: No contingency for "judge is correct and precision really is 7-28%." Plans address measurement validity without addressing production validity.

**Important (weakens the plan, should fix before implementation):**
- Point 7: Symmetric thresholds ignore the base rate asymmetry. Specificity matters more than sensitivity when 72-93% of findings are NOT_GENUINE.
- Point 11: Calibration inversion is likely a rubric-task interaction, not a judge error. Neither plan identifies this, and #73 cannot detect it.
- Point 5: GENUINE partition relies on author-subjective validation. Limitation should be stated.
- Point 3: Missed opportunity to use Factuality as a cross-model calibration check even after rejecting it as primary scorer.

**Minor (correct but undersold or oversold):**
- Point 1: "No natural question" is the wrong argument; absence-detection is the right argument.
- Point 2: Binary gate argument is necessary context but wrong as standalone rejection reason.
- Point 4: gpt-4o dependency is not a real blocker. Drop this argument.
- Point 8: Standalone script needs an output format specification and regression detection plan.
- Point 9: #73 still useful but with narrower scope; plan should acknowledge.
- Point 10: Factuality's semantic analysis should feed back into judge prompt design.
