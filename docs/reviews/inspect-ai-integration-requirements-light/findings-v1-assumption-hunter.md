# Assumption Hunter Review

**Document:** `docs/requirements/inspect-ai-integration-requirements-v1.md`
**Reviewer:** Assumption Hunter
**Date:** 2026-02-16
**Findings:** 20 (5 Critical, 11 Important, 4 Minor)

---

## Executive Summary

The Inspect AI integration requirements document makes foundational assumptions about ground truth validity, statistical methodology, and confidence measurement that block implementation. Three critical failures:

1. **Ground truth is assumed valid without verification** (Finding 001): The entire eval framework optimizes against v3 review findings, but no one validated v3 findings are correct. Garbage in, garbage out at the foundation.

2. **Confidence measurement is undefined** (Finding 013): 95% confidence threshold appears in 5 places but never defines how confidence is calculated. Unimplementable requirement.

3. **Skill versioning strategy is undefined** (Finding 005): FR7.1 requires running evals against different skill versions via git commit, but doesn't specify how this works if skill definitions are external or if checking out old commits breaks eval code.

Additional systemic issues: Statistical thresholds (10% regression, 50% ablation, 70% detection rate) lack empirical justification. Small sample size (N=22) produces unstable metrics but requirements don't validate statistical power. Manual validation workflow assumes human capacity exists but doesn't model throughput or cost.

**Recommendation:** Address 5 Critical findings before implementation. 11 Important findings reveal calibration gaps (thresholds without justification) that undermine success criteria validity.

---

## Findings

### Finding 001: Assumes v3 review findings are valid ground truth without verification
- **Severity:** Critical
- **Phase:** calibrate (primary), survey (contributing)
- **Section:** FR3: Test Datasets
- **Issue:** FR3.1 states v3 review has "22 Critical findings (ground truth count from MEMORY.md v3 summary)" without validating that these findings are actually correct. The entire eval framework's validity depends on ground truth accuracy, but there's no requirement to verify v3 findings before using them as oracle.
- **Why it matters:** If v3 Critical findings contain false positives or miss real issues, the eval framework will optimize for wrong outcomes. Detection rate metrics become meaningless. A skill that catches real problems v3 missed would be scored as having false positives. Garbage in, garbage out at the foundation.
- **Suggestion:** Add FR3.4: Ground truth validation requirement. Before converting v3 to dataset, have 2+ independent reviewers (human or LLM) validate each Critical finding against design doc. Only findings with >90% inter-rater agreement become ground truth. Document validation process and agreement scores in dataset metadata.

---

### Finding 002: Assumes Inspect AI Dataset format is documented and stable
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** FR3.1: Convert v3 review artifacts to Inspect AI Dataset format
- **Issue:** Requirement says "Convert v3 review artifacts to Inspect AI Dataset format" but doesn't specify what that format is, where to find documentation, or whether it's stable across Inspect AI versions. No schema example, no reference to Inspect AI docs section.
- **Why it matters:** If Dataset format is undocumented or changes between Inspect AI versions, conversion work might be wasted or break silently. Developer has to hunt through Inspect AI docs/examples to figure out expected structure. Version incompatibilities could break evals after Inspect AI updates.
- **Suggestion:** Add to FR3.1 acceptance criteria: (1) Document Inspect AI Dataset schema reference (link to docs or reproduce schema), (2) Pin Inspect AI version in requirements.txt with comment about Dataset format dependency, (3) Include example of converted finding in Dataset format.

---

### Finding 003: Assumes manual validation workflow is practical at scale
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** FR2.3: Manual validation workflow, FR3.3: Manual validation gate
- **Issue:** Requirements mandate manual review for <95% confidence findings (FR2.3) and ground truth creation (FR3.3) but don't specify: who performs validation, how long it takes per finding, what happens if validation queue grows large. If v3 has 22 Critical findings and 50% need manual review, that's 11 findings to validate before first eval can run.
- **Why it matters:** Manual validation could become a bottleneck that blocks all eval development. If validation takes 5 minutes per finding, 11 findings = 55 minutes of manual work before first eval. If validation is delegated to subagent, need to specify subagent instructions, acceptance criteria, and how to handle subagent errors.
- **Suggestion:** Add NFR6: Manual validation scalability. Specify: (1) Target validation time <2 minutes per finding, (2) Subagent validation instructions with example prompts, (3) Batch validation workflow (not one-by-one), (4) Fallback: if validation queue exceeds 20 findings, use high-confidence subset only and defer full validation.

---

### Finding 004: Assumes 22 Critical findings is sufficient sample size without statistical justification
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** Open Questions #5, FR3.1: Dataset metadata
- **Issue:** Open question asks "is 22 Critical findings sufficient sample size" but requirements don't specify what statistical power is needed for valid conclusions. Is 22 enough to detect 10% detection rate regression (FR6.2)? What's the confidence interval on baseline metrics with N=22?
- **Why it matters:** Small sample sizes produce unstable metrics. With N=22, missing 2 findings changes detection rate by 9% (2/22), which is close to the 10% regression threshold. Random variation could trigger false regressions. Baseline metrics might not generalize to new test cases.
- **Suggestion:** Add FR3.5: Sample size validation. Before establishing baseline (FR6.1), calculate required sample size for 80% power to detect 10% detection rate change with 95% confidence. If N=22 is insufficient, expand dataset (add requirements-light Critical findings) or relax regression threshold to 15-20%. Document statistical justification in baseline metadata.

---

### Finding 005: Assumes skill version can be referenced by git commit without skill definition being in git at that commit
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** FR7.1: Support running evals against different skill versions
- **Issue:** FR7.1 says eval runner accepts `--skill-version` parameter (git commit hash or branch) but doesn't specify how this works. If skill definitions are in a different repo (superpowers plugin?), git commit hash is meaningless. If skill is defined inline in SKILL.md files that change over time, checking out old commit changes eval code too.
- **Why it matters:** Version comparison is impossible if you can't isolate skill changes from eval changes. If eval runner code and skill definition both live in parallax repo, checking out old commit might check out broken eval code. If skill is external (superpowers plugin), git hash doesn't reference skill version at all.
- **Suggestion:** Add FR7.3 (was deferred, now prerequisite): Define skill versioning strategy. Options: (1) Copy skill content into eval dataset at eval creation time (snapshot approach), (2) Store skills in separate repo with stable import path, (3) Version skill content via content hash instead of git commit. Choose one and specify in FR7.1 acceptance criteria.

---

### Finding 006: Assumes planted flaw detection requires creating new design docs, not reusing existing docs with known issues
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** FR5.1: Planted flaw detection tests
- **Issue:** FR5.1 says "Test dataset includes design docs with planted flaws" implying creation of new synthetic docs. But parallax already has design docs with documented real flaws (v3 review findings). Why create synthetic flaws when you have real ones?
- **Why it matters:** Creating synthetic design docs with planted flaws is expensive (write realistic doc, plant flaw subtly enough to be realistic) and might not reflect real failure modes. Reusing v3 design doc (which had 87 real findings) is cheaper and more realistic. Only need synthetic docs if you want to test flaws v3 didn't have.
- **Suggestion:** Clarify FR5.1: Phase 1 uses v3 design doc as planted flaw test case (flaws are documented findings). Phase 2 (post-MVP) creates synthetic docs for flaw types not represented in v3. Update acceptance criteria to specify which flaw types v3 covers (architectural gaps, assumption violations, edge cases) and which require synthetic docs.

---

### Finding 007: Assumes Bedrock provider support is optional without understanding work context constraints
- **Severity:** Important
- **Phase:** survey (primary)
- **Section:** FR1.2: Anthropic provider with Bedrock optionally supported
- **Issue:** FR1.2 says "Bedrock provider optionally supported for work context" but doesn't specify what work context means or what constraints exist. If work context requires Bedrock (e.g., corporate policy, API key restrictions), optional support becomes mandatory. If work context requires different authentication (IAM roles), Anthropic provider won't work.
- **Why it matters:** If Bedrock is actually required for work usage and marked optional, eval framework won't be usable in work context. If work context has different cost structure (Bedrock pricing differs from direct Anthropic), cost targets (NFR1.2: <$0.50 per run) might be wrong. If authentication differs, setup instructions will be incomplete.
- **Suggestion:** Add FR1.4: Work context requirements analysis. Before implementation, document: (1) What is work context (corporate laptop, specific AWS account, CI/CD environment)?, (2) Which provider is required/preferred in work context?, (3) Authentication differences between providers, (4) Cost differences between Anthropic direct and Bedrock pricing for Sonnet/Opus/Haiku. Update FR1.2 from optional to required or remove work context mention.

---

### Finding 008: Assumes cost calculation based on list pricing without considering prompt caching savings
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** NFR1.1: Cost calculated using Claude API pricing
- **Issue:** NFR1.1 specifies pricing (Sonnet $3/$15 per MTok, Opus $15/$75, Haiku $0.25/$1.25) but these are base rates. ADR-005 mentions prompt caching (90% input cost reduction on cache hits), and eval workloads are perfect for caching (repeated system prompts). Not accounting for caching makes cost estimates 5-10x too high.
- **Why it matters:** Cost targets might be overly conservative. NFR1.2 targets <$0.50 per eval run, but with prompt caching this might be <$0.05. Budget planning based on non-cached pricing overestimates spend. Optimization decisions (e.g., "use Haiku to save money") might be premature if cached Sonnet is already cheap enough.
- **Suggestion:** Add NFR1.3: Prompt caching cost modeling. Calculate expected cache hit rate for eval workloads (system prompt repeated across all findings in dataset). Update cost formula to: input_cost = (input_tokens * (1 - cache_hit_rate) * input_price) + (cached_input_tokens * cached_input_price). Revise cost targets in NFR1.2 based on realistic cached pricing.

---

### Finding 009: Assumes latency metrics matter without defining acceptable latency range or usage context
- **Severity:** Minor
- **Phase:** calibrate (primary)
- **Section:** FR1.3: EvalLog captures latency metrics
- **Issue:** FR1.3 requires logging latency with retry tracking, but no requirement specifies why latency matters or what acceptable range is. NFR4.1 says <5 minutes total runtime, but doesn't break down per-finding latency budget. If latency is just logging for curiosity, it's low-value complexity.
- **Why it matters:** Without acceptance criteria for latency, you can't tell if latency is good or bad. If evals take 4 minutes instead of 5, should you optimize further or is it good enough? If retry tracking shows 20% of requests need retries, is that a problem or expected? Logging without thresholds adds instrumentation debt.
- **Suggestion:** Either: (1) Add NFR4.3: Latency targets (e.g., p50 <10s per finding, p99 <30s, retries <5%), or (2) Remove latency requirement from FR1.3 MVP and defer to post-MVP observability phase. If latency monitoring doesn't block MVP validation, it's premature.

---

### Finding 010: Assumes >70% detection rate target (FR5.1) is validated without source for the threshold
- **Severity:** Minor
- **Phase:** calibrate (primary)
- **Section:** FR5.1: Target >70% detection rate for planted Critical flaws
- **Issue:** FR5.1 acceptance criteria states ">70% detection rate for planted Critical flaws (from FR1.2 acceptance criteria in parallax-review-requirements-v1.md)" but this is circular—it's not clear where 70% threshold comes from or why it's the right number. Was it empirically validated, is it an industry standard, or is it a guess?
- **Why it matters:** If 70% threshold is arbitrary, success criteria is arbitrary. If threshold is too low (70% means missing 3 out of 10 Critical flaws), skill might pass evals but fail in production. If threshold is too high (skill actually achieves 65% and that's state-of-art), skill fails evals unfairly.
- **Suggestion:** Add to Open Questions: What is acceptable detection rate for Critical findings? Validate threshold by: (1) Measuring human reviewer detection rate on same dataset (upper bound), (2) Measuring baseline v3 detection rate (current performance), (3) Setting threshold at 80% of human performance or 20% improvement over baseline, whichever is achievable. Document threshold rationale in FR5.1.

---

### Finding 011: Assumes ablation test >50% drop proves skill content matters without considering base rate
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** FR4.1: Ablation test validates skill content contributes >50%
- **Issue:** FR4.1 says dropping skill content should degrade detection rate by >50% (e.g., 80% → <40%) to prove skill matters. But if baseline model without skill already achieves 30% detection (random guessing or general reasoning), then 40% after ablation only proves 10% value-add, not that skill content is essential.
- **Why it matters:** Ablation threshold doesn't account for model's inherent capability. If Claude Sonnet without any skill instructions catches 50% of Critical findings (strong base reasoning), then 60% with skill is only 10% improvement. Skill content matters less than assumed. Conversely, if base model catches 10%, then 70% with skill proves skill is load-bearing.
- **Suggestion:** Add FR4.4: Baseline model capability test. Run eval with minimal prompt ("Review this design doc for flaws") to measure base detection rate without skill. Revise FR4.1 threshold to: ablated detection rate must drop to within 20% of baseline (proves skill adds >X% beyond base model). Document base rate in ablation test acceptance criteria.

---

### Finding 012: Assumes severity distribution thresholds (Critical <30%, Important 40-50%, Minor 20-30%) are validated without empirical basis
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** FR2.1: Severity calibration scorer validates distribution thresholds
- **Issue:** FR2.1 specifies severity distribution targets (Critical <30%, Important 40-50%, Minor 20-30%) but doesn't cite source or validation. Are these empirically derived from v3 review (22C/47I/18M = 25%/54%/21%, roughly matches), theoretical ideal, or arbitrary? If v3 actual distribution was 25%/54%/21%, why is target <30%/40-50%/20-30% instead of ±5% of v3?
- **Why it matters:** If thresholds don't reflect actual distribution of real design flaws, scorer will always fail or always pass. If v3 naturally produces 25% Critical findings but target is <30%, every review passes even if severity calibration is broken. If target is <20% Critical, every review fails even if severity judgments are accurate. Thresholds need empirical grounding.
- **Suggestion:** Add FR2.4: Severity distribution validation. Analyze v3 review and requirements-light reviews to calculate observed severity distributions. Set thresholds to ±10% of observed distribution (acknowledges natural variation). If observed Critical rate is 25%, threshold is 15-35%. Document observed distributions and threshold derivation in FR2.1 rationale.

---

### Finding 013: Assumes <95% confidence threshold is achievable without defining how confidence is measured
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** FR2.3: <95% confidence findings flagged for manual review
- **Issue:** Requirements repeatedly reference 95% confidence threshold (FR2.3, FR3.3, Open Question #1) but never define how confidence is calculated. Is it LLM self-reported confidence ("I'm 90% sure"), semantic similarity to ground truth, inter-rater agreement, or something else? Without definition, 95% threshold is unimplementable.
- **Why it matters:** Different confidence measures produce wildly different results. LLM self-reported confidence is often poorly calibrated (says 95% but wrong 20% of time). Semantic similarity is expensive (requires embedding model). Inter-rater agreement requires multiple reviewers per finding. If confidence measure is undefined, manual validation gate can't be built.
- **Suggestion:** Add FR2.5: Confidence scoring methodology. Choose one: (1) LLM self-assessment with calibration validation (measure actual accuracy at each confidence level), (2) Semantic similarity threshold (cosine similarity >0.9 to ground truth finding), (3) Multi-reviewer consensus (3 reviewers, ≥2 agree = high confidence). Document chosen method in FR2.3 and validate calibration before using for automated gating.

---

### Finding 014: Assumes regression detection threshold (>10% drop) is sensitive enough without considering variance
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** FR6.2: Regression detected if detection rate drops >10%
- **Issue:** FR6.2 flags regression if detection rate drops >10%, but with N=22 Critical findings, 10% = 2.2 findings. Natural variance in LLM sampling could cause ±1-2 finding differences even with identical skill. If baseline is 80% (17.6/22 detected), rerun might get 75% (16.5/22) purely from sampling, triggering false regression.
- **Why it matters:** 10% threshold might be too sensitive for small datasets, causing false regression alerts. Developer wastes time investigating "regressions" that are actually random noise. Alternatively, 10% might be too lenient—if skill change breaks detection for a specific finding type, might only drop 5% (1 finding) and not trigger alert.
- **Suggestion:** Add FR6.3: Statistical significance testing for regression detection. Don't use fixed 10% threshold; run statistical test (e.g., Fisher's exact test, p<0.05) to determine if detection rate change is significant given sample size. For N=22, calculate minimum detectable effect size. If variance is too high, increase sample size or use multiple eval runs per version to average out noise.

---

### Finding 015: Assumes local MacBook Pro runtime is representative of CI/CD environment performance
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** NFR4.1: Evals complete in <5 minutes on MacBook Pro
- **Issue:** NFR4.1 targets <5 minutes on MacBook Pro but doesn't specify MacBook specs (M1/M2/M3, RAM, network). More importantly, doesn't consider that CI/CD environment (Phase 3) will have different performance characteristics. If CI runner has slower network, runtime might be 10 minutes even though local is 5 minutes.
- **Why it matters:** Performance target only valid for specific hardware. If other developers have slower machines or different network conditions, they can't meet <5 minute target. When evals move to CI/CD (Phase 3), performance assumptions break. If CI runtime is 15 minutes, PR feedback loop becomes impractical.
- **Suggestion:** Update NFR4.1: Specify reference hardware (e.g., M1 MacBook Pro, 16GB RAM, 100Mbps network). Add NFR4.4 (Phase 3): CI/CD runtime target <10 minutes (allows for slower CI environment). Document that local target is for development velocity, CI target is for automation practicality.

---

### Finding 016: Assumes Inspect View UI works without specifying hosting/access requirements
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** NFR4.2: Inspect View UI accessible for debugging
- **Issue:** NFR4.2 says "`inspect view` command launches web UI" but doesn't specify: Does it run locally? What port? Does it require internet access? Can multiple people view same results (team review)? If eval runs in CI/CD, how do you access the UI?
- **Why it matters:** If Inspect View requires internet access or external hosting, might not work in restricted networks. If it's local-only, can't share results with team ("look at my eval results" requires screenshare). If it binds to default port, might conflict with other services. If CI/CD runs eval, no one can access localhost UI.
- **Suggestion:** Add to NFR4.2 acceptance criteria: (1) Inspect View runs on localhost:PORT (specify port or document configuration), (2) Results viewable from exported JSON logs (don't require running web UI), (3) Phase 3: consider deploying Inspect View to shared server for team access to CI/CD eval results.

---

### Finding 017: Assumes dataset size <1MB vs >1MB is the right threshold for git vs external storage without considering git-lfs
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** NFR5.2: Datasets in git if <1MB, external if >1MB
- **Issue:** NFR5.2 uses 1MB as threshold for storing datasets in git vs external with hash references. But git-lfs (Large File Storage) exists specifically for this use case. 1MB is small (22 findings × ~1KB each = 22KB, well under 1MB). When would datasets exceed 1MB to trigger external storage?
- **Why it matters:** 1MB threshold seems arbitrary without usage analysis. If datasets never exceed 1MB, external storage option is YAGNI complexity. If datasets do exceed 1MB (e.g., 1000-finding combined dataset), git performance degrades. External storage adds dependency (where? S3? local filesystem?) and complicates reproducibility (need hash, need storage access, need download step).
- **Suggestion:** Simplify NFR5.2 for MVP: Store all datasets in git (parallax is public repo, git hosts tolerate datasets up to 100MB). Add comment: If dataset size exceeds 50MB, consider git-lfs. Defer external storage to post-MVP only if dataset size actually becomes problem. Remove complexity for theoretical problem.

---

### Finding 018: Assumes coarse-grained ablation tests (section-level) will reveal whether skill content matters without testing incremental degradation
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** FR4.2: Coarse-grained ablation (section-level removal)
- **Issue:** FR4.2 drops entire sections (persona descriptions, verdict logic, synthesis instructions) to test contribution, but this is all-or-nothing. If dropping all personas reduces detection 60% (passes >50% threshold), doesn't tell you whether all personas are necessary or just 1-2 key ones. Might be over-retaining content that doesn't contribute.
- **Why it matters:** Coarse-grained ablation prevents optimization. If all 6 personas together contribute 60% but individually only 10% each, could drop 4 personas and retain 80% of value (4 personas × 10% = 40% retained + 40% baseline = 80% total). Coarse test passes but skill has 4 unnecessary personas adding cost and latency. Conversely, if 1 persona contributes 50% and others 2% each, coarse test masks critical dependency.
- **Suggestion:** Add FR4.5: Incremental ablation test. After coarse-grained ablation validates section matters (FR4.2), run incremental ablation: drop one component at a time, measure impact. Phase 1: section-level (validates approach). Phase 2: component-level (e.g., drop assumption-hunter persona, measure delta). Use results to prune low-contribution content before moving to production.

---

### Finding 019: Assumes F1 score is appropriate metric without considering precision-recall tradeoff preference
- **Severity:** Minor
- **Phase:** calibrate (primary)
- **Section:** FR2.2: Reports detection rate (recall), precision, F1 score
- **Issue:** FR2.2 reports recall, precision, and F1, but doesn't specify which metric is primary optimization target. F1 treats precision and recall equally, but for design review, false negatives (missed real flaws) are worse than false positives (flagged non-issues that get rejected). Should optimize recall over precision, not balance equally.
- **Why it matters:** Different metrics drive different optimization decisions. If optimizing F1, might accept 70% recall / 70% precision (F1=0.70). If optimizing recall, might accept 90% recall / 50% precision (F1=0.64, lower but better outcome—catch more flaws, user filters false positives). Wrong metric leads to wrong skill tuning.
- **Suggestion:** Add FR6.4: Metric prioritization. Specify primary metric is recall (catch real flaws), secondary is precision (reduce noise). Target: ≥80% recall, ≥60% precision (acceptable to flag extra findings if user can quickly reject). Report F1 for reference but don't optimize for it. Document metric tradeoff rationale in FR2.2.

---

### Finding 020: Assumes success criteria checkboxes mean buildable implementation without validation plan
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Success Criteria: MVP Complete When
- **Issue:** Success criteria lists 8 checkboxes (e.g., "Severity calibration scorer runs on v3 Critical findings", "Eval runs locally in <5 minutes") but doesn't specify how to validate each criterion. What does "runs" mean—completes without error, produces expected output, passes threshold tests? Who validates (developer self-check, peer review, automated test)?
- **Why it matters:** Without validation plan, success criteria become subjective. Developer might check "ablation test validates >50% contribution" based on one run that happened to pass, but test might be flaky (50% pass rate). Criteria like "manual validation workflow operational" are vague—does "operational" mean works for 1 finding, 10 findings, 100 findings?
- **Suggestion:** Add section after Success Criteria: Validation Plan. For each criterion, specify: (1) How to test (manual steps, automated test, acceptance test), (2) Pass/fail threshold (e.g., 3/3 runs pass, not just 1/3), (3) Who validates (developer, reviewer, automated CI). Convert subjective checkboxes into objective acceptance tests.

---

## Blind Spot Check

What might I have missed given my focus on assumptions?

**Implementation complexity:** I focused on unstated assumptions but not on whether the stated requirements are actually achievable. For example, FR2.1 severity calibration scorer might be straightforward, but FR7.1 skill version comparison could require significant git plumbing. A feasibility review would catch "this requirement is technically possible but will take 10x longer than estimated."

**User workflow fit:** I validated whether requirements are internally consistent but not whether they match actual user workflow. A UX-focused review would ask: "If manual validation takes 55 minutes (Finding 003), will users actually do it or will they skip validation and corrupt ground truth?" Behavioral assumptions about user compliance aren't covered by assumption hunting.

**Integration friction:** I caught that Bedrock provider support is vaguely specified (Finding 007) but didn't analyze broader integration risks. What if Inspect AI's Dataset format requires all samples to be JSON serializable, but parallax findings include nested objects that don't serialize cleanly? A systems integration review would map all data format boundaries and validate compatibility.

**Cost model accuracy:** Finding 008 catches missing prompt caching in cost calculation, but I didn't validate the base pricing numbers ($3/$15 for Sonnet). If those numbers are stale or apply to different API endpoints (direct vs Bedrock), cost estimates are wrong even after adding caching. A cost optimization review would verify current pricing and identify all cost levers (model choice, batching, sampling parameters).

**Phase boundaries:** I classified findings by phase but didn't validate whether the phase sequencing makes sense. For example, FR4 (ablation tests) is listed in MVP Phase 1, but ablation requires baseline metrics (FR6.1), which requires working scorer (FR2.1), which requires validated ground truth (FR3.3). A dependency analysis would expose that Phase 1 subtasks have hidden ordering constraints that could block parallel work.
