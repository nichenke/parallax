# Requirements Review Summary — Inspect AI Integration (Light Mode)

**Review Date:** 2026-02-16 (re-review)
**Design Document:** `docs/requirements/inspect-ai-integration-requirements-v1.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator
**Note:** Previous review at Session 18 (79 findings). This re-review covers requirements-v1.md as currently published.

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 4 | 5 | 3 | 12 |
| scope-guardian | 3 | 5 | 3 | 11 |
| constraint-finder | 4 | 6 | 6 | 16 |
| assumption-hunter | 3 | 7 | 3 | 13 |
| success-validator | 3 | 8 | 4 | 15 |
| **Total** | **17** | **31** | **19** | **67** |

---

## Key Themes

**The highest-consensus finding (4/5 reviewers independently):** Ground truth quality is unverified. FR0 describes a process checklist — expert examined, metadata present — but never specifies how to verify the resulting ground truth is *high quality*. An eval framework measuring against false-positive-contaminated ground truth produces meaningless detection rates. Every downstream metric (baseline, regression threshold, ablation pass/fail) inherits that corruption.

**The second systemic pattern:** Measurements without definitions. Four thresholds appear as specific numbers with no empirical basis, no definition of how they're measured, and no calibration step: the 95% confidence gate (FR3.3, appears 5 times), the 80% fuzzy match threshold, the >50% ablation drop (FR4.1), the 10% regression threshold (FR6.2). These look like acceptance criteria but cannot be implemented or tested.

**The third pattern:** Deferred-but-specified anti-pattern, three times. FR7.1, FR8.1, and FR9.1 each contain full acceptance criteria immediately contradicted by FR7.2, FR8.2, and FR9.2 which defer the feature entirely. Documents that support both "build it" and "skip it" interpretations cause predictable wasted work.

---

## Problem Framing

The Problem Statement opens with solution context (Inspect AI integration decision) rather than the problem. The document conflates two distinct problems with different timelines and failure modes: (1) ground truth creation — a human judgment workflow, and (2) skill measurement — an engineering problem. The circular validation dependency is correctly identified but dismissed in one line. The actual consequence — that Phase 1 eval will measure consistency against LLM output, not accuracy against verified flaws — is never stated.

Jobs 4 (cost optimization) and 5 (multi-model portability) are presented as "five validated needs" but are anticipated future concerns with no evidence of current pain. The MVP proves integration works, not that skills catch real flaws — the finding quality scorer required to answer the core question is deferred to Phase 2.

## Scope & Boundaries

Three deferred requirements (FR7, FR8, FR9) have complete acceptance criteria written for features that are immediately deferred. FR5.1 (planted flaw detection) appears in Phase 1 scope with full acceptance criteria but requires weeks of synthetic design doc authoring work that doesn't appear in any phase. The Flask validation UI is in the design doc as Phase 1 work but absent from requirements — Phase 0 depends on it as an enabling tool with no documented fallback.

The Open Questions section has four questions that directly gate acceptance criteria in FR2.2, FR4.1, FR4.2, and FR6.2. None have a resolution owner, method, or phase assignment. Phase timelines in the MVP scope section violate the project convention (CLAUDE.md: never include time estimates).

## Constraints & Feasibility

Python environment constraints are absent from requirements. Two cost targets exist in the same document without reconciliation ($0.50 in NFR1.2 vs $2.00 in Success Criteria #7). The NFR numbering scheme has a collision: NFR1.1 and NFR1.2 appear in both API Key Security and Cost Tracking sections, making cross-references ambiguous. API key security policy states intent ("keys never in VCS") but provides no enforcement mechanism.

The Inspect AI version is unbounded above (`>=0.3`), meaning two developers running `make setup` a week apart may get incompatible API versions silently. Ablation tests have a circular dependency: ground truth used to establish baseline that ablation tests then validate against.

## Assumptions

The manual validation UI (Flask tool from design doc) is assumed to exist as a prerequisite for Phase 0 but is out of scope. The 95% confidence threshold for auto-adding ground truth findings appears 5 times across the document but is never defined — who calculates it, against what scale, using what method. The 15-finding minimum has no statistical grounding relative to the 10% regression threshold (at N=15, binomial variance spans ±25%, wider than the threshold itself). The ablation test assumes base model detection capability is near zero — if Sonnet detects 40% of flaws via general reasoning, the ablation test validates presence but not skill quality.

## Success Criteria

FR2.1 (severity calibration scorer) has no defined pass/fail rule — thresholds are listed but the logic producing pass vs fail is absent. Success Criteria #5 conflicts with FR4.2: both use "contributes X% to detection rate" but measure different things (whole-skill vs per-section ablation). The regression threshold in FR6.2 doesn't specify absolute vs relative drop, and doesn't define the behavioral response (block merge? warn? log?). FR0 acceptance criteria are a process checklist with no quality floor.

---

## Critical Findings (17 Total)

### Problem Framing (4 Critical)

1. **[problem-framer-004] Core challenge framed as footnote, not gating constraint**
   - Issue: Circular validation dependency acknowledged in one sentence then dismissed. It gates all other requirements — the document never states this.
   - Suggestion: Add explicit gate: FR0 must complete before FR1–FR6 are meaningful. Phase 1 code running against unvalidated ground truth produces misleading metrics.

2. **[problem-framer-005] Document conflates two distinct problems**
   - Issue: Ground truth creation (human judgment problem) and skill measurement (engineering problem) treated as one, with the prerequisite relationship buried in MVP Scope Summary.
   - Suggestion: Split into two problem statements with explicit prerequisite relationship stated up front.

3. **[problem-framer-006] Eval measures consistency, not accuracy**
   - Issue: Using unvalidated v3 findings makes the framework measure "do new skills match old outputs?" not "do skills catch real flaws?" A prompt change that improves accuracy but shifts phrasing registers as a regression.
   - Suggestion: State this explicitly in Problem Statement. FR0 is a prerequisite, not a phase.

4. **[problem-framer-008] MVP proves integration works, not that skills catch real flaws**
   - Issue: Phase 1 success criteria validate Inspect AI runs and produces a number — not that the number means anything. Finding quality scorer deferred to Phase 2.
   - Suggestion: Add Phase 1 success criterion: "Baseline detection rate measured against ≥15 human-validated findings (not unvalidated LLM outputs)."

### Scope (3 Critical)

5. **[scope-guardian-001] FR5.1 planted flaw detection is Phase 1 with no authoring plan**
   - Issue: Planted flaw test datasets require days/weeks of synthetic design doc authoring. This work appears in no phase, no timeline, no scope statement.
   - Suggestion: Move FR5.1 to Phase 2 explicitly, or scope the authoring work and add it to Phase 1.

6. **[scope-guardian-002] FR7.1 and FR7.2 contradict each other**
   - Issue: FR7.1 has 4 complete acceptance criteria. FR7.2 immediately defers the feature. Both are present.
   - Suggestion: Remove FR7.1 acceptance criteria. Keep only the deferral rationale in FR7.2.

7. **[scope-guardian-003] FR8 and FR9 repeat the deferred-but-specified pattern**
   - Issue: FR8.1 and FR9.1 have full acceptance criteria; FR8.2 and FR9.2 immediately defer them. Same problem as FR7, appearing twice more.
   - Suggestion: Rule: deferred requirements get one sentence (rationale + post-MVP scope), no acceptance criteria.

### Constraints (4 Critical)

8. **[constraint-finder-001] Python environment constraints absent**
   - Issue: No Python version, no dependency manager, no virtual environment specification. Inspect AI requires Python 3.10+, may conflict with existing dependencies.
   - Suggestion: Add NFR: "Python ≥3.11, managed via pyproject.toml with uv/pip, virtual environment required."

9. **[constraint-finder-002] API key security policy has no enforcement mechanism**
   - Issue: "Keys never in VCS" stated but no mechanism (pre-commit scan, `.env` in `.gitignore`, CI check) is required.
   - Suggestion: Add acceptance criterion: pre-commit hook scans for `ANTHROPIC_API_KEY=` patterns. Failing commit blocks with actionable error.

10. **[constraint-finder-003] Dual cost targets contradict each other**
    - Issue: NFR1.2 says <$0.50. Success Criteria #7 says <$2.00. Both are current text, no reconciliation.
    - Suggestion: Remove NFR1.2 and standardize on <$2.00 as the MVP target, noting this is pre-prompt-caching.

11. **[constraint-finder-009] Ablation test has circular dependency**
    - Issue: FR6.1 establishes baseline from first eval run. FR4.1 validates ablation against that baseline. Ground truth established before validation — allows false positives to contaminate baseline.
    - Suggestion: Enforce ground truth gate before FR6.1 baseline can be stored. `make baseline` exits if `critical_findings.jsonl` is empty.

### Assumptions (3 Critical)

12. **[assumption-hunter-001] Ground truth validity assumed without enforcement**
    - Issue: Phase 1 can proceed against unvalidated ground truth. The enforced gate is missing in requirements.
    - Suggestion: `make eval` exits non-zero if `critical_findings.jsonl` is empty. No Phase 1 code merged until ground truth exists.

13. **[assumption-hunter-003] Model output format assumed parseable JSONL**
    - Issue: Entire scoring mechanism depends on `parse_review_output()` succeeding. LLM may return Markdown prose, incomplete JSON, or unexpected field names. Parser failure looks identical to skill failure.
    - Suggestion: Add acceptance criterion: eval task validates output is parseable before scoring. Parser failures logged as eval errors, not scored as 0%.

14. **[assumption-hunter-013] 95% confidence threshold unmeasurable as specified**
    - Issue: FR3.3 gates auto-add on ≥95% confidence but never defines who calculates it, against what scale, using what method. Appears 5 times in the document. Cannot be implemented.
    - Suggestion: Replace with binary classification: `confirmed` vs `needs_review`. All `needs_review` requires explicit user approval. Remove the numeric threshold.

### Success Criteria (3 Critical)

15. **[success-validator-001] FR2.1 scorer has no pass/fail rule**
    - Issue: Distribution thresholds listed (Critical <30%, Important 40-50%, Minor 20-30%) but the logic producing pass vs fail is absent. A developer cannot implement this without inventing the rule.
    - Suggestion: Add: "Scorer returns FAIL if Critical% exceeds 30% OR Important% outside 40-50% OR Minor% outside 20-30%."

16. **[success-validator-002] FR4.1 ablation formula parameterized on unknown**
    - Issue: "detection drops to <(X - 50)%" where X is established at runtime by FR6.1. Boundary cases (X=75%? X=95%?) unspecified. Two developers produce different pass/fail on the same data.
    - Suggestion: Specify formula completely: "If baseline ≥90%: ablation must drop to <40%. If baseline 80-89%: drop to <30%. If baseline <80%: Phase 1 incomplete (must reach ≥90% before ablation)."

17. **[success-validator-003] Success Criteria #5 conflicts with FR4.2**
    - Issue: SC #5 measures whole-skill ablation. FR4.2 measures per-section ablation. Both use "contributes X% to detection rate" but measure different things.
    - Suggestion: Separate: SC #5 = whole-skill ablation (drop all → <40%), FR4.2 = per-section (each section drops >15% when removed). Align units.

---

## Important Findings (Selected)

1. **[assumption-hunter-006] 15-finding minimum has no statistical grounding** — At N=15, binomial variance is ±25% at 95% confidence, wider than the 10% regression threshold. Regression detection will fire on statistical noise.

2. **[assumption-hunter-007] Ablation doesn't measure base model capability** — If Sonnet detects 40% of flaws via general reasoning, a 90%→40% drop "passes" but the skill only adds 50 points over a 40-point base. Add zero-skill baseline to FR4.

3. **[assumption-hunter-011] Manual validation UI assumed available** — Phase 0 depends on Flask validation tool which is out of scope. Document a manual fallback (direct JSONL editing with `validation_status` field).

4. **[assumption-hunter-012] Single sample per eval run hides per-finding stability** — One design doc = one Sample = one aggregate recall number. Convert each finding to its own Sample for N=15 independent measurements, per-finding diagnostics.

5. **[scope-guardian-007] Open Questions 1-4 gate acceptance criteria with no resolution plan** — Questions directly affect FR4.1, FR6.2, FR2.2 thresholds. Need resolution owner and phase assignment.

6. **[constraint-finder-008] NFR numbering collision** — NFR1.1 and NFR1.2 appear in both API Key Security and Cost Tracking sections. Cross-references to NFR IDs are ambiguous.

7. **[constraint-finder-005] Inspect AI version unpinned** — `inspect-ai>=0.3` with no upper bound. Two developers running `make setup` a week apart may get incompatible versions.

8. **[success-validator-005] Dual cost targets** — NFR1.2 says $0.50, SC #7 says $2.00. (See constraint-finder-003 above — resolve by removing NFR1.2.)

9. **[success-validator-008] FR6.2 regression threshold ambiguous** — Absolute vs relative drop unspecified. Behavioral response (block/warn/log) undefined.

10. **[success-validator-011] FR5.1 70% detection target cites wrong source** — Cites parallax-review-requirements-v1.md FR1.2 as justification, but that source is a diversity metric, not a detection rate. Threshold has no valid empirical basis.

---

## Next Steps

1. **Address Critical findings** — The highest-priority cluster to fix before implementation:
   - Remove acceptance criteria from FR7.1, FR8.1, FR9.1 (scope-guardian-002/003) — quick edit
   - Reconcile dual cost targets, remove $0.50 from NFR1.2 (constraint-finder-003)
   - Fix NFR numbering collision (constraint-finder-008) — unblocks cross-references
   - Add FR2.1 pass/fail rule (success-validator-001)
   - Replace 95% confidence threshold with `confirmed`/`needs_review` binary (assumption-hunter-013)
   - Add output parseability acceptance criterion (assumption-hunter-003)
   - Specify ablation formula boundary cases (success-validator-002)
   - Resolve SC #5 / FR4.2 conflict (success-validator-003)

2. **Address Important findings** — Especially:
   - Statistical grounding for N=15 threshold (assumption-hunter-006)
   - Base model capability measurement in ablation (assumption-hunter-007)
   - Open Questions resolution plan (scope-guardian-007)
   - Per-finding Sample structure (assumption-hunter-012)

3. **Minor findings** — Defer most; cosmetic and low-risk.

4. **Re-run after major changes** — If the ground truth gate, measurement definitions, and scope contradictions are all addressed, re-run to verify no new issues introduced.
