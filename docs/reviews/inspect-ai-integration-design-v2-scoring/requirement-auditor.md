# Requirement Auditor Review

## Coverage Matrix

| Requirement | Addressed? | Design Section | Notes |
|---|---|---|---|
| FR-ARCH-1: Per-reviewer eval task decomposition | Yes | Per-Reviewer Task Architecture | Fully covered |
| FR-ARCH-2: Eval-compatible agent interface | Partial | JSONL Output Alignment | Phase 1 mitigation described; Phase 2 mock tools not yet designed |
| FR-ARCH-3: JSONL output format | Yes | JSONL Output Alignment | Covered with fence-stripping and format fix |
| FR-ARCH-4: Ground truth refresh cadence | Yes | Ground Truth Management | Triggers and process defined |
| FR-ARCH-5: Cost budget per eval suite run | No | Makefile Update | Budget constraints from requirements not referenced; no cost tracking in design |
| FR-QUALITY-1: Quality rubric definition | Partial | Scoring Strategy (ADR-007) | ADR-007 is a new approach, but does not reference FR-QUALITY-1 rubric dimensions |
| Phase 1 success criteria | Partial | Phase 1 Test Plan | Criteria 3 (≥50% combined recall) conflicts with ADR-007 scoring approach |
| Detection targets by phase | No | Scoring Strategy (ADR-007) | ADR-007 replaces severity_calibration but does not restate phase detection targets against new metrics |

## Findings

### Finding 1: FR-ARCH-5 cost budget not addressed in ADR-007 scoring strategy
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Scoring Strategy (ADR-007) — Updated scorer wiring
- **Issue:** The requirements specify a full suite + LLM-as-judge grading budget of <$2.00 per run (FR-ARCH-5). The ADR-007 design adds reverse_judge_precision which fires a Haiku judge call per-finding, per-sample, across all 5 reviewer tasks. With a moderate reviewer (say 10 findings per run), that is 50 Haiku judge calls per full eval suite run plus the 5 reviewer tasks themselves. The design does not estimate or bound this cost — it does not reference FR-ARCH-5 at all.
- **Why it matters:** reverse_judge_precision could make the eval suite cost an order of magnitude more than the original severity_calibration approach. If the $2.00 budget is exceeded, the requirement is violated and the design is not compliant. Discovering this post-implementation requires rearchitecting the scorer.
- **Suggestion:** Add a cost estimate section to the scoring strategy: estimate per-finding judge cost (Haiku input ~2K tokens per finding+document, output ~100 tokens), multiply by expected findings per reviewer per run, multiply by 5 reviewers. Compare against FR-ARCH-5 budget. If budget is exceeded, specify a cost cap (max findings scored per run) or throttle (score every Nth finding).

### Finding 2: Phase 1 success criterion 3 (≥50% combined recall) is incompatible with ADR-007
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Phase 1 Test Plan
- **Issue:** Phase 1 success criterion 3 states 'At least 3 of 5 reviewer tasks produce recall > 0.0 (agent is detecting something).' This criterion references recall, which is a Tier 2 must_find_recall metric. But must_find.jsonl is a Phase 2 prerequisite — it does not exist in Phase 1. Phase 1 success criteria were written against the old severity_calibration scorer (expected→actual cross-run matching). ADR-007 retires severity_calibration but the Phase 1 criteria were not updated. The criteria reference a metric that does not exist in Phase 1 under the new architecture.
- **Why it matters:** Phase 1 has no valid completion gate. The Phase 1 test plan references retired metrics (severity_calibration results) while ADR-007 retires them and moves must_find_recall to Phase 2. A developer following the design as written has no clear Phase 1 success definition under ADR-007.
- **Suggestion:** Rewrite Phase 1 success criterion 3 to match ADR-007: 'At least 3 of 5 reviewer tasks produce non-zero reverse_judge_precision score (at least one finding is judged genuine).' Remove the recall criterion from Phase 1 — it is a Phase 2 metric.

### Finding 3: FR-QUALITY-1 rubric dimensions not integrated into reverse_judge_precision
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** FR-QUALITY-1 requires a quality rubric with 4 dimensions: specific and actionable, severity appropriate, suggestion helpful, why it matters convincing. The reverse_judge_precision design does not reference these dimensions. The judge is asked whether a finding is 'genuine' — a binary structural validity check — not whether it is high-quality on the FR-QUALITY-1 rubric. These are different questions: a finding can be genuine (real flaw, document-visible) but score 1/5 on specificity and 1/5 on suggestion helpfulness.
- **Why it matters:** FR-QUALITY-1 is a Phase 2 prerequisite, and ADR-007 is a Phase 2 implementation. Both are Phase 2 scope, but they are designed independently. If ADR-007 is implemented without integrating FR-QUALITY-1, Phase 2 delivers a scorer that measures genuineness but not quality — the original FR-QUALITY-1 gap remains open.
- **Suggestion:** In the Phase 2 prerequisites section, add: 'reverse_judge_precision judge prompt integrates FR-QUALITY-1 rubric dimensions as secondary criteria. Judge output includes quality scores (1–5) per finding in addition to the genuine/not_genuine verdict.' This makes Phase 2 deliver both ADR-007 and FR-QUALITY-1 in a single judge call.

### Finding 4: Contradiction between retirement of severity_calibration and stated comparison utility
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Key Design Decisions — Why keep severity_calibration.py?
- **Issue:** The scoring strategy states 'severity_calibration and llm_judge_match are retired after full implementation.' The Key Design Decisions section states severity_calibration.py is kept 'for comparison' and 'keeps ablation_tests.py functional.' These two statements are contradictory. A retired scorer cannot also serve as a comparison baseline.
- **Why it matters:** A developer implementing ADR-007 faces an ambiguous instruction: retire the scorer (scoring strategy) vs. keep it (key decisions). If they retire it, ablation_tests.py breaks. If they keep it, the scoring strategy instruction is wrong. Either way, the design is inconsistent.
- **Suggestion:** Resolve the contradiction explicitly: 'severity_calibration.py is retained as a comparison baseline (not removed from the codebase). It is no longer the primary production scorer — ADR-007 scorers are primary. It continues to run in make eval (not make reviewer-eval) for comparison. ablation_tests.py continues to use it.' Update the scoring strategy section to say "retired as primary scorer" not "retired."

### Finding 5: No acceptance criteria defined for must_find_recall scorer implementation
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 2: must_find_recall
- **Issue:** The design describes must_find_recall behavior ('what fraction of must-find findings did the reviewer detect?') and curation rules but provides no acceptance criteria for the scorer itself. FR-ARCH-1, FR-ARCH-2, FR-ARCH-3, FR-ARCH-4 all have explicit acceptance criteria tables. ADR-007 scorers have none. There is no definition of when must_find_recall is correctly implemented.
- **Why it matters:** Without acceptance criteria, implementation is unverifiable. The Phase 2 prerequisites list prerequisite 4 as 'full implementation of reverse_judge_precision and must_find_recall scorers' — but there is no way to determine whether the implementation meets requirements without criteria.
- **Suggestion:** Add acceptance criteria for must_find_recall: (1) Given a must_find.jsonl with 3 entries, and a reviewer that finds all 3, scorer returns 1.0. (2) Given a reviewer that finds 1 of 3, scorer returns 0.33. (3) Given an empty must_find.jsonl, scorer raises ValueError (no regression guard to test). (4) make test covers all three cases.

### Finding 6: dataset schema additions not tied to metadata.json update requirement
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Dataset schema additions
- **Issue:** The design states metadata.json is 'updated to reference new files' but does not specify what fields are added. FR-ARCH-4 requires metadata.json to include design_doc_hash — the new schema additions (must_find.jsonl, context_dependent_findings.jsonl) should also appear in metadata.json with their own reference fields and file hashes. The design does not specify the metadata.json schema update.
- **Why it matters:** A developer who adds must_find.jsonl but does not update metadata.json loses the ability to detect when the curated list is stale relative to the document. If the design document changes substantially but must_find.jsonl is not refreshed, the regression guard tests stale findings with no warning.
- **Suggestion:** Add to the dataset schema section: 'metadata.json additions: must_find_hash (content hash of must_find.jsonl), context_dependent_hash, must_find_count (integer), curation_date.' Add a make validate-dataset check that warns when document hash changed but must_find_hash is unchanged.

## Blind Spot Check
I focused on requirement coverage and contradictions. I may have underweighted: (1) whether the requirements themselves are complete enough to evaluate this design against — FR-QUALITY-1 is a Phase 2 prerequisite in requirements-v2 but the design extends it significantly; (2) the anti-goal check — the requirements don't state anti-goals explicitly, making it hard to confirm the design avoids them; (3) the testability of the scoring strategy — the design describes scorer behavior but not how to verify the judge prompt produces correct outputs during development.
