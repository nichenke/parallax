# Feasibility Skeptic Review
# Design: Inspect AI Integration — v2

**Reviewer:** Feasibility Skeptic
**Date:** 2026-02-17
**Design document:** Design: Inspect AI Integration — v2
**Requirements document:** Requirements: Inspect AI Integration — v2

---

## Complexity Assessment

**Overall complexity:** Medium (design is simpler than v1, but several hidden blockers exist before first run)

**Riskiest components:**
1. Ground truth dataset — 9 findings split 5 ways means some reviewers have N=1 ground truth, where a single miss collapses recall to 0.0
2. `assumption-hunter` output format mismatch — the agent currently produces markdown; the design acknowledges this but underestimates the behavioral change required
3. Missing eval source tree — `evals/utils/agent_loader.py` and all eval Python source are absent from the working branch; only `.pyc` artifacts exist

**Simplification opportunities:**
- Start with 2 reviewers (scope-guardian and problem-framer — both confirmed JSONL, both have ground truth) before building all 5 tasks; this produces a passing eval faster and exposes scorer issues earlier
- Replace the ground truth refresh process (5 manual steps) with a single script that computes the hash and warns if it differs; the current manual process will be skipped in practice

---

## Findings

### Finding 1: Eval Source Tree Does Not Exist On Disk
- **Severity:** Critical
- **Phase:** plan (primary)
- **Section:** Per-Reviewer Task Architecture / Agent Loader
- **Issue:** The design references `evals/utils/agent_loader.py` and `evals/reviewer_eval.py` as artifacts to implement. Neither file exists on disk — the entire `evals/` directory contains only compiled `.pyc` artifacts from a previous session. The design describes code to write, not code that exists. `make reviewer-eval` cannot run.
- **Why it matters:** Phase 1 completion criterion #1 is "`make reviewer-eval` runs without parse errors." The prerequisite file must be written before any other Phase 1 criterion is testable. This is not a design gap — it is the primary implementation task — but the design presents it as if `agent_loader.py` already exists (MEMORY.md says "partial implementation committed: `evals/utils/agent_loader.py`"). On the current branch it does not.
- **Suggestion:** Add an explicit "current implementation state" section to the design. List which files exist vs which are to-be-built. This prevents a reviewer or implementer from assuming a partially-built state that doesn't exist.

---

### Finding 2: assumption-hunter Output Format Change Is a Behavioral Modification, Not a Format Update
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** JSONL Output Alignment
- **Issue:** The design treats the assumption-hunter output format change as a one-line edit: "Update `assumption-hunter.md` output format section." This understates the actual work. The assumption-hunter was deliberately designed with markdown output — its output format section uses a fenced markdown block with prose structure, and the agent has `tools: ["Read", "Grep", "Glob", "Write"]` in its frontmatter, meaning it was built for interactive use with filesystem access. Changing to JSONL is not a format swap; it requires verifying that the agent generates valid JSONL without fences, that it numbers findings correctly (`v1-assumption-hunter-NNN`), and that it includes all required fields when running without tool access in eval context. The v1 eval produced accuracy: 0.000 precisely because this kind of mismatch was underestimated.
- **Why it matters:** If the assumption-hunter JSONL change doesn't work, the scorer returns 0 for that reviewer task, which looks identical to "agent found no issues." FR-ARCH-3 requires "zero findings parsed treated as output format failure, not zero findings found," but the design has no mechanism to distinguish the two at the task level.
- **Suggestion:** Before implementing `reviewer_eval.py`, test each agent manually: pass document content as a user message, confirm the raw output is valid JSONL with no fences, confirm all required fields are present. Treat this as a prerequisite gate, not an implementation detail. Log results in a compatibility table (agent | JSONL native | fence-free | all fields | tool-free).

---

### Finding 3: Ground Truth Has N=1 Coverage for At Least One Reviewer
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Per-Reviewer Tasks / Ground Truth Management
- **Issue:** The design lists 9 testable findings across 5 reviewer tasks. scope-guardian has 1 finding (id 013). With N=1, recall is binary: 1.0 or 0.0. A single non-detection produces recall=0.0, which is indistinguishable from the agent being completely broken. The design sets Phase 1 success criteria as "≥1 reviewer task achieves recall ≥ 0.90 and precision ≥ 0.80" — but scope-guardian cannot achieve 0.90 recall; it can only score 1.0 or 0.0. Partial credit is structurally impossible.
- **Why it matters:** The eval framework produces meaningless signal for any reviewer with N<3 ground truth findings. The noise (due to LLM non-determinism) exceeds the signal. A reviewer task passing or failing Phase 1 criteria with N=1 tells you nothing about real capability.
- **Suggestion:** Before Phase 1 runs, expand ground truth to minimum N=3 per reviewer. For scope-guardian specifically, this means running `parallax:requirements --light` on the requirements-v2 doc, validating the findings, and extracting all scope-guardian findings with `validation_status == "real_flaw"`. The requirements review summary for inspect-ai-integration-v2 exists (`docs/reviews/inspect-ai-integration-v2-requirements-light/summary.md`) with 8 scope-guardian findings — these need to be validated and added to the dataset before Phase 1 can produce meaningful results.

---

### Finding 4: The `reviewer` Field in Existing Ground Truth Is Unverified
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Dataset Loader / Per-Reviewer Tasks
- **Issue:** The entire per-reviewer task architecture depends on filtering ground truth by `reviewer` field. The design's `load_validated_findings()` filter requires each finding to have `f.get("reviewer") == reviewer_filter`. The existing dataset was validated from full-skill output (the `parallax:requirements --light` orchestration), not from individual agent runs. There is no confirmation that findings in `critical_findings.jsonl` carry a `reviewer` field populated with the agent's exact name. If the field is missing or uses a different naming convention (e.g., `"assumption_hunter"` vs `"assumption-hunter"`), every per-reviewer task returns an empty dataset and the eval never fires.
- **Why it matters:** An empty dataset causes Inspect AI to skip all samples — the eval completes with 0 scores, no error. This failure is silent. The implementer sees a green run with no findings detected and no indication that the dataset filter returned nothing.
- **Suggestion:** Add a mandatory pre-flight check: load the dataset, group by `reviewer` field value, print counts. Fail with an explicit error if any expected reviewer has 0 findings. Run this check as `make validate-dataset` before `make reviewer-eval`. Also: inspect the existing JSONL manually to confirm the `reviewer` field naming convention before writing the filter logic.

---

### Finding 5: The Frontmatter `tools` Field Conflicts with Eval Context
- **Severity:** Important
- **Phase:** design (primary), survey (contributing)
- **Section:** FR-ARCH-2: Eval-Compatible Agent Interface
- **Issue:** All 5 reviewer agents declare `tools: ["Read", "Grep", "Glob", "Write"]` in their YAML frontmatter. This declaration is meaningful in Claude Code's native context — it grants filesystem access. In Inspect AI eval context, where the agent is invoked via `system_message()` with no tools provisioned, the frontmatter is stripped by `agent_loader.py` — but the agent's behavioral expectations are not. The scope-guardian's review process says "Read the design document thoroughly" as step 1, which implies filesystem access. In eval context the document arrives in `Sample.input`, not via a tool call. The agent may attempt to read a file path rather than treat the prompt content as the document — exactly the failure mode discovered in Session 21 ("model receiving path not content").
- **Why it matters:** An agent that attempts to call `Read` tool in eval context produces an error or a confused response, not findings. FR-ARCH-2 requires agents to "function correctly in eval context without modifications to the agent file" — but the agents' review processes assume tool availability. The document must be passed in a way that the agent recognizes as "the thing to review" without triggering a tool call.
- **Suggestion:** Add explicit instruction to agent prompts (or to the `system_message()` wrapper): "The document to review is provided in this prompt. Do not attempt to read files — the full document content follows." Alternatively, use a `user_message()` or message template that makes the document's presence unambiguous. Test this with a single agent before building all 5 tasks.

---

### Finding 6: The JSONL Output Format Is Defined in Three Places with No Canonical Source
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** JSONL Output Alignment
- **Issue:** The required JSONL schema appears in the design doc, in individual agent prompt files, and (implicitly) in `output_parser.py`. The design acknowledges this fragmentation but offers no resolution — it states the schema and says "Update `assumption-hunter.md` output format section," which adds a fourth location (the design doc itself) rather than designating a canonical source. When the schema changes (e.g., adding `contributing` phase, changing `id` format), the implementer must update all locations manually.
- **Why it matters:** Schema drift between agent prompts and the parser was the exact failure mode in v1. The design corrects the symptom (markdown vs JSONL) without addressing the root cause (no schema governance). The next schema change will re-introduce this failure.
- **Suggestion:** Designate `schemas/reviewer-findings-v1.0.0.schema.json` (which already exists in the repo) as the canonical schema. Update agent prompts to reference it by name rather than embedding the schema inline. The parser validates against it. This makes drift visible: a failing schema validation produces an explicit error, not 0 findings.

---

### Finding 7: The Ground Truth Refresh Process Is Described but Not Enforced
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Ground Truth Management
- **Issue:** The 5-step refresh process requires a human to: run a review, open the validation UI, update the JSONL, update metadata.json, and run the eval. FR-ARCH-4 requires `make validate` to re-run if the document hash differs — but the Makefile target shown in the design only runs the Inspect eval, not a hash check. There is no `make validate-hash` or automatic trigger. The refresh process relies entirely on the developer noticing the document changed and running the steps manually.
- **Why it matters:** Stale ground truth produces misleading eval results. Session 19 documented exactly this: "Stale findings discovered during validation UI use — must run fresh review before validating." A manual process that requires 5 steps will be skipped when time is short, producing false pass/fail signals that mislead the design iteration loop.
- **Suggestion:** Add a `make check-hash` target that computes the current document hash, compares it to `metadata.json`, and exits non-zero if they differ. Make `make reviewer-eval` depend on `check-hash`. This turns an advisory process into an enforcement gate without requiring full automation.

---

### Finding 8: Phase 1 Success Criteria Are Inconsistent
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** Phase 1 Test Plan
- **Issue:** The Phase 1 test plan has 5 completion criteria. Criterion #3 requires "≥1 reviewer task achieves recall ≥ 0.90 and precision ≥ 0.80." Criterion #2 requires "at least 1 reviewer task achieves recall > 0.0." These are not additive gates — criterion #3 is a strict superset of criterion #2. Additionally, the 90%/80% thresholds originated in requirements-v1 and are described in requirements-v2 as "provisional." Using them as Phase 1 completion criteria without restating them as confirmed targets means Phase 1 is evaluated against unvalidated thresholds.
- **Why it matters:** If the Phase 1 run achieves recall=0.5 for one reviewer, criterion #2 passes but criterion #3 fails. Does Phase 1 complete? The criteria don't specify whether all 5 must pass, or any 1, or a named reviewer. Ambiguous completion gates cause scope disagreement mid-implementation.
- **Suggestion:** Collapse to a single, unambiguous Phase 1 exit gate. Example: "All 5 reviewer tasks run without crashing AND at least 2 reviewer tasks achieve recall ≥ 0.50 on their ground truth set." Save 90%/80% for Phase 2. Explicitly state whether the gate is AND (all reviewers must meet it) or OR (at least one must).

---

### Finding 9: The `make cost-report` Target Is Required by FR-ARCH-5 but Absent from the Design
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Makefile Update / FR-ARCH-5
- **Issue:** FR-ARCH-5 requires `make cost-report` to read logs and report cost per run, and sets a budget of <$0.50 for the full suite. The design's Makefile section shows only `make reviewer-eval`. There is no design for how `cost-report` reads Inspect AI logs, what format the cost data is in, or how per-reviewer cost is computed. The requirements review summary flagged this as an orthogonal Phase 1 concern — but the requirement exists in v2 without being addressed in the design.
- **Why it matters:** Without `cost-report`, the $0.50 budget constraint is unverifiable. The first multi-model run in Phase 1.5 could exceed budget with no alerting. More immediately: if the acceptance criteria include `make cost-report` functionality, Phase 1 cannot be declared complete without implementing it.
- **Suggestion:** Either descope `make cost-report` from Phase 1 (defer to Phase 1.5 when multi-model cost comparison is actually needed) and document that decision, or add a concrete implementation design: which Inspect AI log fields contain cost data, what the output format looks like, and what "flags for optimization" means operationally.

---

### Finding 10: `load_agent_content` Frontmatter Stripping Is Fragile
- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Agent Loader
- **Issue:** The `load_agent_content` function strips YAML frontmatter using string search for `"---"`. The implementation uses `content.index("---", 3)` to find the closing delimiter. This fails silently if the frontmatter contains a `---` in a field value (e.g., in the `description` multiline block). All 5 agent files use multiline `description` blocks in their frontmatter — a `---` in those blocks would cause the function to truncate the system prompt mid-frontmatter, passing garbage to the model.
- **Why it matters:** Blast radius is limited — agent prompts are controlled files. But the failure mode is silent: the model receives a malformed prompt, produces confused output, and the scorer returns 0 findings. The implementer would need `inspect view` to trace the root cause.
- **Suggestion:** Replace string search with a proper YAML parser (`import yaml`). Split on the first `---...---` block using `yaml.safe_load_all()` or a regex that anchors to line boundaries (`^---$`). Add a unit test that passes a prompt with `---` in a description field and confirms the full prompt body is preserved.

---

### Finding 11: The Design Omits the reviewer_eval.py Implementation Detail Entirely
- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Per-Reviewer Tasks
- **Issue:** The design shows the task structure for one reviewer (`assumption_hunter_eval`) and states the same pattern applies to the other 4. It does not address: how the 5 tasks are discovered and run together by `make reviewer-eval`, whether they share a dataset loader instance or instantiate separately, how Inspect AI task naming works when multiple `@task` functions exist in one file, or what happens when `load_validated_findings()` returns an empty dataset for a reviewer with no ground truth.
- **Why it matters:** These are not hard problems, but each is a 30-minute debugging session if encountered without anticipation. The "all 5 tasks run without crashing" Phase 1 criterion requires that Inspect AI can discover and execute all 5 `@task` functions from a single `inspect eval evals/reviewer_eval.py` invocation — this is correct Inspect AI behavior, but it should be verified against the installed version.
- **Suggestion:** Add a spike task: create `reviewer_eval.py` with 2 stubbed `@task` functions (no real scorers, empty datasets), run `make reviewer-eval`, confirm both tasks appear in `inspect view`. This confirms the multi-task discovery pattern before investing in scorers.

---

## Blind Spot Check

This review focused on buildability and hidden complexity. The following concerns fall outside the feasibility lens and would be caught by other reviewers:

**Correctness of the scorer logic:** The `severity_calibration()` scorer is carried over from v1 with the note "Keep severity_calibration.py for comparison." Whether this scorer correctly measures recall and precision for the per-reviewer task architecture is a correctness question, not a feasibility question — but it is the most likely source of continued 0.000 accuracy even after the format issues are fixed.

**Ground truth validity:** Whether the 9 validated findings are actually correct (real flaws in the requirements doc, not reviewer quality failures) is a quality question. The requirements review summary notes "25% of Critical findings were quality failures" in v1 — applying that rate to 9 findings suggests 2 may be invalid ground truth, which would make the recall ceiling ~78% before any implementation work.

**Test coverage of edge cases:** The design does not address what happens when the model outputs more findings than the ground truth (high recall, low precision) vs fewer (high precision, low recall). The scorer behavior in each case determines whether Phase 1 criteria are achievable at all.
