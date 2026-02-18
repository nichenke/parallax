# ADR-007: Two-Tier Eval Scoring — Reverse Judge Precision + Must-Find Recall

**Date:** 2026-02-18
**Status:** Accepted
**Deciders:** @nichenke
**Related:** Issue #65 (eval scorer ID matching), Issue #66 (LLM-as-judge), Issue #68 (context-dependent findings), ADR-006, session 30 diagnostic

---

## Context

After merging the Phase 1 eval framework (PR #46) and frozen document snapshots (PR #64), `make reviewer-eval` showed accuracy=0.000 across all 5 reviewer tasks. Session 29 added LLM-as-judge (`llm_judge_match`) which improved problem-framer and success-validator to 0.5 recall, but 3/5 tasks remained at 0.0.

**Session 30 diagnostic** confirmed two distinct root causes:

**Root cause 1 — Context contamination:** Ground truth was captured in interactive Claude Code sessions with MEMORY.md and CLAUDE.md loaded. Some golden findings require out-of-band project context to discover (e.g., "API key security undefined" requires knowing the Bedrock vs. direct API setup from MEMORY.md). Clean eval runs — which only have the frozen document — structurally cannot find these findings. The ground truth was contaminated at capture time.

**Root cause 2 — Genuine run-to-run variance:** Even for document-visible findings, independent review sessions emphasise different angles. The model finds legitimately different-but-valid flaws each run. Cross-run matching (expected → actual) fails even when the reviewer is doing its job correctly.

**Prototype validation (session 30):**

Running `reverse_judge_precision` (ask: "is each actual finding a genuine flaw in the document?") on problem-framer-eval produced:
- `severity_calibration` (string fuzzy match): 0.000
- `llm_judge_match` (expected → actual direction): 0.000
- `reverse_judge_precision` (actual → document direction): **1.000**

All 9 actual findings were validated as genuine by the Haiku judge reading the full document. The key fix from the prototype: do not truncate the document to the judge — Haiku has 200K context and truncation caused false NOs for findings that reference the second half of the document.

---

## Options Considered

**Option A — Superset ground truth:** Run N review sessions, union-validate all findings, score recall against the superset. Rejected: expensive to build, grows unbounded, goes stale when the document changes. Still fails for context-dependent findings.

**Option B — Reverse judge only:** Score only precision (are findings real?), no recall. Rejected: precision alone cannot detect coverage regression. A reviewer that finds one trivial real flaw per run scores 1.0 while being useless.

**Option C — Two-tier hybrid (chosen):** Primary scorer measures precision via reverse judge. Secondary scorer measures must-find recall against a small curated list. Both run on every eval task.

---

## Decision

Adopt two-tier eval scoring:

### Tier 1: `reverse_judge_precision` (primary quality signal)

For each actual finding in the reviewer's output, ask an external judge: "Is this finding a genuine flaw in the document?" Return precision = real_findings / total_findings.

**Judge model:** Haiku (cheap, fast, deterministic at T=0)
**Judge temperature:** 0.0 (deterministic evaluation tool)
**Reviewer temperature:** model default (~1.0, matches production)
**Document truncation:** none — pass full document to judge

**Encoded criteria — a finding is GENUINE if:**
- It identifies a specific, nameable gap, inconsistency, or invalid assumption in the document
- That gap materially affects whether the design/plan can succeed (including logic bombs that make success improbable until resolved — not just editorial fixes)
- It is discoverable from the document content alone without external context

**Encoded false positive list — a finding is NOT genuine if:**
- It describes an implementation detail rather than a requirement/design gap (what vs. how confusion)
- It assumes a constraint the document never states (hallucinated requirement)
- It is a style or completeness preference without a specific structural gap
- It describes a hypothetical future concern rather than a current document problem
- It duplicates another finding from a different angle without adding new information
- It references external context not present in the document under review

This explicit false positive list mirrors the code-review plugin's approach (0-100 confidence with explicit false positive exclusions). It is encoded in the judge system prompt and should also inform reviewer agent prompts.

### Tier 2: `must_find_recall` (regression guard)

Against a curated `must_find.jsonl` per dataset: what fraction of must-find findings did the reviewer detect?

**`must_find.jsonl` schema:**
```jsonl
{"id": "pf-001", "title": "...", "issue": "...", "severity": "Critical", "min_recall": 0.90}
{"id": "pf-002", "title": "...", "issue": "...", "severity": "Critical", "min_recall": 0.60}
```

**Curation rules:**
- Only include findings discoverable from the frozen document content alone (no external context required)
- No ceiling on list size — reflects actual document quality debt
- Each finding carries `min_recall` threshold — high for unambiguous flaws, lower for genuinely subtle ones
- Context-dependent findings (those excluded from must-find) are logged separately in `context_dependent_findings.jsonl` as a reviewer coverage improvement backlog (see Issue #68)

**MVP behaviour:** Scorer ignores `min_recall`, applies a single global threshold, reports found/not-found per finding as a diagnostic signal. `min_recall` is reserved for Phase 2 when N≥3 runs make per-finding recall statistics meaningful.

---

## Temperature and N Considerations

**Reviewer temperature:** Runs at model default (~1.0) to match production behaviour. This is already the case in the current implementation — `generate()` with no temperature argument.

**Judge temperature:** Explicitly 0.0. The evaluation tool should be deterministic.

**Implication for N:** At T≈1 for reviewers, each run is stochastic. N=1 gives a point sample, not a recall estimate. Must-find recall from N=1 is binary (found or not) — not a statistical claim.

**MVP:** N=1. Report must-find found/not-found as a diagnostic indicator. Design schema and Makefile to support N>1 from day one.

**Phase 2:** N=3 runs per eval cycle. Per-finding recall across runs becomes meaningful. `min_recall` thresholds are enforced. N is per execution environment (model + version) — a recall estimate for Sonnet 4.6 does not transfer to Opus or GPT-4 without a separate N=3 baseline run.

---

## Consequences

**Positive:**
- Dissolves the genuine-difference problem — model is not penalised for finding different-but-valid flaws
- Precision gives a quality signal independent of expected finding set
- Must-find guard catches coverage regression without requiring comprehensive ground truth enumeration
- Ground truth capture workflow is lighter — curate must-find (small, stable), note context-dependent findings, done
- No cross-run comparison infrastructure needed for primary metric

**Negative:**
- Requires full implementation cycle: new scorers, must-find curation, context_dependent log, updated dataset schema
- Prototype code (`reverse_judge_scorer.py`) is throwaway — full implementation goes through design/review/plan cycle
- Must-find list requires human judgment to curate and maintain
- Per-finding `min_recall` thresholds are not enforceable at N=1 (deferred to Phase 2)
- Precision can be gamed by a reviewer that outputs few, safe findings — must-find guard mitigates but does not eliminate this

**Supersedes:**
- `severity_calibration` scorer (string fuzzy match against expected set) — retire after full implementation
- `llm_judge_match` scorer (LLM judge in expected → actual direction) — retire after full implementation
- 90% recall / 80% precision thresholds from requirements-v2 FR-QUALITY-1 — superseded by precision ≥ 80% (primary) + per-finding must-find thresholds (secondary)
