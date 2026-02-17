# Edge Case Prober Review
## Design: Inspect AI Integration v2

**Review Date:** 2026-02-17
**Design Document:** `docs/plans/2026-02-17-inspect-ai-integration-design-v2.md`
**Requirements Document:** `docs/requirements/inspect-ai-integration-requirements-v2.md`
**Reviewer:** Edge Case Prober

---

## Findings

### Finding 1: JSONL Fence Stripping is Absent — Zero Findings Silently Misreads as Pass

- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** JSONL Output Alignment
- **Issue:** The design mandates JSONL output from agents and relies on `output_parser.py` to parse it, but no fence-stripping step exists in the design. Claude (and all frontier LLMs) routinely wrap structured output in markdown code fences even when instructed not to, producing output like ` ```json\n{...}\n``` `. A strict line-by-line JSONL parser returns zero findings for this valid-but-fenced response. The scorer then records recall = 0.0, which is indistinguishable from the agent genuinely finding nothing. FR-ARCH-3 flags "zero findings parsed treated as output format failure" but there is no acceptance criterion in the design that verifies the parser handles fences, and no runtime signal distinguishes format failure from true zero.
- **Why it matters:** The v1 failure mode was `accuracy: 0.000` due to a structural mismatch. The parser silently returning zero is a direct path back to v1's 0.000 result. If this lands in Phase 1 testing, the eval looks broken when the agent is actually functional — triggering debug cycles against a working component.
- **Suggestion:** Add fence-stripping as an explicit step in `output_parser.py` before JSONL line parsing. Strip ` ```json `, ` ``` `, and leading/trailing whitespace. Add a test case that provides fenced-but-valid JSONL and asserts the parser produces the correct finding count. Also add a distinct log signal when zero findings are parsed (e.g., `"parse_result": "empty"` in EvalLog metadata) so the operator can distinguish format failure from genuine zero.

---

### Finding 2: `assumption-hunter.md` Frontmatter Declares Markdown Output — Design Doesn't Audit Before Running

- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** JSONL Output Alignment / Per-Reviewer Task Architecture
- **Issue:** The design acknowledges that `assumption-hunter.md` outputs markdown, not JSONL, and states the fix is to update the output format section. However, the design document provides no audit gate — there is no Phase 1 prerequisite step to verify the fix was applied before `reviewer_eval.py` is run. The live `assumption-hunter.md` file (at `/Users/nic/src/design-parallax/parallax/agents/assumption-hunter.md`) still specifies markdown output format in its Output format section as of this review. If `reviewer_eval.py` is implemented and run before this file is corrected, the assumption-hunter task silently produces prose and scores zero recall against its 2-finding ground truth — exactly v1's failure pattern. Beyond assumption-hunter: the design states FR-ARCH-2 requires all agents to function in eval context, but no audit is specified for the other 4 agents either.
- **Why it matters:** The fix is documented in the design but not enforced. Implementation order is: write `reviewer_eval.py` → run `make reviewer-eval` → discover markdown output → debug. The design knows about this failure mode and doesn't prevent it.
- **Suggestion:** Add a Phase 1 prerequisite checklist to the design, before `reviewer_eval.py` implementation: (1) Audit all 5 agent files against FR-ARCH-2 criteria — JSONL output format confirmed, no tool calls required, self-contained. (2) Run each agent manually against a sample document and verify output is parseable JSONL. Gate `make reviewer-eval` behind `make test-agents` (a fast smoke test that instantiates each agent and checks for JSONL). This matches how you'd gate a deploy behind a smoke test.

---

### Finding 3: `content.index("---", 3)` Raises ValueError on Single-Delimiter Files — Crashes Agent Loader

- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** Agent Loader (`evals/utils/agent_loader.py`)
- **Issue:** The `load_agent_content` function uses `content.index("---", 3)` to find the closing frontmatter delimiter. `str.index()` raises `ValueError` if the substring is not found. If any agent file has malformed frontmatter (opening `---` but no closing `---`), or has `---` only at the start of a heading like `---\ntitle: foo\n` without a paired close, the loader crashes with an unhandled exception. Every `@task` that calls `load_agent_content()` fails at instantiation — `make reviewer-eval` crashes before a single sample runs. The error is not task-specific; it takes down the entire eval suite.
- **Why it matters:** Blast radius is 5/5 tasks. A single malformed agent file kills the entire `make reviewer-eval` run with a Python traceback, not a meaningful diagnostic message. The current agents appear well-formed, but this is a latent bomb for any future agent addition or hand-edit of frontmatter.
- **Suggestion:** Replace `content.index("---", 3)` with a `try/except ValueError` or use `content.find("---", 3)` and check for `-1`. If the closing delimiter is missing, raise a descriptive `ValueError` with the agent name: `raise ValueError(f"Malformed frontmatter in {agent_name}.md: no closing '---' delimiter")`. Add a test case for malformed frontmatter. As a guard, the design should also specify that `load_agent_content()` must raise a named exception (not propagate a bare `ValueError`) so callers can produce useful error messages.

---

### Finding 4: Per-Reviewer Ground Truth at N=1 or N=2 — Single Missed Finding Is a 50–100-Point Recall Swing

- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Per-Reviewer Tasks / Ground Truth Management
- **Issue:** The ground truth table shows `scope_guardian_eval` has 1 validated finding. At N=1, recall is binary: 1.0 or 0.0. There is no intermediate state. For `assumption_hunter_eval` and others at N=2, missing a single finding drops recall by 50 percentage points. The design sets Phase 1 success criteria that include "≥1 reviewer task achieves recall ≥ 0.90" — but with N=1 or N=2, this threshold is either trivially met (agent regenerates the one finding) or permanently unreachable (agent paraphrases it differently). The requirements document (FR-ARCH-1) does not specify a minimum per-reviewer ground truth count, and no statistical confidence bound is defined anywhere. A score of "recall = 1.0" with N=1 is not evidence the agent is working; it's noise.
- **Why it matters:** The eval framework is designed to measure agent quality. At N=1, it measures luck. Decisions about whether to ship prompt changes or agents will be based on statistically meaningless signals. The v2 requirements-light review (from `docs/reviews/inspect-ai-integration-v2-requirements-light/summary.md`) flagged this: "N=2 creates 50pp recall swings from single missed finding."
- **Suggestion:** Set a minimum per-reviewer ground truth count in the design (recommend N≥5 per reviewer for any metric to be informative). If current ground truth cannot meet this, document Phase 1 explicitly as a "format compliance check only" (can the agent produce parseable JSONL?) and defer quantitative recall targets to Phase 2 when ground truth is expanded. Adding a disclaimer to eval output when N<5 per reviewer would prevent misinterpretation of results.

---

### Finding 5: Document Hash Comparison Is Unspecified — Staleness Check Is Inoperable

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Ground Truth Management / FR-ARCH-4
- **Issue:** FR-ARCH-4 requires `metadata.json` to include `design_doc_hash` and for `make validate` to re-run if the hash differs. The design does not specify: (1) which hash algorithm is used (MD5, SHA-256?), (2) whether the hash covers raw bytes or normalized text (CRLF/LF difference between macOS dev and CI causes a different hash for an identical document), (3) what `make validate` actually does when a mismatch is detected — does it block the eval, emit a warning, or just log it? Without these specifications, the hash check either always triggers (CRLF normalization), never triggers (wrong algorithm), or triggers but takes no meaningful action.
- **Why it matters:** The design explicitly learned from Session 19 that "ground truth is living" and stale findings cause false positives that mislead the eval framework. The staleness check is the only mechanism protecting against this. An inoperable check means stale ground truth can accumulate silently, producing accuracy: 0.000 results that look like agent regressions but are actually stale baselines.
- **Suggestion:** Specify the hash algorithm (SHA-256 recommended, consistent with Python `hashlib` defaults), hash the document after UTF-8 decode + LF normalization (strip `\r`), and define the behavior on mismatch: emit a warning with instructions (do not silently block). Add the hash computation to a utility function so it can be unit-tested. Document: "hash mismatch means the reviewed document has changed since ground truth was captured — re-run `parallax:requirements --light` and re-validate before running evals."

---

### Finding 6: Frontmatter Stripping Uses String Index Arithmetic — Fails on Agents With Inline `---` Separators

- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Agent Loader (`evals/utils/agent_loader.py`)
- **Issue:** The frontmatter stripping logic searches for the second `---` delimiter at offset 3 (past the opening `---`). This fails for agent files that contain a `---` horizontal rule in the body content between the frontmatter and the end of the file. The scope-guardian agent already contains `---` as a section separator in its output format example (it uses them to separate JSONL blocks conceptually). If body content contains `---` before the intended frontmatter close, `content.index("---", 3)` matches the first body `---`, truncating the system prompt mid-content.
- **Why it matters:** A truncated system prompt silently strips the agent's analytical focus areas, voice rules, and review process. The agent receives partial instructions and produces degraded output. The scorer records lower recall. The defect is attributed to the agent's quality, not the loader.
- **Suggestion:** Use a regex-based frontmatter parser (PyYAML's `safe_load` on the frontmatter block, or the `python-frontmatter` library) that properly handles the YAML block boundary. Alternatively, require that frontmatter close delimiter appears on a line by itself, and parse line-by-line until finding a line that is exactly `---` after the opening block. The current substring search is brittle.

---

### Finding 7: `make reviewer-eval` Runs All 5 Tasks Sequentially — No Parallelism, No Per-Task Failure Isolation

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Makefile Update
- **Issue:** The Makefile target runs `inspect eval evals/reviewer_eval.py` as a single command. Inspect AI runs all `@task` functions in the file sequentially by default. If one task crashes at runtime (e.g., an API 429, a malformed agent response that breaks the scorer), the remaining tasks do not run. There is no per-task failure isolation in the design — a crash in `assumption_hunter_eval` blocks `constraint_finder_eval` from producing any data. Additionally, the design does not address what happens when the Anthropic API returns a 429 (rate limit) mid-eval run: does Inspect AI retry, abort, or produce partial results?
- **Why it matters:** An eval suite that produces partial results silently is worse than one that fails fast. Partial results can be mistaken for complete results. With N=2 per reviewer, a single aborted sample produces recall = 0.0 for that reviewer — identical to total failure.
- **Suggestion:** Specify the expected behavior when a task fails mid-run (Inspect AI's behavior on API errors should be validated, not assumed). Add per-task invocation as an option: `inspect eval evals/reviewer_eval.py::assumption_hunter_eval` so developers can run and debug one reviewer at a time. Document the retry behavior for rate-limit errors. If Inspect AI does not handle retries, add a `--max-retries` flag or exponential backoff wrapper.

---

### Finding 8: Finding ID Format Mismatch Between Design and Agent Prompts

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** JSONL Output Alignment / Per-Reviewer Tasks
- **Issue:** The JSONL schema in the design specifies `"id": "<reviewer>-<NNN>"` (no version prefix). The agent prompts (scope-guardian, constraint-finder, success-validator, problem-framer) all specify `"id": "v1-<agent-name>-NNN"`. The existing ground truth dataset uses `v1-` prefixed IDs (e.g., `v1-assumption-hunter-001`). If the scorer performs ID-based matching, and an agent outputs `assumption-hunter-001` (no `v1-` prefix) while the ground truth expects `v1-assumption-hunter-001`, every finding is a miss. Recall = 0.0 from a format mismatch, not agent quality. The design acknowledges ID format as a debugging step ("Check if IDs differ by version prefix") but does not resolve the inconsistency.
- **Why it matters:** The design explicitly lists this as a debugging hint, which means the author knows it's a live risk. This is a pre-known failure mode the design tolerates rather than eliminates. If Phase 1 scoring uses ID matching, the entire suite returns zero. If Phase 1 scoring uses fuzzy title matching, the ID schema in the design is misleading documentation that will cause incorrect agent prompts in future.
- **Suggestion:** Decide and enforce a canonical ID format in one place. Either: (a) Update the design's JSONL schema to match `v1-<agent-name>-NNN` (matching existing agent prompts and ground truth), or (b) Update all agent prompts and ground truth to drop the `v1-` prefix. Document the decision in the design. Add a validation test that creates a sample finding with the correct ID format and asserts the scorer matches it against ground truth.

---

### Finding 9: Phase 1 Success Criteria "Non-Zero Detection" Is Not a Gate

- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Phase 1 Test Plan
- **Issue:** Phase 1 completion criterion #2 is "Non-zero detection: At least 1 reviewer task achieves recall > 0.0." This is satisfied by detecting 1 finding out of 10. At N=1 for scope-guardian, an agent that parrots back the sample input would satisfy this criterion. "Non-zero" as a completion gate means Phase 1 can declare success at near-zero quality. The requirements (v2-requirements-light review, finding #10) flagged this: "Non-zero accuracy is not a threshold." The design does not define a numeric floor.
- **Why it matters:** Phase 1.5 (multi-model comparison) and Phase 2 (LLM-as-judge) are gated on "Phase 1 non-zero accuracy." If the gate is satisfied by a single fluky detection, the framework advances to more complex and expensive phases without establishing that the basic per-reviewer task architecture actually works.
- **Suggestion:** Replace "recall > 0.0" with a concrete floor: recommend ≥50% recall on the reviewer with the most ground truth findings (currently assumption-hunter or constraint-finder at N=2), OR confirm that Phase 1 is explicitly a "smoke test" (does the pipeline not crash, does output parse) and reserve accuracy thresholds for Phase 2. Either decision is fine; the design must pick one.

---

### Finding 10: Agent Prompts Declare `tools: ["Read", "Grep", "Glob", "Write"]` — Eval Context Has No Tools

- **Severity:** Important
- **Phase:** design (primary)
- **Section:** FR-ARCH-2 / Per-Reviewer Task Architecture
- **Issue:** All agent files declare `tools: ["Read", "Grep", "Glob", "Write"]` in their YAML frontmatter. When these agents run in Claude Code production context, they can read files. In Inspect AI eval context (single-turn, no tool calls), the tools are absent. FR-ARCH-2 states "Agents do not require tool calls to produce findings" — but the assumption-hunter agent's review process explicitly says "Read the design document thoroughly" and "Read the requirements document to understand stated constraints." The agent is instructed to read files. In eval context, it receives document content in the prompt. This instruction-behavior mismatch may cause the agent to attempt tool calls (that fail silently or error), produce an empty response, or perform adequately anyway. The design does not test which of these actually happens.
- **Why it matters:** If the agent attempts a Read tool call that isn't available, Inspect AI's behavior is unspecified in the design — it may produce an error message instead of findings, or silently produce no output. Either path returns recall = 0.0. FR-ARCH-2's acceptance criterion "Agents do not require tool calls to produce findings" is assumed true without validation.
- **Suggestion:** Add a specific instruction to each agent's system prompt for eval context: "The document content is provided directly in this message. Do not attempt to read files — all necessary content is already present." Alternatively, create eval-specific agent variants that strip tool references and add explicit content-in-prompt instructions. Validate with a test run before Phase 1 completion.

---

### Finding 11: `make reviewer-eval` Tagged With Git Hash — Logs Accumulate Without a Rotation Policy

- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Makefile Update
- **Issue:** Each `make reviewer-eval` run creates log files in `$(LOG_DIR)` tagged with a git commit hash. The design has no log rotation, disk space limit, or cleanup target. At ~100KB per run and daily usage during active development, logs accumulate to gigabytes over months. The `make view` target (from the existing Makefile) shows the most recent log — older logs stay on disk indefinitely.
- **Why it matters:** Disk impact is low in absolute terms but log directory clutter makes `ls logs/` unusable for humans, and baseline comparison scripts that glob the log directory may pick up stale logs if not carefully written.
- **Suggestion:** Add a `make clean-logs` target that removes logs older than N days (configurable). Document the log retention policy in the Makefile comment. This is a minor operational hygiene issue, not a correctness problem.

---

### Finding 12: Ground Truth Dataset Path Is Hardcoded Relative to `__file__` — Breaks When Dataset Is Renamed

- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Dataset Loader — Reviewer Filter
- **Issue:** The design references `DATASET_PATH` as a hardcoded path in `reviewer_eval.py`, constructed relative to `__file__`. The dataset directory is named `inspect-ai-integration-requirements-light` — a specific, unwieldy name. The design's ground truth management section references moving to v2 ground truth (for requirements-v2 and design-v2), which implies a differently named dataset. When that happens, every `@task` function that references the old `DATASET_PATH` must be updated. There is no indirection layer (e.g., a `metadata.json` pointer or environment variable) that separates "which dataset to use" from "where tasks are defined."
- **Why it matters:** This is a maintenance friction point, not a correctness failure. But given that the design explicitly plans to evolve ground truth datasets across v1 and v2 documents, hardcoding the dataset path in task definitions creates an update burden proportional to the number of tasks.
- **Suggestion:** Define `DATASET_PATH` as a module-level constant in `reviewer_eval.py` with a comment pointing to `metadata.json` as the authoritative source. Consider accepting `PARALLAX_DATASET_PATH` as an environment variable override so different ground truth datasets can be selected at runtime without code changes (useful for v1 vs v2 comparison runs).

---

### Finding 13: No Failure Mode for Empty Reviewer Filter Result

- **Severity:** Minor
- **Phase:** design (primary), plan (contributing)
- **Section:** Dataset Loader — Reviewer Filter
- **Issue:** `load_validated_findings()` with `reviewer_filter="assumption-hunter"` returns an empty dataset if no findings match. The design does not specify what happens when the filtered dataset is empty: does `Task` instantiate with zero samples (runs but scores nothing), does it raise, or does Inspect AI silently skip it? The post-review finding exclusion via reviewer_filter is correct design — but a typo in `reviewer_filter` (e.g., `"assumption_hunter"` with underscore vs `"assumption-hunter"` with hyphen) returns an empty dataset and produces recall = 0.0 with no error.
- **Why it matters:** A typo in the reviewer filter string is silent. The task runs, produces no matches, and the score is indistinguishable from the agent missing all findings. This is a debugging dead end.
- **Suggestion:** Add a guard in `load_validated_findings()`: if `reviewer_filter` is provided and the filtered result is empty, raise a `ValueError` listing the available reviewer names found in the dataset. This turns a silent misconfiguration into an immediate diagnostic. Add a test asserting that an invalid `reviewer_filter` raises.

---

## Blind Spot Check

My focus is on what breaks — boundary conditions, silent failures, wrong-input paths. Three systemic issues this lens underweights:

**Correctness of the eval design itself.** I've found structural failures (fence stripping, ID mismatch, N=1 ground truth) but haven't evaluated whether the scorer logic correctly implements recall and precision semantics. A Requirement Auditor review would probe whether the scorer matches the FR-ARCH-1 acceptance criteria as written.

**Rollout sequencing.** The design describes Phase 1 prerequisites but doesn't sequence them explicitly. Which must complete before which? A Feasibility Skeptic would map the dependency graph and identify where parallelism is safe vs where sequential gates are required.

**The reviewer quality feedback loop.** The design tests whether agents detect findings, but not whether the findings agents produce are good (correct severity, actionable suggestion, non-duplicate). That gap is acknowledged as Phase 2 (FR-QUALITY-1). A First Principles reviewer would ask whether Phase 1 alone — proving the pipeline plumbs end-to-end — is sufficient signal to justify Phase 2 investment.
