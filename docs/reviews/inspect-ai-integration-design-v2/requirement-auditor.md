# Requirement Auditor Review
## Inspect AI Integration — Design v2 vs Requirements v2

**Date:** 2026-02-17
**Design document:** `docs/plans/2026-02-17-inspect-ai-integration-design-v2.md`
**Requirements document:** `docs/requirements/inspect-ai-integration-requirements-v2.md`
**Reviewer:** Requirement Auditor

---

## Coverage Matrix

| Requirement | Addressed? | Design Section | Notes |
|---|---|---|---|
| FR-ARCH-1: Per-reviewer eval task decomposition | Yes | Per-Reviewer Task Architecture | One `@task` per agent, reviewer_filter, post-review exclusion all covered |
| FR-ARCH-1 AC: `evals/reviewer_eval.py` with one `@task` per agent | Yes | Per-Reviewer Tasks | Code pattern shown, 5 tasks enumerated |
| FR-ARCH-1 AC: `system_message(load_agent_content(...))` solver | Yes | Per-Reviewer Tasks | Explicit in code snippet |
| FR-ARCH-1 AC: Ground truth filters by `reviewer == agent_name` | Yes | Dataset Loader — Reviewer Filter | reviewer_filter param shown |
| FR-ARCH-1 AC: Excludes post-review findings | Yes | Special case: post-review finding | Explicitly handled |
| FR-ARCH-1 AC: `make reviewer-eval` runs all tasks | Yes | Makefile Update | Shown |
| FR-ARCH-2: Agent self-contained in eval context (no tool calls) | Partial | JSONL Output Alignment | Only addresses output format; agent body text ("Read the design document") implies tool use |
| FR-ARCH-2 AC: Prompt instructs "content provided in this message" | No | — | No design element adds or verifies this instruction in any agent file |
| FR-ARCH-2 AC: Agents do not require tool calls | No | — | `assumption-hunter.md` declares `tools: ["Read", "Grep", "Glob", "Write"]`; agent bodies say "Read the document" |
| FR-ARCH-2 AC: Agent output parseable by output_parser.py | Partial | JSONL Output Alignment | assumption-hunter fix acknowledged; other agents' body text not audited |
| FR-ARCH-3: All agents output JSONL | Partial | JSONL Output Alignment | assumption-hunter fix described; claims others "Already JSONL" without audit evidence |
| FR-ARCH-3 AC: All 5 agents output valid JSONL | Partial | JSONL Output Alignment | No audit or test verifies the 4 "already JSONL" agents produce parseable output |
| FR-ARCH-3 AC: Zero findings as output format failure | No | — | Design does not specify how or where this detection occurs |
| FR-ARCH-4: Ground truth refresh cadence | Partial | Ground Truth Management | Triggers listed; automated hash-check behavior not designed |
| FR-ARCH-4 AC: `metadata.json` includes `design_doc_hash` | Yes | Ground Truth Management | Referenced |
| FR-ARCH-4 AC: `make validate` re-runs if hash differs | No | — | No design element implements hash comparison; only refresh process (manual) described |
| FR-ARCH-4 AC: Post-review findings stored with `"discovery": "implementation"` | No | — | Design excludes post-review findings; does not store them with the required field |
| FR-ARCH-5: Cost budget per eval suite run | Partial | Phase 2 Design Prerequisites | Budgets listed; `make cost-report` deferred to Phase 1.5 prerequisites, not Phase 1 |
| FR-ARCH-5 AC: `make cost-report` reads logs and reports cost per run | No | — | Explicitly deferred to "Before Phase 1.5" section — not in Phase 1 |
| FR-ARCH-5 AC: Eval run cost logged in EvalLog metadata | No | — | No design element ensures cost metadata is captured in Phase 1 |
| FR-QUALITY-1: Quality rubric definition (Phase 2 prerequisite) | Partial | Phase 2 Design Prerequisites | Listed as a gate but no rubric content designed |
| FR-QUALITY-1 AC: Rubric documented with 1/5 and 5/5 examples per dimension | No | — | Design treats this as a future prerequisite with no design content |
| FR-QUALITY-1 AC: LLM-as-judge prompt references rubric explicitly | No | — | Not designed; correctly deferred to Phase 2 |
| FR-QUALITY-1 AC: Target aggregate quality score defined | No | — | Not designed; correctly deferred to Phase 2 |

---

## Findings

### Finding 1: Agent Body Text Contradicts FR-ARCH-2 — Tool-Call Instructions Not Removed
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** JSONL Output Alignment / FR-ARCH-2
- **Issue:** FR-ARCH-2 requires agents to function in eval context without tool calls. The design fixes `assumption-hunter.md`'s output format (markdown → JSONL) but does not address the agent body text that instructs models to use tools. The `scope-guardian.md` review process reads: "1. Read the design document thoroughly." The `success-validator.md` review process reads identically: "1. Read the design document thoroughly." These instructions prompt the model to attempt a `Read` tool call that does not exist in eval context. The frontmatter is stripped by `agent_loader.py` — the tool-call instructions in body text are not.

  Additionally, FR-ARCH-2 acceptance criterion 2 requires agent prompts to contain the instruction: "The design document content will be provided to you in this message." No design element adds this instruction to any agent file. The design assumes stripping frontmatter is sufficient to make agents eval-compatible.

- **Why it matters:** In eval context (no tools), a model that receives "Read the design document" with no file path in the prompt will either hallucinate a reading step, attempt a tool call that fails, or skip the step and produce fewer findings. Any of these outcomes produces a misleading detection baseline — the agent looks worse in eval not because its analysis is weak but because context delivery is wrong. This invalidates all Phase 1 recall measurements.
- **Suggestion:** Enumerate each of the 5 in-scope agent files and document the exact change needed to body text. Add acceptance criterion to FR-ARCH-2: "All 5 agent files pass a pre-Phase-1 audit checklist: no 'Read the file' instructions, no tool references in review steps, contains explicit 'Document content follows' transition language." The audit checklist is a Phase 1 prerequisite, not an assumption.

---

### Finding 2: FR-ARCH-4 Automated Hash Check Has No Design Element
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Ground Truth Management / FR-ARCH-4
- **Issue:** FR-ARCH-4's second acceptance criterion reads: "`make validate` re-runs if document hash differs." The design describes the hash field in `metadata.json` and the manual refresh process (5-step procedure), but no design element computes a document hash, compares it to `metadata.json`, or triggers `make validate` automatically. The Makefile snippet shown adds only `make reviewer-eval`. There is no `make validate` target in the design and no hash-comparison logic anywhere in the designed codebase.

  FR-ARCH-4's third acceptance criterion is also unmet: "Post-review findings stored with `'discovery': 'implementation'` field." The design explicitly excludes `v1-post-review-001` from per-reviewer tasks with a note that it "may be included in a future 'implementation discovery' dataset." It is currently stored in `critical_findings.jsonl` with no `discovery` field.

- **Why it matters:** Without automated hash-check, the ground truth dataset silently goes stale when the reviewed document changes. Stale ground truth was identified as a root cause of false positives in Session 19. The requirement exists to prevent exactly this failure mode. A manual process that depends on a developer remembering to refresh is the current state — not an improvement.
- **Suggestion:** Design the `make validate` target explicitly: it reads `metadata.json`, computes the current document hash, and aborts with an error if they differ. Separately, add the `"discovery": "implementation"` field to `v1-post-review-001` in `critical_findings.jsonl` now. Both are small, concrete additions that close the gap.

---

### Finding 3: FR-ARCH-5 Cost Tracking Deferred Out of Phase 1 With No Substitute
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Phase 2 Design Prerequisites / FR-ARCH-5
- **Issue:** FR-ARCH-5 sets budget thresholds for Phase 1 (single-reviewer task <$0.10, full suite <$0.50) and requires `make cost-report` as an acceptance criterion. The design places `make cost-report` under "Before Phase 1.5 (multi-model comparison)" prerequisites — not Phase 1. The Phase 1 Test Plan has five completion criteria; none mention cost. There is no substitute: no log inspection step, no manual cost estimate procedure, no `EvalLog metadata` capture mechanism designed.

  The requirement's second acceptance criterion — "Eval run cost logged in EvalLog metadata" — is not addressed anywhere in the design. Inspect AI logs token counts but not dollar costs; the conversion requires a pricing table that is not designed.

- **Why it matters:** Phase 1 can complete its five stated criteria, declare success, and move to Phase 1.5 without ever verifying it meets the $0.50 budget target. Multi-model comparison (Phase 1.5) at 3× cost could run $1.50 per suite run — within the stated multi-model budget only if the per-suite budget is confirmed first. Running Phase 1.5 blind on cost reproduces the budget discipline problem the requirement was written to prevent.
- **Suggestion:** Add a sixth Phase 1 completion criterion: "Single reviewer task cost verified <$0.10 by inspecting EvalLog token counts × Sonnet pricing. Full suite cost verified <$0.50." This requires no `make cost-report` automation — a one-time manual calculation closes the Phase 1 gap. Defer automation to Phase 1.5 as the design intends, but require manual verification for Phase 1.

---

### Finding 4: Five-Agent Scope Claimed Without Defining Which Five Agents
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Per-Reviewer Task Architecture / FR-ARCH-1
- **Issue:** The repo contains 11 agent files: assumption-hunter, scope-guardian, problem-framer, constraint-finder, success-validator, review-synthesizer, edge-case-prober, feasibility-skeptic, first-principles, prior-art-scout, and requirement-auditor. The design targets 5 reviewer agents for per-reviewer tasks but never states which 5. The task listing shows assumption-hunter, constraint-finder, problem-framer, scope-guardian, and success-validator — consistent with the `parallax:requirements --light` reviewer set — but this is inferred from context, not stated.

  FR-ARCH-2 acceptance criterion 2 requires agents to work from a single document input with no external context. `prior-art-scout`, `feasibility-skeptic`, and `edge-case-prober` are excluded without documented rationale. The assumption-hunter requirements-light review (Critical finding `assumption-hunter-002`) identified that some reviewer types structurally cannot function in single-turn eval context. The design does not address which agents are excluded or why.

- **Why it matters:** Without an explicit agent scope statement, two failure modes emerge: (1) a future contributor adds a per-reviewer task for `prior-art-scout`, which structurally underperforms in single-turn eval and produces a misleading baseline, or (2) a requirement-auditor or edge-case-prober task is missing from Phase 1 coverage without anyone knowing it was excluded. Both are silent scope problems.
- **Suggestion:** Add a design section: "Phase 1 Agent Scope." List the 5 agents with rationale. For the 6 excluded agents, state the exclusion reason: single-document limitation (prior-art-scout, edge-case-prober), orchestration role (review-synthesizer), or Phase 3+ agent bridge (requirement-auditor, feasibility-skeptic, first-principles). This is a 10-line section that closes a systematic coverage gap.

---

### Finding 5: Ground Truth Finding Count Mismatch — Duplicate ID Across Two Reviewer Sets
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Per-Reviewer Tasks — Reviewers with ground truth in current dataset
- **Issue:** The design states finding `013` appears in the assumption-hunter ground truth set ("assumption_hunter_eval — 2 findings (001, 013)") and in the scope-guardian ground truth set ("scope_guardian_eval — 1 finding (013)"). If both reference the same finding ID `v1-assumption-hunter-013` (or equivalent), this finding cannot belong to both reviewer sets under FR-ARCH-1's filter logic (`reviewer == agent_name`). A single finding has one `reviewer` field. If the ID is the same finding with different reviewer attributions, one attribution is wrong. If there are two distinct findings both numbered 013, the ID scheme is broken.

  The design's total count of "9 testable findings" across 5 reviewers (2+2+2+1+2) assumes no overlap. If finding 013 is shared between assumption-hunter and scope-guardian, the true non-overlapping count is 8.

- **Why it matters:** The ground truth dataset is the foundation of all Phase 1 metrics. An ambiguous finding attribution produces incorrect per-reviewer recall scores. The design cannot proceed to implementation without resolving this — the reviewer_filter logic will either include the finding in two tasks (double-counting) or exclude it from one (undercounting). Either way, detection scores are wrong.
- **Suggestion:** Inspect `datasets/inspect-ai-integration-requirements-light/critical_findings.jsonl` and confirm whether finding 013 is a single entry with one `reviewer` value or two entries. If one entry, remove it from the scope-guardian task list in the design. If two distinct findings share the ID `013`, fix the ID scheme to be globally unique.

---

### Finding 6: JSONL Output Alignment Relies on "Already JSONL" Claim Without Verification
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** JSONL Output Alignment / FR-ARCH-3
- **Issue:** The design states four agents are "Already JSONL" (scope-guardian, problem-framer, constraint-finder, success-validator) and marks them as requiring no change. FR-ARCH-3 requires parseable JSONL from all 5 agents. Confirming this claim requires reading each agent's output format instruction and verifying it matches the required schema. The design provides no evidence this check was performed.

  A concrete gap: the `scope-guardian.md` and `success-validator.md` output format sections hardcode `"phase": {"primary": "calibrate", "contributing": null}` — a fixed value that cannot represent design-phase or plan-phase findings. The FR-ARCH-3 schema allows `"primary": "survey|calibrate|design|plan"`. Agents that hardcode `calibrate` will produce schema-valid but semantically incorrect output for any finding that belongs to a different phase. The scorer, which checks severity not phase, won't catch this.

  FR-ARCH-3 also requires: "Zero findings parsed treated as output format failure." No design element implements this check — not in the scorer, not in the Makefile, not in any test plan criterion.

- **Why it matters:** Phase hardcoding reduces information value from the eval framework. Phase distribution is a signal for systemic detection (are all findings clustering in calibrate? Is design-phase coverage missing?). Hardcoded phases make this signal meaningless. The zero-findings detection gap means a misconfigured agent produces silence instead of an error — identical to a broken eval run.
- **Suggestion:** Audit each agent's output format section against the full FR-ARCH-3 schema, including the phase enum. Fix hardcoded phase values to allow the reviewing agent to determine phase from context. Add a test in Phase 1 Test Plan criterion 1: "Scorer returns format-error for any task where parsed findings count is zero."

---

### Finding 7: FR-QUALITY-1 Has No Design Content — Rubric Undefined Except as a Gate
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Phase 2 Design Prerequisites / FR-QUALITY-1
- **Issue:** FR-QUALITY-1 requires the quality rubric to be defined before Phase 2 begins, with 1/5 and 5/5 examples per dimension. The design lists FR-QUALITY-1 as a Phase 2 prerequisite item: "Quality rubric defined and documented." No design content is provided — no dimensions, no example structure, no candidate scoring model. This is appropriate deferral for a Phase 2 item, but the acceptance criteria for FR-QUALITY-1 include "Target aggregate quality score defined." The design provides no target (not even a provisional placeholder), which means the scorer cannot have a pass/fail threshold when it is eventually implemented.

- **Why it matters:** A Phase 2 gate with no defined target score produces a scorer that runs but cannot declare pass or fail. The requirements-light review of v2 requirements (success-validator finding, Critical #10) independently identified that "non-zero accuracy is not a threshold." The same problem exists for FR-QUALITY-1 — without a numeric target, Phase 2 never formally completes either.
- **Suggestion:** Add one line to the Phase 2 Design Prerequisites section: "Target aggregate quality score: ≥3.5/5.0 (provisional — adjust after Phase 2 baseline run)." This is not design work — it is filling in a required field from the requirement's acceptance criteria. The design can defer rubric dimension content to Phase 2 but must carry forward the target.

---

### Finding 8: ID Schema Discrepancy Between Requirement and Design
- **Severity:** Minor
- **Phase:** calibrate (primary)
- **Section:** JSONL Output Alignment / FR-ARCH-3
- **Issue:** FR-ARCH-3 specifies the finding ID schema as `"id": "<reviewer>-<NNN>"` (example: `"id": "assumption-hunter-001"`). The design's JSONL schema block shows `"id": "v1-<agent-name>-NNN"` and the existing dataset uses `v1-assumption-hunter-001`. The `v1-` prefix is present in the design but absent from the requirement's schema definition. This is a minor discrepancy — the design and dataset agree with each other but disagree with the requirement.

- **Why it matters:** The requirement is the authoritative source. If the scorer validates finding IDs against the schema, the `v1-` prefix causes parse failure or ID mismatch. If it does not validate IDs, the discrepancy is harmless but signals that the requirement and design were not cross-checked on this field.
- **Suggestion:** Update FR-ARCH-3 to specify `"id": "v1-<reviewer>-<NNN>"` matching actual usage, or update the design and dataset to drop the `v1-` prefix. Either is acceptable — pick one and make them match.

---

## Blind Spot Check

My focus was requirement-to-design traceability. The following design quality issues fall outside that scope but would surface under other review lenses:

**Assumption Hunter perspective:** The design assumes `agent_loader.py` handles all frontmatter stripping edge cases (nested `---` in body text, Windows CRLF line endings). The implementation `content.index("---", 3)` raises `ValueError` if the closing `---` is missing. No error handling is designed.

**Edge Case Prober perspective:** The design specifies `reviewer_filter=None` returns all findings (correct), but does not specify behavior when `reviewer_filter` matches zero findings. An empty dataset produces an eval task with no samples, which in Inspect AI produces a division-by-zero in score aggregation. The Phase 1 test plan's "No task crashes at instantiation time" criterion does not cover empty-dataset behavior at eval runtime.

**Feasibility Skeptic perspective:** The Phase 1 Test Plan criterion 3 targets "≥1 reviewer task achieves recall ≥ 0.90 and precision ≥ 0.80." With 2 findings per reviewer, achieving 0.90 recall requires detecting 1.8 findings — which rounds to 2/2 = 100%. The 90% target is unreachable as stated for a 2-sample ground truth: results will be 0%, 50%, or 100%. This criterion will always show 0 or 1 passing tasks, regardless of prompt quality.
