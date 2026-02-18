# Edge Case Prober Review

## Findings

### Finding 1: Judge returns ambiguous verdict for borderline findings — no tiebreaker defined
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** The judge prompt encodes GENUINE and NOT genuine criteria but provides no guidance for the ambiguous middle: a finding that is partially document-visible, partially context-dependent, and addresses a real gap but one of borderline materiality. The judge at T=0 must produce a binary YES/NO with no partial credit output. For borderline cases, small prompt wording changes will flip the verdict — making precision scores sensitive to judge prompt versions in ways that are invisible in the output.
- **Why it matters:** Borderline findings in the 0.3–0.7 confidence range are where reviewer quality differentiation actually lives. A regime that forces binary verdicts on ambiguous cases makes the precision signal noisy precisely where signal matters most. Two model versions with meaningfully different reviewer quality could produce identical precision scores if their borderline-finding distributions differ but cancel out.
- **Suggestion:** Add a three-way output to the judge: `{"verdict": "genuine"|"not_genuine"|"borderline", "confidence": 0.0-1.0, "reason": "..."}`. Treat "borderline" as 0.5 in precision calculation. Log borderline count as a separate diagnostic. This preserves the binary precision metric while giving insight into distribution.

### Finding 2: must_find.jsonl with min_recall thresholds has undefined behavior when N < threshold denominator
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 2: must_find_recall, MVP behaviour
- **Issue:** The design states 'min_recall not enforced [in MVP], found/not-found reported per finding as diagnostic.' This defers enforcement to Phase 2 with 'N≥3 runs.' But the design does not specify what N means: N runs of the same reviewer on the same document? N runs across different model temperatures? N different model versions? Without this definition, the Phase 2 prerequisite 'Makefile updated to run N=3 per eval cycle' is unspecified, and the N=3 determination is untested.
- **Why it matters:** If N=3 means 3 independent runs at T=1.0, recall variance will be high (the genuine-difference problem). If N=3 means 3 runs at T=0, all 3 are identical — providing no statistical value. The design's own diagnosis of the problem (genuine run-to-run variance) makes N-run averaging at T=1 essential, but this is not explicit.
- **Suggestion:** Specify N explicitly: 'N=3 independent runs at the reviewer's production temperature (T≈1.0). A finding is "detected" if it appears in at least 1 of 3 runs. min_recall = detections/3.' Document that N=3 at T=0 provides no variance estimate and is not a valid approach.

### Finding 3: context_dependent_findings.jsonl has no defined validation gate before writing
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Dataset schema additions
- **Issue:** The design defines context_dependent_findings.jsonl as a backlog of excluded findings with their `required_context` field. There is no defined process for validating that a finding is actually context-dependent before writing it to this file. A finding curator who incorrectly classifies a document-visible finding as context-dependent removes it from the regression guard permanently — it will never appear in must_find.jsonl and never trigger a regression alarm.
- **Why it matters:** context_dependent_findings.jsonl is a one-way valve: once a finding goes in, it is excluded from all future recall checks. Silent misclassification means real document flaws have no regression coverage. The design acknowledges this file as a 'backlog' but does not say how items are validated before being placed there permanently.
- **Suggestion:** Before any finding is written to context_dependent_findings.jsonl, require a 'zero-shot test': pass only the frozen document to Haiku and ask it to find this specific issue. If Haiku locates it, the finding is document-visible and belongs in must_find.jsonl. Log the zero-shot test result in the JSONL record alongside required_context.

### Finding 4: Precision calculation denominator undefined when reviewer produces zero findings
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** Score = real_findings / total_findings. When a reviewer produces zero findings, this is 0/0 — undefined. The design does not specify whether zero-finding output is (a) treated as precision=0.0, (b) precision=None (excluded from mean), or (c) a parse error that blocks scoring. The design notes that zero-findings output from any agent is already a Phase 1 gating failure, but Phase 2 scorers must handle this case to avoid crashing on edge inputs.
- **Why it matters:** Division by zero in a scorer crashes the entire eval run. Inspect AI's mean() scorer will propagate NaN or raise depending on implementation. A single reviewer that produces empty output on one sample crashes all 5 tasks if the exception is unhandled.
- **Suggestion:** Explicitly define: 'If total_findings == 0, return Score(value=0.0, explanation="No findings produced — parse failure or empty output").' Add a test: provide empty string as reviewer output, confirm scorer returns Score(0.0) not an exception.

### Finding 5: Haiku judge context limit not tested for large reviewer outputs
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Scoring Strategy (ADR-007) — Tier 1: reverse_judge_precision
- **Issue:** The design specifies 'pass full document to judge — do not truncate. Haiku has 200K context.' This is correct for the document, but the judge also receives each finding as input. A prolific reviewer that produces 30 findings with long issue/suggestion text could produce a judge prompt that approaches 200K tokens when the full document (potentially long design/requirements) is included per-finding. The design does not bound reviewer output length or document length.
- **Why it matters:** At scale (large documents, verbose reviewers), per-finding judge calls could approach or exceed context limits. Haiku context overflow would silently truncate the document, reintroducing the precision degradation (0.22 vs 1.00) the design specifically fixed.
- **Suggestion:** Add a guard: log the estimated token count per judge call (document tokens + finding tokens). If any judge call exceeds 150K tokens, emit a warning and record it in eval metadata. This does not require truncation — just visibility before it becomes a problem.

### Finding 6: Phase 2 prerequisite ordering is ambiguous — scorer and curation can conflict
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Phase 2 Design Prerequisites (not in Phase 1)
- **Issue:** Phase 2 prerequisites list: (1) non-zero Phase 1 precision, (2) must_find.jsonl curated, (3) context_dependent_findings.jsonl populated, (4) full implementation of both scorers. These prerequisites have an implicit ordering constraint: must_find.jsonl must be curated before the must_find_recall scorer is tested against it, and the reverse_judge_precision scorer must be implemented before curation can be validated (prerequisite 1 depends on scorer existing). The document presents these as a flat list, not a sequenced dependency graph.
- **Why it matters:** A developer who attempts prerequisites 2 and 3 before prerequisite 4 produces datasets with no automated validation. Curation errors go undetected until Phase 2 is fully implemented. The implementation order matters for catching mistakes early.
- **Suggestion:** Sequence the prerequisites explicitly: (1) Implement prototype reverse_judge_precision scorer → (2) Curate must_find.jsonl using zero-shot validation → (3) Run prototype scorer against curated list to confirm non-zero recall → (4) Implement production scorers replacing prototype.

## Blind Spot Check
I focused on failure modes at runtime and during curation. I may have underweighted: (1) failure modes in the synthesized score reporting — what does the Inspect AI evaluation log show when both scorers run and one produces null? (2) the interaction between the Phase 1 parse-error gate and Phase 2 scorers — if Phase 1 is not complete, Phase 2 scorers will be running on potentially malformed input. (3) multi-document reviewer runs where different documents produce wildly different finding counts — the precision mean across documents may hide per-document distribution problems.
