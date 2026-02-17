# Requirements Review Summary — Inspect AI Integration (Light Mode)

**Review Date:** 2026-02-16
**Design Document:** `docs/requirements/inspect-ai-integration-requirements-v1.md`
**Reviewers:** problem-framer, scope-guardian, constraint-finder, assumption-hunter, success-validator

---

## Finding Counts

| Reviewer | Critical | Important | Minor | Total |
|----------|----------|-----------|-------|-------|
| problem-framer | 2 | 6 | 3 | 11 |
| scope-guardian | 2 | 8 | 6 | 16 |
| constraint-finder | 3 | 9 | 6 | 18 |
| assumption-hunter | 3 | 10 | 7 | 20 |
| success-validator | 2 | 7 | 5 | 14 |
| **Total** | **12** | **40** | **27** | **79** |

---

## Key Themes

**The requirements document has a fundamental problem framing issue:** It treats Inspect AI integration as the goal, when the actual problem is "we don't know if parallax skills work." This manifests in three systemic failures:

1. **Circular validation dependency** — The eval framework measures "do new skills match v3 outputs" without first validating that v3 outputs are correct. Ground truth is unvalidated LLM outputs, not confirmed design flaws. This chicken-and-egg problem blocks the entire approach.

2. **MVP solves the wrong problem** — Phase 1 validates "Inspect AI works" (technical integration success) but defers finding quality scorer to Phase 2. The MVP cannot answer the core question: "do skills catch real design flaws?"

3. **Unimplementable specifications** — Multiple critical requirements lack definitions: 95% confidence measurement undefined (appears 5 times), detection rate thresholds missing, ablation test baseline X undefined, ground truth Dataset schema unspecified.

**Problem Framing:**
Problem-framer identified that jobs-to-be-done conflate problem with solution (Inspect AI framed as answer within problem description). Jobs 4-5 (cost optimization, multi-model portability) solve theoretical problems without evidence they exist. The document jumps directly to solution-oriented requirements without explicitly stating the problem.

**Scope & Boundaries:**
Scope-guardian found contradictions between deferred items and acceptance criteria (FR8 multi-model marked "deferred" but has full acceptance criteria). Planted flaw detection (FR5.1) implies weeks of dataset authoring work not captured in Phase 1's 1-week timeline. MVP scope has 20-40% hidden tooling effort (multi-source dataset loading, confidence measurement workflow, version comparison infrastructure).

**Constraints & Feasibility:**
Constraint-finder identified three critical blockers: Python environment unspecified (blocks installation), API key security undefined (violates work policies), circular ablation tests (ground truth established before validation). The $0.50 cost target is infeasible—22 samples × 15.5k tokens = $1.02. Manual validation workflow (78 minutes for 87 findings) blocks the <5 minute automation target.

**Assumptions:**
Assumption-hunter found the entire framework optimizes against unvalidated v3 findings (Critical finding 001). Statistical methodology lacks justification: 10% regression threshold doesn't account for N=22 variance, 50% ablation threshold doesn't measure base model capability, 70% detection rate has no empirical source. Prompt caching (90% cost savings) isn't in cost calculations, making estimates 5-10× too high.

**Success Criteria:**
Success-validator identified that only 2/8 success criteria are quantitative. FR2.2 detection rate has no target thresholds (can't determine pass/fail), ablation test baseline X is undefined (test can't run), 95% confidence threshold calculation method not specified (appears in 5 requirements). The $0.50 cost target has no token budget breakdown showing it's achievable.

---

## Critical Findings (12 Total)

### Problem Framing (2 Critical)

1. **v1-problem-framer-006 — Ground truth validation circular dependency**
   - Issue: v3 findings are unvalidated LLM outputs, not confirmed design flaws. Eval framework will measure "do new skills match old outputs" rather than "do skills catch real flaws." This chicken-and-egg problem is the actual blocker.
   - Suggestion: Establish ground truth via human expert review of 22 v3 Critical findings BEFORE building eval framework. Each finding validated as: (a) real flaw, (b) false positive, (c) ambiguous. Only use (a) as ground truth. This validates the foundation before investing in measurement infrastructure.

2. **v1-problem-framer-008 — MVP solves measurement, not validation**
   - Issue: Phase 1 validates "Inspect AI works" not "parallax skills work." Finding quality scorer deferred to Phase 2 means MVP cannot answer core question: "do skills catch design flaws?"
   - Suggestion: Reframe MVP as "validate ground truth exists" not "build eval framework." Phase 1: Human expert validation of v3 Critical findings. Phase 2: Build eval framework against validated ground truth. Inspect AI integration is Phase 2 work, not Phase 1.

### Scope Boundaries (2 Critical)

3. **v1-scope-guardian-004 — Ground truth dataset format not specified**
   - Issue: Inspect AI Dataset schema is undefined. FR3.1 requires converting artifacts to "Inspect AI Dataset format" but doesn't specify Sample schema, input/target fields, or metadata structure. Blocks implementation start.
   - Suggestion: Research Inspect AI Sample format, document schema in FR3.1 acceptance criteria. Example: `Sample(input=design_doc_text, target=expected_findings_jsonl, metadata={...})`. Must define before conversion work begins.

4. **v1-scope-guardian-013 — Confidence measurement undefined**
   - Issue: FR2.3 requires flagging <95% confidence findings but doesn't define how confidence is measured. Blocks manual validation workflow (Success Criteria #5).
   - Suggestion: Define confidence measurement in FR2.3: (a) LLM self-assessment score 0-100, (b) semantic similarity to known patterns, (c) human evaluator agreement rate. Without definition, requirement is unimplementable.

### Constraints (3 Critical)

5. **v1-constraint-finder-001 — Python environment constraints missing**
   - Issue: No Python version, venv strategy, or dependency conflict resolution specified. Inspect AI requires Python 3.10+, may conflict with existing project dependencies. Blocks installation (Success Criteria #1).
   - Suggestion: Add NFR: Python 3.11+ required, use dedicated venv `parallax-evals/`, document Inspect AI version pinning. Address potential conflicts with Claude Code's Python environment.

6. **v1-constraint-finder-002 — API key security undefined**
   - Issue: No separation between work/personal keys, rotation policies, or CI/CD access patterns. Work context uses Bedrock (IAM roles), personal uses direct API (env vars). Violates security policies if keys mixed.
   - Suggestion: Add NFR: Separate API key namespaces (ANTHROPIC_API_KEY for personal, AWS credentials for work). Document key rotation frequency (30 days). CI/CD uses GitHub Secrets, not hardcoded keys.

7. **v1-constraint-finder-009 — Circular validation in ablation tests**
   - Issue: FR6.1 establishes baseline from first eval run, then FR4.1 validates ablation against that baseline. Ground truth established before validation, allowing false positives to contaminate baseline. Invalidates entire eval framework.
   - Suggestion: Reorder phases: (1) Validate ground truth via human expert review, (2) Establish baseline against validated ground truth, (3) Run ablation tests against validated baseline. Break circular dependency.

### Assumptions (3 Critical)

8. **v1-assumption-hunter-001 — Ground truth validity assumed**
   - Issue: Entire eval framework optimizes against v3 review findings without validating they're correct. If v3 has false positives or missed issues, eval framework will optimize for wrong outcomes.
   - Suggestion: Add FR0 (prerequisite): Human expert validation of v3 Critical findings. Create `datasets/v3_review_validated/` with expert-confirmed findings. Use only validated findings as ground truth. Document validation process in acceptance criteria.

9. **v1-assumption-hunter-013 — Confidence measurement undefined**
   - Issue: 95% confidence threshold appears in 5 places (FR2.3, FR3.3, NFR4.1, Success Criteria, Open Questions) but never defines how confidence is calculated. Requirement is literally unimplementable without measurement methodology.
   - Suggestion: Add FR2.4: "Confidence calculation methodology" — Specify: (a) LLM logprobs, (b) semantic similarity scores, (c) multi-model agreement, (d) human calibration. Document which method used for 95% threshold.

10. **v1-assumption-hunter-005 — Skill versioning strategy missing**
    - Issue: FR7.1 requires running evals against different skill versions via git commit, but doesn't specify how this works if skill definitions are external or if checking out old commits breaks eval code.
    - Suggestion: Add FR7.3: "Version compatibility matrix" — Document backward compatibility strategy. Options: (a) evals track skill schema versions, (b) skill changes are additive only, (c) major versions require new eval suites. Choose explicit strategy.

### Success Criteria (2 Critical)

11. **v1-success-validator-001 — FR2.2 detection rate has no target thresholds**
    - Issue: "Compares detected Critical findings to ground truth" with "detection rate (recall), precision, F1" but no target values. Cannot determine success vs failure.
    - Suggestion: Add quantified thresholds to FR2.2: "Target: recall ≥70%, precision ≥80%, F1 ≥0.74. MVP passes if all three thresholds met on v3 Critical findings."

12. **v1-success-validator-002 — FR4.1 ablation test baseline undefined**
    - Issue: "Baseline: Full skill content → detection rate X%" but X is never defined. "Ablation: Drop content → detection rate < (X - 50)%" cannot run without baseline value.
    - Suggestion: Add to FR4.1: "Baseline X established in FR6.1 (first eval run). Example: if baseline = 75%, ablation must drop to <25%. Test fails if detection rate remains >25% after content removal."

---

## Important Findings (40 Total - Top 10 Shown)

### High-Impact Important Findings

1. **v1-problem-framer-001 — No explicit problem statement**
   - Jobs-to-be-done section jumps directly to solution-oriented descriptions without stating underlying problem. Makes it difficult to evaluate if requirements address root cause.
   - Suggestion: Add "Problem Statement" section before Jobs: "Parallax skills are developed iteratively with no systematic way to measure effectiveness. Changes to skill prompts may improve, degrade, or have no effect on finding quality—we cannot tell which. This blocks empirical improvement and risks shipping broken skills to production."

2. **v1-scope-guardian-005 — Planted flaw detection implies weeks of hidden work**
   - FR5.1 requires test dataset with planted flaws but doesn't account for authoring effort (design docs with known issues, ground truth labels, multiple flaw categories). Could add 2-4 weeks to Phase 1.
   - Suggestion: Move planted flaw tests to explicit deferral list. Phase 1 uses only real review findings from v3. Phase 3 (post-MVP) adds synthetic test cases with planted flaws.

3. **v1-scope-guardian-008 — Multi-model comparison scope contradiction**
   - FR8.1 has full acceptance criteria (implies MVP scope), FR8.2 defers to post-MVP. Contradiction creates scope uncertainty.
   - Suggestion: Remove FR8.1 acceptance criteria, consolidate into FR8.2. Clarify: "Multi-model comparison deferred to Phase 2. MVP validates single-model (Sonnet) integration pattern first."

4. **v1-constraint-finder-003 — Token consumption exceeds cost target**
   - NFR1.2 targets <$0.50 per eval run, but 22 samples × 700 tokens/sample × 15.5k output tokens = ~340k tokens = $1.02 (Sonnet input $3/MTok, output $15/MTok). Math doesn't work.
   - Suggestion: Revise NFR1.2 cost target to <$2.00 per eval run (realistic for 22 samples), OR reduce sample size to 10 Critical findings (<$0.50), OR use Haiku for severity calibration ($0.08).

5. **v1-constraint-finder-004 — Manual validation doesn't scale**
   - FR3.3 requires manual validation of <95% confidence findings. 87 findings × 54 seconds/finding = 78 minutes human time. Blocks NFR4.1's <5 minute automation target.
   - Suggestion: Add NFR: "Manual validation occurs during dataset creation (one-time cost), not during eval runs. Once dataset validated, evals run fully automated. Human time is setup cost, not runtime cost."

6. **v1-assumption-hunter-008 — Prompt caching not in cost calculations**
   - ADR-005 cites prompt caching as 90% input cost reduction, but NFR1 cost targets don't account for it. Estimates may be 5-10× too high if caching works, or accurate if caching doesn't apply.
   - Suggestion: Add cost calculation methodology to NFR1.2: "Cost assumes cold cache (no prompt caching). With caching: input tokens 10% of cost, output tokens dominate. Revise targets after caching validation."

7. **v1-assumption-hunter-014 — Regression threshold ignores statistical variance**
   - FR6.2 flags regression if detection rate drops >10% with N=22 samples. Statistical noise alone could cause 10% variance (confidence intervals overlap). False positive regression alerts likely.
   - Suggestion: Add statistical significance test to FR6.2: "Regression detected if detection rate drop >10% AND p<0.05 (two-proportion z-test). Prevents false alarms from natural variance."

8. **v1-success-validator-003 — 20% section contribution threshold lacks justification**
   - FR4.2 states ablation test passes "if each section contributes >20% to detection rate" but doesn't justify 20%. Why not 10% or 30%? No empirical basis provided.
   - Suggestion: Add justification to FR4.2: "20% threshold chosen to detect meaningful contributions (reject noise). Empirical calibration: run pilot ablations, set threshold at 2× observed noise level."

9. **v1-success-validator-005 — $0.50 cost target may be unachievable**
   - NFR1.2 targets <$0.50 per eval run but provides no token budget breakdown showing it's achievable. May be aspirational rather than realistic.
   - Suggestion: Add token budget to NFR1.2: "Budget: 22 samples × 500 input tokens × $3/MTok + 22 × 5k output tokens × $15/MTok = $1.68. Reduce to <$0.50 via: (a) 10 samples ($0.76), (b) Haiku ($0.08), (c) batch API ($0.38 with 50% discount)."

10. **v1-success-validator-009 — 70% detection rate borrowed without validation**
    - FR5.1 targets ">70% detection rate for planted Critical flaws" citing "FR1.2 acceptance criteria in parallax-review-requirements-v1.md." That target was for diversity metrics, not detection rate. Misapplied threshold.
    - Suggestion: Justify 70% threshold empirically or remove it. If keeping, cite correct source: "70% target based on [research/baseline/pilot data]. Lower bound for useful tool—below this, too many flaws missed."

---

## Next Steps

### Immediate Actions (Resolve Critical Blockers)

1. **STOP — Validate ground truth first** (problem-framer-006, assumption-hunter-001, constraint-finder-009)
   - DO NOT build eval framework until v3 Critical findings validated by human expert
   - Create validation process: expert reviews each finding, marks as real/false-positive/ambiguous
   - Use only confirmed real findings as ground truth
   - Document validation process in FR0 (prerequisite requirement)

2. **Reframe MVP goal** (problem-framer-008)
   - Phase 1: Validate ground truth exists (human expert review of v3 Critical findings)
   - Phase 2: Build eval framework against validated ground truth (Inspect AI integration)
   - Current Phase 1 is actually Phase 2 work

3. **Define unimplementable requirements** (scope-guardian-004, scope-guardian-013, assumption-hunter-013, success-validator-001, success-validator-002)
   - Research and document Inspect AI Dataset schema (FR3.1)
   - Define confidence measurement methodology (FR2.3)
   - Add detection rate target thresholds (FR2.2)
   - Define ablation test baseline X (FR4.1)

4. **Fix cost target** (constraint-finder-003, success-validator-005)
   - Revise NFR1.2 to <$2.00 per eval run (realistic) OR reduce sample size OR use Haiku
   - Add token budget breakdown showing target is achievable

5. **Add missing constraints** (constraint-finder-001, constraint-finder-002)
   - Document Python environment requirements (version, venv, dependencies)
   - Define API key security policies (work/personal separation, rotation)

### Secondary Actions (Address Important Findings)

6. **Clarify scope boundaries**
   - Remove planted flaw detection from Phase 1 (scope-guardian-005)
   - Resolve multi-model comparison contradiction (scope-guardian-008)
   - Document hidden tooling effort (scope-guardian-010)

7. **Fix statistical methodology**
   - Add statistical significance tests to regression detection (assumption-hunter-014)
   - Justify ablation threshold or make it configurable (success-validator-003)
   - Validate or remove 70% detection rate target (success-validator-009)

8. **Improve cost modeling**
   - Account for prompt caching in cost calculations (assumption-hunter-008)
   - Separate one-time setup costs from runtime costs (constraint-finder-004)

### Decision Points

9. **Review requirements after addressing Critical findings**
   - If ground truth validation fails (many false positives in v3), pivot to different approach
   - If cost target cannot be met, reconsider MVP scope or tool choice
   - If Inspect AI Dataset schema is incompatible, evaluate alternatives

10. **Consider re-running requirements review**
    - After resolving 12 Critical findings, requirements may change substantially
    - Re-review validates fixes don't introduce new issues

---

## Review Metadata

**Total findings:** 79 (12 Critical, 40 Important, 27 Minor)

**Critical finding themes:**
- Ground truth validation (4 findings across 3 reviewers) — systemic issue
- Undefined requirements (5 findings) — implementation blockers
- Circular dependencies (2 findings) — design flaws
- Missing constraints (1 finding) — environment setup

**Reviewer consensus areas:**
- All 5 reviewers flagged ground truth validation issues (Critical or Important)
- 4 reviewers flagged 95% confidence measurement undefined
- 4 reviewers flagged cost target infeasibility
- 3 reviewers flagged statistical methodology gaps

**High-confidence findings:**
- Findings flagged by 3+ reviewers are highest priority
- Ground truth validation is THE blocker (unanimous across reviewers)
- Confidence measurement undefined appears in 5 requirements but has no definition

**Estimated rework:**
- Addressing 12 Critical findings: 1-2 days (requirements rewrite)
- Addressing top 10 Important findings: 2-3 days (scope clarification, cost modeling)
- Ground truth validation prerequisite: 2-4 weeks (human expert review of v3 findings)

**MVP timeline impact:**
- Original estimate: 1 week (Phase 1)
- Revised estimate: 3-5 weeks (ground truth validation + Phase 1)
- Blocker: Cannot start Inspect AI integration until ground truth validated
