# Prior Art Scout Review

## Prior Art Landscape

The two-tier scoring approach (reverse_judge_precision + must_find_recall) overlaps with well-established patterns in LLM evaluation:

- **Faithfulness/Hallucination detection (RAGAS, TruLens):** Measures whether LLM outputs are grounded in source context. reverse_judge_precision is structurally identical to RAGAS "faithfulness" scoring — a judge verifies each generated claim against the source document. RAGAS is MIT-licensed, has a Python SDK, and integrates with evaluation frameworks.
- **Answer Correctness / Semantic Recall (RAGAS):** Measures what fraction of ground truth answers appear in the generated output. must_find_recall is structurally identical to RAGAS "answer_recall" metric.
- **G-Eval (OpenAI/MIT):** LLM-as-judge framework that uses chain-of-thought prompting to score generated outputs on arbitrary criteria. The design's genuineness criterion is a G-Eval-style rubric.
- **LLM-as-judge calibration (Zheng et al., 2023 — "Judging LLM-as-a-judge"):** Published research on position bias, verbosity bias, and self-enhancement bias in LLM judges. Haiku has not been specifically calibrated for adversarial design finding evaluation.
- **Braintrust:** The project already has access to Braintrust (free tier, 1M spans, 10K scores). Braintrust natively implements LLM-as-judge scoring with per-trace logging, dataset management, and score aggregation — the infrastructure ADR-007 is building manually.

## Findings

### Finding 1: RAGAS faithfulness scorer implements reverse_judge_precision with calibrated defaults
- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** RAGAS faithfulness (pip install ragas) takes a list of claims (findings) and a context (design document) and returns a faithfulness score 0–1 — identical to the reverse_judge_precision design. RAGAS has been calibrated against human annotators on document-grounded tasks. The design builds this scorer from scratch with an uncalibrated Haiku judge and a custom false positive list. RAGAS integrates with LangSmith (which the project has access to) and supports Anthropic models.
- **Why it matters:** Building a custom precision scorer involves significant prompt engineering, calibration work, and ongoing maintenance. RAGAS delivers the same metric with documented calibration methodology and an active maintenance community. Using RAGAS for the precision scorer would reduce implementation surface area and provide calibration benchmarks out of the box.
- **Suggestion:** Evaluate RAGAS faithfulness as a drop-in implementation for reverse_judge_precision before building custom. Concerns to evaluate: (1) Does RAGAS faithfulness handle adversarial design findings (not factual QA)? (2) Does it integrate cleanly with Inspect AI's scorer interface? (3) Is the false positive list encodable as RAGAS criticism criteria? If RAGAS integration takes more than one session, the custom approach is preferable — but the evaluation should be explicit, not skipped.

### Finding 2: Braintrust already implements the two-tier eval infrastructure the design proposes building
- **Severity:** Important
- **Phase:** survey (primary)
- **Section:** Scoring Strategy (ADR-007) — Overall architecture
- **Issue:** Braintrust (in the project budget, free tier with 1M spans) natively implements: dataset management with frozen snapshots, LLM-as-judge scoring (configurable), per-trace score logging, score aggregation across runs, and regression detection between eval versions. The design proposes building all of these manually in Inspect AI. The rationale for Inspect AI over Braintrust was covered in ADR-005, but ADR-005 predates the ADR-007 scoring strategy. The specific requirements of ADR-007 (reverse judge, curated recall list, multi-run aggregation) may be better served by Braintrust's purpose-built eval infrastructure than by Inspect AI extensions.
- **Why it matters:** The curation workflow (must_find.jsonl, context_dependent_findings.jsonl) and scorer infrastructure being built in this design are exactly what Braintrust's dataset and scoring APIs manage. Building this in Inspect AI requires maintaining custom JSONL management, curation protocols, and scorer code that Braintrust provides as platform features.
- **Suggestion:** The comparison was not made in ADR-005 specifically for the two-tier scoring approach. Add a decision record: 'Evaluated Braintrust for ADR-007 scoring infrastructure. Decision: [stay with Inspect AI because X / migrate curation and scoring to Braintrust because Y].' The existing investment in Inspect AI infrastructure is a real switching cost — but the decision should be documented, not implicit.

### Finding 3: G-Eval chain-of-thought prompting produces more reliable binary classifications than direct judgment
- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Section:** Scoring Strategy (ADR-007) — Tier 1, judge prompt design
- **Issue:** The design specifies the judge at T=0 outputs a binary genuine/not_genuine verdict. G-Eval (published: "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment," 2023) demonstrated that requiring the judge to generate evaluation steps before the verdict (chain-of-thought) significantly improves calibration versus direct verdicts — especially for abstract criteria like "is this a genuine design flaw?" The design does not reference G-Eval or chain-of-thought prompting for the judge.
- **Why it matters:** A judge that produces a direct YES/NO without reasoning is less reliable than one that reasons through the false positive criteria before deciding. For Haiku (a smaller, faster model), this reliability gap is larger — Haiku is more susceptible to prompt-surface-level pattern matching without chain-of-thought prompting. Adding reasoning steps to the judge output also produces interpretable explanations for why a finding was classified as NOT genuine — essential for debugging false negatives in the curation process.
- **Suggestion:** Update the judge design to use chain-of-thought output: `{"reasoning": "This finding claims X is missing. Checking against the false positive criteria: (1) Is it an implementation detail? No — it identifies a requirement gap. (2) Hallucinated constraint? No — the document references X in section Y. Verdict: genuine.", "verdict": "genuine"}`. Parse the verdict field for scoring; log the reasoning field for debugging. This is compatible with T=0 determinism.

### Finding 4: "Discovered from document content alone" is a known hard problem in QA faithfulness research
- **Severity:** Minor
- **Phase:** survey (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1, Encoded criteria — GENUINE
- **Issue:** The criterion "Discoverable from the document content alone (no external context required)" is a standard faithfulness requirement in open-domain QA evaluation. Research (Goyal et al., 2020; Krysciński et al., 2020) has established that faithfulness classification is harder than it appears — judges frequently hallucinate support for a claim from the document even when no such support exists. The design does not reference this literature or its implications for judge reliability on design review tasks.
- **Why it matters:** The faithfulness classification problem is unsolved even for factual QA. For design review (where "document support" is often implicit reasoning, not explicit text), the classification difficulty is higher. This is not a blocker — the design's calibration approach is the right mitigation — but the design should acknowledge this as a known hard problem with a reference, not present the criterion as straightforwardly evaluable.
- **Suggestion:** Add a note in the scoring strategy: 'Document-grounded classification (determining whether a finding requires external context) is known to be difficult for LLM judges — see faithfulness evaluation research. Haiku calibration against known context-dependent findings (from context_dependent_findings.jsonl) is essential before trusting judge verdicts on this criterion.'

## Blind Spot Check
I focused on existing solutions and research the design may have missed. I may have underweighted: (1) that the project has already invested significantly in Inspect AI infrastructure, making RAGAS/Braintrust comparison a non-trivial switching cost; (2) that the design's custom false positive list provides domain-specific calibration that generic frameworks (RAGAS) may not match for design review without significant tuning; (3) that the prior art in LLM eval scoring is mostly for factual QA tasks, not adversarial design review — the design may genuinely be in novel territory where prior art provides partial guidance only.
