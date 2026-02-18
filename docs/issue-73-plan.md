# Issue #73 — Judge Calibration Gate: Implementation Plan

Generated: 2026-02-18, based on first precision/recall baseline from feat/confidence-eval.

## Revised Scope: Judge May Be Too Strict, Not Too Lenient

Original issue assumed the risk was leniency (judge says GENUINE to everything). First baseline
shows the opposite: precision is 7–28%, meaning the judge calls 72–93% of findings NOT_GENUINE.

Reading the judge reasoning shows the NOT_GENUINE calls are largely correct — reviewers ARE
producing hallucinated constraints, hypothetical concerns, and meta-reflections that deserve
NOT_GENUINE. But some verdicts are arguable, and calibration inversion for assumption-hunter and
constraint-finder raises the question of systematic over-strictness.

**The calibration gate must test both directions:**
1. Known NOT_GENUINE (judge should reject) — catches leniency
2. Known GENUINE (judge should accept) — catches over-strictness

## Calibration Set Design

### Partition A: 6 known NOT_GENUINE (hand-crafted, one per FP category)

Each crafted against the v2 frozen document, unambiguously in one FP category.

| Category | Description |
|---|---|
| implementation_detail | No CI/CD pipeline specification for running eval suite |
| hallucinated_constraint | References Docker containerization requirement in "Section 4.2" (no such section) |
| style_preference | Phase names should use lowercase-hyphenated format instead of "Phase 1", "Phase 1.5" |
| hypothetical_future | If reviewer count grows beyond 20, eval cost scaling will exceed budget |
| duplicate | Rephrase an existing real_flaw from a different angle without new information |
| context_dependent | Phase 1 exit criteria conflict with "the original v1 thresholds from January session" (requires MEMORY.md knowledge) |

### Partition B: 6 known GENUINE (from v2 critical_findings.jsonl real_flaws)

Copy the 6 `real_flaw` entries from `datasets/inspect-ai-integration-requirements-v2/critical_findings.jsonl`,
add `"expected_verdict": "GENUINE"`. Self-contained — no cross-file references. These are manually
validated real flaws; the judge should accept them.

**Total: 12 calibration examples against v2 frozen document.**

## Acceptance Thresholds

- **Specificity** (true negative rate, Partition A): ≥ 5/6 (83%). One miss tolerable — "duplicate"
  and "context_dependent" categories have inherent ambiguity. Below 5/6 = judge too lenient,
  precision metric is inflated.

- **Sensitivity** (true positive rate, Partition B): ≥ 5/6 (83%). One miss tolerable. Below 5/6 =
  judge too strict, precision metric is deflated. This is the new concern.

**Both thresholds must pass.** MVP: informational, not blocking `make reviewer-eval`. Phase 2: hard gate.

## Files

### New

| File | Purpose |
|---|---|
| `datasets/calibration/false_positive_examples.jsonl` | 6 hand-crafted NOT_GENUINE findings, one per FP category |
| `datasets/calibration/genuine_examples.jsonl` | 6 real_flaw entries from v2 dataset with `expected_verdict: GENUINE` |
| `datasets/calibration/metadata.json` | design_doc_path → v2 frozen doc, thresholds, version |
| `evals/judge_calibration_eval.py` | Standalone Python script (not Inspect AI task — see below) |
| `tests/evals/test_judge_calibration.py` | Unit tests with mocked judge |

### Modified

| File | Change |
|---|---|
| `Makefile` | Add `calibrate-judge` target: `.venv-evals/bin/python evals/judge_calibration_eval.py` |

### Not modified

`evals/reviewer_eval.py` — calibration is informational at MVP, not blocking reviewer eval.

## Implementation: Standalone Script, Not Inspect AI Task

Inspect AI tasks assume `generate()` produces model output, then scorers evaluate it. Calibration
has no generation step — we're testing the scorer's internal judge, not a reviewer agent.
A standalone script calls `_reverse_judge_one` directly and prints category-level pass/fail.

This is simpler, faster to build, and easier to run. If Inspect AI integration is later wanted,
wrap the script results.

## Ordering: #73 Before #79

#79 (autoevals Factuality) compares a second scorer against `reverse_judge_precision` to measure
agreement/disagreement. If the judge itself isn't calibrated, ensembling two uncalibrated signals
is meaningless.

**#73 unblocks:**
- **#79 directly** — trust the judge before comparing it to alternatives
- **Judge prompt iteration** — calibration set becomes the regression test if sensitivity fails
- **Confidence stratification interpretation** — "high-conf precision = 0.000" for assumption-hunter
  may be a judge error, not genuine calibration inversion. Can't tell until judge is calibrated.
- **Ground truth expansion** — if judge passes calibration, 7–28% precision is real (reviewers
  hallucinate that much), and effort shifts to reviewer prompt improvement

## Risks

**Small calibration set (N=12):** One wrong judgment shifts specificity/sensitivity by 17pp. Low
statistical power for subtle drift. Acceptable for MVP — the machinery is what matters; set grows
over time.

**FP examples too easy:** If hand-crafted examples are obviously absurd, gate passes but doesn't
prove borderline handling. Mitigation: model on the `datasets/quality_failures/` examples — those
are real-world FP patterns.
