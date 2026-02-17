# Requirements Review Summary — inspect-ai-integration-v2 (Light Mode)

**Review Date:** 2026-02-17
**Design Document:** `docs/requirements/inspect-ai-integration-requirements-v2.md` (on `feat/inspect-ai-integration-design`)
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 3 | 4 | 1 | 8 |
| scope-guardian | 1 | 4 | 3 | 8 |
| constraint-finder | 2 | 6 | 2 | 10 |
| assumption-hunter | 3 | 4 | 2 | 9 |
| success-validator | 2 | 5 | 2 | 9 |
| **Total** | **11** | **23** | **10** | **44** |

---

## Key Themes

**Problem Framing & Success Criteria:**
v2 removed the explicit success criteria that v1 had, replacing them with a phase map. This is a regression — the phase map shows status but not completion gates. Without a numeric exit criterion for Phase 1 ("non-zero accuracy" is not a threshold), Phase 1 never formally completes and Phase 1.5 has no baseline to compare against. Three reviewers flagged this independently. The v1 90%/80% targets appear in an example but are never confirmed or deprecated in v2 — it's unclear whether they apply to Phase 1, Phase 2, or at all.

**Open Questions Blocking Implementation:**
Three of the four open questions are scope-determining decisions, not deferrable design questions: (1) ground truth size directly determines whether Phase 1 can proceed with 10 findings, (2) reviewer consensus deduplication determines how FR-ARCH-1 ground truth filtering is implemented, (3) ablation decomposition determines whether `reviewer_eval.py` needs per-agent ablation variants. Leaving these as open questions forces implementation-time scope calls that invalidate the review.

**Environmental Constraints Unspecified:**
Multiple constraints were discovered that block implementation but aren't documented: Python version not pinned (Inspect AI requires 3.10+), Inspect AI version not pinned (the API broke once already during v1 implementation — Session 21), API credential model unaddressed (Bedrock vs direct API, multi-provider for Phase 1.5), and working directory sensitivity (discovered in Session 20, not surfaced as a requirement). These are not optional notes — they are implementation blockers.

**Assumption: Ground Truth is Adequate:**
The 10 Critical findings are assumed sufficient. With per-reviewer filtering, each reviewer may have only 2 findings. At N=2, one miss swings recall by 50 percentage points — noise dominates signal. There is no minimum per-reviewer coverage requirement and no statistical confidence threshold. The ground truth may also lack reliable reviewer attribution fields (needed for FR-ARCH-1 filtering) since it was validated from full-skill output, not from individual agent runs.

**Schema Fragmentation:**
The JSONL schema exists in three places simultaneously: requirements doc, agent prompts, and `output_parser.py`. No single source of truth is designated. Schema drift between agent prompts and the parser was exactly how v1 failed (assumption-hunter output was markdown, not JSONL). FR-ARCH-3 mandates JSONL but doesn't address where the canonical schema lives or how agents reference it.

**Missing Reference Document:**
ADR-006 is referenced by name in the Background section and FR-ARCH-1 for "full decision rationale," but it does not exist on disk. Requirements that delegate key rationale to a missing document are self-incomplete.

---

## Critical Findings

1. **[problem-framer] — Problem statement unchanged despite v1 root cause being wrong**
   - Issue: v1 failed because skills are orchestration workflows, not single-turn reviewers. The problem statement doesn't capture this — future maintainers can't understand why v1 failed from reading the problem statement.
   - Suggestion: Update problem statement to explain v1 failure mode and what v2 corrects.

2. **[problem-framer] — ADR-006 referenced but does not exist on disk**
   - Issue: Background and FR-ARCH-1 both defer to "ADR-006 for full decision rationale" — the file doesn't exist.
   - Suggestion: Create `docs/requirements/adr-006-per-reviewer-eval-task-decomposition.md` or remove the reference and inline the rationale.

3. **[problem-framer] — v2 has no document-level success criteria**
   - Issue: v1 had explicit numbered success criteria. v2 replaced them with a phase map that shows status but not completion gates. "Phase 1 is the immediate target" doesn't define what Phase 1 done looks like.
   - Suggestion: Add explicit success criteria: minimum recall/precision thresholds for Phase 1 to be complete, conditions for Phase 1.5 to begin.

4. **[scope-guardian] — Open question on ground truth size is scope-determining**
   - Issue: Open Question 3 (10 findings sufficient?) directly gates whether Phase 1 can start. A dataset that grows mid-phase invalidates any baseline taken before expansion.
   - Suggestion: Resolve to either "10 Critical findings are sufficient for Phase 1" (with rationale) or specify what expansion is needed before Phase 1 begins.

5. **[constraint-finder] — Python version constraint unspecified**
   - Issue: Inspect AI requires Python 3.10+. No minimum version pinned in `pyproject.toml`. Environment-specific failures will be silent.
   - Suggestion: Add `python_requires = ">=3.10"` to `pyproject.toml`.

6. **[constraint-finder] — Inspect AI version not pinned**
   - Issue: The framework API already broke once during implementation. `pip install --upgrade` can silently re-break the eval.
   - Suggestion: Pin `inspect-ai>=X.Y.Z,<X.(Y+1).0` in `pyproject.toml`. Log the version when Phase 1 is validated.

7. **[assumption-hunter] — Agent files assumed eval-compatible without audit**
   - Issue: FR-ARCH-2 requires all agents to work in eval context without modification, but there's no audit step verifying this. Non-compliant agents are surprise scope with no tracking.
   - Suggestion: Add Phase 1 prerequisite: audit all 5 reviewer agent files against FR-ARCH-2 criteria before implementing `reviewer_eval.py`.

8. **[assumption-hunter] — Single-document input assumption excludes context-dependent reviewer types**
   - Issue: Agents whose persona requires external context (e.g., prior-art-scout needs reference material) structurally cannot function in single-turn eval — producing a misleading detection baseline.
   - Suggestion: Document which agents are viable in single-document context and which require multi-document eval designs. Scope Phase 1 to context-independent agents only.

9. **[assumption-hunter] — LLM output assumed to be clean JSONL without fencing**
   - Issue: LLMs routinely wrap structured output in markdown fences. A strict parser returns 0 findings for a valid-but-fenced response — indistinguishable from "agent found nothing."
   - Suggestion: Add acceptance criterion to FR-ARCH-3: parser must handle and strip common output wrappers (```json, ``` fences). Or require agents to output raw JSONL with explicit "no fences" instruction.

10. **[success-validator] — Phase 1 has no numeric completion criterion**
    - Issue: "Non-zero accuracy" is not a threshold — it could mean 1 finding detected out of 10. Phase 1 never formally completes.
    - Suggestion: Define Phase 1 exit gate: e.g., ≥50% recall across all reviewer agents on the validated ground truth dataset.

11. **[success-validator] — v1 detection targets (90%/80%) neither confirmed nor deprecated in v2**
    - Issue: These targets appear in a FR-QUALITY-1 example but their phase-applicability is undefined. The scorer cannot determine pass/fail.
    - Suggestion: Explicitly state: these thresholds apply to Phase 2 completion, not Phase 1. Phase 1 target is ≥X% (define the number).

---

## Important Findings

1. **[problem-framer]** — v2 embeds solution prescription ("unit of testing is individual reviewer agent") in the problem statement
2. **[problem-framer]** — FR-ARCH-2 dual-context requirement creates unanalyzed design tension (eval degrading production agent quality)
3. **[problem-framer]** — FR-ARCH-3 root cause is missing instructions, not missing format mandate — "zero findings as format failure" could mask real zero-finding results
4. **[problem-framer]** — Mock-tools architecture excluded from FR-ARCH-1 without documented rationale, leaving orchestration layer coverage gap silently absent
5. **[scope-guardian]** — Phase 1.5 not in deferred list but blocked on Google account — ambiguous phases attract implicit scope
6. **[scope-guardian]** — FR-ARCH-5 cost tooling (`make cost-report`, automated budget flag) is orthogonal to Phase 1 blocking problem
7. **[scope-guardian]** — Open question on ablation decomposition (per-agent vs combined) determines `reviewer_eval.py` structure
8. **[scope-guardian]** — Open question on reviewer consensus deduplication determines ground truth filtering logic
9. **[constraint-finder]** — Content hash function not specified — platform CRLF/LF differences cause spurious hash mismatches between macOS dev and CI
10. **[constraint-finder]** — API credential model unaddressed — Bedrock vs direct API, multi-provider for Phase 1.5
11. **[constraint-finder]** — No rate limit constraint for Phase 1.5 multi-model runs (15 concurrent tasks can 429, producing misleading partial results)
12. **[constraint-finder]** — Ground truth per-reviewer N=2 avg creates 50pp recall swings from single missed finding
13. **[constraint-finder]** — Eval working directory sensitivity not captured as a requirement (discovered Session 20)
14. **[constraint-finder]** — Cost budgets assume direct API pricing; Bedrock pricing differs
15. **[assumption-hunter]** — Ground truth reviewer attribution unverified — v1 findings validated from full-skill output may lack `reviewer` field needed for FR-ARCH-1 filtering
16. **[assumption-hunter]** — Batch API Inspect AI integration unvalidated — 50% cost reduction assumes transparent abstraction
17. **[assumption-hunter]** — JSONL schema fragmentation: 3 locations, no canonical source
18. **[assumption-hunter]** — FR-QUALITY-1 1/5 rubric examples require synthetic degraded findings; existing ground truth only has valid examples
19. **[success-validator]** — FR-ARCH-2 acceptance criteria verify structure but not behavioral correctness
20. **[success-validator]** — FR-ARCH-4 staleness check triggers re-run but defines no acceptable outcome or follow-up action
21. **[success-validator]** — FR-ARCH-5 budget overrun only "flags for optimization" — no enforcement; ignored in practice
22. **[success-validator]** — Quality rubric target score (≥3.5/5.0) written as "e.g." not a firm requirement
23. **[success-validator]** — No eval reliability requirement (LLM non-determinism: same eval passes/fails across runs)

---

## Next Steps

1. **Address Critical findings before Phase 1 implementation**
   - Resolve 4 open questions (ground truth size, consensus deduplication, ablation scope, reviewer attribution)
   - Create ADR-006 or inline its rationale
   - Add Phase 1 numeric exit gate (≥X% recall)
   - Pin Python + Inspect AI versions
   - Audit all 5 agent files against FR-ARCH-2 criteria
   - Add parser fence-stripping to FR-ARCH-3 acceptance criteria

2. **Review Important findings before closing Phase 1 scope**
   - Move Phase 1.5 to deferred list
   - Descope `make cost-report` from Phase 1
   - Document JSONL schema canonical location
   - Address reviewer attribution in existing ground truth dataset

3. **Consider Minor findings for document polish**

4. **Re-run requirements review if major scope changes result**
