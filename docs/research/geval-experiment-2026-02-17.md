# G-Eval Chain-of-Thought Experiment — Issue #75

**Date:** 2026-02-17
**Updated:** 2026-02-18 (ground truth cleanup run)
**Status:** Complete — decision: REJECT G-Eval for Haiku judge
**ADR:** See ADR-008 update

## Setup

Compared two judge prompt strategies on labeled findings from both eval datasets.

**Final corpus (after ground truth cleanup):** 13 labeled findings

| Label | Source | Count |
|-------|--------|-------|
| GENUINE | `must_find.jsonl` (both datasets, deduplicated) | 7 |
| NOT_GENUINE | `context_dependent_findings.jsonl` (both datasets, deduplicated) | 6 |

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

### Final run (clean ground truth, N=13)

| Metric | Direct | G-Eval |
|--------|--------|--------|
| Accuracy | 84.6% (11/13) | 69.2% (9/13) |
| False positives | 0 | 2 |
| False negatives | 2 | 2 |
| FP rate (FP / actual NOT_GENUINE) | 0.0% | 33.3% |
| FN rate (FN / actual GENUINE) | 28.6% | 28.6% |
| Avg latency/finding | 5.0s | 50.3s |
| max_tokens | 150 | 1000 |

### Initial run (stale ground truth, N=12) — for reference

| Metric | Direct | G-Eval |
|--------|--------|--------|
| Accuracy | 66.7% (8/12) | 58.3% (7/12) |
| FP rate | 0.0% | 50.0% |
| FN rate | 50.0% | 37.5% |
| Avg latency/finding | 3.9s | 47.3s |

The initial run included 4 ground truth entries that were incorrect or stale (see Ground Truth Cleanup below). After removing them the corpus shrank from 12 to 13 (2 removed, 3 added from the fixed ID collision). The clean-corpus run is the authoritative result.

## Per-Finding Analysis (final run)

### Cases G-Eval fixed (direct wrong, G-Eval correct)
- `scope-guardian-013` (confidence undefined) → G-Eval: GENUINE ✓

### Cases G-Eval broke (direct correct, G-Eval wrong)
- `problem-framer-006` (v2 has no success criteria) → G-Eval: GENUINE ✗ (context-dependent, requires v1 knowledge)
- `problem-framer-001` (problem statement unchanged) → G-Eval: GENUINE ✗ (context-dependent, requires v1 knowledge)
- `success-validator-002` (ablation baseline undefined — X% never defined) → G-Eval: NOT_GENUINE ✗

### Consistent errors (both wrong)
- `problem-framer-008` (MVP solves measurement not validation) — judge finds FR0 + SC#4 address it. Plausible counterargument; this is a hard finding.
- `scope-guardian-013` — only G-Eval gets this right; direct misses it.

## Ground Truth Cleanup

The adversarial Opus review of the initial run identified 4 must_find entries that were incorrect or stale. Cleanup performed before final run:

| Entry | Action | Reason |
|-------|--------|--------|
| `constraint-finder-009` (circular validation) | Moved to `context_dependent_findings` | FR0 was added to document specifically to break the circularity; judge correctly sees FR0. Finding was valid pre-FR0 but not retired. |
| `constraint-finder-002` (API key security undefined) | Moved to `context_dependent_findings` | NFR1.2 explicitly specifies the credential model; judge correctly sees it as addressed. Enforcement mechanism is design-realm, not requirements-realm. |
| `assumption-hunter-013` (confidence undefined) | Fixed in-place | Claimed "5 places" but only FR2.1 and FR3.3 actually use the threshold. Corrected to accurate locations. |
| `success-validator-002` (v2 context_dependent) | Renamed to `success-validator-003` | ID collision with the must_find entry of the same ID from the v2 dataset. Dedup-by-first-seen silently dropped the GENUINE entry. |

## Issues Discovered

### Parser bug (fixed)
G-Eval model outputs markdown-formatted verdict lines (`**Verdict: GENUINE**`, `## Verdict: NOT_GENUINE`)
instead of plain text. Original `startswith("VERDICT:")` parser failed to match.

**Fix:** Regex search across full output: `re.finditer(r"verdict:\s*(not_genuine|genuine)", reasoning, re.IGNORECASE)`. Parser now handles all markdown variants.

### Flaky integration test (pre-existing, fixed)
`assumption-hunter-001` was failing intermittently (T=1 variance in API calls). Root cause: PYTHONPATH
resolved to stale main worktree module when running from main repo. Fixed by always using full
`PYTHONPATH=<worktree>` prefix. All 83 tests pass after fix.

## Answers to Issue #75 Questions

**1. Does G-Eval materially improve Haiku's NO rate on known false positives?**
No — it made FP rate *worse* (0% → 33.3% on clean corpus). G-Eval's step-by-step reasoning
evaluates context-dependent findings as plausible without catching the "requires v1 context" issue.

**2. What's the prompt structure?**
4-step rubric (Evidence → Flaw type → Constraint check → Context independence) then explicit verdict line.
Works correctly when parsed with regex. Verdict appears in markdown-formatted bold/header.

**3. Does it increase token cost?**
Yes, ~7x (max_tokens 150 → 1000). At scale: 13 findings × 1000 tokens = 13k output tokens per sample,
vs 13 × 150 = 2k. Expect 4-6x actual output token multiplier depending on hit rate.

**4. Does it slow down parallel judge calls?**
Yes, ~10x (50s vs 5s per finding at T=0). Even with full parallelism, latency impact is significant.

## ADR Decision

**Reject G-Eval for Haiku judge.**

On clean ground truth: G-Eval achieves identical FN rate (28.6%) to direct but introduces false positives
(FP rate 0% → 33.3%), at 10x latency and ~7x token cost. Net accuracy: 84.6% (direct) vs 69.2% (G-Eval).

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
