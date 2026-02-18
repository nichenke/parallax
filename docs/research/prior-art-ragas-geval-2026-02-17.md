# Prior Art Analysis: RAGAS Faithfulness & G-Eval CoT Scoring

**Date:** 2026-02-17
**Issues:** #74 (RAGAS faithfulness), #75 (G-Eval chain-of-thought)
**Context:** ADR-007 two-tier eval scoring for parallax adversarial design review

---

## 1. RAGAS Faithfulness (Issue #74)

### What It Does Mechanically

RAGAS faithfulness operates in two LLM calls per evaluation:

1. **Claim decomposition:** An LLM extracts atomic claims from the generated answer. Each claim is a single factual assertion.
2. **NLI verification:** For each claim, an LLM (or classifier model) judges: "Can this claim be directly inferred from the given context?" Verdict: 1 (supported) or 0 (not supported).

Score = supported_claims / total_claims. Range: 0.0 to 1.0.

### Output Format

A single float per sample. Per-claim verdicts are intermediate artifacts, not surfaced in the standard API. The metric is sample-level, not corpus-level.

### Judge Models

- Default: whatever LLM you configure (GPT-4, Claude, etc.) via LangChain wrappers.
- Alternative: Vectara HHEM-2.1-Open (fine-tuned T5 classifier) for the NLI step only. Free, small, fast -- but tuned for RAG/QA entailment, not design review.
- Model is swappable. RAGAS v0.4 supports `LangchainLLMWrapper` for any LangChain-compatible model, including Claude via Bedrock.

### Known Failure Modes

- **Neutral-as-unfaithful:** Claims neither supported nor contradicted are scored as unfaithful. This is a strict entailment standard -- correct for RAG grounding, problematic for design review where findings involve inference.
- **Ambiguous context:** Faithfulness drops when context is ambiguous (reported 0.65 in ambiguous-term tests). Design documents are inherently ambiguous.
- **Context length:** Documented issues with >8K token contexts requiring chunking. Parallax passes full documents (potentially 50K+) to the judge.
- **Judge bias:** OpenAI judges favor concise claims, underrating verbose answers by ~10%.
- **Claim decomposition quality:** If the LLM decomposes findings poorly (merging two issues into one claim, or splitting one issue into five), the precision denominator shifts. This is a hidden sensitivity.

### Overlap with Parallax

RAGAS faithfulness is structurally isomorphic to `reverse_judge_precision`. Both ask: "Is this output grounded in the source material?" The key differences:

| Dimension | RAGAS Faithfulness | `reverse_judge_precision` |
|---|---|---|
| Question asked | "Can this claim be inferred from context?" | "Is this finding a genuine flaw in the document?" |
| Entailment standard | Strict NLI (must be directly inferable) | Genuineness (real gap, non-hallucinated, document-visible) |
| False positive criteria | None -- binary entailment only | 6 explicit categories (implementation detail, hallucinated constraint, style preference, hypothetical concern, duplicate, external context) |
| Claim unit | Atomic claim (auto-decomposed) | Finding (structured output from reviewer) |
| Two-step decomposition | Required (claims then NLI) | Not needed (findings are already atomic units) |

The critical gap: RAGAS checks entailment ("does the context say this?"), not genuineness ("is this a real problem in the context?"). A design finding like "the document does not specify error handling for API timeouts" is *not entailed* by the document (the document says nothing about it), but *is genuine* (the absence is a real gap). RAGAS would score this as unfaithful. Parallax would score it as genuine. This is a fundamental semantic mismatch for absence-detection findings, which are the majority of design review output.

### Overlap with `must_find_recall`

None. RAGAS faithfulness is precision-directional only. It has no recall component against a curated ground truth set.

### Verdict: **Skip**

RAGAS faithfulness solves the wrong problem for design review. Its strict entailment standard would false-positive on every absence-detection finding ("X is missing from the document"). The claim decomposition step adds cost and a sensitivity axis that parallax avoids by treating structured findings as atomic units. The explicit false positive taxonomy in ADR-007 is more precise than binary entailment for the design review domain.

**What to adopt from RAGAS:** The *pattern* of per-claim granularity and the two-call architecture (decompose then judge) is sound. Parallax already follows this pattern -- reviewer produces findings (decomposition), judge evaluates each (verification). No code to adopt; the architectural insight is already embedded.

---

## 2. G-Eval Chain-of-Thought Scoring (Issue #75)

### What It Does Mechanically

G-Eval operates in three steps:

1. **Auto-CoT generation:** Given evaluation criteria, the LLM generates a structured list of evaluation steps (once, cached for reuse).
2. **Form-filling evaluation:** The LLM applies the generated steps to each sample, reasoning through each step before producing a score.
3. **Token probability weighting:** The raw score token's log-probability is used to compute a weighted score, reducing bias from the LLM's tendency to favor certain score values.

### Output Format

Typically a Likert-scale score (1-5 or 1-10), but can be adapted to binary yes/no. DeepEval's implementation supports binary verdicts where each evaluation step produces yes/no/unsure, with final scores computed from weighted step verdicts.

### Judge Models

- Original paper: GPT-4 (Spearman correlation 0.514 with human on summarization).
- DeepEval implementation: any LLM via their wrapper. Supports Claude.
- **Token probability requirement:** The log-probability weighting step requires API support for logprobs. Claude's API supports logprobs (top_logprobs parameter, 0-20 tokens). This is available but adds API complexity.

### Known Failure Modes

- **Score consistency:** LLMs may assign different scores to the same input across runs. The CoT + probability weighting mitigates but does not eliminate this.
- **Evaluation step quality:** Auto-generated evaluation steps can be vague or miss criteria. Manual step specification is more reliable (DeepEval allows overriding auto-generated steps with explicit `evaluation_steps`).
- **Token cost:** CoT reasoning chains are 3-10x longer than direct verdict outputs. For parallax, each finding-level judge call would cost 3-10x more tokens.
- **Smaller model degradation:** The original paper benchmarked GPT-4. Performance with smaller models (GPT-3.5 class, Haiku class) is not rigorously benchmarked in the literature. The CoT approach should help smaller models by forcing structured reasoning, but the token probability weighting may be less meaningful when the model's probability distribution is less calibrated.

### Overlap with Parallax

G-Eval's core insight is directly relevant to Issue #73 (judge calibration gate): forcing the judge to reason through evaluation steps before rendering a verdict should reduce Haiku's tendency toward shallow YES responses. The question is whether the improvement justifies the cost.

| Dimension | G-Eval CoT | Current parallax judge | Proposed adaptation |
|---|---|---|---|
| Reasoning order | Steps first, then verdict | Verdict + one-sentence reason | Steps first, then verdict |
| Probability weighting | Yes (requires logprobs API) | No | Defer (adds complexity) |
| Auto-generated steps | Yes | No (criteria are hardcoded) | No (use explicit steps from ADR-007 criteria) |
| Cost multiplier | 3-10x per judge call | 1x | ~3x (reasoning chain, no probability weighting) |
| Binary support | Yes (via DeepEval) | Yes (YES/NO) | Yes |

### Overlap with `must_find_recall`

None. G-Eval is a scoring technique, not a recall metric. It could improve the judge used *within* must_find_recall (better matching accuracy), but does not replace the recall measurement itself.

### Verdict: **Adapt** (the CoT reasoning pattern; skip token probability weighting)

The valuable part of G-Eval for parallax is *reasoning before verdict*, not the probability weighting machinery. Concrete adaptation:

1. **Restructure the judge prompt** from "Answer YES or NO, then explain" to "Evaluate against these steps, then give your verdict":
   - Step 1: Does the finding identify a specific, nameable gap in the document?
   - Step 2: Is the described problem actually present in or absent from the document?
   - Step 3: Could this finding be discovered from the document alone?
   - Step 4: Does it match any false positive category? (list the 6 categories)
   - Verdict: GENUINE or NOT_GENUINE

2. **Skip auto-CoT generation.** The evaluation steps are already defined in ADR-007. Auto-generation adds variance and cost for no benefit.

3. **Skip token probability weighting.** It adds API complexity (logprobs parsing), and for binary classification the benefit over forced-reasoning is marginal. If calibration remains a problem after adopting reasoning-first prompts, revisit.

4. **Expected cost impact:** ~3x token increase per judge call (reasoning chain vs. one sentence). At Haiku pricing ($0.25/MTok input, $1.25/MTok output), this is negligible for the eval workload (hundreds of findings, not millions).

---

## Comparative Summary

| Capability | RAGAS Faithfulness | G-Eval CoT | `reverse_judge_precision` | `must_find_recall` |
|---|---|---|---|---|
| What it measures | Entailment of claims in context | Quality score with structured reasoning | Genuineness of findings against document | Coverage of curated must-find findings |
| Handles absence-detection | No (absence != entailment) | N/A (scoring technique) | Yes (core design) | Yes (must-find includes absences) |
| Per-item granularity | Per claim | Per sample | Per finding | Per must-find finding |
| Custom false positive criteria | No | Yes (via evaluation steps) | Yes (6 categories in judge prompt) | N/A |
| Open source implementation | Yes (explodinggradients/ragas, MIT) | Yes (DeepEval, Apache 2.0) | Custom (parallax) | Custom (parallax) |
| Inspect AI compatible | No native integration | No native integration | Yes (Inspect scorer) | Yes (Inspect scorer) |

## Final Verdicts

| Technique | Verdict | Reasoning |
|---|---|---|
| RAGAS faithfulness | **Skip** | Strict entailment semantics are wrong for design review (absence-detection findings are the majority of output). Claim decomposition adds unnecessary cost since parallax findings are already atomic. The architectural pattern is already embedded in ADR-007. |
| G-Eval CoT (reasoning pattern) | **Adapt** | Reasoning-before-verdict directly addresses the Haiku calibration concern (Issue #73). Hardcode the evaluation steps from ADR-007 criteria instead of auto-generating. Skip probability weighting. ~3x token cost increase is acceptable at Haiku pricing. |
| G-Eval probability weighting | **Defer** | Adds API complexity for marginal benefit on binary classification. Revisit if reasoning-first prompts do not resolve calibration issues. |

## Concrete Next Steps

1. Restructure the judge prompt in Issue #71 implementation to use reasoning-first format (4 evaluation steps from ADR-007 criteria, then verdict). This is a prompt change, not an architecture change.
2. Run the experiment proposed in Issue #75: 20 findings, direct-verdict vs. reasoning-first, compare NO rates on known false positives.
3. Close Issue #74 with "skip" decision and link to this analysis.
4. Update Issue #75 to reflect "adapt reasoning pattern, skip probability weighting" decision.

---

## Sources

- [RAGAS Faithfulness Documentation](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [RAGAS Faithfulness Source Code](https://github.com/explodinggradients/ragas/blob/main/src/ragas/metrics/_faithfulness.py)
- [G-Eval Paper (Liu et al., 2023)](https://arxiv.org/abs/2303.16634)
- [G-Eval Simply Explained - Confident AI](https://www.confident-ai.com/blog/g-eval-the-definitive-guide)
- [DeepEval G-Eval Implementation](https://deepeval.com/docs/metrics-llm-evals)
- [Faithfulness Metrics Under the Microscope](https://thecodexandthecompass.substack.com/p/faithfulness-metrics-under-the-microscope)
- [G-Eval for LLM Evaluation - Comet](https://www.comet.com/site/blog/g-eval-for-llm-evaluation/)
- [RAGAS vs DeepEval Comparison](https://medium.com/@sjha979/ragas-vs-deepeval-measuring-faithfulness-and-response-relevancy-in-rag-evaluation-2b3a9984bc77)
