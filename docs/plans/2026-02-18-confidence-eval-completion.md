# Plan: Complete #72 Confidence Eval — Full Next Steps

**Date:** 2026-02-18
**Branch:** feat/confidence-eval (PR #89)
**Worktree:** `/Users/nic/src/design-parallax/parallax/.worktrees/feat/confidence-eval`

## Context

PR #89 (feat/confidence-eval) has confidence scoring working mechanically but has two problems
blocking merge:

1. **Calibration inversion** for assumption-hunter and constraint-finder: high-confidence findings
   have 0% precision, low-confidence have 12-14%. Root cause: the 75-confidence anchor says
   "directly supported by document evidence" which doesn't fit absence-detection reviewers.

2. **Unknown judge accuracy**: precision of 7-28% could be real (reviewers hallucinate) or
   inflated strictness (judge miscalibrated). Manual spot-check of real findings is the fastest
   way to determine judge accuracy.

Additionally: #79 needs closing with corrected reasoning, #73 needs redesign.

## Sequence (sequential, not parallel)

Rubric fix first, then spot-check the post-fix findings. Reasoning:
- Rubric fix is justified regardless of judge accuracy (mechanical mismatch)
- Spot-checking post-fix findings evaluates the system we'd actually ship
- G-Eval experiment (84.6% judge accuracy) gives reasonable prior that judge is mostly right

---

### Step 1 — Fix absence-detection rubric

**Session:** Claude Code in feat/confidence-eval worktree

Files:
- `agents/assumption-hunter.md`
- `agents/constraint-finder.md`

Change the 75-confidence anchor from:
> 75: Highly confident — double-checked, directly supported by document evidence, will impact
> design validity

To something like:
> 75: Highly confident — the gap or unstated assumption is clearly relevant to the document's
> stated scope and purpose; the document creates a context in which this issue would be expected
> to be addressed

Leave the other anchors (0, 25, 50, 100) unchanged.
Leave the 3 requirements-focused reviewers unchanged (calibration direction already correct).

---

### Step 2 — Re-run eval

```bash
cd /Users/nic/src/design-parallax/parallax/.worktrees/feat/confidence-eval
make reviewer-eval
```

Check calibration direction for all 5 reviewers. Success = high-conf precision > low-conf
precision for assumption-hunter and constraint-finder. If inversion persists: deeper prompt issue.

Write results to `docs/evals/reviewer-eval-2026-02-18-post-rubric-fix.md`.
Commit rubric fix + new eval results.

---

### Step 3 — Extract post-fix findings for spot-check

Write an extraction script that reads the 5 .eval log files and outputs a markdown review doc.

Per finding:
- Finding ID, title, severity, confidence score
- Issue text (the finding's claim)
- Judge verdict (GENUINE / NOT_GENUINE)
- Judge reasoning (full text)
- Checkbox: `[ ] AGREE  [ ] DISAGREE  [ ] UNSURE`

Extraction data lives in `sample.scores['reverse_judge_precision'].metadata['judge_results']`:
```python
{"finding_id": "...", "finding_title": "...", "confidence": 90, "is_genuine": bool, "reasoning": "..."}
```

Use `inspect_ai.log.read_eval_log()` to read .eval files.

Output: `docs/evals/spot-check-post-rubric-fix.md`

**Sampling:** Review all findings (~52). At ~1 min each, ~1 hour human time.
Alternative: sample 25 (all GENUINE + stratified NOT_GENUINE). Label explicitly if sampled.

---

### Step 4 — Human spot-check

For each finding: read the claim, read the judge reasoning, check the frozen document if needed.
Mark AGREE / DISAGREE / UNSURE.

Frozen documents:
- v2: `datasets/inspect-ai-integration-requirements-v2/inspect-ai-integration-requirements-v2.md`
- light: `datasets/inspect-ai-integration-requirements-light/inspect-ai-integration-requirements-v1.md`

---

### Step 5 — Calculate judge accuracy

Count: AGREE / (AGREE + DISAGREE). Break down by:
- Overall accuracy
- Accuracy on GENUINE vs NOT_GENUINE verdicts (sensitivity vs specificity)
- Accuracy by reviewer type (absence-detection vs requirements-focused)
- Accuracy by confidence band (high ≥80 vs low <80)

Write results to `docs/evals/judge-accuracy-post-rubric-fix.md`.

**Decision point:**
- Judge accuracy ≥ 80%: judge is trustworthy → precision numbers are real → proceed to merge
- Judge accuracy < 80%: fix judge prompt → re-run eval → re-spot-check
- Accuracy diverges by reviewer type: tells us exactly where judge struggles

---

### Step 6 — Issue cleanup (can run anytime, independent)

**Close #79:**
- REJECT confirmed by adversarial review
- Correct argument: absence-detection mismatch (same root cause as RAGAS in ADR-008)
- Drop the "gpt-4o dependency" and "no natural question" arguments
- Note missed $0.50 cross-check opportunity
- ADR-008 prior art sweep now complete

**Update #73:**
- Original approach (synthetic calibration set N=12) replaced by manual spot-check
- N=12 has 42% false-pass probability — not a real validation gate
- Manual spot-check of real findings is strictly better (real data, larger N)
- Spot-check results from Step 5 ARE the calibration data
- Synthetic calibration eval may become a regression test later

---

### Step 7 — Merge gate

PR #89 can merge when ALL of:
1. Calibration inversion gone for assumption-hunter and constraint-finder (Step 2)
2. Judge accuracy ≥ 80% on spot-check (Step 5)
3. #79 closed, #73 updated (Step 6)

If all pass: merge PR #89, close #72.
If judge accuracy is low: fix judge prompt, re-run, re-spot-check. Branch stays open.

---

## Files Modified

| File | Step | Change |
|---|---|---|
| `agents/assumption-hunter.md` | 1 | 75-anchor rewording |
| `agents/constraint-finder.md` | 1 | 75-anchor rewording |
| `docs/evals/reviewer-eval-2026-02-18-post-rubric-fix.md` | 2 | Post-fix eval results (new) |
| `docs/evals/spot-check-post-rubric-fix.md` | 3 | Extraction for human review (new) |
| `docs/evals/judge-accuracy-post-rubric-fix.md` | 5 | Spot-check results (new) |

## Verification

1. After Step 2: `make reviewer-eval` completes clean, all 5 reviewers produce findings with confidence
2. After Step 2: high-conf precision > low-conf precision for ALL 5 reviewers
3. After Step 5: judge accuracy number calculated and documented
4. After merge: `git log --oneline main..feat/confidence-eval` shows clean commit history

## Parallel Session Allocation

- **Session 1:** Steps 1-2 (rubric fix + eval run)
- **Session 2:** Step 6 (issue cleanup — gh commands only, independent)
- **Session 3:** Steps 3-5 (extraction + human review + accuracy calc — after Session 1 completes)
