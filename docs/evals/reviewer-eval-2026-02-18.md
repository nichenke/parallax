# Reviewer Eval Results — 2026-02-18

**Git hash:** 3a12077
**Branch:** feat/confidence-eval
**Goal:** First full precision+recall measurement after confidence self-scoring (#72)

## Summary

First ever live eval run with `reverse_judge_precision` + `must_find_recall` scored against
fresh reviewer output. No prior baseline exists for comparison.

Confidence field is emitted consistently on all findings. Schema validation passes.
Confidence calibration is partially inverted (see below).

## Scores

| Reviewer | dataset | precision | recall | findings | must_find |
|---|---|---|---|---|---|
| assumption-hunter | v2 | 0.077 (1/13) | 0.667 (2/3) | 13 | 3 |
| constraint-finder | light | 0.077 (1/13) | 0.000 (0/5) | 13 | 5 |
| problem-framer | v2 | 0.286 (2/7) | 0.000 (0/3) | 7 | 3 |
| scope-guardian | v2 | 0.111 (1/9) | 0.667 (2/3) | 9 | 3 |
| success-validator | v2 | 0.200 (2/10) | 0.667 (2/3) | 10 | 3 |

## Confidence Calibration

High-confidence band = confidence ≥ 80. Expected: high-conf precision > low-conf precision.

| Reviewer | high-conf precision | low-conf precision | direction |
|---|---|---|---|
| assumption-hunter | 0.000 (0/5) | 0.125 (1/8) | **INVERTED** |
| constraint-finder | 0.000 (0/6) | 0.143 (1/7) | **INVERTED** |
| problem-framer | 0.667 (2/3) | 0.000 (0/4) | correct |
| scope-guardian | 0.250 (1/4) | 0.000 (0/5) | correct |
| success-validator | 0.500 (2/4) | 0.000 (0/6) | correct |

Assumption-hunter and constraint-finder are most confident about their hallucinations.
The three requirements-focused reviewers (problem-framer, scope-guardian, success-validator)
show correct direction: high confidence correlates with genuineness.

## Precision Interpretation

The judge (Haiku) is calling most findings NOT_GENUINE because reviewers raise concerns that
the document already explicitly addresses. Example: assumption-hunter flags single-turn context
as an unaddressed assumption, but FR-ARCH-2 specifies exactly this as a requirement.

Three possible explanations (unresolved, see Issues #73 and #79):
1. **Judge is too strict** — Haiku misapplies the false-positive criteria, calling genuine
   findings NOT_GENUINE. Precision is artificially depressed.
2. **Reviewers are hallucinating** — Reviewers are confidently producing findings about
   issues the document actually addresses. Precision is correctly low.
3. **Both** — Partial truth in each direction, blended effect.

Resolution requires:
- #73: calibration gate — do we trust the judge before trusting precision?
- #79: Factuality cross-check — independent signal to validate/refute judge verdicts

## Recall Interpretation

- **constraint-finder 0/5**: The 5 must_find entries in the light dataset are all tagged to
  other reviewers (scope-guardian, assumption-hunter, success-validator). Constraint-finder
  is legitimately out of domain for most of them.
- **problem-framer 0/3**: The v2 must_find entries are specific eval-framework flaws.
  Problem-framer's fresh output finds different problem-framing issues (valid but not
  matching the specific expected entries). Possible must_find staleness.
- **All others 2/3**: Consistently missing "Assumes agent files are already eval-compatible
  without modification." May be a document-updated-since finding.

## Confidence Field Validation

All 5 reviewers emit `confidence` on every finding including blind_spot_check (always 50).
Schema validation passes. Confidence values observed: 50–95, anchored per rubric (0/25/50/75/100)
but reviewers interpolate freely.

## Open Questions for #73 / #79

1. Is 7–28% precision genuinely low, or is the judge calling correct findings NOT_GENUINE?
2. Why is calibration inverted for assumption-hunter and constraint-finder specifically?
   These two reviewers generate findings about assumptions/constraints — areas where the
   v2 document may be more explicit than older versions they were trained on.
3. Would autoevals Factuality agree with Haiku on the NOT_GENUINE calls?
