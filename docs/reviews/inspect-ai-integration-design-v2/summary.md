# Review Summary: Inspect AI Integration Design v2

**Date:** 2026-02-17
**Design:** `docs/plans/2026-02-17-inspect-ai-integration-design-v2.md`
**Requirements:** `docs/requirements/inspect-ai-integration-requirements-v2.md`
**Stage:** design
**Verdict:** revise

---

## Verdict Reasoning

Four Critical findings are blockers before a single line of `reviewer_eval.py` can be written: the agent output format is unfixed (v1's root failure), fence-stripping is absent from the output parser (a second silent-zero path), agent body text instructs tool calls that don't exist in eval context (a third silent-zero path), and the reviewer field attribution in the existing ground truth dataset is unverified (the per-reviewer filter may return empty datasets on first run). Any one of these reproduces `accuracy: 0.000` silently. The design also has structural calibration gaps — N=2 ground truth produces statistically incoherent signal, and the eval measures recall on a stripped proxy that differs significantly from the production orchestration context. To proceed, the design must add explicit pre-Phase 1 audit gates for the four implementation blockers and must explicitly frame what Phase 1 can and cannot claim to validate. The per-reviewer task architecture (v2's core insight) is sound; the surrounding specification needs to tighten.

---

## Finding Counts

- **Critical:** 11
- **Important:** 14
- **Minor:** 9
- **Contradictions:** 1

## Findings by Phase

- **Design flaws:** 8
- **Calibrate gaps:** 5
- **Plan concerns:** 4
- **Survey gaps:** 1

**Systemic issue note:** 5 of 11 Critical findings (45%) have calibrate phase as their primary or contributing phase. This exceeds the 30% threshold — systemic issue detected. Consider escalating calibrate-phase gaps (eval scope framing, ground truth depth, success criteria) to requirements review before Phase 1 implementation begins.

---

## Auto-Fixable Findings

The following findings are mechanical corrections requiring no design judgment:

1. **ADR-006 file missing on disk** — create `docs/requirements/adr-006-per-reviewer-eval-task-decomposition.md` using session notes from Sessions 21-23.
2. **`v1-post-review-001` missing `"discovery": "implementation"` field** — add the field to `datasets/inspect-ai-integration-requirements-light/critical_findings.jsonl`.
3. **FR-ARCH-3 ID schema mismatch** — update `docs/requirements/inspect-ai-integration-requirements-v2.md` FR-ARCH-3 schema to use `v1-<reviewer>-<NNN>` matching actual usage in the design and dataset.
4. **`git rev-parse` silent failure** — add `2>/dev/null || echo unknown` fallback in the Makefile git tag command.
5. **FR-QUALITY-1 missing target score** — add placeholder `"Target aggregate quality score: >=3.5/5.0 (provisional)"` to the Phase 2 Design Prerequisites section.

All other findings require human judgment to resolve.

---

## Critical Findings

### C-1: assumption-hunter.md still outputs markdown — no audit gate enforces the fix before Phase 1

- **Severity:** Critical
- **Severity range:** Critical (Assumption Hunter, Edge Case Prober, Feasibility Skeptic)
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (001), Edge Case Prober (2), Feasibility Skeptic (2)
- **Section:** JSONL Output Alignment
- **Issue:** The design acknowledges that `assumption-hunter.md` outputs markdown (not JSONL) and states the fix is to "update the output format section." The actual agent file still contains the markdown output template and no JSONL block as of this review. More critically, the design provides no audit gate — there is no Phase 1 prerequisite step to verify the fix was applied before `reviewer_eval.py` is written and run. The design also does not audit the other 4 agents for FR-ARCH-2 compliance; it asserts they are "already JSONL" without evidence.
- **Why it matters:** The v1 `accuracy: 0.000` failure was caused by exactly this mismatch. If implementation begins from the current state, the assumption-hunter task silently produces prose output, the scorer returns recall = 0.0, and the debugging loop restarts from the same place that cost Session 21.
- **Suggestion:** Add a mandatory Phase 1 prerequisite checklist before `reviewer_eval.py` implementation: (1) Open all 5 agent files, confirm output format section produces JSONL (not markdown). (2) Run each agent manually against a sample document, verify raw output is parseable JSONL with no fences and all required fields. Gate `make reviewer-eval` behind `make audit-agents` (a smoke test that instantiates each agent and checks for JSONL). Create a compatibility table: `agent | JSONL native | fence-free | all fields | tool-free`.
- **Fixability:** human-decision
- **Status:** open

---

### C-2: JSONL fence-stripping absent from output parser — Claude wraps JSONL in fences by default

- **Severity:** Critical
- **Severity range:** Critical (Assumption Hunter, Edge Case Prober, Prior Art Scout)
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Assumption Hunter (007), Edge Case Prober (1), Prior Art Scout (5)
- **Section:** JSONL Output Alignment / `output_parser.py`
- **Issue:** The design mandates JSONL output from agents and relies on `output_parser.py` to parse it line-by-line. No fence-stripping step is designed. Claude models are trained to wrap structured output in markdown code fences even when instructed not to, and the agent prompt examples in the codebase show JSONL inside fence blocks — actively training the model toward fenced output. A strict line-by-line parser returns zero findings for fenced-but-valid JSONL. This is the second independent path back to `accuracy: 0.000`. The requirements review (summary.md, Critical finding #9) flagged this; the design does not resolve it.
- **Why it matters:** Zero parsed findings is indistinguishable from "the agent found nothing." This failure mode silently invalidates all Phase 1 recall measurements without any diagnostic signal.
- **Suggestion (from all three reviewers):** Add fence-stripping to `output_parser.py` as an explicit acceptance criterion before any other scorer work — strip leading ` ```json ` or ` ``` ` and trailing ` ``` ` delimiters before line-by-line JSON parsing. The `llm-output-parser` PyPI package provides this as a one-call utility. In parallel, update agent system prompts to include: "Output raw JSONL only. Do not wrap output in markdown code fences." Add a test case that provides fenced-but-valid JSONL and asserts the parser produces the correct finding count. Add a distinct log signal when zero findings are parsed (e.g., `"parse_result": "empty"`) to distinguish format failure from genuine zero.
- **Fixability:** human-decision
- **Status:** open

---

### C-3: Frontmatter parser crashes on malformed or missing delimiter — blast radius is 5/5 tasks

- **Severity:** Critical
- **Severity range:** Critical (Edge Case Prober); Important (Assumption Hunter, Feasibility Skeptic); addressed via library by Prior Art Scout
- **Phase:** plan (primary)
- **Flagged by:** Assumption Hunter (006), Edge Case Prober (3, 6), Feasibility Skeptic (10), Prior Art Scout (1)
- **Section:** `evals/utils/agent_loader.py`
- **Issue:** `load_agent_content()` uses `content.index("---", 3)` to find the closing frontmatter delimiter. `str.index()` raises `ValueError` if the substring is not found — crashing the entire eval suite (all 5 tasks) if any agent file has malformed or missing frontmatter. Additionally, if any agent body contains a `---` horizontal rule before the intended frontmatter close, `content.index()` matches the body delimiter, truncating the system prompt mid-content and silently degrading the agent's instructions. The `python-frontmatter` library (MIT, 400k+ monthly downloads) handles both edge cases natively and does exactly what `agent_loader.py` is being built to do.
- **Why it matters:** A single malformed agent file kills the entire `make reviewer-eval` run. Silent prompt truncation produces degraded output attributable to the agent (not the loader), making root cause diagnosis misleading.
- **Suggestion:** Replace the custom frontmatter parsing with `python-frontmatter` (`pip install python-frontmatter`). Usage: `import frontmatter; post = frontmatter.load(path); content = post.content`. This eliminates the `ValueError` and horizontal-rule truncation bugs in one dependency addition. Add `python-frontmatter` to `pyproject.toml`. If the custom parser is retained, add `try/except ValueError` with a descriptive error naming the agent file, and use a regex anchored to line boundaries (`^---$`) rather than substring search.
- **Fixability:** human-decision
- **Status:** open

---

### C-4: N=1 to N=2 ground truth per reviewer produces statistically incoherent eval signal

- **Severity:** Critical
- **Severity range:** Critical (Assumption Hunter, Edge Case Prober, Feasibility Skeptic, First Principles — all four independently)
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** Assumption Hunter (004), Edge Case Prober (4), Feasibility Skeptic (3), First Principles (6)
- **Section:** Per-Reviewer Tasks / Ground Truth Management / Phase 1 Test Plan
- **Issue:** The ground truth table shows scope-guardian has 1 finding (N=1), and assumption-hunter, constraint-finder, problem-framer, success-validator each have 2 (N=2). At N=1, recall is binary — 1.0 or 0.0. At N=2, a single missed finding drops recall by 50 percentage points. The Phase 1 success criterion requires "≥1 reviewer task achieves recall ≥ 0.90" — but at N=2, the only reachable values are 0.0, 0.5, and 1.0; the 0.90 threshold is only achievable at 100% (2/2). The design cannot distinguish "this agent has a systematic gap" from "this agent missed one edge-case finding in a 2-finding dataset." LLM non-determinism alone causes ±50-point recall swings at this sample size.
- **Why it matters:** Phase 1 will produce numbers that look like signal but are noise. Prompt tuning decisions made on N=2 data are arbitrary — an agent that paraphrases one finding slightly differently "fails" Phase 1 regardless of its actual capability. The eval framework's purpose is empirical improvement; N=2 is below the minimum viable measurement threshold.
- **Suggestion (four-reviewer consensus):** Before Phase 1 runs: (a) Set a minimum ground truth count of N≥5 per reviewer. The requirements-light review for v2 (`docs/reviews/inspect-ai-integration-v2-requirements-light/summary.md`) contains additional findings per reviewer that can be validated and added. (b) Alternatively, explicitly reframe Phase 1 as a smoke test only ("does the pipeline not crash? does output parse?") with no recall targets, deferring quantitative thresholds to Phase 2 when ground truth is expanded. The design must choose one path — leaving N=2 unaddressed while calling Phase 1 a "detection baseline" is misleading. Add a disclaimer to eval output when N<5 per reviewer.
- **Fixability:** human-decision
- **Status:** open

---

### C-5: reviewer field attribution in existing ground truth is unverified — per-reviewer filter may return empty datasets

- **Severity:** Critical
- **Severity range:** Critical (Assumption Hunter, Feasibility Skeptic)
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (003), Feasibility Skeptic (4)
- **Section:** Dataset Loader — Reviewer Filter
- **Issue:** The entire per-reviewer task architecture depends on filtering ground truth by `reviewer` field (`f.get("reviewer") == reviewer_filter`). The existing 10 findings were validated from full-skill output (parallax:requirements --light orchestration), not from individual agent runs. There is no confirmation that findings in `critical_findings.jsonl` carry a `reviewer` field populated with each agent's exact name. If the field is missing, or uses a different naming convention (e.g., `"assumption_hunter"` with underscore vs `"assumption-hunter"` with hyphen, or display name `"Assumption Hunter"` vs filename), every per-reviewer task returns an empty dataset. An empty dataset produces recall = 0.0 with no error — silent failure.
- **Why it matters:** This is the per-reviewer architecture's single point of failure. If the field convention is wrong, the entire v2 approach collapses to v1's outcome (0.000 accuracy) before a single agent prompt is tested.
- **Suggestion:** Add a mandatory pre-flight check before `reviewer_eval.py` implementation: open `critical_findings.jsonl`, print all unique `reviewer` field values, verify each matches the expected agent filename (without `.md`). Add `make validate-dataset` that loads the dataset, groups by reviewer field, prints counts, and fails explicitly if any expected reviewer has 0 findings. Document the expected reviewer field values in `metadata.json`. If the field is missing from existing findings, add a data migration step to annotate each finding before proceeding.
- **Fixability:** human-decision
- **Status:** open

---

### C-6: ADR-006 cited as authority for key design decisions but does not exist on disk

- **Severity:** Critical
- **Severity range:** Critical (Assumption Hunter)
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (002)
- **Section:** Overview / Key Design Decisions
- **Issue:** The design's Overview section and the requirements Background section both delegate key rationale to ADR-006 ("full rationale for the per-reviewer task architecture"). The file `docs/requirements/adr-006-per-reviewer-eval-task-decomposition.md` does not exist on disk. This was flagged in the requirements review (summary.md, Critical finding #2) and persisted into the design. Any reviewer or future maintainer who wants to understand why the v1 approach was abandoned cannot do so from documents alone — the design's Key Decisions section partially duplicates rationale but is incomplete.
- **Why it matters:** Two consequences: (1) The decision cannot be audited or challenged without reconstructing context from session notes. (2) The design's own completeness depends on a non-existent document.
- **Suggestion:** Create `docs/requirements/adr-006-per-reviewer-eval-task-decomposition.md` using the rationale in Sessions 21-23 session notes (the content is captured there — it needs promotion to a durable artifact). This is listed as auto-fixable above in terms of creating the file, but the content requires human authorship from the session notes.
- **Fixability:** human-decision (content) / auto-fixable (file creation placeholder)
- **Status:** open

---

### C-7: Agent body text instructs "Read the document" — tool calls unavailable in eval context invalidate FR-ARCH-2

- **Severity:** Critical
- **Severity range:** Critical (Requirement Auditor); Important (Feasibility Skeptic, Edge Case Prober)
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Requirement Auditor (1), Feasibility Skeptic (5), Edge Case Prober (10)
- **Section:** FR-ARCH-2 / JSONL Output Alignment
- **Issue:** FR-ARCH-2 requires agents to function in eval context without tool calls. The design fixes `assumption-hunter.md`'s output format but does not address agent body text that instructs models to use tools. `scope-guardian.md` review process step 1: "Read the design document thoroughly." `success-validator.md` review process step 1: "Read the design document thoroughly." All 5 agents declare `tools: ["Read", "Grep", "Glob", "Write"]` in frontmatter. Frontmatter is stripped by `agent_loader.py` — the tool-call instructions in body text are not. FR-ARCH-2 acceptance criterion 2 requires agent prompts to contain "The design document content will be provided to you in this message" — no design element adds this instruction to any agent file.
- **Why it matters:** In eval context, a model that receives "Read the design document" with no file path may attempt a tool call that fails, hallucinate a reading step, or skip it and produce fewer findings. Any of these outcomes produces a misleading detection baseline — the agent appears weaker than it is because context delivery is wrong, not because its analysis is weak. Session 21 documented this exact failure: "model receiving path not content."
- **Suggestion:** Enumerate each of the 5 in-scope agent files and document the exact body text change needed: remove or qualify "Read the [document]" instructions, add explicit "Document content follows in this message" transition language. Add an acceptance criterion to FR-ARCH-2: "All 5 agent files pass a pre-Phase-1 audit checklist: no 'Read the file' instructions in review steps, contains explicit content-in-prompt transition." The audit checklist is a Phase 1 prerequisite, not an assumption.
- **Fixability:** human-decision
- **Status:** open

---

### C-8: FR-ARCH-4 automated hash check has no design element — ground truth staleness is unprotected

- **Severity:** Critical
- **Severity range:** Critical (Requirement Auditor); Important (Feasibility Skeptic, Edge Case Prober)
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor (2), Feasibility Skeptic (7), Edge Case Prober (5)
- **Section:** Ground Truth Management / FR-ARCH-4
- **Issue:** FR-ARCH-4's second acceptance criterion: "`make validate` re-runs if document hash differs." The design describes the `design_doc_hash` field in `metadata.json` and the manual 5-step refresh process, but no design element computes a document hash, compares it to `metadata.json`, or triggers `make validate` automatically. There is no `make validate` target in the design. FR-ARCH-4's third acceptance criterion is also unmet: "Post-review findings stored with `'discovery': 'implementation'` field" — `v1-post-review-001` is in the dataset without this field. Edge Case Prober additionally notes the hash spec is underspecified: no algorithm (MD5, SHA-256?), no CRLF normalization — a CRLF difference between macOS dev and CI causes the same document to hash differently.
- **Why it matters:** Stale ground truth was identified as a root cause of false positives in Session 19. The staleness check is the only mechanism protecting against this. A manual process that requires a developer to remember 5 steps will be skipped under time pressure, producing false eval signals that mislead the iteration loop.
- **Suggestion:** Design the `make validate` target explicitly: reads `metadata.json`, computes SHA-256 hash of the reviewed document after UTF-8 decode + LF normalization (strip `\r`), aborts with a warning if hashes differ. Add `make check-hash` dependency to `make reviewer-eval` so staleness is enforced at eval runtime. Separately, add the `"discovery": "implementation"` field to `v1-post-review-001` now (listed as auto-fixable).
- **Fixability:** human-decision
- **Status:** open

---

### C-9: Eval validates a stripped-down proxy, not the production artifact — scope of Phase 1 claims is overstated

- **Severity:** Critical
- **Severity range:** Critical (First Principles)
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** First Principles (1)
- **Section:** Overview and Context / Per-Reviewer Task Architecture
- **Issue:** The design tests individual reviewer agents reading a document in a single-turn, tool-free context. The thing parallax ships is an orchestration workflow that dispatches agents with tools, collects output, runs a synthesizer, deduplicates findings, and produces a consolidated report. V2 corrects v1's error (testing the skill, not the agents) but overcorrects: agents in the stripped eval context differ from agents in production context on tools, system prompt layering, context window state, and synthesizer filtering. A green Phase 1 dashboard does not imply the full skill works. An agent that scores 90% recall in isolation may produce 50% recall through the full pipeline if synthesis deduplication or tool-calling context changes its behavior.
- **Why it matters:** The stated problem is "we cannot measure skill effectiveness." Phase 1 measures something easier — isolated agent detection in a clean lab. If eval results are misread as validating the full skill, false confidence accumulates until a production failure reveals the gap.
- **Suggestion:** Reframe the eval explicitly in the design. Add a section: "What Phase 1 validates and does not validate." State: "Phase 1 validates the signal layer (do agents detect findings when given document content directly?). Phase 3 validates the system layer (does the full orchestration pipeline preserve those findings through synthesis?). A Phase 1 pass does not imply the full skill works end-to-end." This costs nothing and prevents the most predictable misreading of results.
- **Fixability:** human-decision
- **Status:** open

---

### C-10: Ground truth is sourced from the same agents under test — eval is partially self-referential

- **Severity:** Critical
- **Severity range:** Critical (First Principles)
- **Phase:** calibrate (primary)
- **Flagged by:** First Principles (2)
- **Section:** Ground Truth Management / Phase 1 Test Plan
- **Issue:** The 10 Critical findings used as ground truth were produced by the parallax review skill (which dispatches these same reviewer agents), then manually validated. The eval then tests whether each reviewer agent detects findings from its own prior output. Attribution — which finding belongs to which reviewer — may be inferred from finding ID prefixes (e.g., `assumption-hunter-001`) rather than established independently based on the finding's nature. If so, the ground truth labels are circular by construction: assumption-hunter is tested on findings assumption-hunter produced, making high recall nearly tautological regardless of prompt quality. The eval measures prompt stability (can the agent reproduce its own output?) not detection capability (can the agent catch real design flaws it hasn't seen before?).
- **Why it matters:** Optimizing for reproduction of prior output can mask failures in generalization. The eval framework's purpose is to detect capability regressions when prompts change — but if high recall is achieved by prompt stability alone, regressions are invisible until a genuinely new document is reviewed.
- **Suggestion:** Ground truth requires two independent properties: (a) each finding is a real design flaw (human validation addresses this), and (b) each finding is attributable to a specific reviewer persona based on the nature of the finding, not who produced it. Re-examine the reviewer attribution in the existing dataset — confirm it was assigned based on each agent's stated focus areas, not the finding ID prefix. Add at least a few findings from a different review artifact to test generalization, not just reproduction.
- **Fixability:** human-decision
- **Status:** open

---

### C-11: Custom fuzzy title scorer built from scratch; 0.8 threshold is invented, not empirical

- **Severity:** Critical
- **Severity range:** Critical (Prior Art Scout)
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Prior Art Scout (2)
- **Section:** Scorer — ID-based matching with fuzzy fallback
- **Issue:** The design specifies a fuzzy title similarity fallback at threshold 0.8 without referencing any library or empirical basis. Two issues: (1) The implementation appears custom-built — RapidFuzz (MIT, C++ backend, industry standard for Python fuzzy matching) provides `fuzz.WRatio()` and `fuzz.token_sort_ratio()` for exactly this use case and is not mentioned. (2) The 0.8 threshold is a round number. In a ground truth dataset of 2 findings per reviewer, a threshold 1 point too high silently drops valid matches, collapsing recall to 0. A threshold too low produces false matches across different findings. Neither direction is detectable without calibration.
- **Why it matters:** A wrong fuzzy match threshold is a silent accuracy killer. Phase 1 success criteria require recall ≥ 0.90. If the fuzzy fallback mismatches due to an uncalibrated threshold, the scorer reports 0.50 recall (one miss from two findings) with no clear diagnostic — the failure looks like an agent problem, not a scorer problem.
- **Suggestion:** Use `rapidfuzz.fuzz.WRatio()` for the fuzzy fallback (`pip install rapidfuzz`). Before hardcoding 0.8, calibrate the threshold: take the existing 10 ground truth findings, generate paraphrased title variants, compute similarity for true pairs vs non-pairs, set the threshold at the F1-maximizing boundary. Alternatively, evaluate `model_graded_fact()` (Inspect AI built-in) as the semantic fallback — LLM-as-judge matching eliminates the threshold calibration problem entirely. Document which approach is chosen.
- **Fixability:** human-decision
- **Status:** open

---

## Important Findings

### I-1: Phase 1 success criteria are weak and internally inconsistent

- **Severity:** Important
- **Phase:** calibrate (primary)
- **Flagged by:** Assumption Hunter (009), Edge Case Prober (9), Feasibility Skeptic (8)
- **Section:** Phase 1 Test Plan
- **Issue:** Three overlapping problems: (a) "At least 1 reviewer task achieves recall ≥ 0.90" — 4 of 5 agents broken constitutes Phase 1 complete under this criterion. (b) Criterion #2 ("at least 1 reviewer task achieves recall > 0.0") is subsumed by criterion #3 (≥0.90) — they are not additive gates, creating ambiguity when one passes and the other fails. (c) The 90%/80% thresholds from requirements-v1 are carried forward as if confirmed; requirements-v2 describes them as provisional. The design does not reconfirm them as Phase 1 targets.
- **Why it matters:** Ambiguous completion gates cause scope disagreement mid-implementation. A criterion that allows 4 of 5 agents to fail is not a meaningful validation of a 5-reviewer framework.
- **Suggestion:** Collapse to one unambiguous exit gate: "All 5 reviewer tasks produce parseable JSONL output (zero parse errors) AND at least 3 of 5 tasks achieve recall > 0.0 AND at least 1 task achieves recall ≥ 0.50." Save 90%/80% thresholds for Phase 2 when ground truth is expanded. Explicitly state whether the gate is AND (all reviewers must meet it) or OR (at least one).
- **Fixability:** human-decision
- **Status:** open

---

### I-2: Phase 1 recall-only metric creates perverse incentive — precision not measured

- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** First Principles (3)
- **Section:** Phase 1 Test Plan / FR-ARCH-1
- **Issue:** Phase 1 success metrics optimize for recall (does the agent detect ground truth findings?). The stated problem in v1 requirements was that parallax produces too many Important findings — a calibration failure caused by excess findings, not missed findings. The harder problem — precision (does the agent avoid false positives, stay in its lane, avoid duplicating other reviewers?) — is not measured in Phase 1. An agent that floods its output with findings achieves high recall while degrading the actual user experience.
- **Why it matters:** A recall-only eval creates a perverse incentive during prompt tuning: adding "be aggressive, find more issues" to any agent prompt improves recall scores while degrading real-world output quality. This is measurably the wrong optimization target given the stated calibration problem.
- **Suggestion:** Phase 1 must measure precision alongside recall. The completion gate should require F1 or a precision floor (e.g., precision ≥ 0.60 at the same time as recall ≥ 0.50). Without a precision constraint, eval scores can improve while the skill gets worse for users.
- **Fixability:** human-decision
- **Status:** open

---

### I-3: JSONL schema defined in three locations with no canonical source — schema drift is the v1 root cause

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic (6), First Principles (4)
- **Section:** JSONL Output Alignment
- **Issue:** The required JSONL schema appears in the design doc, in individual agent prompt files, and in `output_parser.py`. The design adds a fourth location without designating a canonical source. When the schema changes (e.g., adding the `contributing` phase field, changing ID format), every location must be updated manually. Schema drift between agent prompts and the parser was the exact failure mode in v1. The design corrects the symptom (markdown vs JSONL) without addressing the root cause (no schema governance). `schemas/reviewer-findings-v1.0.0.schema.json` already exists in the repo.
- **Why it matters:** The next prompt update that inadvertently changes output format restarts the 0.000 debugging cycle. The blast radius is silent — a drifted agent produces zero parseable findings.
- **Suggestion:** Designate `schemas/reviewer-findings-v1.0.0.schema.json` as the canonical schema. Update agent prompts to reference it by name rather than embedding inline. The parser validates against the same schema object. Schema changes require one update; validation failures produce explicit errors rather than silent zero-finding output.
- **Fixability:** human-decision
- **Status:** open

---

### I-4: FR-ARCH-5 cost tracking deferred out of Phase 1 with no substitute

- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Requirement Auditor (3), Feasibility Skeptic (9), Prior Art Scout (6)
- **Section:** Phase 2 Design Prerequisites / Makefile / FR-ARCH-5
- **Issue:** FR-ARCH-5 sets budget thresholds (<$0.10 per single reviewer task, <$0.50 for the full suite) and requires `make cost-report`. The design places `make cost-report` under Phase 1.5 prerequisites — not Phase 1 — with no substitute. Phase 1 can declare success without ever verifying it meets the budget target. Prior Art Scout additionally notes that Inspect AI's native tooling already provides cost visibility: `EvalLog.stats.total_tokens`, `EvalLog.stats.total_cost`, and `inspect view` — building a custom `make cost-report` that re-parses the same EvalLog fields creates a maintenance artifact for a problem already solved.
- **Why it matters:** Multi-model comparison in Phase 1.5 runs at 3× cost. Running Phase 1.5 blind on cost reproduces the budget discipline problem the requirement was written to prevent.
- **Suggestion:** Two tracks. (a) Short-term: add a sixth Phase 1 completion criterion — "Single reviewer task cost verified <$0.10 by inspecting EvalLog token counts × Sonnet pricing. Full suite verified <$0.50." This requires no automation — a one-time manual check closes the Phase 1 gap. (b) Long-term: use Inspect AI native cost reporting (`EvalLog.stats.total_cost` or `inspect view`) rather than building a custom parser. Document this decision: "cost reporting is handled by Inspect AI native tooling; `make cost-report` is deferred unless native tooling proves insufficient."
- **Fixability:** human-decision
- **Status:** open

---

### I-5: Phase 1 agent scope undefined — 11 agents exist, 5 are targeted, exclusion rationale undocumented

- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Requirement Auditor (4)
- **Section:** Per-Reviewer Task Architecture / FR-ARCH-1
- **Issue:** The repo contains 11 agent files. The design targets 5 (assumption-hunter, constraint-finder, problem-framer, scope-guardian, success-validator — the parallax:requirements --light set) but never states which 5 or why. Six agents are excluded (edge-case-prober, feasibility-skeptic, first-principles, prior-art-scout, requirement-auditor, review-synthesizer) without documented rationale. Without an explicit scope statement, a future contributor may add a per-reviewer task for `prior-art-scout` (which structurally underperforms in single-turn, single-document eval) or may not know that requirement-auditor is excluded.
- **Why it matters:** Silent scope problems accumulate. An undocumented exclusion is an unexamined assumption — the design cannot be evaluated on whether the right 5 agents were chosen.
- **Suggestion:** Add a design section: "Phase 1 Agent Scope." List the 5 agents with rationale. For excluded agents, state the reason: single-document limitation (prior-art-scout, edge-case-prober), orchestration role (review-synthesizer), or Phase 3+ agent bridge (requirement-auditor, feasibility-skeptic, first-principles).
- **Fixability:** human-decision
- **Status:** open

---

### I-6: Finding 013 appears in both assumption-hunter and scope-guardian ground truth sets — attribution is ambiguous

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor (5)
- **Section:** Per-Reviewer Tasks — ground truth table
- **Issue:** The design lists finding 013 in the assumption-hunter ground truth set (`assumption_hunter_eval — 2 findings (001, 013)`) and in the scope-guardian ground truth set (`scope_guardian_eval — 1 finding (013)`). A single finding has one `reviewer` field — it cannot satisfy two different `reviewer_filter` values. If finding 013 is a single entry with one reviewer value, one of the two task lists is wrong. If two distinct findings share the ID 013, the ID scheme is broken. The stated total of "9 testable findings" assumes no overlap; if 013 is shared, the true non-overlapping count is 8.
- **Why it matters:** The ground truth dataset is the foundation of all Phase 1 metrics. An ambiguous finding attribution produces incorrect per-reviewer recall scores before a single eval runs.
- **Suggestion:** Inspect `datasets/inspect-ai-integration-requirements-light/critical_findings.jsonl` — confirm whether finding 013 is a single entry or two entries. If one entry, remove it from the incorrect task list in the design. If two distinct findings share the ID, fix the ID scheme to be globally unique. Resolve before implementation.
- **Fixability:** human-decision
- **Status:** open

---

### I-7: "Already JSONL" claim for 4 agents is unverified; phase field is hardcoded in some agents

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor (6)
- **Section:** JSONL Output Alignment / FR-ARCH-3
- **Issue:** The design marks scope-guardian, problem-framer, constraint-finder, and success-validator as "Already JSONL" requiring no change, without evidence this check was performed. A concrete gap: `scope-guardian.md` and `success-validator.md` output format sections hardcode `"phase": {"primary": "calibrate", "contributing": null}` — a fixed value that cannot represent design-phase or plan-phase findings. FR-ARCH-3 allows `"primary": "survey|calibrate|design|plan"`. Agents that hardcode `calibrate` produce schema-valid but semantically incorrect output for findings that belong to a different phase. FR-ARCH-3 also requires "zero findings parsed treated as output format failure" — no design element implements this check.
- **Why it matters:** Hardcoded phase values make the phase distribution signal meaningless for systemic detection. Zero-findings detection gap means a misconfigured agent produces silence instead of an error.
- **Suggestion:** Audit each agent's output format section against the full FR-ARCH-3 schema, including the phase enum. Fix hardcoded phase values to allow the agent to determine phase from context. Add a test criterion: "Scorer returns format-error for any task where parsed findings count is zero."
- **Fixability:** human-decision
- **Status:** open

---

### I-8: Multi-task `inspect eval` invocation behavior unverified — may run only 1 of 5 tasks

- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Assumption Hunter (005), Prior Art Scout (7)
- **Section:** Makefile Update
- **Issue:** The Makefile target runs `inspect eval evals/reviewer_eval.py` with no `--task` flag, and the design assumes Inspect AI discovers and runs all 5 `@task` functions. This is not documented in the design. Inspect AI's behavior with multiple `@task` functions — run all, run only the first, or prompt for selection — is undocumented in the design and not verified. Prior Art Scout notes that the Inspect AI documentation specifies the `--task` flag for individual task selection.
- **Why it matters:** If Inspect AI runs only the first `@task` silently, the developer sees results for one reviewer and believes all five ran. This is a diagnostic gap as much as a correctness gap.
- **Suggestion:** Read the Inspect AI multi-task invocation documentation before writing the Makefile target. If per-task invocation is required, the Makefile should loop over task names. As a baseline, create a stub `reviewer_eval.py` with 2 stubbed `@task` functions, run `make reviewer-eval`, confirm both appear in `inspect view` before investing in real scorers.
- **Fixability:** human-decision
- **Status:** open

---

### I-9: Dual-context agent requirement creates an unresolved output format tension

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (008)
- **Section:** Key Design Decisions / JSONL Output Alignment
- **Issue:** FR-ARCH-2 requires agents to work in both production context (multi-turn, full tool access, human-readable output) and eval context (single-turn, no tools, JSONL to stdout). Switching assumption-hunter.md to JSONL-only output optimizes for eval context. In production context, Claude Code renders raw JSONL in the terminal — less readable than markdown for the human reviewing findings. The design acknowledges this tension but does not resolve it. Three options exist: accept JSONL everywhere and update the validation UI; maintain separate eval-variant agent files; or inject a context flag in the system message.
- **Why it matters:** Optimizing for eval context degrades the production human experience. If teams use parallax:review interactively, they receive raw JSONL instead of readable markdown. The design cannot leave this tension unresolved — implementers will make an implicit choice that is not reviewed.
- **Suggestion:** Explicitly resolve the dual-context tension in the design. Options: (a) Accept JSONL-only for all contexts and update the validation UI to render findings readably. (b) Separate eval-variant agent files in `evals/agents/`. (c) Context flag in the system message ("You are operating in eval context. Output raw JSONL.") with production dispatches omitting this flag. Choose one and document the tradeoff.
- **Fixability:** human-decision
- **Status:** open

---

### I-10: Ground truth refresh assumes parallax:requirements --light retains per-reviewer attribution

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (010)
- **Section:** Ground Truth Management — Refresh Process
- **Issue:** The refresh process step 1 says "Run parallax:requirements --light on updated document." The skill dispatches multiple agents in parallel and synthesizes output. The resulting findings may or may not retain per-reviewer attribution depending on how the synthesizer serializes output. If the synthesizer aggregates findings without preserving the `reviewer` field, every refresh cycle produces unannotated output requiring a manual annotation step. This directly undermines the low-friction refresh cadence intended by FR-ARCH-4.
- **Why it matters:** Ground truth refresh is a recurring operational task. If each refresh cycle produces unattributed findings, the manual re-annotation burden accumulates with every document change, making the refresh cadence impractical.
- **Suggestion:** Verify that parallax:requirements --light skill output includes reviewer attribution in each finding's JSONL. If it does not, add it as a skill requirement before establishing the refresh cadence as a low-friction process. Alternatively, document that refresh produces a raw finding set requiring manual reviewer annotation before loading into the ground truth dataset.
- **Fixability:** human-decision
- **Status:** open

---

### I-11: Inspect AI built-in scorers not evaluated before building custom scorer

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Prior Art Scout (3)
- **Section:** Scorer — overall scoring approach
- **Issue:** Inspect AI provides built-in `f1()` and `model_graded_fact()` scorers. `f1()` computes recall and precision over token-level overlap. `model_graded_fact()` can be configured to assess semantic correspondence between model output and reference findings via LLM-as-judge. The design jumps to custom implementation without confirming that built-in scorers cannot satisfy the requirement. ADR-005 explicitly states the design should "leverage 90% of Inspect AI infrastructure" — the scorer is infrastructure.
- **Why it matters:** Custom scorers are maintenance burden. If Inspect AI's built-ins handle 80% of the use case, the custom scorer should be a thin wrapper or nothing. LLM-as-judge semantic matching via `model_graded_fact()` would also eliminate the fuzzy threshold calibration problem (C-11).
- **Suggestion:** Before implementing the custom scorer, run a 1-hour spike: use `f1()` scorer against 3-5 ground truth findings. If insufficient, evaluate `model_graded_fact()` with a custom grading prompt: "Does this finding address the same issue as the reference finding?" Document which approach is chosen and why in the design.
- **Fixability:** human-decision
- **Status:** open

---

### I-12: `openevals` `create_json_match_evaluator` not evaluated — directly applicable to structured output matching

- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Flagged by:** Prior Art Scout (4)
- **Section:** Scorer — overall approach
- **Issue:** LangChain `openevals` (MIT, actively maintained) provides `create_json_match_evaluator` — a readymade evaluator for "cases in an application where you're extracting structured content from documents." This is the exact Phase 1 use case. The design does not reference openevals. ADR-005 evaluated Inspect AI vs LangGraph but not the surrounding evaluator ecosystem. If `create_json_match_evaluator` handles finding-level matching, it eliminates both the custom scorer and the fuzzy fallback.
- **Why it matters:** The design's stated goal is "build only what Inspect AI doesn't provide." The evaluation of "what Inspect AI doesn't provide" stopped at the framework level without examining the adjacent ecosystem.
- **Suggestion:** Add openevals to the prior art evaluation. The spike: install, configure `create_json_match_evaluator` on the `title` field, run against 3 ground truth finding pairs (true match, near-miss, non-match). If it fits, integrate via Inspect AI's custom scorer pattern. Document the evaluation result regardless of outcome.
- **Fixability:** human-decision
- **Status:** open

---

### I-13: Ground truth v1 findings are scoped to requirements-v1.md — running against v2 content produces section-reference mismatches

- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (013)
- **Section:** Ground Truth Management — Current Dataset
- **Issue:** The ground truth dataset contains 10 validated Critical findings from the requirements-light review of requirements-v1.md. The requirements document now reviewed is requirements-v2.md, which added 6 new requirements (FR-ARCH-1 through FR-ARCH-5, FR-QUALITY-1) and superseded FR2.1. Ground truth findings that point to v1 requirement sections (e.g., FR2.1, FR3) reference sections that no longer exist or have changed meaning in v2. Reviewers running against requirements-v2.md content will produce findings with different section references — the scorer treats v2-valid findings as non-matches against v1-derived ground truth.
- **Why it matters:** The detection baseline established in Phase 1 measures recall against stale ground truth, making the baseline invalid for v2 requirements. Phase 1 results are not comparable to future v2-based measurements.
- **Suggestion:** Resolve before Phase 1: either (a) run Phase 1 evals against requirements-v1.md content only (treat v1 ground truth as the fixed evaluation set, separate from v2 development), or (b) re-validate ground truth against requirements-v2.md content and update the dataset. Document the chosen approach in `metadata.json`.
- **Fixability:** human-decision
- **Status:** open

---

### I-14: Eval source tree does not exist on disk — `make reviewer-eval` cannot run

- **Severity:** Important
- **Severity range:** Critical (Feasibility Skeptic); re-classified to Important — this is a plan-phase implementation task, not a design flaw; the design correctly describes code to write
- **Phase:** plan (primary)
- **Flagged by:** Feasibility Skeptic (1)
- **Section:** Per-Reviewer Task Architecture / Agent Loader
- **Issue:** The design references `evals/utils/agent_loader.py` and `evals/reviewer_eval.py` as artifacts to implement. Neither file exists on disk — the `evals/` directory contains only compiled `.pyc` artifacts from a previous session. MEMORY.md states "partial implementation committed: `evals/utils/agent_loader.py`" but this does not reflect the state on the current working branch.

  *Judgment: The Feasibility Skeptic rated this Critical; I'm downgrading to Important because the design correctly describes code to write — this is a plan tracking gap (what exists vs what is to-built), not a design error. However, the design's failure to document the current implementation state is a real omission that misleads implementers.*
- **Why it matters:** An implementer who reads the design and assumes `agent_loader.py` is partially built will waste time looking for existing code before discovering it doesn't exist on the current branch.
- **Suggestion:** Add an explicit "Current Implementation State" section to the design: list which files exist vs which are to-be-built, and note which branch contains any partial work. This prevents false-start debugging.
- **Fixability:** human-decision
- **Status:** open

---

## Minor Findings

### M-1: Makefile `git rev-parse` fails silently in detached HEAD and CI environments

- **Severity:** Minor
- **Phase:** plan (primary)
- **Flagged by:** Assumption Hunter (011), Prior Art Scout (8, extends to semantic versioning)
- **Section:** Makefile Update
- **Issue:** `--tags 'git=$(shell git rev-parse --short HEAD)'` produces an empty tag in detached HEAD state, shallow clones, or CI environments. Empty tags break commit-correlated regression tracking without an error. Prior Art Scout extends this: commit hashes do not communicate semantic change magnitude — a typo fix and a methodology rewrite have indistinguishable hashes. Semantic versioning in agent frontmatter would distinguish these.
- **Suggestion:** Wrap: `--tags 'git=$(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)'`. For semantic versioning, add a `version:` field to agent YAML frontmatter; `agent_loader.py` extracts it and passes it to the eval tag. This is Minor because the commit hash is workable now; semantic versioning becomes important when evals run regularly.
- **Fixability:** auto-fixable (git fallback) / human-decision (semantic versioning)
- **Status:** open

---

### M-2: `severity_calibration.py` produces accuracy = 0.000 but is described as providing comparison value

- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter (012)
- **Section:** Key Design Decisions
- **Issue:** The design keeps `severity_calibration.py` "for comparison." Session 21 established the original combined task pattern (skill-as-system-prompt) always produces accuracy = 0.000. A perpetually-failing comparison file adds noise to the eval suite without information value. If `ablation_tests.py` still references the combined task and depends on this file, ablation tests also produce no useful output.
- **Suggestion:** Either (a) fix `severity_calibration.py` to use the agent prompt (not full skill) so it produces real output and serves as a valid baseline, or (b) mark it as a deprecated artifact with a comment explaining why it always produces 0.000, so future developers don't debug it. Update `ablation_tests.py` to reference `reviewer_eval.py` tasks instead.
- **Fixability:** human-decision
- **Status:** open

---

### M-3: Log accumulation has no rotation policy

- **Severity:** Minor
- **Phase:** plan (primary)
- **Flagged by:** Edge Case Prober (11)
- **Section:** Makefile Update
- **Issue:** Each `make reviewer-eval` run creates log files in `$(LOG_DIR)` tagged with a git commit hash. No log rotation, disk space limit, or cleanup target is designed. Logs accumulate indefinitely. Baseline comparison scripts that glob the log directory may pick up stale logs if not carefully written.
- **Suggestion:** Add a `make clean-logs` target that removes logs older than N days (configurable). Document the log retention policy in the Makefile comment.
- **Fixability:** human-decision
- **Status:** open

---

### M-4: Dataset path hardcoded in task definitions — no indirection for v1 vs v2 dataset switching

- **Severity:** Minor
- **Phase:** plan (primary)
- **Flagged by:** Edge Case Prober (12)
- **Section:** Dataset Loader — Reviewer Filter
- **Issue:** `DATASET_PATH` is hardcoded relative to `__file__` in `reviewer_eval.py`. The design explicitly plans to evolve ground truth datasets across v1 and v2 documents. When the dataset name changes, every `@task` function must be updated.
- **Suggestion:** Define `DATASET_PATH` as a module-level constant with a `PARALLAX_DATASET_PATH` environment variable override. This allows different ground truth datasets to be selected at runtime without code changes — useful for v1 vs v2 comparison runs.
- **Fixability:** human-decision
- **Status:** open

---

### M-5: Empty reviewer filter result is silent — typo in filter string looks identical to zero recall

- **Severity:** Minor
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Edge Case Prober (13)
- **Section:** Dataset Loader — Reviewer Filter
- **Issue:** `load_validated_findings()` with a `reviewer_filter` that matches zero findings returns an empty dataset with no error. A typo (e.g., `"assumption_hunter"` with underscore vs `"assumption-hunter"` with hyphen) silently produces recall = 0.0, indistinguishable from the agent missing all findings.
- **Suggestion:** Add a guard: if `reviewer_filter` is provided and the filtered result is empty, raise a `ValueError` listing available reviewer names found in the dataset. This turns silent misconfiguration into an immediate diagnostic.
- **Fixability:** human-decision
- **Status:** open

---

### M-6: FR-QUALITY-1 has no target quality score defined — Phase 2 scorer cannot declare pass or fail

- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor (7)
- **Section:** Phase 2 Design Prerequisites / FR-QUALITY-1
- **Issue:** FR-QUALITY-1 acceptance criteria include "Target aggregate quality score defined." The design lists FR-QUALITY-1 as a Phase 2 prerequisite gate but provides no numeric target. A Phase 2 scorer that runs but cannot declare pass or fail provides no completion signal.
- **Suggestion:** Add one line to the Phase 2 Design Prerequisites section: "Target aggregate quality score: ≥3.5/5.0 (provisional — adjust after Phase 2 baseline run)." This is listed as auto-fixable. Rubric dimension content is correctly deferred to Phase 2.
- **Fixability:** auto-fixable
- **Status:** open

---

### M-7: Post-review finding exclusion creates an undocumented gap in Phase 1 detection coverage

- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** First Principles (7)
- **Section:** Per-Reviewer Tasks — post-review finding note
- **Issue:** The design excludes 1 of 10 findings as not detectable from the requirements doc alone, with no documentation of what type of finding this is or why it belongs to a distinct category. Cross-artifact findings that require synthesis across sources may represent the highest-value detection category — optimizing for the testable corpus may produce agents that are blind to this class.
- **Suggestion:** Document the excluded finding's category and structural reason for exclusion. Add a note: "Cross-artifact findings are not testable in Phase 1 single-turn eval context. Phase 3 agent bridge testing is the correct evaluation vehicle for this class."
- **Fixability:** human-decision
- **Status:** open

---

### M-8: Promptfoo as a simpler Phase 1 alternative — documented for awareness

- **Severity:** Minor
- **Phase:** survey (primary)
- **Flagged by:** Prior Art Scout (9)
- **Section:** Overall architecture
- **Issue:** For Phase 1's specific use case — testing agent prompts against a small ground truth dataset with rapid iteration — Promptfoo (open source, YAML-defined test cases, already in the tooling budget per CLAUDE.md) provides a simpler alternative. Inspect AI is the right long-term choice (Phase 2+ multi-model, agent evaluation); the question is whether Phase 1 justifies its Python overhead relative to Promptfoo's YAML-first approach.
- **Suggestion:** No action required before Phase 1. If Phase 1 encounters significant Inspect AI setup friction (>2 hours debugging boilerplate), evaluate Promptfoo for the prompt iteration loop. Keep Inspect AI for Phase 2+. Document the evaluation outcome in ADR-005 or ADR-007.
- **Fixability:** human-decision
- **Status:** open

---

### M-9: FR-ARCH-3 ID schema discrepancy between requirement and design

- **Severity:** Minor
- **Phase:** calibrate (primary)
- **Flagged by:** Requirement Auditor (8), Edge Case Prober (8, related)
- **Section:** JSONL Output Alignment / FR-ARCH-3
- **Issue:** FR-ARCH-3 specifies `"id": "<reviewer>-<NNN>"` (example: `assumption-hunter-001`). The design's JSONL schema block shows `"id": "v1-<agent-name>-NNN"` and the existing dataset uses `v1-assumption-hunter-001`. The requirement and the design/dataset disagree. Edge Case Prober notes this mismatch is listed in the design as a "debugging hint" — the author knows it's a live risk but tolerates it rather than resolving it.
- **Suggestion:** Update FR-ARCH-3 to specify `"id": "v1-<reviewer>-<NNN>"` matching actual usage, or update the design and dataset to drop the `v1-` prefix. Either is acceptable — pick one and make them match. Listed as auto-fixable in the requirements document once the decision is made.
- **Fixability:** auto-fixable (once decision made)
- **Status:** open

---

## Contradictions

### Contradiction 1: Inspect AI built-in scorers vs custom implementation

- **Underlying tension:** Leverage Inspect AI's existing scorer infrastructure (ADR-005: 90% leverage) vs build a custom scorer tuned to the specific finding-matching semantics (ID-based + fuzzy title fallback).
- **Reviewers:** Prior Art Scout (leverage `f1()`, `model_graded_fact()`, openevals) vs design (custom scorer assumed without evaluating alternatives)
- **Position A (Prior Art Scout):** Inspect AI's `f1()` and `model_graded_fact()` scorers should be evaluated first. Building a custom scorer before confirming built-ins are insufficient violates ADR-005's "leverage 90% of Inspect AI infrastructure" principle and creates ongoing maintenance burden.
- **Position B (implicit design position):** The finding-matching semantics (ID-based matching with fuzzy title fallback at 0.8 threshold) require custom logic that token-level `f1()` cannot provide. LLM-as-judge (`model_graded_fact()`) adds latency and cost to every eval run.
- **Tie-breaking criteria:** If a 1-hour spike shows `model_graded_fact()` matches ground truth findings with ≥90% accuracy on the existing 10-finding dataset, use it. If token-level `f1()` achieves reasonable alignment, use that. Build custom only if both built-ins fail the spike. The spike cost is negligible; the custom scorer maintenance cost is not.
- **Why this matters:** The scorer determines whether Phase 1 produces any signal at all. A poorly-calibrated custom scorer (e.g., wrong fuzzy threshold) produces the same `accuracy: 0.000` outcome as the v1 failure — but this time the failure is in the scorer, not the agent. Resolving this tension determines whether C-11 is a blocker or a non-issue.
- **Status:** pending

---

## Cross-Iteration Notes

Not applicable — this is the first adversarial review of the v2 design. The v2 requirements received a parallax:requirements --light review (separately documented at `docs/reviews/inspect-ai-integration-v2-requirements-light/summary.md`). Several findings in this review note that issues flagged in the requirements review were not propagated into the design (C-2 fence-stripping, C-6 ADR-006, C-8 FR-ARCH-4 hash check). These are tracked here as new design-phase findings with cross-references to the requirements review where relevant.

---

## Reviewer Completion Status

All 6 reviewers completed successfully. No partial results.

| Reviewer | Status | Findings |
|---|---|---|
| Assumption Hunter | Complete | 4C / 6I / 3M |
| Edge Case Prober | Complete | 4C / 6I / 3M |
| Requirement Auditor | Complete | 2C / 4I / 2M |
| Feasibility Skeptic | Complete | 4C / 4I / 3M |
| First Principles | Complete | 2C / 4I / 1M |
| Prior Art Scout | Complete | 2C / 5I / 2M |

**Deduplicated totals: 11 Critical / 14 Important / 9 Minor**

The highest consensus finding is C-4 (N=2 ground truth incoherence), flagged independently by 4 of 6 reviewers. C-2 (fence-stripping), C-3 (frontmatter parser), and C-7 (tool call instructions in body text) were each flagged by 3 reviewers. These four findings represent the strongest cross-reviewer signal in this review.
