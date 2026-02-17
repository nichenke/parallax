# Requirements: Inspect AI Integration for Parallax Eval Framework

**Date:** 2026-02-16
**Status:** Draft v1.0 (Post-Brainstorm)
**Scope:** Eval framework integration for systematic skill validation
**Related:** Issue #5 (Eval Framework), ADR-005 (Inspect AI Integration Decision)

---

## Problem Statement

Parallax skills are developed iteratively with no systematic way to measure effectiveness. Changes to skill prompts may improve, degrade, or have no effect on finding quality—we cannot tell which. This blocks empirical improvement and risks shipping broken skills to production.

**Core challenge:** Ground truth validation is circular. We need verified design flaws to test detection capability, but we need detection capability to find design flaws.

**Initial approach:** Manual validation of v3 Critical findings to establish high-confidence ground truth baseline, then expand incrementally with manual review gates.

---

## Jobs-to-Be-Done

This integration addresses five validated needs from the parallax development workflow:

**Job 1: Validate skill effectiveness systematically**
- Pain: No empirical way to know if skills actually catch design flaws, or if prompt changes break detection capability
- Solution: Eval framework that measures detection rate against ground truth, validates severity calibration, assesses finding quality
- Requirements: FR1 (Inspect AI integration), FR2 (custom scorers), FR3 (test datasets)
- Outcome: Data-driven confidence that skills work as intended

**Job 2: Detect skill degradation before deployment**
- Pain: Skill changes might silently break detection capability (e.g., removing key persona descriptions reduces finding coverage)
- Solution: Ablation tests that verify skill content contributes to outcomes (drop content → detection rate drops >50%)
- Requirements: FR4 (ablation tests), FR5 (negative test cases)
- Outcome: Regression detection prevents broken skills from reaching production

**Job 3: Iterate on skill prompts empirically**
- Pain: No baseline metrics to measure whether prompt changes improve or degrade performance
- Solution: Ground truth datasets with known findings, regression detection across skill versions
- Requirements: FR3 (test datasets), FR6 (baseline metrics), FR7 (version comparison)
- Outcome: Data-driven skill improvement, not guesswork

**Job 4: Optimize cost without sacrificing quality**
- Pain: Running evals on every model/configuration is expensive, but need to validate multi-model portability
- Solution: Model tiering (Haiku for mechanical scorers, Sonnet for LLM-as-judge), batch API for offline runs (50% cost reduction)
- Requirements: NFR1 (cost tracking), NFR2 (model tiering), NFR3 (batch API integration)
- Outcome: Sustainable eval runs within $2000/month budget

**Job 5: Validate multi-model portability**
- Pain: Skills developed on Sonnet might fail on Haiku (cost optimization) or Opus (quality baseline)
- Solution: Multi-model comparison evals using Inspect AI model roles pattern
- Requirements: FR8 (multi-model comparison), FR9 (model role configuration)
- Outcome: Confidence that skills work across Claude model tiers

**User outcome:** Run evals locally to validate skill changes in <5 minutes, with clear pass/fail signals and regression detection.

---

## Functional Requirements

### FR0: Ground Truth Validation (Prerequisite)

**FR0:** Establish validated ground truth via human expert review of v3 Critical findings
- **Rationale:** Break circular validation dependency—cannot validate eval framework against unvalidated LLM outputs. Ground truth quality determines eval framework validity.
- **Source:** Critical findings v1-problem-framer-006, v1-assumption-hunter-001, v1-constraint-finder-009
- **Acceptance Criteria:**
  - Expert reviewer (human, not LLM) examines each of 22 v3 Critical findings
  - Each finding classified as: (a) real design flaw, (b) false positive, (c) ambiguous/needs-context
  - Only category (a) findings used as ground truth for eval framework
  - Validation process documented: criteria for classification, false positive rate
  - If multiple reviewers: inter-rater agreement measured (Cohen's kappa ≥0.6)
  - `datasets/v3_review_validated/` created with confirmed findings only
  - Each finding includes metadata: reviewer ID, confidence score, validation date
  - Target: ≥15 confirmed real flaws (68% validation rate) for sufficient test data

---

### FR1: Inspect AI Integration

**FR1.1:** Install and configure Inspect AI in parallax repo
- **Rationale:** Leverage 90% of eval infrastructure (runner, logging, metrics, batch API) instead of building custom
- **Source:** ADR-005 (Inspect AI integration decision)
- **Acceptance Criteria:**
  - `evals/` directory with Python eval definitions
  - `scorers/` directory with custom scoring functions
  - `inspect eval` CLI runs successfully on test dataset
  - Inspect View (web UI) displays eval results

**FR1.2:** Use Anthropic provider with native Claude support
- **Rationale:** Zero integration friction, streaming support, beta features (prompt caching)
- **Source:** ADR-005 (Claude integration analysis)
- **Acceptance Criteria:**
  - `ANTHROPIC_API_KEY` environment variable configuration
  - Evals run on `claude-sonnet-4-5`, `claude-opus-4-6`, `claude-haiku-4-5`
  - Bedrock provider optionally supported for work context

**FR1.3:** EvalLog captures inputs, outputs, scores, token usage, latency
- **Rationale:** NFR1 (cost tracking), FR6 (baseline metrics), debugging
- **Source:** ADR-005 (Inspect AI logging & metrics)
- **Acceptance Criteria:**
  - Each eval run produces EvalLog JSON artifact
  - Log includes per-sample token counts (input, output, total)
  - Log includes latency metrics with retry tracking
  - Logs viewable in Inspect View UI

---

### FR2: Custom Scorers (Phase 1: Severity Calibration)

**FR2.1:** Build `severity_calibration_scorer.py` as first scorer
- **Rationale:** Simplest scorer (no LLM-as-judge), validates integration pattern, addresses known issue (too many Important findings)
- **Source:** ADR-005 (custom scorers), user Q&A (start with Critical findings)
- **Acceptance Criteria:**
  - Scorer accepts review artifact (JSONL findings), returns severity distribution metrics
  - Validates Critical findings < 30%, Important 40-50%, Minor 20-30% (configurable thresholds)
  - Returns pass/fail + distribution breakdown
  - <95% confidence findings flagged for manual review

**FR2.2:** Scorer validates only Critical findings in MVP
- **Rationale:** Highest confidence data, validates framework before expanding to Important/Minor
- **Source:** User Q&A (start with Critical to get framework working), Critical finding v1-success-validator-001
- **Acceptance Criteria:**
  - Scorer filters to Critical severity findings only
  - Compares detected Critical findings to ground truth Critical findings
  - Reports detection rate (recall), precision, F1 score
  - Initial target thresholds (provisional, adjust after analyzing failures):
    - Detection rate (recall) ≥90% (per Success Criteria #4)
    - Precision ≥80% (minimize false positives)
    - F1 score ≥0.74 (balanced performance)
  - Any result below thresholds triggers failure analysis to understand gaps and tune thresholds
  - Post-MVP: Background job reviews "passing but not perfect" cases (e.g., 91-99% detection) to detect slippage over time

---

### FR3: Test Datasets

**FR3.1:** Convert validated ground truth to format consumable by Inspect AI
- **Rationale:** Eval framework requires machine-readable dataset in Inspect AI's expected format
- **Source:** ADR-005 (test datasets), user Q&A (start with v3), Critical finding v1-scope-guardian-004
- **Acceptance Criteria:**
  - Validated findings from FR0 converted to Inspect AI-compatible format
  - Dataset includes only confirmed Critical findings (≥15 from ground truth validation)
  - Inspect AI eval task can load and process the dataset without errors
  - Dataset schema documented (research Inspect AI Dataset/Sample format during Phase 1 design)
  - Conversion process documented for future dataset additions

**FR3.2:** Support incremental dataset expansion
- **Rationale:** Validate integration pattern with v3 first, then add requirements-light, pattern-extraction, parallax-review
- **Source:** User Q&A (C - start with v3, expand incrementally)
- **Acceptance Criteria:**
  - Dataset loading supports multiple sources (`datasets/v3_review/`, `datasets/requirements_light/`)
  - Evals can run on single dataset or combined datasets
  - Ground truth counts tracked per dataset for regression detection

**FR3.3:** Manual validation gate for ground truth creation
- **Rationale:** Prevent false positives from becoming permanent ground truth
- **Source:** User Q&A (95% confidence threshold, manual review)
- **Acceptance Criteria:**
  - Script to extract findings from review artifacts
  - Subagent validates each finding against design doc
  - Only ≥95% confidence findings auto-added to ground truth
  - <95% confidence findings require user approval

---

### FR4: Ablation Tests (Negative Testing)

**FR4.1:** Test that dropping skill content degrades detection rate >50%
- **Rationale:** Validates that skill content actually matters (not just model inference)
- **Source:** User Q&A (adversarial and ablation tests), Issue #5 (ablation test type), Critical finding v1-success-validator-002
- **Acceptance Criteria:**
  - **Baseline (X):** Full skill content achieves detection rate X% on validated ground truth (established in FR6.1)
  - **Baseline prerequisite:** X must be ≥90% (per Success Criteria #4) to validate baseline quality before ablation
  - **Ablation:** Drop all/most skill content → detection rate drops to <(X - 50)%
  - **Pass criteria:** If baseline X=90%, ablation must drop to <40%. If drop is only to 60%, test fails (skill content not contributing)
  - **Example thresholds (provisional):**
    - Baseline 90% → ablation <40% = PASS (50% absolute drop)
    - Baseline 90% → ablation 60% = FAIL (only 30% drop, skill content weak)
    - Baseline 70% → ablation <20% = PASS (would pass but baseline below threshold)
  - Test fails if ablation doesn't significantly degrade performance (skill content not contributing)

**FR4.2:** Coarse-grained ablation for MVP (section-level removal)
- **Rationale:** Validates major components contribute, defers fine-grained tuning to post-MVP
- **Source:** User Q&A (Q3 - coarse-grained for MVP)
- **Acceptance Criteria:**
  - Ablation test drops entire sections: persona descriptions, verdict logic, synthesis instructions
  - Each ablation measures impact on Critical finding detection rate
  - Test passes if each section contributes >20% to detection rate

**FR4.3:** Fine-grained ablation deferred to post-MVP
- **Rationale:** Individual persona contribution analysis (e.g., drop assumption-hunter → specific blind spots) requires more test data
- **Source:** User Q&A (Q3 - fine-grained post-MVP)
- **Post-MVP scope:** Per-persona ablation tests, blind spot detection validation

---

### FR5: Adversarial Tests (Robustness)

**FR5.1:** Planted flaw detection tests
- **Rationale:** Validates reviewers catch known design issues (from Issue #5 description: "plant-and-detect")
- **Source:** User Q&A (Q2 - C + B), Issue #5 (plant-and-detect test concept)
- **Acceptance Criteria:**
  - Test dataset includes design docs with planted flaws (architectural gaps, assumption violations, edge case failures)
  - Ground truth labels which flaws exist in each doc
  - Eval measures detection rate (recall), false positive rate (precision)
  - Target: >70% detection rate for planted Critical flaws (from FR1.2 acceptance criteria in parallax-review-requirements-v1.md)

**FR5.2:** Skill degradation tests (ablation overlap)
- **Rationale:** Validates removing key skill components breaks detection capability
- **Source:** User Q&A (Q2 - B, skill degradation via ablation tests)
- **Acceptance Criteria:**
  - See FR4 (ablation tests) — same implementation, different framing

**FR5.3:** Input corruption tests deferred to post-MVP
- **Rationale:** Malformed inputs, missing sections, contradictory statements — complex edge cases
- **Source:** User Q&A (Q2 - defer A to post-MVP)
- **Post-MVP scope:** Robustness testing against malformed design docs

---

### FR6: Baseline Metrics and Regression Detection

**FR6.1:** Establish baseline metrics for v3 review Critical findings
- **Rationale:** Regression detection requires known-good baseline
- **Source:** FR3 (iterative improvement via baselines)
- **Acceptance Criteria:**
  - First eval run on v3 Critical findings establishes baseline detection rate
  - Baseline stored in `evals/baselines/v3_critical_baseline.json`
  - Baseline includes: detection rate, precision, recall, F1, token count, latency, cost

**FR6.2:** Compare subsequent eval runs to baseline
- **Rationale:** Detect regressions when skill changes degrade performance
- **Source:** FR3 (empirical skill improvement)
- **Acceptance Criteria:**
  - Eval runner compares current run to baseline
  - Regression detected if detection rate drops >10% (configurable threshold)
  - Report highlights: detection rate delta, new false positives, new false negatives

---

### FR7: Version Comparison

**FR7.1:** Eval runs must be comparable by skill/plugin version
- **Rationale:** A/B test prompt changes (e.g., "Does adding blind spot check improve coverage?"), track skill evolution, detect regressions
- **Source:** FR3 (empirical iteration), Critical finding v1-assumption-hunter-005
- **Acceptance Criteria:**
  - Each eval run captures skill/plugin version metadata
  - Eval results can be filtered and compared by version
  - Version identifiers are unique and stable (same skill content → same version)
  - Report compares metrics across versions side-by-side

**FR7.2:** Deferred to post-MVP (versioning mechanism is Phase 2 design research)
- **Rationale:** Requires design research - versioning strategy depends on skill packaging (git commit, content hash, plugin version)
- **Phase 2 design questions:**
  - How to version skills: git commit hash, content hash, plugin semantic version?
  - Native solutions: Claude API (prompt versioning), OpenAI (fine-tune versioning)
  - Skill snapshot vs reference: copy skill content into dataset or reference external version?
  - If skills are in superpowers plugin: how to track plugin version across parallax eval runs?
- **Post-MVP scope:** Implement chosen versioning strategy, automated version comparison in CI/CD

---

### FR8: Multi-Model Comparison

**FR8.1:** Support model roles pattern (Sonnet vs Opus vs Haiku)
- **Rationale:** Validate reviewer selection, optimize cost/quality tradeoff
- **Source:** ADR-005 (multi-model comparison), Job 5 (multi-model portability)
- **Acceptance Criteria:**
  - Eval task uses `task_with()` pattern to swap models
  - Run same eval on `claude-sonnet-4-5`, `claude-opus-4-6`, `claude-haiku-4-5`
  - Report compares detection rate, cost, latency across models

**FR8.2:** Deferred to post-MVP
- **Rationale:** Validate integration pattern first with single model (Sonnet), then expand
- **Post-MVP scope:** Full multi-model comparison suite

---

### FR9: Model Role Configuration

**FR9.1:** Support model role aliases (reviewer, grader)
- **Rationale:** Inspect AI pattern for multi-model orchestration
- **Source:** ADR-005 (model roles pattern)
- **Acceptance Criteria:**
  - Eval definitions use `Model(provider="anthropic", model="claude-sonnet-4-5")` with aliases
  - Scorer can reference `model("grader")` for LLM-as-judge evaluation

**FR9.2:** Deferred to post-MVP
- **Rationale:** MVP uses single model for both review and grading
- **Post-MVP scope:** Separate models for review (Sonnet) vs grading (Haiku for cost)

---

## Non-Functional Requirements

### NFR1: API Key Security

**NFR1.1:** API keys never committed to version control
- **Rationale:** Security policy compliance, prevent credential leaks
- **Source:** Critical finding v1-constraint-finder-002
- **Acceptance Criteria:**
  - API keys stored in environment variables or local config files (gitignored)
  - `.gitignore` includes patterns for credential files
  - Pre-commit hook blocks commits containing API key patterns

**NFR1.2:** Work/personal key separation for audit compliance
- **Rationale:** Billing attribution, corporate policy compliance
- **Source:** Critical finding v1-constraint-finder-002
- **Acceptance Criteria:**
  - Personal development uses personal API keys or Bedrock credentials
  - Work context uses separate Bedrock IAM roles
  - Key rotation procedure documented (frequency and process TBD in Phase 1)

---

### NFR2: Cost Tracking

**NFR1.1:** Log token usage and cost per eval run
- **Rationale:** Stay within $2000/month budget, optimize spend
- **Source:** CLAUDE.md (budget), ADR-005 (cost optimization)
- **Acceptance Criteria:**
  - EvalLog includes per-sample token counts (input, output, total)
  - Cost calculated using Claude API pricing (Sonnet $3/$15 per MTok, Opus $15/$75, Haiku $0.25/$1.25)
  - Summary report shows total cost per eval run

**NFR1.2:** Target <$0.50 per eval run (MVP)
- **Rationale:** Enable frequent iteration without budget concerns
- **Source:** ADR-005 (cost target)
- **Acceptance Criteria:**
  - v3 Critical findings eval (22 findings) costs <$0.50
  - If cost exceeds target, report flags for optimization (model tiering, batch API)

---

### NFR3: Model Tiering

**NFR2.1:** Use Sonnet for LLM-as-judge scorers (post-MVP)
- **Rationale:** Balance cost and quality for subjective evaluation
- **Source:** ADR-005 (model tiering), CLAUDE.md (opusplan mode)
- **Post-MVP scope:** Finding quality scorer, pattern extraction scorer

**NFR2.2:** Use Haiku for mechanical scorers (post-MVP)
- **Rationale:** Severity calibration is deterministic math, doesn't need Sonnet
- **Source:** ADR-005 (model tiering)
- **Post-MVP scope:** Optimize severity calibration scorer to use Haiku

**NFR2.3:** Use Opus sparingly for baseline establishment
- **Rationale:** Highest quality model for ground truth validation, too expensive for regular evals
- **Source:** ADR-005 (model tiering)
- **Post-MVP scope:** Run Opus baseline once, use Sonnet for iterations

---

### NFR4: Batch API Integration

**NFR3.1:** Deferred to post-initial-development
- **Rationale:** 1-24 hour delay would slow down development velocity, add after MVP validated
- **Source:** User Q&A (Q6 - defer batch to avoid slowing development)
- **Post-MVP scope:** Batch API integration for 50% cost reduction on offline evals

**NFR3.2:** Batch API only for offline evals (not interactive)
- **Rationale:** 1-24 hour delay unsuitable for interactive review sessions
- **Source:** ADR-005 (batch timing limitations)
- **Post-MVP scope:** CI/CD nightly evals via batch API

---

### NFR5: Development Velocity

**NFR4.1:** Local eval runs complete in <5 minutes for rapid iteration
- **Rationale:** Enable tight feedback loop during scorer development
- **Source:** Job 1 outcome (data-driven confidence), user Q&A (local validation)
- **Acceptance Criteria:**
  - v3 Critical findings eval (22 findings) completes in <5 minutes on MacBook Pro
  - If eval exceeds 5 minutes, flag for optimization (reduce test dataset size, use Haiku)

**NFR4.2:** Inspect View UI accessible for debugging
- **Rationale:** Visual debugging faster than parsing JSON logs
- **Source:** ADR-005 (Inspect AI log viewer)
- **Acceptance Criteria:**
  - `inspect view` command launches web UI
  - UI displays eval results, per-sample scores, token usage, errors

---

### NFR6: Reproducibility

**NFR5.1:** Eval definitions in version control (git)
- **Rationale:** Track eval changes alongside skill changes
- **Source:** ADR-005 (eval definitions in evals/ directory)
- **Acceptance Criteria:**
  - `evals/` and `scorers/` directories in git
  - Eval runs use git commit hash for versioning
  - Reproducing eval requires only: git checkout, dataset, API key

**NFR5.2:** Datasets in version control (git) or referenced by hash
- **Rationale:** Ground truth stability for regression detection
- **Source:** FR6 (baseline metrics)
- **Acceptance Criteria:**
  - `datasets/` directory in git (if datasets <1MB) OR
  - Datasets stored externally with content hash references (if datasets >1MB)

---

## MVP Scope Summary

**Phase 0: Establish Ground Truth (Target: 2-4 weeks, PREREQUISITE)**
1. Human expert validation of v3 Critical findings (22 findings)
2. Each finding classified: real flaw / false positive / ambiguous
3. Document validation process and criteria
4. Create `datasets/v3_review_validated/` with confirmed findings only
5. Target: ≥15 validated findings for sufficient test data
6. Success criteria: Ground truth dataset exists, validation documented

**Phase 1: Validate Integration Pattern (Target: 1 week)**
1. Install Inspect AI, configure Anthropic provider
2. Build `severity_calibration_scorer.py` (Critical findings only)
3. Convert validated ground truth to Inspect AI Dataset format
4. Run first eval: baseline detection rate for validated Critical findings
5. Build coarse-grained ablation test (drop skill content → detection rate drops >50%)
6. Success criteria: Eval runs locally, validates against confirmed flaws, ablation test passes

**Phase 2: Expand Test Coverage (Post-MVP)**
7. Add Important/Minor findings to severity calibration
8. Build `finding_quality_scorer.py` (LLM-as-judge)
9. Build `pattern_extraction_scorer.py` (semantic clustering validation)
10. Expand datasets: requirements-light, pattern-extraction, parallax-review
11. Multi-model comparison (Sonnet vs Opus vs Haiku)

**Phase 3: Automate and Optimize (Post-MVP)**
12. CI/CD integration (run evals on PR branches)
13. Batch API integration (50% cost reduction)
14. Model tiering optimization (Haiku for mechanical, Sonnet for LLM-as-judge)
15. Fine-grained ablation tests (per-persona contribution)

**Explicitly Deferred:**
- Finding quality scorer (LLM-as-judge complexity)
- Pattern extraction scorer (requires semantic clustering validation)
- Transcript analysis scorer (Issue #37, complex implementation)
- Input corruption adversarial tests (edge case complexity)
- Multi-model comparison (validate single model first)
- Batch API (avoid slowing initial development)
- CI/CD automation (manual evals sufficient for MVP)
- Fine-grained ablation (coarse-grained validates pattern first)

---

## Success Criteria

**MVP Complete When:**
1. ✅ Ground truth validated (Phase 0): ≥15 confirmed Critical findings from v3 review
2. ✅ Inspect AI installed, configured with Anthropic provider
3. ✅ Severity calibration scorer runs on validated Critical findings
4. ✅ Baseline detection rate ≥90% on validated ground truth (proves skills catch real flaws) — threshold provisional, adjust based on MVP results
5. ✅ Ablation test validates skill content contributes >50% to detection rate
6. ✅ Eval runs locally in <5 minutes
7. ✅ Cost per eval run <$2.00 (revised from $0.50, see constraint-finder-003)
8. ✅ EvalLog captures token usage, cost, latency

**Post-MVP Expansion Criteria:**
- All four scorers operational (severity, quality, patterns, transcripts)
- Multi-model comparison suite (Sonnet vs Opus vs Haiku)
- CI/CD integration (evals run on PR branches)
- Batch API integration (50% cost reduction on nightly evals)
- Fine-grained ablation tests (per-persona contribution analysis)

---

## Open Questions

1. **Ablation threshold:** Is >50% detection rate drop the right threshold for "skill content matters"? Or should it be stricter (>70%)?
2. **Baseline update frequency:** How often should baselines be recalculated as skills evolve? After every major skill change, or periodically (weekly/monthly)?
3. **Multi-model grading:** Should we use Haiku as LLM-as-judge grader (cost) or Sonnet (quality)? Or start with Sonnet, optimize to Haiku later?
4. **Dataset size for MVP:** 15+ validated Critical findings from v3 review — is this sufficient sample size, or should we include requirements-light Critical findings too?

---

## References

- **ADR-005:** Prior art integration decisions (Inspect AI + LangGraph)
- **Issue #5:** Skill testing eval/grader framework
- **parallax-review-requirements-v1.md:** Design review skill requirements (FR1.2 planted flaw detection target)
- **MEMORY.md:** v3 review summary (87 findings, 22 Critical, 47 Important, 18 Minor)
- **Inspect AI docs:** https://inspect.aisi.org.uk/
