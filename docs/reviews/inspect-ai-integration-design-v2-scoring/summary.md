# Review Summary: Inspect AI Integration Design v2 — Scoring Strategy (ADR-007)

**Date:** 2026-02-17
**Design:** docs/plans/2026-02-17-inspect-ai-integration-design-v2.md
**Requirements:** docs/requirements/inspect-ai-integration-requirements-v2.md
**Stage:** design
**Verdict:** REVISE

---

## Verdict Reasoning

Three Critical findings block Phase 2 implementation: (1) the genuineness criterion conflates genuine (real flaw) with material (threatens success), systematically misclassifying Important/Minor findings as false positives; (2) reverse_judge_precision detects hallucination regression only — not coverage regression — but is presented as the "primary quality signal" without naming this limitation; (3) Phase 1 success criterion 3 references must_find_recall, a Phase 2 metric that does not exist in Phase 1 under ADR-007. All three are fixable with prose clarifications plus one structural change to the Phase 1 success criteria. No architecture rethink is required.

---

## Finding Counts
- Critical: 6
- Important: 11
- Minor: 5
- Contradictions: 1

## Findings by Phase
- Survey gaps: 3
- Calibrate gaps: 4
- Design flaws: 14
- Plan concerns: 1

## Auto-Fixable Findings
- None. All findings require human decision.

---

## Critical Findings

### C-1: Genuineness criterion conflates genuine with material — biases precision against Important/Minor findings
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** First Principles, Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Tier 1, Encoded criteria — GENUINE
- **Issue:** The GENUINE criterion requires that a finding "materially affects whether the design/plan can succeed." This gates reverse_judge_precision on severity (Critical impact) rather than reality (real, non-hallucinated gap). A finding that correctly identifies an Important or Minor structural gap is rated NOT genuine by the judge — not because it is false, but because it does not threaten success. The precision score becomes 'fraction of Critical findings' masquerading as 'fraction of real findings.'
- **Why it matters:** A reviewer that calibrates severity correctly — finding Important issues as Important, not inflating them to Critical — is penalized. A reviewer that inflates all findings to "logic bomb" severity scores higher on precision. This inverts the quality incentive: precision rewards false urgency over accurate calibration.
- **Suggestion:** Split genuineness into two independent checks: (A) Is this finding real? (document-visible, non-hallucinated, not a style preference). This is the precision gate — any finding passing A is genuine. (B) Is this finding material? (threatens success). This informs severity classification but is not a prerequisite for genuineness. Rewrite GENUINE criterion: "Identifies a specific, nameable gap or inconsistency that is discoverable from the document content alone and is not hallucinated, duplicated, or a style preference." Remove "materially affects whether the design/plan can succeed" from the genuineness criterion — move it to the CRITICAL severity definition instead.
- **Fixability:** human-decision
- **Status:** pending

### C-2: reverse_judge_precision detects hallucination only — coverage regression is undetectable in Phase 1
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Flagged by:** First Principles
- **Section:** Scoring Strategy (ADR-007) — Why cross-run matching fails
- **Issue:** The design frames reverse_judge_precision as the "primary quality signal." It is not a complete quality signal — it measures whether the reviewer is producing genuine findings (hallucination detection), not whether it is finding the findings it should find (coverage detection). A reviewer that degrades from 10 genuine findings to 2 genuine findings + 8 hallucinations scores lower on precision — correctly. A reviewer that degrades from 10 genuine findings to 2 genuine findings but no hallucinations scores 100% precision — incorrectly suggesting no degradation. Coverage regression is the dominant failure mode in the genuine-difference problem. Phase 1 does not detect it.
- **Why it matters:** Presenting precision as the "primary quality signal" without naming the coverage blind spot creates false confidence. Phase 1 could show precision=1.0 while the reviewer is missing 80% of real document flaws. The limitation needs to be explicit in the design — not discovered post-implementation.
- **Suggestion:** Add a named limitation box to the scoring strategy: "**Phase 1 limitation:** reverse_judge_precision detects hallucination regression (reviewer produces false findings). It does not detect coverage regression (reviewer misses genuine findings). must_find_recall (Phase 2) fills this gap. Phase 1 precision=1.0 is consistent with a reviewer that only finds 2 genuine flaws in a document with 20 real flaws." Update the "primary quality signal" phrasing to "primary available signal in Phase 1."
- **Fixability:** human-decision
- **Status:** pending

### C-3: Phase 1 success criterion 3 references a Phase 2 metric — creates unresolvable gate
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Phase 1 Test Plan
- **Issue:** Phase 1 success criterion 3 states "At least 3 of 5 reviewer tasks produce recall > 0.0 (agent is detecting something)." recall here refers to must_find_recall, which requires must_find.jsonl — a Phase 2 artifact. must_find.jsonl curation is listed as a Phase 2 prerequisite. Phase 1 cannot complete criterion 3 because the metric does not exist in Phase 1. The Phase 1 test plan was written against the old severity_calibration scorer and was not updated when ADR-007 was added.
- **Why it matters:** Phase 1 has no valid completion gate as written. A developer following the design cannot determine when Phase 1 is done. The gate blocks Phase 2 indefinitely.
- **Suggestion:** Replace Phase 1 success criterion 3 with: "At least 3 of 5 reviewer tasks produce non-zero reverse_judge_precision score (at least one finding per reviewer is judged genuine by the Haiku judge)." Remove recall from Phase 1 success criteria entirely — it is a Phase 2 metric.
- **Fixability:** human-decision
- **Status:** pending

### C-4: Haiku judge bias uncalibrated — false positive detection reliability unverified
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** The design relies on Haiku to reliably identify false positives from the encoded list (implementation details, hallucinated constraints, style preferences, etc.). Haiku is optimized for speed and cost, not rigorous adversarial classification. At T=0, a systematically lenient judge produces inflated precision scores regardless of reviewer quality. No calibration step verifies Haiku's behavior against known false positives before the judge is trusted.
- **Why it matters:** If Haiku is systematically lenient on any false positive category (e.g., consistently marking "hypothetical future concern" findings as genuine), precision scores cluster near 1.0 for all reviewers. The primary quality signal loses discriminative power. A broken reviewer and a high-quality one look identical.
- **Suggestion:** Gate Phase 1 reverse_judge_precision on a calibration run: (1) Select 5 known false positives from each category in the encoded list. (2) Run Haiku judge on each against the frozen document. (3) Confirm Haiku rates all 5 as NOT genuine. (4) Document the calibration run result. Gate Phase 1 on calibration accuracy ≥80%. This is a one-time step before deploying the judge.
- **Fixability:** human-decision
- **Status:** pending

### C-5: must_find.jsonl curation protocol undefined — no validation gate before items are written
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober, Assumption Hunter, Feasibility Skeptic
- **Section:** Scoring Strategy (ADR-007) — Tier 2: must_find_recall, Curation rules
- **Issue:** The curation rule "only include findings discoverable from the frozen document content alone" is a correctness requirement but has no enforcement mechanism. A finding curator who incorrectly classifies a context-dependent finding as document-visible adds a permanent false floor to must_find_recall — the metric can never reach its threshold. This is the same classification problem that caused the original accuracy=0.000 failure. The curation rules describe the standard but provide no protocol for validating it is met.
- **Why it matters:** must_find_recall is the regression guard. A corrupted must_find.jsonl (containing context-dependent findings) makes every eval run look like a regression. Trust in the metric evaporates. The curation process is the highest-leverage point for introducing systematic error into the eval framework.
- **Suggestion:** Specify a curation validation protocol: "For each must_find candidate, run a zero-shot validation: pass only the frozen document to Haiku with the prompt 'Does this document contain evidence of the following issue: [issue text]?' If Haiku cannot locate supporting evidence, classify as context_dependent. Log the zero-shot result in the must_find.jsonl record as 'validation': 'zero_shot_confirmed'." Add a make validate-dataset command that re-runs zero-shot validation on the current must_find.jsonl whenever the frozen document changes.
- **Fixability:** human-decision
- **Status:** pending

### C-6: FR-ARCH-5 cost budget not referenced — ADR-007 judge call volume unestimated
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Requirement Auditor
- **Section:** Scoring Strategy (ADR-007) — Updated scorer wiring
- **Issue:** FR-ARCH-5 requires: Full suite + LLM-as-judge grading <$2.00 per run. reverse_judge_precision fires one Haiku judge call per finding per sample across all 5 reviewer tasks. A reviewer that produces 10 findings generates 50 Haiku judge calls per full suite run. The design does not estimate this cost or reference FR-ARCH-5. At Haiku pricing (~$0.25/M input tokens), 50 calls × ~2K tokens each = 100K tokens = ~$0.025 — within budget. But this calculation is absent from the design, and the budget check is not automated.
- **Why it matters:** Without an explicit cost estimate in the design and a make cost-report implementation, the budget requirement is unverified. A future design iteration (multi-model comparison, longer documents) could push costs above $2.00 with no warning.
- **Suggestion:** Add a cost estimate table to the scoring strategy section: estimated per-finding judge cost, expected findings per reviewer, total judge calls per full suite run, estimated total cost vs FR-ARCH-5 budget. Link to the FR-ARCH-5 requirement. Confirm make cost-report is in scope for Phase 2 delivery.
- **Fixability:** human-decision
- **Status:** pending

---

## Important Findings

### I-1: "Duplicates another finding" false positive category is not operationalizable per-finding
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Tier 1, Encoded false positives
- **Issue:** The judge evaluates one finding at a time against the document. It cannot detect duplication without access to the full finding set. Redundant findings inflate the total_findings denominator, lowering precision — but the per-finding judge cannot detect this.
- **Why it matters:** The false positive category is unenforced. Redundant findings systematically lower precision in ways the judge cannot catch.
- **Suggestion:** Either (a) remove this category from the per-finding judge prompt and handle deduplication as a post-processing step before scoring; or (b) pass the full finding list to the judge alongside the individual finding.
- **Fixability:** human-decision
- **Status:** pending

### I-2: Judge output is binary — no tiebreaker for borderline findings; no confidence signal
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** Binary genuine/not_genuine verdict at T=0 produces no confidence signal. Borderline findings (partial document support, partial context-dependence) receive the same binary verdict as clear cases. Distribution of borderline findings cannot be tracked across reviewer versions.
- **Why it matters:** Precision improvement between two reviewer versions may be invisible if the distribution of borderline findings shifts without changing the binary verdict ratio.
- **Suggestion:** Add confidence field to judge output: `{"verdict": "genuine", "confidence": 0.85, "reason": "..."}`. Treat borderline (confidence < 0.6) as 0.5 for precision calculation. Log borderline count separately.
- **Fixability:** human-decision
- **Status:** pending

### I-3: Phase 2 prerequisites have circular dependency — non-zero precision requires scorer that is Phase 2 work
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Phase 2 Design Prerequisites (not in Phase 1)
- **Issue:** Prerequisite 1 requires non-zero Phase 1 precision, but the production precision scorer is listed as Phase 2 work. The prototype scorer is described as "throwaway."
- **Why it matters:** A throwaway prototype cannot gate Phase 2 entry. The prerequisite is unachievable as written.
- **Suggestion:** Clarify: either the prototype scorer is "good enough to gate Phase 2" (not throwaway), or replace prerequisite 1 with "Phase 1 produces non-zero parseable JSONL from at least one reviewer."
- **Fixability:** human-decision
- **Status:** pending

### I-4: severity_calibration retirement contradicts "keep for comparison" design decision
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Scoring Strategy (ADR-007) vs. Key Design Decisions
- **Issue:** The scoring strategy says severity_calibration and llm_judge_match are "retired after full implementation." Key Design Decisions says severity_calibration.py is retained for comparison and keeps ablation_tests.py functional. Direct contradiction.
- **Why it matters:** Developer receives conflicting instructions. ablation_tests.py breaks if scorer is removed.
- **Suggestion:** Resolve: severity_calibration.py is retained as non-primary comparison baseline. Update scoring strategy to say "retired as primary scorer" not "retired."
- **Fixability:** human-decision
- **Status:** pending

### I-5: FR-QUALITY-1 rubric dimensions not integrated into reverse_judge_precision
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** FR-QUALITY-1 defines 4 quality dimensions (specific/actionable, severity appropriate, suggestion helpful, why it matters convincing). The reverse_judge_precision judge measures genuineness only. Phase 2 delivers a scorer but does not close FR-QUALITY-1.
- **Why it matters:** If ADR-007 and FR-QUALITY-1 are not integrated, Phase 2 ships genuine-detection without quality-measurement. Two separate scorer phases are required instead of one.
- **Suggestion:** Add to Phase 2 prerequisites: "reverse_judge_precision judge integrates FR-QUALITY-1 rubric as secondary scoring dimensions. Judge output includes quality scores 1–5 per dimension alongside genuine/not_genuine verdict."
- **Fixability:** human-decision
- **Status:** pending

### I-6: must_find_recall acceptance criteria absent — Phase 2 implementation unverifiable
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Scoring Strategy (ADR-007) — Tier 2: must_find_recall
- **Issue:** All FRs have acceptance criteria. ADR-007 scorers have none. Phase 2 prerequisite 4 ("full implementation of both scorers") is unverifiable without criteria.
- **Why it matters:** Implementation completeness cannot be determined.
- **Suggestion:** Add acceptance criteria for must_find_recall: N=3 in list, finds all 3 → 1.0; finds 1 of 3 → 0.33; empty list → ValueError. make test covers all three.
- **Fixability:** human-decision
- **Status:** pending

### I-7: RAGAS faithfulness scorer implements reverse_judge_precision with calibrated defaults — not evaluated
- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Flagged by:** Prior Art Scout
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** RAGAS faithfulness is structurally identical to reverse_judge_precision — a judge verifies each claim against the source document. RAGAS is MIT-licensed, calibrated against human annotators, and supports Anthropic models. The design builds this from scratch without evaluating RAGAS as an alternative.
- **Why it matters:** Custom scorer requires prompt engineering, calibration, and maintenance that RAGAS delivers as a platform feature.
- **Suggestion:** Explicitly evaluate RAGAS faithfulness as a drop-in before committing to a custom scorer. Document the decision.
- **Fixability:** human-decision
- **Status:** pending

### I-8: G-Eval chain-of-thought prompting more reliable than direct binary judgment — not referenced
- **Severity:** Important
- **Phase:** survey (primary), design (contributing)
- **Flagged by:** Prior Art Scout
- **Section:** Scoring Strategy (ADR-007) — Tier 1, judge prompt design
- **Issue:** G-Eval research demonstrated that chain-of-thought reasoning before verdict improves judge calibration — especially for smaller models like Haiku. The design specifies direct binary verdict with no reasoning step.
- **Why it matters:** Direct binary judgment from Haiku is less reliable than reasoning-first. The reasoning output also provides interpretable debugging.
- **Suggestion:** Update judge design to chain-of-thought output: reasoning field + verdict field. Parse verdict for scoring; log reasoning for debugging. Compatible with T=0.
- **Fixability:** human-decision
- **Status:** pending

### I-9: Haiku judge not calibrated against known false positives — reliability unverified before deployment
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter, Edge Case Prober
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** The judge system prompt will be deployed without calibration against known false positives from the encoded list. This is a separate concern from C-4 (which focuses on the full gate) — this finding is specifically about the false positive list categories themselves. Each encoded category (implementation detail, hallucinated constraint, style preference, hypothetical future concern) should be verified with a concrete example.
- **Why it matters:** Abstract false positive categories without concrete examples are ambiguous. Haiku will pattern-match to the abstract wording inconsistently.
- **Suggestion:** Add one concrete example finding for each false positive category to the judge prompt as a few-shot calibration. Show both the finding text and the NOT genuine classification with a one-sentence reason.
- **Fixability:** human-decision
- **Status:** pending

### I-10: context_dependent_findings.jsonl has no re-evaluation path or version trigger
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober, Feasibility Skeptic
- **Section:** Scoring Strategy (ADR-007) — Dataset schema additions
- **Issue:** Findings written to context_dependent_findings.jsonl are permanently excluded. No re-evaluation trigger exists for when agents gain multi-document capability. No review_after field or issue link in the schema.
- **Why it matters:** Exclusions accumulate silently. Findings that become document-visible in later phases remain excluded permanently.
- **Suggestion:** Add review_after field (phase gate) and issue_link to the schema. make validate-dataset warns when context_dependent findings have review_after <= current phase and no promotion decision recorded.
- **Fixability:** human-decision
- **Status:** pending

### I-11: Braintrust implements ADR-007 infrastructure as platform features — not evaluated for scoring strategy
- **Severity:** Important
- **Phase:** survey (primary)
- **Flagged by:** Prior Art Scout
- **Section:** Scoring Strategy (ADR-007) — Overall architecture
- **Issue:** Braintrust (in project budget, 1M spans free tier) provides dataset management, LLM-as-judge scoring, per-trace logging, and regression detection — the infrastructure ADR-007 builds manually. ADR-005 predates ADR-007; the specific scoring requirements were not evaluated against Braintrust.
- **Why it matters:** Building dataset curation, scorer infrastructure, and regression detection in Inspect AI requires maintaining code that Braintrust provides as platform features.
- **Suggestion:** Add a decision record addressing Braintrust specifically for ADR-007 scoring requirements. Document switching cost and why Inspect AI is preferred (if it is).
- **Fixability:** human-decision
- **Status:** pending

---

## Minor Findings

### M-1: "Duplicates" false positive presupposes full-set access not available to per-finding judge
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Tier 1, Encoded false positives
- **Issue:** Already subsumed by I-1 above. Noted separately for completeness — the operational problem (per-finding judge cannot see duplicates) is distinct from the scoring problem (redundancy inflates denominator).
- **Fixability:** human-decision
- **Status:** pending

### M-2: Frozen document assumed semantically self-contained — cross-document findings rated as false positives
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** Findings that correctly identify cross-document gaps (design vs ADR) are rated NOT genuine by a single-document judge.
- **Suggestion:** Add judge prompt clause: "If a finding references an external document, treat this as plausible evidence of a genuine cross-document gap — do not rate NOT genuine solely because the referenced document is absent."
- **Fixability:** human-decision
- **Status:** pending

### M-3: metadata.json schema update for new dataset files not specified
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Scoring Strategy (ADR-007) — Dataset schema additions
- **Issue:** Design says metadata.json is "updated to reference new files" without specifying new field names or content hashes for must_find.jsonl and context_dependent_findings.jsonl.
- **Suggestion:** Add must_find_hash, context_dependent_hash, must_find_count, and curation_date fields to metadata.json schema. Add validation step when document hash changes but must_find_hash is unchanged.
- **Fixability:** human-decision
- **Status:** pending

### M-4: N-run aggregation not formally compared to must_find curation as alternative
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** First Principles
- **Section:** Scoring Strategy (ADR-007) — Overall architecture
- **Issue:** N=5 run union sampling may resolve the genuine-difference problem without requiring must_find.jsonl curation. The design defers this to Phase 2.5 but does not document the tradeoff comparison.
- **Suggestion:** Add a design decision note: compare N-run aggregation vs must_find curation on cost, complexity, and signal quality. Document the chosen approach and why.
- **Fixability:** human-decision
- **Status:** pending

### M-5: precision and recall share the same Haiku judge — correlated errors possible
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Scoring Strategy (ADR-007) — Updated scorer wiring
- **Issue:** Both reverse_judge_precision and must_find_recall use the same Haiku judge (different questions but same model). Systematic judge bias affects both metrics in correlated ways — a lenient judge inflates precision and over-detects recall simultaneously.
- **Suggestion:** Note in the design that precision and recall share a judge, and their errors are correlated — not independent quality signals when the judge is biased. This is a known limitation of single-judge eval frameworks.
- **Fixability:** human-decision
- **Status:** pending

---

## Contradictions

### Contradiction 1: severity_calibration.py retirement vs. retention for comparison
- **Underlying tension:** Clean architecture (remove deprecated scorer) vs. continuity (keep comparison baseline and avoid breaking ablation_tests.py)
- **Reviewers:** Requirement Auditor (flagged as I-4 above)
- **Position A (scoring strategy section):** severity_calibration and llm_judge_match are retired after full ADR-007 implementation. Implies removal or disabling.
- **Position B (key design decisions section):** severity_calibration.py is kept for comparison, keeps ablation_tests.py functional. Implies retention.
- **Tie-breaking criteria:** If ablation_tests.py has any tests that depend on severity_calibration producing results, Position B wins — removing it breaks the test suite. If ablation_tests.py can function with a no-op scorer, Position A is cleaner.
- **Why this matters:** A developer implementing ADR-007 gets conflicting instructions. The implementation will be inconsistent across developers.
- **Status:** pending

---

## Systemic Issue Detection

**33% of Critical findings (2/6) are calibrate gaps** — the genuineness criterion design (C-1) and the coverage regression blind spot (C-2) both reflect calibration problems in the scoring strategy's theoretical model, not just implementation gaps. These are upstream design model problems, not execution errors. No automatic escalation threshold reached (30% calibrate = borderline), but the pattern warrants noting: the scoring strategy section needs a design model review, not just prose fixes.

**Phase 1 definition is inconsistent across the document** — Phase 1 Test Plan, Phase 2 prerequisites, and the scoring strategy section use different models of what Phase 1 delivers. This cross-section inconsistency is a structural problem (not a single finding) that will cause confusion during implementation. A single reconciliation pass across all three sections is recommended before implementation begins.
