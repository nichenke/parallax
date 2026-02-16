# Feasibility Skeptic Review

## Changes from Prior Review

This is iteration 3. Prior review (iteration 2) identified 11 findings from Feasibility Skeptic (2 Critical, 9 Important). Key changes since iteration 2:

**Accepted dispositions synced to design doc (23 total from all reviewers):**
- Voice guidelines added to Per-Reviewer Output Format section
- Primary + contributing phase classification specified in Finding Phase Classification
- Severity range handling specified in Verdict Logic
- Prompt caching architecture added in Reviewer Prompt Architecture section
- Auto-fix mechanism added in UX Flow Step 4
- Cross-iteration tracking mechanism added to design
- Reviewer capabilities section added specifying tool access

**Previously flagged issues that should be resolved:**
- Finding 2 (JSONL format missing) — still not in design per iteration 2 dominant theme
- Finding 3 (Minimum viable reviewer set) — coverage analysis not specified
- Finding 4 (Synthesis consolidation heuristics) — deduplication rules still undefined
- Finding 7 (Verdict timing) — still computed before user processing
- Finding 9 (Reviewer prompt versioning) — versioning strategy not specified
- Finding 10 (Second Brain test case) — external validation still not run
- Finding 11 (Cost per review run) — empirical data still unknown

**New areas to examine in iteration 3:**
- How well do synced sections address prior documentation debt?
- Do newly-added sections introduce implementation complexity?
- Are multi-causal phase classification and systemic issue detection buildable as specified?

## Complexity Assessment

**Overall complexity:** Medium-High

Design complexity increased with iteration 2 accepted dispositions. Auto-fix mechanism, cross-iteration finding tracking, primary+contributing phase classification, and systemic issue detection all add state management and judgment requirements. The design is buildable but significantly more complex than MVP described in iteration 1.

**Riskiest components:**
1. **Cross-iteration finding tracking with semantic matching** — LLM-based finding deduplication across iterations requires N_new × N_prior comparisons. For 30 findings across 3 iterations, that's up to 900 semantic similarity evaluations. Token cost and latency risk.
2. **Auto-fix git workflow** — Separate commit for auto-fixes before human processing conflicts with user's ability to reject fixes. Temporal ordering is unsolvable if user makes intervening changes.
3. **Systemic issue detection** — Threshold-based pattern detection (">30% of findings share contributing phase") requires semantic clustering of root causes. Classification taxonomy undefined, detection heuristics undefined.

**Simplification opportunities:**
1. **Defer cross-iteration semantic matching to v2** — Use section-based anchoring for MVP (simple but lossy). Add LLM semantic matching after empirical data shows it's worth the cost.
2. **Cut auto-fix from MVP** — Evaluate whether finding type distribution justifies automation (if 90% require human judgment, auto-fix is 10% value for 40% complexity).
3. **Make systemic detection advisory, not automatic** — Synthesizer flags potential patterns for user review rather than auto-escalating. Removes need for root cause taxonomy and threshold tuning.

## Findings

### Finding 1: Design Doc Sync Incomplete — JSONL Still Missing
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Output Artifacts, Per-Reviewer Output Format, Summary Format
- **Issue:** Iteration 2 dominant theme was documentation debt — 23 accepted dispositions not reflected in design doc. Sync completed for most areas (voice guidelines, prompt caching, phase classification), but JSONL format specification is still completely missing. MEMORY.md states "JSONL as canonical output format—decided but not yet implemented." Multiple iteration 2 disposition notes reference JSONL ("jq filters by severity/persona/phase"). Four reviewers flagged this independently in iteration 2. Design doc still specifies markdown-only output.
- **Why it matters:** JSONL vs markdown affects finding IDs (stable JSON id field vs text hashing), disposition tracking (structured fields vs prose), CLI tooling (jq vs grep), and machine processability. This is the largest structural decision not documented. If JSONL is canonical, current markdown spec describes throwaway scaffolding. Migration later requires rewriting file I/O and parsing logic.
- **Suggestion:** Add JSONL schema specification to design doc or explicitly defer to v2 with migration path. Minimal schema: one JSON object per finding with `{id, reviewer, severity, phase_primary, phase_contributing, section, issue, why_it_matters, suggestion, iteration, disposition, disposition_note}`. Specify whether reviewers output JSON directly or synthesizer converts markdown to JSONL. Clarify "markdown works for MVP" means "sufficient for prototype" (acceptable) or "permanent format" (conflicts with JSONL decision).

### Finding 2: Cross-Iteration Finding Tracking Complexity Underestimated
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** Cross-Iteration Finding Tracking (newly added section)
- **Issue:** Design now specifies "Finding IDs: Stable hash derived from section + issue content" with note "see Assumption Hunter Finding 3 for hash brittleness concerns" but provides no resolution. Text-based hashing breaks when findings evolve ("no retry logic" iteration 1 becomes "retry lacks backoff" iteration 2 = different hash). Alternative is "LLM-based matching: synthesizer compares new findings to prior findings and flags semantic overlap" but token cost and complexity are not estimated.
- **Why it matters:** LLM semantic matching requires N_new × N_prior comparisons every re-review. For 30 findings across 3 iterations: iteration 2 does 30×30=900 comparisons, iteration 3 does 30×60=1800 comparisons. Each comparison is ~200 tokens (finding A text + finding B text + "are these the same issue?" prompt) × $3 per million input tokens = $0.54 for iteration 2, $1.08 for iteration 3. Costs scale quadratically with iterations. Additionally, synthesizer must make 1800 semantic similarity judgments—error-prone and latency-heavy.
- **Suggestion:** Simplify cross-iteration tracking for MVP. Option 1: Section-based anchoring (findings tracked by section heading + reviewer, simple but lossy). Option 2: Hybrid approach—hash for exact matches, flag potential semantic matches for user confirmation (synthesizer shows "Finding 12 may relate to prior Finding 3, confirm?"). Option 3: Defer semantic matching to v2, use iteration 1-2 data to validate it's worth the cost. Recommend option 1 or 2 for MVP.

### Finding 3: Auto-Fix Git Workflow Has Unsolvable Temporal Ordering
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** UX Flow Step 4 (Auto-Fix, newly added)
- **Issue:** Design now specifies auto-fix step: "Synthesizer classifies findings as auto-fixable vs human-decision-required. Auto-fixable findings applied to design artifact automatically. Auto-fixes committed as separate git commit from human-reviewed changes." This requires: (1) auto-fixes run before user sees findings, (2) auto-fixes modify design doc and commit, (3) user then processes remaining findings and commits. If user made other edits to design doc between starting review and processing findings, auto-fix commit includes unrelated changes. If user rejects an auto-fix during processing, it's already committed. Temporal ordering is unsolvable.
- **Why it matters:** Auto-fix as specified is invasive—modifies source files and commits automatically without user approval for each fix. Conflicts with Git Safety Protocol ("NEVER commit changes unless user explicitly asks"). Additionally, the "separate commit" requirement is impossible if user has intervening changes. If auto-fixes run before user review, user can't reject bad fixes. If after, separate commit is impossible (changes intermixed).
- **Suggestion:** Radically simplify auto-fix or cut from MVP. Option 1: Defer to post-MVP—evaluate finding type distribution from first 5-10 reviews to see if auto-fix ROI justifies complexity. Option 2: Auto-fixes presented as suggested patches (diff format), user approves before application (not automatic). Option 3: Conservative criteria (formatting/whitespace only, zero semantic changes) with explicit approval. Recommend option 1—cut from MVP, validate need with data.

### Finding 4: Systemic Issue Detection Requires Undefined Root Cause Taxonomy
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Finding Phase Classification (primary+contributing), Synthesis responsibilities
- **Issue:** Design now specifies "When >30% of findings share a contributing phase, the synthesizer flags a systemic issue." Implementation requires: (1) detecting which findings "share" a contributing phase (exact match of phase label? semantic similarity of root causes?), (2) computing percentage (how are multi-label findings counted?), (3) determining what "systemic issue" means (advisory flag? automatic escalation?). Root cause attribution is judgment-heavy. Synthesizer must cluster findings semantically to detect patterns.
- **Why it matters:** The 30% threshold is arbitrary (why not 25%? 40%?). "Share a common root cause" is subjective—if 12 findings trace to "missing error handling" but phrased differently, does synthesizer detect this? If threshold is too low, every review triggers false systemic escalations. If too high, real systemic issues are missed. Root cause taxonomy is undefined in design (what are valid contributing phases? how granular?).
- **Suggestion:** Make systemic detection advisory, not automatic, for MVP. Synthesizer notes when multiple findings have same contributing phase label ("7 findings have calibrate gap as contributing phase—may indicate systemic requirements issue") but doesn't auto-escalate. User decides whether pattern is meaningful. Remove 30% threshold (too arbitrary without empirical data). Defer automated clustering to post-MVP when eval data shows whether it adds value.

### Finding 5: Verdict Still Computed Before User Processes Findings
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Verdict Logic, UX Flow Step 5 (Present Summary)
- **Issue:** Iteration 2 flagged this (Finding 43 from Feasibility Skeptic). Design sync did not address it. UX flow still shows verdict presented in Step 5 before findings processed in Step 6. Verdict depends on severity ratings that may be false positives. If user rejects 3 Critical findings as invalid during processing, the "revise" verdict should become "proceed." Design doesn't specify verdict recomputation.
- **Why it matters:** Presenting incorrect verdict wastes cycles and creates anchoring bias. User sees "revise" based on 5 Critical findings, processes findings, rejects 4 as false positives. Actual verdict should be "proceed" but user already committed to revision mindset. Alternatively, user sees "proceed" (no Critical), processes findings, realizes Important finding should be Critical, but workflow said "proceed."
- **Suggestion:** Recompute verdict after finding processing based on accepted findings only. Reorder UX flow: Step 5 shows finding counts (no verdict), Step 6 processes findings, Step 7 computes final verdict based on accepted findings. Alternatively: show provisional verdict in Step 5, final verdict in Step 7, explain difference. Simplest: eliminate provisional verdict, let user decide after processing.

### Finding 6: Synthesis Consolidation Heuristics Still Undefined
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Synthesis responsibilities (deduplication, contradiction surfacing)
- **Issue:** Iteration 2 flagged this (Finding 40 from Feasibility Skeptic). Design sync did not add consolidation rules. Synthesizer must "deduplicate findings flagged by multiple reviewers into single entries" but design provides no heuristics. When are two findings "the same issue"? Same section + similar keywords? Same root cause? Same suggested fix? Iteration 2 had 55 findings across 6 reviewers—how many were duplicates? No data.
- **Why it matters:** Aggressive deduplication loses nuance and reduces finding count artificially. Conservative deduplication floods user with near-duplicates. Inconsistent consolidation across review runs makes iteration comparison unreliable ("finding count dropped from 55 to 30—did design improve or did synthesizer consolidate more?"). Deduplication judgment directly affects verdict (Critical finding count determines revise vs proceed).
- **Suggestion:** Define explicit consolidation rules in Synthesis section. Conservative baseline: deduplicate only if findings reference exact same section AND same root cause. Group related findings under common heading but preserve as separate entries with cross-references ("Flagged by 3 reviewers: Assumption Hunter, Edge Case Prober, Feasibility Skeptic"). Track deduplication decisions in summary ("15 findings consolidated from 22 reviewer flags"). Test on first 2-3 review runs, tune heuristics based on false merges.

### Finding 7: No Exit Criteria for Re-Review Loop
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** Verdict Logic (revise path), UX Flow
- **Issue:** Iteration 2 flagged this (Finding 24 from Edge Case Prober). Design sync did not add stopping criteria. Design specifies `revise` verdict triggers re-review after user updates design. If iteration 2 produces new Critical findings (different from iteration 1), user revises again. Iteration 3 produces more findings. When does loop end? When findings = 0 (unrealistic)? When no new Critical? When user decides "good enough"? Design treats all Critical findings as blockers but provides no framework for acceptable risk.
- **Why it matters:** Without stopping criteria, reviews iterate indefinitely. Real designs have tradeoffs—some edge cases deferred intentionally, some Important findings accepted as constraints. Current verdict logic has no "proceed despite Critical findings with justification" option. User needs escape hatch.
- **Suggestion:** Add review convergence criteria to Verdict Logic section. Options: (1) Explicit threshold ("2 consecutive iterations with no new Critical findings"), (2) User override ("proceed despite Critical findings" with required justification recorded in summary), (3) Iteration count flag (if >3 iterations, prompt user to reconsider scope), (4) Add "defer" disposition for findings user accepts as out-of-scope. Recommend option 2 + option 4 (user control + explicit deferral tracking).

### Finding 8: Reviewer Prompt Versioning Strategy Missing
- **Severity:** Important
- **Phase:** plan (primary), design (contributing)
- **Section:** Reviewer Prompt Architecture (newly added section)
- **Issue:** Design now specifies prompt caching structure (stable prefix + variable suffix) but doesn't address prompt versioning. Iteration 2 notes "Prompt changes to stable prefix invalidate cache and should be tracked as versioned changes" but no versioning strategy specified. If Assumption Hunter's prompt changes between iteration 1 and iteration 2 of reviewing same design, finding differences could be due to prompt changes (not design improvements).
- **Why it matters:** Eval framework depends on comparing review quality across iterations. If you can't distinguish "design improved" from "prompts got better" or "prompts missed things," eval data is noisy. Cross-iteration finding tracking requires stable finding IDs, but if prompts change, same logical issue phrased differently breaks ID matching. Prompt changes invalidate cache (90% cost savings lost) so versioning has cost implications.
- **Suggestion:** Add prompt versioning to Reviewer Prompt Architecture section. Specify: (1) Each prompt file includes version header, (2) Summary.md records prompt versions used per review run, (3) When comparing iterations, note prompt version changes, (4) Major prompt refactor increments version, findings non-comparable to prior versions. Alternatively: adopt immutable prompt strategy post-MVP (prompts locked, improvements go into new personas).

### Finding 9: Cost Per Review Run Still Unknown
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Prototype Scope (cost logging mentioned)
- **Issue:** Iteration 2 flagged this (Finding 55 from Feasibility Skeptic). Design now mentions "Cost logging per review run in JSONL output" but no empirical data from prior review runs. After iteration 1 (smoke test, 44 findings) and iteration 2 (validation run, 55 findings), actual cost data should exist. How much did each review cost? Token counts? Cache hit rate? Budget validation?
- **Why it matters:** Budget is $2000/month with $150-400 projected API spend. Unknown costs make iteration risky. If reviews cost $5 each, you can afford 30-60/month. If $0.20 each, hundreds. Without data, flying blind on burn rate. Critical for eval phase with many review iterations. Additionally, model tiering decisions (Haiku for mechanical reviewers) depend on cost/quality tradeoffs—need baseline.
- **Suggestion:** Instrument next review run (iteration 3) with comprehensive cost logging. Capture: (1) input tokens per reviewer (design + requirements + system prompt), (2) output tokens per reviewer, (3) synthesizer tokens, (4) cache hit rate if enabled, (5) total cost at Sonnet pricing. Log to JSONL as specified. Use data to validate budget assumptions and inform model tiering (test Haiku for 1-2 reviewers, compare quality).

### Finding 10: Minimum Viable Reviewer Set Still Unvalidated
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Reviewer Personas (6 design-stage, 9 total across stages)
- **Issue:** Iteration 2 flagged this (Finding 39 from Feasibility Skeptic). Design sync did not add coverage analysis methodology. Design specifies 6 reviewers for design stage, 9 total personas across stages. No evidence all are necessary or sufficient. Prior Art Scout and First Principles Challenger have overlap (both question problem framing). Edge Case Prober and Feasibility Skeptic both examine "what could go wrong."
- **Why it matters:** Each reviewer adds cost ($0.20-0.50 per reviewer at Sonnet pricing for 5-10k token reviews) and coordination overhead (deduplication, consolidation). If 3 reviewers catch 80% of findings, running 6 is low ROI. Conversely, if gaps exist (security review missing from design stage), 6 insufficient. Problem statement says "optimal N is empirical" but doesn't specify validation method.
- **Suggestion:** Add coverage analysis to Open Questions or Evaluation section. Specify methodology: (1) Tag each finding with which reviewer(s) flagged it, (2) Calculate unique findings per reviewer (high value = keep), (3) Calculate overlap between reviewer pairs (>50% = consolidate), (4) Identify finding categories no reviewer catches (missing persona). Start with 3 core reviewers (Requirement Auditor, Feasibility Skeptic, Edge Case Prober), add one at a time, measure incremental coverage. Run on first 3-5 reviews before committing to 6.

### Finding 11: Second Brain Test Case Still Not Run
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Prototype Scope ("Validate with: Second Brain Design test case")
- **Issue:** Iteration 2 flagged this (Finding 54 from Feasibility Skeptic). Design still claims validation with "Second Brain Design test case (3 reviews, 40+ findings in original session)." Iteration 1 ran smoke test (parallax reviewing itself). Iteration 2 ran validation (same design doc, second review). No external test case executed. The Second Brain case is real project with known design flaws—gold standard for validation.
- **Why it matters:** Self-review validates tool runs but not that it produces value. Second Brain case answers: did review system catch the same 40+ issues manual process found? Did it catch different issues? Did it miss critical issues? Did it flood with false positives? This is eval that shows whether tool works. Without it, you've built tool, tested execution, but not validated outcome quality.
- **Suggestion:** Run Second Brain test case before finalizing design as approved. Use findings to validate: (1) personas catch real design flaws (not generic concerns), (2) finding counts comparable to manual review (not 10x higher/lower), (3) severity calibration sensible (Critical actually critical), (4) phase classification routes correctly (design flaws vs calibrate gaps). If test reveals failures, update design before marking approved.

### Finding 12: Inspect AI and LangGraph Evaluation Still Deferred
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Open Questions, problem statement build-vs-leverage
- **Issue:** Iteration 2 Prior Art Scout flagged Inspect AI (Finding 13) and LangGraph (Finding 14) as Critical—mature frameworks solving 60-80% of what's being custom-built. Disposition was "evaluate during implementation." Design sync added these to "Evaluate in early eval phase" section but didn't specify evaluation criteria or decision framework. Custom orchestration is 40-60% of implementation surface area.
- **Why it matters:** CLAUDE.md says "BUILD adversarial review (novel), LEVERAGE mature frameworks" but design custom-builds infrastructure. Novel contribution (finding classification, persona prompts) is 20% of surface area. Building custom orchestration (reviewer dispatch, state management, retry logic, progress tracking) is 80%. If Inspect AI and LangGraph already solve this, custom build is wasted effort and maintenance burden.
- **Suggestion:** Add evaluation criteria to design. Specify decision framework: (1) Prototype single reviewer as Inspect solver, measure integration effort, (2) Prototype finding processing with LangGraph state management, validate human-in-loop patterns work, (3) Compare custom vs framework on: implementation time, maintenance burden, feature completeness, (4) Decision rule: if framework covers >70% of needs with <2x integration complexity, adopt framework. Document decision in design whether framework or custom.

## Blind Spot Check

Given my focus on buildability and simplification, I likely underweight:

**Value validation I'm not performing:** I'm flagging that Second Brain test case hasn't run (Finding 11) but not estimating impact if it fails. If external validation shows tool catches <50% of manual review findings or produces 2x false positives, the entire design needs rethinking. I'm treating test case as "nice to have validation" when it's actually "go/no-go for design approval." Should be blocker, not suggestion.

**Prompt engineering difficulty I'm minimizing:** I'm flagging synthesizer consolidation heuristics are undefined (Finding 6) but underestimating how hard semantic deduplication actually is. "When are two findings the same issue?" is core AI alignment problem, not simple prompt engineering. If synthesizer can't reliably deduplicate, user gets flooded with near-duplicates (bad UX). If it over-consolidates, nuance is lost (bad quality). This may be harder than buildable, may require fundamental rethink.

**Long-term maintenance burden:** I'm evaluating MVP complexity but not post-MVP evolution costs. Cross-iteration tracking (Finding 2), prompt versioning (Finding 8), and systemic issue detection (Finding 4) all add ongoing maintenance as prompt library grows. Correction compounding (problem statement concept) requires prompt updates that invalidate cache and break cross-iteration finding IDs. Maintenance burden scales with reviewer count and prompt iteration frequency.

**Integration complexity I'm ignoring:** Design is scoped to parallax:review in isolation, but it's meant for pipeline (parallax:orchestrate calling review as gate). I'm not evaluating how verdict logic, finding classifications, and review artifacts integrate with upstream (parallax:calibrate requirements) and downstream (parallax:plan execution). That's systems architecture concern outside Feasibility Skeptic scope but critical for orchestrator phase.

**User workflow assumptions:** I'm accepting that interactive finding-by-finding processing is valuable but haven't validated this. Alternative: async batch review (all findings in summary.md, user processes in external tool, pastes back dispositions). Simpler implementation (zero state management), potentially better UX (user uses preferred editor/tools). Interactive mode may be complexity with no ROI.
