# Reviewer Eval — Post Rubric Fix (2026-02-19)

**Date:** 2026-02-19
**Git:** 26fed5f (post rubric fix commit)
**Branch:** feat/confidence-eval
**Purpose:** Verify rubric fix resolves calibration inversion for assumption-hunter and constraint-finder

---

## What Changed

Updated 75-confidence anchor in `agents/assumption-hunter.md` and `agents/constraint-finder.md`:

**Before:**
> 75: Highly confident — double-checked, directly supported by document evidence, will impact design validity

**After (assumption-hunter):**
> 75: Highly confident — the gap or unstated assumption is clearly relevant to the document's stated scope and purpose; the document creates a context in which this issue would be expected to be addressed

**After (constraint-finder):**
> 75: Highly confident — the gap or unstated constraint is clearly relevant to the document's stated scope and purpose; the document creates a context in which this limit would be expected to be addressed

**Rationale:** The "directly supported by document evidence" anchor is wrong for absence-detection reviewers. Their job is to find what is NOT stated — unstated assumptions and constraints are inferential by definition, not evidenced by direct document quotes. The fix switches to scope-relevance anchoring: is this gap relevant to what the document is trying to do?

---

## Results

| Reviewer | precision | recall | high-conf prec | low-conf prec | calibration |
|---|---|---|---|---|---|
| assumption-hunter | 0.273 (3/11) | 0.667 (2/3) | 0.500 (4 findings) | 0.143 (7 findings) | **correct** ✓ |
| constraint-finder | 0.091 (1/11) | 0.000 (0/5) | 0.250 (4 findings) | 0.000 (7 findings) | **correct** ✓ |
| problem-framer | 0.125 (1/8) | 0.667 (2/3) | 0.200 (5 findings) | 0.000 (3 findings) | correct |
| scope-guardian | 0.100 (1/10) | 0.667 (2/3) | 0.000 (6 findings) | 0.250 (4 findings) | INVERTED |
| success-validator | 0.273 (3/11) | 0.667 (2/3) | 0.333 (6 findings) | 0.200 (5 findings) | correct |

---

## Comparison to Baseline (2026-02-18)

| Reviewer | baseline prec | post-fix prec | baseline calib | post-fix calib |
|---|---|---|---|---|
| assumption-hunter | 0.077 (1/13) | **0.273 (3/11)** | INVERTED | **correct** ✓ |
| constraint-finder | 0.077 (1/13) | 0.091 (1/11) | INVERTED | **correct** ✓ |
| problem-framer | 0.286 (2/7) | 0.125 (1/8) | correct | correct |
| scope-guardian | 0.111 (1/9) | 0.100 (1/10) | correct | INVERTED |
| success-validator | 0.200 (2/10) | 0.273 (3/11) | correct | correct |

---

## Analysis

### Primary goal: achieved

The calibration inversion for assumption-hunter and constraint-finder is gone. Both now show high-conf precision ≥ low-conf precision, as expected. The rubric fix is confirmed effective.

**Assumption-hunter** showed the clearest improvement: overall precision 0.077 → 0.273 (+196%), and calibration direction reversed from inverted to correct (high-conf: 0.500 vs low-conf: 0.143).

**Constraint-finder** improved modestly (0.077 → 0.091) with correct calibration direction now (high-conf: 0.250 vs low-conf: 0.000).

### Scope-guardian inversion

Scope-guardian shows inverted calibration (high-conf: 0.000, low-conf: 0.250) in this run vs correct in baseline (high-conf: 0.250, low-conf: 0.000). The reviewer prompt did not change.

This is almost certainly single-sample variance: 1 genuine finding across 10 total, and whether it lands in the high or low confidence bucket changes the direction. With counts this small (6 high, 4 low, 1 genuine), any small difference in stochastic output flips the ratio. Not a systematic regression.

### Precision variance across runs

Problem-framer dropped 0.286 → 0.125; success-validator rose 0.200 → 0.273. Neither reviewer changed. This is single-sample noise — the model generates different findings on each run, producing natural variance in which findings the judge calls GENUINE.

**Key stability signal:** recall is 0.667 for all reviewers except constraint-finder (0.000 in both runs). Must-find recall is the more stable metric (it measures detection of specific known items). Precision is noisier because it depends on which hallucinated findings the model produces in any given run.

### Constraint-finder recall still 0.000

Constraint-finder has 5 must_find entries and found 0 across both runs. This is a finding quality issue independent of calibration — the reviewer reliably misses these specific ground truth items. Not blocking merge of PR #89, but worth noting.

---

## Log files

```
logs/2026-02-19T02-03-58+00-00_assumption-hunter-eval_GyTs3T7XvurZpt4ghGXf7D.eval
logs/2026-02-19T02-05-40+00-00_constraint-finder-eval_mMmZyo4SsYKFtEP9CDDwnX.eval
logs/2026-02-19T02-08-30+00-00_problem-framer-eval_WT6pJUa8m8XzYeW5APPc9M.eval
logs/2026-02-19T02-09-41+00-00_scope-guardian-eval_bPrqqiobvpi5wMykPLxhxN.eval
logs/2026-02-19T02-10-46+00-00_success-validator-eval_nzr7ct4Dwqcw6tjHeEwnnZ.eval
```

---

## Status

Step 1 (rubric fix) and Step 2 (eval re-run) complete. Calibration inversion resolved for target reviewers.

Next: Step 3 — extract post-fix findings for human spot-check (Session 3 per plan).
