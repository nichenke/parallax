# Issue #79: autoevals Factuality Scorer — Research & Decision

**Date:** 2026-02-18
**Issue:** #79 (Evaluate autoevals Factuality scorer as supplementary precision signal)
**Outcome:** REJECT
**Related:** ADR-008, docs/research/prior-art-braintrust-vercel-2026-02-17.md

---

## 1. Scope

Issue #79 asked: can Braintrust's `autoevals` Factuality scorer serve as a supplementary precision signal or cross-check against `reverse_judge_precision`?

The prior art research (ADR-008) flagged `autoevals` as a "maybe — evaluate Factuality scorer as supplementary signal." That open question is resolved here.

**Conclusion:** REJECT. The mismatch is semantic, not calibration-related. No experiment needed.

---

## 2. What Factuality Does

`autoevals.Factuality` compares a submitted answer (`output`) against an expert answer (`expected`) given a question (`input`). It uses a 5-category rating with partial credit:

| Category | Meaning | Score |
|----------|---------|-------|
| A | Output is a subset of expected, fully consistent | 0.4 |
| B | Output is a superset of expected, fully consistent | 0.6 |
| C | Output and expected are equivalent | 1.0 |
| D | Output and expected disagree | 0.0 |
| E | Output and expected differ but are on unrelated subjects | 1.0 |

Under the hood, `Factuality` is built on `LLMClassifier`: a Mustache prompt template that asks the model to pick a category, with tool-call extraction mapping the choice to a 0-1 score. Default model is gpt-4o; Claude requires Braintrust proxy or LiteLLM tool-call translation.

---

## 3. Input Mapping Analysis

Factuality assumes: `input` = question, `output` = submitted answer, `expected` = expert answer.

Design review findings don't map to this frame:

| Factuality slot | Natural meaning | Parallax forced mapping | Problem |
|-----------------|-----------------|------------------------|---------|
| `input` | A question | The frozen document? The review prompt? | No natural question exists |
| `output` | The answer being graded | A reviewer finding | Findings are claims, not answers |
| `expected` | The expert answer | ??? | There is no "expert answer" for genuineness |

The question for genuineness is: *"Is this finding supported by the document?"* There is no expert answer — that's exactly what we're trying to determine. `expected` would have to be the document itself, which Factuality would then treat as the gold-standard answer to an implied question. This is a forced mapping with no semantic grounding.

Any attempt to fit findings into the Factuality frame requires writing logic to construct artificial `input`/`expected` values — at which point you have built a custom scorer anyway, and the Factuality abstraction adds nothing.

---

## 4. Category Mismatch with the Genuineness Gate

CLAUDE.md states: **the genuineness gate is binary.** A finding is GENUINE or NOT_GENUINE. Partial credit is explicitly prohibited:

> "Once you allow NOT_GENUINE findings to score positively because they seem humanly useful, every false positive gets a defense and the precision metric becomes meaningless."

Factuality's partial credit structure directly violates this guardrail:

- A hallucinated finding that's a "superset" of something in the document (category B) scores 0.6 — a false positive rewarded.
- A finding that's "on a different topic" from the expert answer (category E) scores 1.0 — semantically irrelevant to genuineness.
- The only "this is wrong" category (D, score 0.0) conflates a different kind of disagreement than "this finding is fabricated."

Mapping 5-category partial-credit scores to a binary gate would require thresholding (score > X → GENUINE). This reintroduces calibration complexity while inheriting the conceptual mismatch. It doesn't simplify; it complicates.

---

## 5. Model and Infrastructure Notes

The default model for `autoevals` Factuality is gpt-4o. Running it with Claude requires either:
- **Braintrust proxy:** routes OpenAI-format calls to Claude. Adds SaaS dependency.
- **LiteLLM:** translates tool-call schemas between providers. Adds local infrastructure.

Neither is a blocker, but the overhead is real for a scorer that doesn't fit the domain. Inspect AI already has native Anthropic provider support with no translation layer.

---

## 6. Ordering Answer (Moot)

Issue #73 (judge calibration gate) listed as a prerequisite: "*#73 before #79.*" The intent was: don't evaluate a supplementary scorer before establishing whether the primary judge is miscalibrated.

This dependency is now moot. The reject decision is based on semantic mismatch, not calibration concerns. Even if #73 found the Haiku judge to be severely miscalibrated, Factuality would still be the wrong remedy — it operates on a different task definition and violates the binary gate requirement.

---

## 7. Decision

**REJECT autoevals Factuality as a supplementary scorer.**

| Criterion | Assessment |
|-----------|------------|
| Input mapping fit | Poor — no natural question/answer frame for design findings |
| Binary gate compatibility | Incompatible — partial credit violates CLAUDE.md guardrail |
| Model support | Requires translation layer for Claude |
| Added value over `reverse_judge_precision` | None — would need custom scaffolding to approximate what the existing scorer already does cleanly |

**This is the same class of rejection as RAGAS in ADR-008:** an entailment/factuality framework applied to a binary-gate classification problem. The prior art sweep pattern holds.

---

## 8. What to Adopt from autoevals

One engineering pattern is worth noting for future reference:

**`LLMClassifier` base class** — Mustache prompt template + `choice_scores` dict + tool-call extraction. Clean separation of prompt template, choice mapping, and score extraction. If we ever need an alternative to Inspect AI's `@scorer` decorator API (e.g., for a TypeScript-adjacent context or cross-platform scorer portability), `LLMClassifier` is the reference implementation to study.

No code to adopt now. Note is for future reference only.

---

## 9. Relationship to ADR-008

ADR-008 covers the prior art sweep: RAGAS (skip), Braintrust (keep Inspect AI, consider autoevals), Vercel (skip), G-Eval (reject for Haiku). The "consider autoevals" note in ADR-008 is now resolved:

- Issue #76 (Braintrust platform): SKIP — keep Inspect AI. Documented in prior art research.
- Issue #79 (autoevals Factuality): REJECT — category mismatch with binary gate. Documented here.
- Issue #75 (G-Eval): REJECTED — same FN rate, worse FP rate, 10x latency. Documented.

**ADR-008 prior art sweep is now complete.** All "maybe" items have been investigated and resolved.

---

## Sources

- [autoevals Factuality source (GitHub)](https://github.com/braintrustdata/autoevals)
- [LLMClassifier implementation](https://github.com/braintrustdata/autoevals/blob/main/py/autoevals/llm.py)
- `docs/research/prior-art-braintrust-vercel-2026-02-17.md` — Issues #76 and #78 analysis
- ADR-008 (G-Eval experiment, session 32) — recorded in MEMORY.md
- CLAUDE.md §"Eval Design Guardrails" — the genuineness gate is binary
