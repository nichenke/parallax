# G-Eval Chain-of-Thought Experiment — Issue #75

**Date:** 2026-02-17
**Status:** Complete — decision: REJECT G-Eval for Haiku judge
**ADR:** See ADR-008 update

## Setup

Compared two judge prompt strategies on 12 labeled findings from the eval datasets:

| Label | Source | Count |
|-------|--------|-------|
| GENUINE | `must_find.jsonl` (both datasets, deduplicated) | 8 |
| NOT_GENUINE | `context_dependent_findings.jsonl` (both datasets, deduplicated) | 4 |

**Model:** `anthropic/claude-haiku-4-5-20251001` (T=0)

### Direct prompt (baseline)
- Verdict-first: `GENUINE or NOT_GENUINE` on first line + one sentence reasoning
- `max_tokens=150`

### G-Eval prompt (chain-of-thought)
- 4-step reasoning rubric before verdict:
  1. Evidence: find/quote relevant document text
  2. Flaw type: design gap vs. implementation/style detail
  3. Constraint check: hallucinated constraints?
  4. Context independence: can this be evaluated from doc alone?
- Verdict at end: `Verdict: GENUINE` or `Verdict: NOT_GENUINE`
- `max_tokens=1000`

## Results

| Metric | Direct | G-Eval |
|--------|--------|--------|
| Accuracy | 66.7% (8/12) | 58.3% (7/12) |
| False positives | 0 | 2 |
| False negatives | 4 | 3 |
| FP rate (FP / actual NOT_GENUINE) | 0.0% | 50.0% |
| FN rate (FN / actual GENUINE) | 50.0% | 37.5% |
| Avg latency/finding | 3.9s | 47.3s |
| max_tokens | 150 | 1000 |

## Per-Finding Analysis

### Cases G-Eval fixed (direct wrong, G-Eval correct)
- `problem-framer-008` (MVP solves measurement not validation) → G-Eval: GENUINE ✓
- `scope-guardian-013` (confidence undefined) → G-Eval: GENUINE ✓

### Cases G-Eval broke (direct correct, G-Eval wrong)
- `problem-framer-001` (problem statement unchanged) → G-Eval: GENUINE ✗ (context-dependent, references v1)
- `success-validator-002` (v1 thresholds not superseded) → G-Eval: GENUINE ✗ (context-dependent, references v1)
- `assumption-hunter-013` (confidence threshold undefined) → G-Eval correctly notes only 2 occurrences found vs claimed 5 → NOT_GENUINE (ground truth may be wrong here)

### Consistent errors (both wrong)
- `constraint-finder-009` (circular validation) — judge finds FR0 breaks circularity
- `constraint-finder-002` (API key security undefined) — judge finds NFR1.2 covers it
- `constraint-finder-009` — plausible counterargument; ground truth may be stale

## Issues Discovered

### Parser bug (fixed)
G-Eval model outputs markdown-formatted verdict lines (`**Verdict: GENUINE**`, `## Verdict: NOT_GENUINE`)
instead of plain text. Original `startswith("VERDICT:")` parser failed to match.

**Fix:** Regex search across full output: `re.finditer(r"verdict:\s*(not_genuine|genuine)", reasoning, re.IGNORECASE)`. Parser now handles all markdown variants.

### Flaky integration test (pre-existing)
`assumption-hunter-001` was failing intermittently (T=1 variance in API calls). Fixed by using full
PYTHONPATH — was resolving to stale main worktree module. All 83 tests pass after fix.

## Answers to Issue #75 Questions

**1. Does G-Eval materially improve Haiku's NO rate on known false positives?**
No — it made the false positive rate *worse* (0% → 50%). G-Eval's step-by-step reasoning
evaluates context-dependent findings as plausible without catching the "requires v1 context" issue.

**2. What's the prompt structure?**
4-step rubric (Evidence → Flaw type → Constraint check → Context independence) then explicit verdict line.
Works correctly when parsed with regex. Verdict appears in markdown-formatted bold/header.

**3. Does it increase token cost?**
Yes, ~7x (max_tokens 150 → 1000). At scale: 12 findings × 1000 tokens = 12k output tokens per sample,
vs 12 × 150 = 1.8k. Cost multiplier depends on hit rate but expect 4-6x for output tokens.

**4. Does it slow down parallel judge calls?**
Yes, ~12x (47s vs 4s per finding at T=0). Even with full parallelism, latency impact is significant.

## ADR Decision

**Reject G-Eval for Haiku judge.**

Trade-off is unfavorable: FN reduction (50% → 37.5%) offset by FP introduction (0% → 50%),
12x latency, 7x token cost, no overall accuracy improvement.

**Root cause:** Haiku is not capable enough for reliable 4-step reasoning on nuanced design review findings.
The chain-of-thought gives it more opportunity to rationalize — it finds textual evidence that looks
supportive but misses context-dependence, then commits to GENUINE.

**Future option:** G-Eval with Sonnet judge. A more capable model may handle the 4-step reasoning
correctly. Experiment deferred until judge calibration is identified as a blocking problem.

## Artifacts

- Experiment script: `experiments/geval_comparison.py`
- Detail script: `experiments/geval_detail.py`
- Code: `scorers/reverse_judge_scorer.py` — `_geval_judge_one()` + `prompt_style` param preserved
  for future experimentation; default remains `"direct"`.
