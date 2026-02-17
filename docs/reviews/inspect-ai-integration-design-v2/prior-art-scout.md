# Prior Art Scout Review — Inspect AI Integration Design v2

**Document:** `docs/plans/2026-02-17-inspect-ai-integration-design-v2.md`
**Requirements:** `docs/requirements/inspect-ai-integration-requirements-v2.md`
**Reviewer:** Prior Art Scout
**Date:** 2026-02-17
**Findings:** 9 (2 Critical, 5 Important, 2 Minor)

---

## Prior Art Landscape

This design builds on Inspect AI as the eval runner — that decision is documented and sound (ADR-005). The remaining custom-built components are:

1. **`agent_loader.py`** — YAML frontmatter parser to extract system prompts from agent markdown files
2. **`reviewer_eval.py`** — per-reviewer `@task` functions with ID-based and fuzzy title scoring
3. **`dataset_loader.py` update** — reviewer-name-based ground truth filtering
4. **Fuzzy matching scorer** — title similarity at 0.8 threshold as a fallback for ID-based matching
5. **Custom JSONL output parser** — parses agent output to extract structured findings
6. **Makefile orchestration** — wraps `inspect eval` invocations with tagging, cost reporting

The relevant prior art landscape includes:

- **Inspect AI built-in scorers:** `includes()`, `match()`, `pattern()`, `model_graded_fact()`, `f1()` — the framework has native recall/precision scoring for list-valued targets
- **OpenEvals (`langchain-ai/openevals`):** Readymade evaluators including `create_json_match_evaluator` for structured output extraction matching — directly applicable to JSONL finding comparison
- **RapidFuzz / TheFuzz:** Industry-standard fuzzy string matching libraries with `token_sort_ratio`, `token_set_ratio`, and `WRatio` methods — the obvious substrate for the 0.8 threshold title similarity fallback
- **`lm-format-enforcer` / `llm-output-parser`:** Libraries for constraining and parsing LLM structured outputs, including markdown fence stripping — standard approach to the fence-wrapping problem
- **Python `frontmatter` library (`python-frontmatter`):** Dedicated YAML/TOML frontmatter parser for Markdown files — does exactly what `agent_loader.py` is being built to do
- **Promptfoo:** Open-source prompt testing with YAML-defined assertions, built-in JSON extraction, and CI/CD integration — alternative framing for what the eval framework is building

The design's decision to use Inspect AI is well-researched. The question this review addresses is: within that decision, what components of the custom implementation layer are being built unnecessarily?

---

## Findings

### Finding 1: Custom frontmatter parser reinvents `python-frontmatter`
- **Severity:** Critical
- **Phase:** plan (primary)
- **Section:** `agent_loader.py` — Agent Loader
- **Issue:** `agent_loader.py` is described as stripping YAML frontmatter from agent markdown files using `content.index('---', 3)`. The `python-frontmatter` library (PyPI: `python-frontmatter`, MIT license, 400k+ monthly downloads) parses exactly this format. It handles edge cases that the custom implementation misses: missing frontmatter blocks (returns content unchanged), frontmatter delimiters appearing in body content (correctly bounded by line-start `---`), TOML and JSON frontmatter variants, and encoding edge cases. The assumption-hunter review (Finding 006 in the co-located review) independently identified that the custom `content.index('---', 3)` approach raises `ValueError` on missing frontmatter and incorrectly truncates body content containing horizontal rules (`---`). Both failure modes are handled by `python-frontmatter` without additional code.
- **Why it matters:** The custom parser is one missed edge case from silently corrupting the system prompt loaded into every eval task. Silent corruption — where the agent receives a truncated or empty prompt — produces zero findings, which is indistinguishable at the scorer level from "the agent found nothing." The v1 failure (accuracy 0.000 from markdown output) was exactly this class of silent format failure. Building a brittle parser where a battle-tested library exists for free restarts the debugging loop that cost Session 21.
- **Suggestion:** Replace the custom frontmatter parsing in `agent_loader.py` with `python-frontmatter`. Installation: `pip install python-frontmatter`. Usage: `import frontmatter; post = frontmatter.load(path); content = post.content`. This eliminates the `ValueError` and horizontal-rule truncation bugs identified in the assumption-hunter review, requires no custom parsing logic, and handles all edge cases documented in the library. Add `python-frontmatter` to `pyproject.toml` dependencies.

---

### Finding 2: Custom fuzzy title matching reinvents RapidFuzz — and the 0.8 threshold is invented, not empirical
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** Scorer — ID-based matching with fuzzy fallback
- **Issue:** The design specifies a fuzzy title similarity fallback at threshold 0.8 for when ID-based matching fails. Two issues: (1) The implementation is described without referencing any library — the design appears to build string similarity from scratch. RapidFuzz (MIT license, C++ backend, 5-100x faster than TheFuzz, industry standard for Python fuzzy matching) provides `fuzz.token_sort_ratio()` and `fuzz.WRatio()` that implement exactly the token-order-invariant similarity needed for finding titles. TheFuzz (formerly FuzzyWuzzy) is the legacy alternative. Neither is mentioned. (2) The 0.8 threshold is stated without any empirical basis. In a ground truth dataset of 10 findings with 2 per reviewer, a threshold that is 1 point too high silently drops valid matches, collapsing recall to 0 for that reviewer. A threshold too low produces false matches across different findings. The threshold requires calibration against actual title pairs from the existing ground truth before being hardcoded into the scorer.
- **Why it matters:** A wrong fuzzy match threshold is a silent accuracy killer. The design's Phase 1 success criteria require recall ≥ 0.90. If the fuzzy fallback mismatches due to an uncalibrated threshold, the scorer reports 0.50 recall (one miss out of two findings) for that reviewer — Phase 1 fails with no clear diagnostic. The failure is in the threshold, not the agent. Building custom string similarity rather than using RapidFuzz adds implementation surface that obscures this diagnostic further.
- **Suggestion:** Use `rapidfuzz.fuzz.WRatio()` (or `token_sort_ratio()` for title-length-normalized comparison) for the fuzzy fallback. Install: `pip install rapidfuzz`. Before hardcoding 0.8, calibrate the threshold: take the existing 10 ground truth findings, generate paraphrased title variants (manually or via LLM), compute similarity scores for true pairs vs non-pairs, and set the threshold at the boundary that maximizes F1 on this calibration set. Document the calibration result in the design. A threshold derived from data is defensible; 0.8 as a round number is not.

---

### Finding 3: Inspect AI's built-in `f1()` scorer already computes recall and precision over lists — the custom scorer may be unnecessary
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scorer — overall scoring approach
- **Issue:** The design builds a custom scorer that matches model output IDs to ground truth IDs and computes recall and precision. Inspect AI provides a built-in `f1()` scorer that computes F1 (which implies recall and precision) over token-level overlap between model output and reference targets. More directly applicable: Inspect AI's `model_graded_fact()` scorer can be configured with a custom grading prompt to assess whether a given finding from the model output semantically corresponds to a given ground truth finding — this is LLM-as-judge semantic matching, not string matching. Neither is evaluated in the design. The design jumps to custom implementation without confirming that built-in scorers cannot satisfy the requirement.
- **Why it matters:** Custom scorers are maintenance burden. Every change to the scoring logic requires code review, testing, and deployment. If Inspect AI's `f1()` or `model_graded_fact()` handles 80% of the use case, the custom scorer should be a thin wrapper (or nothing) not a full implementation. ADR-005 explicitly states the design should "leverage 90% of Inspect AI infrastructure" — the scorer is infrastructure.
- **Suggestion:** Before implementing the custom scorer, run a 1-hour spike: use `f1()` scorer against a sample of 3-5 ground truth findings from the existing dataset. Measure whether token-level F1 aligns with the desired recall metric. If `f1()` is insufficient (likely for ID-based matching), evaluate `model_graded_fact()` with a custom grading prompt: "Does this finding address the same issue as the reference finding? GRADE: C (yes) or GRADE: I (no)." If semantic matching via LLM-as-judge is acceptable for the fallback (instead of fuzzy title similarity), this eliminates the threshold calibration problem entirely. Document which approach is chosen and why in the design.

---

### Finding 4: `langchain-ai/openevals` `create_json_match_evaluator` is readymade for structured output extraction — not evaluated
- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Section:** Scorer — overall approach and dataset_loader.py
- **Issue:** The LangChain `openevals` library (MIT license, actively maintained by LangChain team) provides `create_json_match_evaluator` — a readymade evaluator specifically for "cases in an application where you're extracting structured content from documents." This is the exact use case: the eval checks whether a model's structured JSONL output (finding extraction) matches reference structured output (ground truth findings). The design does not reference `openevals` and does not appear to have evaluated it. ADR-005 evaluated Inspect AI vs LangGraph but not the openevals package, which sits between them in the stack — not a full orchestration framework, but readymade evaluation logic for structured extraction.
- **Why it matters:** If `create_json_match_evaluator` handles finding-level matching (JSON object comparison with configurable key weights), it eliminates both the custom scorer and the fuzzy fallback. The scorer becomes a configuration call, not implementation. The design's stated goal is "build only what Inspect AI doesn't provide" — but the evaluation of "what Inspect AI doesn't provide" stopped at the framework level without examining the surrounding ecosystem of evaluator libraries that integrate with or complement Inspect AI.
- **Suggestion:** Add `openevals` to the prior art evaluation. The spike is short: install `openevals`, configure `create_json_match_evaluator` to match on the `title` field (or `id` field when present), and run against 3 ground truth finding pairs (true match, near-miss, non-match). Determine whether its matching logic produces the expected pass/fail. If it fits, integrate via Inspect AI's custom scorer pattern — `openevals` evaluators can be called from within an Inspect `@scorer` function. Document the evaluation result in the design regardless of outcome.

---

### Finding 5: JSONL output parsing ignores the fence-stripping problem that is well-solved in existing libraries
- **Severity:** Important
- **Phase:** plan (primary), design (contributing)
- **Section:** JSONL Output Alignment — output parser
- **Issue:** The design states agents output JSONL and the scorer parses it, but does not address what happens when Claude wraps the JSONL in markdown code fences (` ```json ... ``` `). This is not an edge case — Claude is trained to wrap structured output in fences by default, and the agent prompt examples in the codebase (e.g., `assumption-hunter.md`) show JSONL inside fence blocks in their `output format` sections, which trains the model toward fenced output. The `llm-output-parser` PyPI package, the `openevals` code extraction utilities, and multiple documented patterns (regex strip on ` ``` ` delimiters) solve this deterministically. The assumption-hunter review (Finding 007) and the requirements review (Critical finding #9 in `summary.md`) both independently flagged this. The design does not resolve it.
- **Why it matters:** Fenced output produces zero parsed findings. Zero parsed findings is the v1 failure mode (accuracy 0.000). The design explicitly cites fixing the v1 failure as its motivation. Not addressing fence-stripping in the output parser means the v1 failure recurs on any agent that outputs fenced JSONL, which is the majority behavior for Claude models given current training. This is the highest-probability silent failure in the design.
- **Suggestion:** Add fence-stripping as an explicit acceptance criterion in FR-ARCH-3 and implement it in `output_parser.py` before any other scorer work. The implementation is 3-5 lines: strip leading ```` ```json ```` or ```` ``` ```` and trailing ```` ``` ```` delimiters before line-by-line JSON parsing. Libraries like `llm-output-parser` (PyPI) provide this as a one-call utility. In parallel, update agent system prompts to include: "Output raw JSONL only. Do not wrap output in markdown code fences." Both defenses are needed — the prompt instruction reduces fence frequency; the parser handles the cases where fencing still occurs.

---

### Finding 6: The Makefile `cost-report` target builds custom log parsing that Inspect View already provides
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Makefile Update — `make cost-report`
- **Issue:** FR-ARCH-5 requires `make cost-report` to read EvalLogs and report token usage and cost. Inspect AI's `EvalLog` already captures per-sample token counts, cost, and latency. Inspect View (the built-in web UI, launched via `inspect view`) displays this information in a browsable interface. The `inspect eval` CLI outputs a summary including total tokens and estimated cost after each run. Building a custom `make cost-report` target that re-parses the same EvalLog JSON adds a maintenance artifact for a problem Inspect AI already solves via its native reporting path.
- **Why it matters:** Custom log parsers drift from the actual log format as Inspect AI evolves. The EvalLog schema has already changed at least once during this project (Session 21 documented API deviations). A custom parser that reads EvalLog fields by name breaks silently when those fields are renamed or restructured. The requirements review (`summary.md`, Important finding #6) flagged that `make cost-report` is "orthogonal to Phase 1 blocking problem" — it is also solving a problem that already has a native solution.
- **Suggestion:** Remove `make cost-report` from Phase 1 scope and rely on Inspect View and the CLI summary for cost visibility. If programmatic cost access is needed in Phase 2, use the Inspect AI Python API (`EvalLog.stats.total_tokens`, `EvalLog.stats.total_cost`) rather than re-parsing raw JSON. Document the decision in the design: "cost reporting is handled by Inspect AI native tooling; `make cost-report` is deferred unless native tooling proves insufficient."

---

### Finding 7: The multi-task Makefile invocation pattern has a documented Inspect AI convention — use it
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Makefile Update — `make reviewer-eval`
- **Issue:** The design states `inspect eval evals/reviewer_eval.py` runs all 5 `@task` functions, but the assumption-hunter review (Finding 005) identifies that Inspect AI's behavior with multiple `@task` functions in one module is undocumented in the design. The Inspect AI documentation specifies the `--task` flag for selecting individual tasks from a multi-task module, and the convention for running all tasks is either separate invocations or a task registry pattern. The design builds a Makefile target without first verifying which invocation pattern Inspect AI requires. This is a case of building a wrapper for a convention before reading the convention documentation.
- **Why it matters:** If `inspect eval reviewer_eval.py` without `--task` silently runs only the first `@task` function, the Makefile target provides false confidence — the developer sees a completed eval for one reviewer and believes all five ran. This is a diagnostic gap, not just a correctness gap.
- **Suggestion:** Read the Inspect AI multi-task invocation documentation before writing the Makefile target. The Inspect AI docs at `https://inspect.aisi.org.uk/` cover task selection. If per-task invocation is required, the Makefile should loop: one `inspect eval` call per task name (`assumption_hunter_eval`, `constraint_finder_eval`, etc.) or use a wrapper script. This is a 30-minute documentation read, not a design question.

---

### Finding 8: Python `semantic-version` or `bump2version` handles the git-tag-based version correlation pattern
- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Makefile Update — git tag generation
- **Issue:** The Makefile uses `git rev-parse --short HEAD` to tag eval runs for commit correlation. This is the right primitive, but commit hashes do not communicate semantic change magnitude — a typo fix and a methodology rewrite have indistinguishable hashes. Standard practice for eval regression tracking uses semantic versioning alongside commit hashes: major (methodology change), minor (wording refinement), patch (typo). Tools like `bump2version` (PyPI) or `semantic-release` automate this alongside git. The assumption-hunter review (Finding 011) correctly identified the `git rev-parse` silent failure in detached HEAD environments but did not surface the semantic versioning gap.
- **Why it matters:** Recall drops from 0.90 to 0.82 are only interpretable if the eval consumer knows whether the change between the two runs was a methodology rewrite or a wording fix. Commit hashes do not carry this information. The eval log shows a performance change happened; semantic version shows what class of change caused it. Without this, regression attribution is guesswork.
- **Suggestion:** Add semantic versioning to agent prompt files (a `version:` field in the YAML frontmatter that `agent_loader.py` can extract and pass to the Inspect AI eval tag). This requires no external tooling — the version lives in the agent file, incremented by the developer when making changes. The Makefile tag becomes `--tags 'git=$(shell git rev-parse --short HEAD 2>/dev/null || echo unknown),agent-version=$(AGENT_VERSION)'`. This is a Minor finding because the commit hash is a workable substitute for now; semantic versioning becomes important when the eval suite runs regularly.

---

### Finding 9: Promptfoo is a near-equivalent alternative for the Phase 1 use case — it may be simpler for prompt iteration
- **Severity:** Minor
- **Phase:** survey (primary)
- **Section:** Overall architecture — choice of eval framework
- **Issue:** The design is committed to Inspect AI (ADR-005, well-justified). However, for Phase 1's specific use case — testing agent prompts against a small ground truth dataset with rapid iteration — Promptfoo (open source, MIT-adjacent license, free up to 10k probes/month as noted in CLAUDE.md) is a simpler fit. Promptfoo uses YAML-defined test cases, built-in JSON extraction, LLM-as-judge assertions, and CI/CD integration with no Python code required. The iteration loop (change prompt → run eval → see pass/fail) is faster in Promptfoo because the eval is declarative (YAML) rather than imperative (Python `@task`). Promptfoo is already in the tooling budget.
- **Why it matters:** This is a Minor finding because Inspect AI is the right long-term choice (multi-model comparison, batch API, agent evaluation in Phase 3). The question is whether Phase 1 — which is fundamentally prompt iteration against a small dataset — justifies Inspect AI's Python overhead relative to Promptfoo's YAML-first approach. If the team finds Python eval setup friction is slowing prompt iteration, Promptfoo is the documented alternative. This is not a recommendation to switch — it is a flag that the alternative exists and is already budgeted.
- **Suggestion:** No action required before Phase 1. If Phase 1 implementation encounters significant Python/Inspect AI setup friction (>2 hours of debugging boilerplate), evaluate Promptfoo for the prompt iteration loop specifically. Keep Inspect AI for Phase 2+ (agent evaluation, multi-model comparison). Document the evaluation outcome in ADR-005 or a new ADR-007.

---

## Blind Spot Check

**What this review may have missed:**

1. **Inspect AI version specifics:** The design references Inspect AI patterns (Dataset/Sample/Task/Scorer) that are version-sensitive. The review identified relevant prior art but did not verify whether the `f1()` scorer or `model_graded_fact()` patterns cited exist in the specific pinned version of Inspect AI used by this project. Version pinning (surfaced as Critical in the requirements review) matters here — recommendations to use built-in scorers are only valid if those scorers exist in the pinned version.

2. **The novel contribution is the ground truth curation workflow, not the scorer:** The custom scorer, fuzzy matching, and dataset filtering are all plumbing. The genuinely novel piece of this design is the ground truth refresh cadence (metadata hash, living ground truth, per-reviewer attribution). No existing tool provides a "ground truth lifecycle management" workflow for LLM eval frameworks — this is legitimately custom work. This review focused on the plumbing layer; the ground truth lifecycle design deserves its own review pass.

3. **Dual-context agent format tension may require a new standard:** The assumption-hunter review (Finding 008) and the requirements review correctly identified that changing agent output to JSONL degrades human readability in production. The standard industry approach — separate eval variants from production agents — is the right answer, but no existing tool provides a "canonical agent with context-specific output format injection" pattern. This may be a genuinely novel design problem that neither Inspect AI, Promptfoo, nor OpenEvals has solved.

---

## Sources

- [Inspect AI Scorers documentation](https://inspect.aisi.org.uk/scorers.html)
- [Inspect AI GitHub](https://github.com/UKGovernmentBEIS/inspect_ai)
- [OpenEvals — readymade evaluators for LLM apps](https://github.com/langchain-ai/openevals)
- [Quickly Start Evaluating LLMs With OpenEvals — LangChain blog](https://blog.langchain.com/evaluating-llms-with-openevals/)
- [RapidFuzz — rapid fuzzy string matching in Python](https://github.com/rapidfuzz/RapidFuzz)
- [python-frontmatter — PyPI](https://pypi.org/project/python-frontmatter/)
- [llm-output-parser — PyPI](https://pypi.org/project/llm-output-parser/)
- [lm-format-enforcer — enforce LLM output format](https://github.com/noamgat/lm-format-enforcer)
- [Promptfoo — test your prompts and agents](https://github.com/promptfoo/promptfoo)
- [Inspect AI Review 2025 — NeuRL Creators](https://neurlcreators.substack.com/p/inspect-ai-evaluation-framework-review)
- [Hamel's Inspect AI guide](https://hamel.dev/notes/llm/evals/inspect.html)
