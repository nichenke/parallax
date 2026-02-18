# Prior Art Analysis: Braintrust & Vercel AI SDK Testing Patterns

**Date:** 2026-02-17
**Issues:** #76 (Braintrust re-evaluation), #78 (Vercel AI SDK testing)
**Context:** ADR-007 two-tier eval scoring, ADR-005 Inspect AI integration decision

---

## 1. Braintrust (Issue #76)

### What It Actually Does

Braintrust is a proprietary SaaS platform (with open-source `autoevals` library, MIT) providing: experiment tracking with diff-based comparison across runs, dataset management with versioning, LLM-as-judge scoring, human annotation UI, production log monitoring, and CI/CD integration via GitHub Action that posts score diffs to PRs.

**Scorer API:** Scorers receive `{input, output, expected, metadata}` and return a score 0-1. Custom LLM-as-judge scorers are defined via prompt templates with `{{input}}`/`{{output}}`/`{{expected}}` variables, model selection, and choice-to-score mappings. Chain-of-thought reasoning is configurable. The `autoevals` library (MIT, standalone, no platform dependency) provides Factuality, ClosedQA, Semantic Similarity, Levenshtein, and JSON validation scorers.

**Dataset management:** Datasets are versioned within the platform. Experiments pin to dataset versions for reproducibility. Datasets can be built from production logs, user feedback, or manual curation. No frozen-document-alongside-ground-truth pattern native to the platform -- documents would need to be stored as metadata fields.

**Run-to-run variance:** Not directly addressed. Braintrust compares experiments (prompt A vs prompt B, model X vs model Y) but does not have built-in N-run statistical aggregation or per-item recall estimation across stochastic runs. Variance is handled implicitly through experiment comparison UI, not explicitly through statistical methodology.

**Cost model:** Free tier: 1M spans, 10K scores, 14-day retention. Pro: $249/month (unlimited spans, 50K scores, 30-day retention). Enterprise: custom pricing, hybrid self-hosting (control plane stays in Braintrust cloud). The `autoevals` library is free and standalone.

### Fit Analysis for Parallax

**`reverse_judge_precision`:** Braintrust's custom LLM-as-judge scorer could implement this. Define a prompt template that takes `{{output}}` (finding) and `{{metadata.document}}` (frozen doc), ask genuineness question, map YES/NO to 1/0. The 6-category false positive list goes in the prompt. Mechanically workable, but no cleaner than Inspect AI's `@scorer` decorator -- both are "write a prompt, call an LLM, parse the result."

**`must_find_recall`:** Braintrust has no native recall-against-curated-list primitive. You would implement this as a custom code scorer that iterates `expected` findings and checks for matches in `output`. Same custom code as Inspect AI.

**What Braintrust adds over Inspect AI:**
- Experiment comparison UI with score diffs (Inspect View shows individual runs, not cross-run comparison)
- Human annotation UI for ground truth curation
- GitHub Action for PR-level score regression (Inspect AI requires custom CI wiring)
- Production log monitoring (irrelevant for parallax -- no production deployment)

**What parallax loses switching to Braintrust:**
- Full open-source stack (Braintrust platform is proprietary)
- Batch API integration (Inspect AI has native Anthropic batch support, 50% cost reduction)
- Sandboxed execution (Docker/K8s -- irrelevant for parallax but indicates infrastructure depth)
- Deep agent evaluation patterns (multi-turn, tool use -- Braintrust is shallower here)
- 14-day free tier retention vs unlimited local logs
- Self-contained local-first workflow (Braintrust requires SaaS for experiment tracking)

**Verdict: Keep Inspect AI. Consider `autoevals` library for supplementary scorers.**

The ADR-007 scoring needs are custom by nature -- `reverse_judge_precision` and `must_find_recall` require domain-specific prompts and logic that neither platform provides out of the box. Braintrust's advantages (comparison UI, annotation, CI integration) are convenience features, not capability gaps. The 10K score free tier limit would be consumed quickly during iterative scorer development. Inspect AI's batch API integration and local-first model are better fits for parallax's cost-conscious, OSS-first philosophy.

---

## 2. Vercel AI SDK Testing Patterns (Issue #78)

### What It Actually Provides

The Vercel AI SDK (`vercel/ai`, MIT) has two distinct testing-relevant capabilities:

**1. Mock providers for unit testing:** `MockLanguageModelV1` and `simulateReadableStream` let you stub LLM responses for deterministic unit tests. This is application-layer testing infrastructure -- test that your code handles LLM responses correctly without calling a real model. Equivalent to mocking an HTTP client. Not an eval framework.

**2. Eval-driven development pattern (blog/docs guidance):** Vercel recommends three grading tiers: code-based (exact match, JSON validation), human feedback, and LLM-as-judge. Their published approach uses Vitest as the test runner with AI SDK calls in test cases. Sentry's `vitest-evals` library (open source) extends this with `Task`/`Scorer` abstractions and JUnit XML export for CI integration via Codecov.

### Applicability to Parallax

**Mock providers:** Not applicable. Parallax evals need to call real LLMs (that is the point -- measuring reviewer agent quality). Mock providers solve a different problem (application integration testing).

**Vitest-evals pattern:** The "evals are just tests" philosophy is interesting but does not add capability over Inspect AI. Vitest-evals provides `Task` (input -> output) and `Scorer` (output -> 0-1 score) -- structurally identical to Inspect AI's `@task` and `@scorer` but in TypeScript instead of Python. Sentry's vitest-evals uses Braintrust `autoevals` for LLM-as-judge scoring (Factuality, ClosedQA).

**Run-to-run variance:** Not addressed. Vercel's guidance acknowledges non-determinism as a challenge but offers no statistical methodology (no N-run aggregation, no per-item recall thresholds). The advice is effectively "run evals, compare results manually."

**Vercel's next-evals-oss:** 20 fixture-based tasks for testing AI model competency at Next.js code generation. Eval structure: scaffold project, run agent, assert build/lint/test pass. This is a functional correctness eval (did the code work?), not a quality eval (is the analysis good?). Not transferable to design review scoring.

**Verdict: Skip.** Nothing here that Inspect AI does not already provide. The mock providers solve a problem parallax does not have. The eval patterns are structurally identical to Inspect AI but less mature for LLM evaluation specifically. The "evals as tests" insight is valid but already embedded in parallax's Makefile-driven eval workflow.

---

## 3. Comparative Table

| Dimension | Inspect AI | Braintrust | Vercel/vitest-evals |
|---|---|---|---|
| **Eval runner** | Native CLI + Python API | SaaS + SDK | Vitest (test runner) |
| **LLM-as-judge** | `model_graded_fact()` + custom `@scorer` | Custom prompt templates + `autoevals` | Via `autoevals` (Braintrust library) |
| **Custom scorer API** | `@scorer` decorator, full Python | JS/TS/Python functions, 0-1 return | `Scorer` class, 0-1 return |
| **Dataset versioning** | File-based (JSONL in git) | Platform-managed, versioned | File-based (fixtures in git) |
| **Frozen doc snapshots** | Stored in `Sample.input` | Store as metadata field | Store as test fixture |
| **Batch API (cost)** | Native Anthropic batch (50% off) | No batch support | No batch support |
| **N-run aggregation** | Custom (build it) | Not native | Not native |
| **Run comparison** | Inspect View (single-run) | Experiment diff UI (strong) | JUnit XML / Codecov |
| **CI/CD integration** | Custom (Makefile, GH Actions) | Native GitHub Action | JUnit XML export |
| **Open source** | MIT (full stack) | Proprietary (autoevals MIT) | MIT |
| **Cost** | Free (pay LLM tokens) | Free tier 10K scores, Pro $249/mo | Free (pay LLM tokens) |
| **Claude native support** | Yes (Anthropic provider) | Yes (via LangChain) | Yes (via AI SDK) |
| **Agent eval depth** | Deep (multi-turn, tool use, sandbox) | Shallow (single-turn focus) | Shallow (function-level) |

### Scored Against ADR-007 Needs

| ADR-007 Requirement | Inspect AI | Braintrust | Vercel |
|---|---|---|---|
| `reverse_judge_precision` (custom LLM judge, per-finding, 6-category FP list) | Custom scorer, full control | Custom scorer, equivalent | Custom scorer, equivalent |
| `must_find_recall` (curated list, per-finding found/not-found) | Custom scorer, full control | Custom scorer, equivalent | Custom scorer, equivalent |
| Frozen document in eval pipeline | `Sample.input` (validated) | Metadata field (unvalidated) | Test fixture (workable) |
| Judge at T=0, reviewer at T~1 | Full temperature control | Model config supported | Model config supported |
| N=1 MVP, N=3 Phase 2 | Custom loop (build it) | No native N-run | No native N-run |
| `min_recall` per finding (Phase 2) | Custom scorer logic | Custom scorer logic | Custom scorer logic |
| Batch API for cost | Native (50% reduction) | Not available | Not available |

---

## 4. Golden Path Verdict

**Inspect AI remains the correct choice. ADR-005 stands.**

The core finding: all three approaches require the same amount of custom scorer code for parallax's specific needs. `reverse_judge_precision` and `must_find_recall` are domain-specific metrics that no platform provides natively. The differentiator is infrastructure around those custom scorers, and Inspect AI wins on the dimensions that matter for parallax:

1. **Cost:** Batch API integration saves 50% on eval runs. At projected eval volumes ($150-400/mo API spend), this is material. Braintrust adds $0-249/mo platform cost on top of LLM tokens with no batch discount.

2. **Open source / local-first:** Full MIT stack, all data local, no SaaS dependency, no retention limits. Aligns with parallax's development philosophy.

3. **Agent eval depth:** Inspect AI is built for agent evaluation (multi-turn, tool use, sandboxing). Parallax's reviewer agents are single-turn today but may evolve. Braintrust is explicitly weaker here.

4. **Existing investment:** Phase 1 implemented, 65 tests passing, scorer prototype validated. Switching cost is non-zero for no capability gain.

### What Would Change This Decision

- Inspect AI development stalls or the project is abandoned (unlikely -- AISI actively maintains it)
- Parallax needs a human annotation UI for ground truth curation at scale (Braintrust's strongest feature -- but parallax's must-find lists are small and curated in JSONL)
- Cross-experiment comparison becomes a bottleneck (Braintrust's diff UI is better than Inspect View for A/B comparison)

### What to Adopt

| Source | Adopt | How |
|---|---|---|
| Braintrust `autoevals` | **Maybe** -- evaluate `Factuality` scorer as a supplementary signal alongside `reverse_judge_precision` | `pip install autoevals`, use standalone (no platform) |
| Braintrust experiment comparison | **No** -- build lightweight comparison in Makefile/scripts when needed | N/A |
| Vercel mock providers | **No** -- not applicable to eval workload | N/A |
| Vitest-evals "evals as tests" | **Already embedded** -- parallax runs evals via `make reviewer-eval` | N/A |

---

## Sources

- [Braintrust Scorer Docs](https://www.braintrust.dev/docs/evaluate/write-scorers)
- [Braintrust Experiments Docs](https://www.braintrust.dev/docs/core/experiments)
- [Braintrust Pricing](https://www.braintrust.dev/pricing)
- [Braintrust autoevals (GitHub, MIT)](https://github.com/braintrustdata/autoevals)
- [Custom LLM-as-Judge with Braintrust (OpenAI Cookbook)](https://cookbook.openai.com/examples/custom-llm-as-a-judge)
- [Vercel AI SDK Testing Docs](https://ai-sdk.dev/docs/ai-sdk-core/testing)
- [Vercel Eval-Driven Development](https://vercel.com/blog/eval-driven-development-build-better-ai-faster)
- [Vercel Introduction to Evals](https://vercel.com/guides/an-introduction-to-evals)
- [Sentry vitest-evals (GitHub)](https://github.com/getsentry/vitest-evals)
- [Sentry: Evals Are Just Tests](https://blog.sentry.io/evals-are-just-tests-so-why-arent-engineers-writing-them/)
- [Vercel next-evals-oss (GitHub)](https://github.com/vercel/next-evals-oss)
- [Hamel Husain: Selecting The Right AI Evals Tool](https://hamel.dev/blog/posts/eval-tools/)
- [Arize: Braintrust Open Source Alternative](https://arize.com/docs/phoenix/resources/frequently-asked-questions/braintrust-open-source-alternative-llm-evaluation-platform-comparison)
- [Langfuse: Braintrust Alternatives](https://langfuse.com/faq/all/best-braintrustdata-alternatives)
