# Issue #72 — Completion Notes

## State right now (worktree `feat/confidence-eval`)

- 10 old `findings-v1-*.jsonl` files staged for `git rm` — not yet committed
- Schema has `confidence` **wrongly changed to optional** — needs reverting
- Nothing else in the worktree

---

## Step 1 — Revert the schema change

In the worktree, `schemas/reviewer-findings-v1.0.0.schema.json` has `confidence` missing from the `required` array. Put it back:

```json
"required": ["type", "id", "title", "severity", "confidence", "phase", "section", "issue", "why_it_matters", "suggestion"]
```

Main already has this correct. The worktree diverged. Revert `schemas/reviewer-findings-v1.0.0.schema.json` to match main, then `git add` it.

---

## Step 2 — Commit what's staged

```bash
cd /Users/nic/src/design-parallax/parallax/.worktrees/feat/confidence-eval
git add schemas/reviewer-findings-v1.0.0.schema.json
git commit -m "remove pre-confidence historic findings, keep confidence required"
```

---

## Step 3 — Run the eval

```bash
cd /Users/nic/src/design-parallax/parallax/.worktrees/feat/confidence-eval
make reviewer-eval
```

Runs all 5 reviewer tasks (assumption-hunter, constraint-finder, problem-framer, scope-guardian,
success-validator) against both datasets. Produces fresh `findings-v1-*.jsonl` files with
`confidence` on every finding.

---

## Step 4 — Read the results

Look for two things:

**a) Did recall hold?**
The `must_find_recall` score should be at or near 1.0 for each reviewer. If any must_find entry
dropped out, the synthesizer's `confidence < 80` filter may have suppressed it. That's the thing
to investigate — not a ground truth problem, a threshold problem.

**b) Did schema pass?**
If any finding is missing `confidence`, the schema validator will reject it. That means a reviewer
prompt isn't emitting the field consistently. Fix the prompt, re-run.

---

## Step 5 — Update ground truth (only if needed)

The `must_find` entries do **not** need a `confidence` field added to them. They test topic
coverage, not calibration. Leave them as-is unless:

- Recall regressed: a previously-found entry is now missed → investigate the synthesizer threshold,
  don't remove the must_find entry
- A fresh finding is obviously critical and missing from must_find → add it

---

## Step 6 — Commit results + open PR

```bash
git add docs/reviews/
git commit -m "feat: fresh confidence eval findings, validate confidence field required"
```

Push and open PR. Close #72 when merged.

---

## Follow-on: Issue #79 (Factuality scorer)

\#79 was blocked on #72 because it needs real `confidence` data to calibrate against. After #72
closes:

1. Look at the distribution of `confidence` values on must_find findings — are reviewers scoring
   obvious critical flaws at 85+, or hedging at 60?
2. That distribution is the calibration baseline for the Factuality scorer.
3. The scorer tests whether confidence correlates with genuineness — high-confidence NOT_GENUINE
   findings indicate a miscalibrated reviewer.
4. Don't design the scorer until you have the distribution data from step 1.

---

## What you don't need to do

- Don't add `confidence` to `must_find.jsonl` entries (wrong layer)
- Don't add `min_confidence` expectations anywhere (that's #79's job, and only after data)
- Don't remove must_find entries because confidence scores look low — that's a calibration signal,
  not a ground truth error
