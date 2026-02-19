# Opus Spot-Check Analysis — Post Judge Prompt Fix (2026-02-19)

**Note:** Independent analysis by Claude Opus 4.6. Not the human reviewer's responses.

**Purpose:** Evaluate whether the judge prompt fix (targeting 4 bias patterns) corrected the right biases without overcorrecting (introducing new leniency).

**Previous analysis accuracy:** 74.5% (38/51 AGREE). Judge was too aggressive dismissing findings as NOT_GENUINE. All 9 GENUINE verdicts were correct; 13/42 NOT_GENUINE verdicts were wrong.

**New results:** 36 GENUINE, 15 NOT_GENUINE across 51 findings (was 9 GENUINE, 42 NOT_GENUINE pre-fix). The judge shifted dramatically toward GENUINE.

---

## Findings by Reviewer

### assumption-hunter

#### assumption-hunter-001
**Finding:** Ground truth validation methodology unstated
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** The document states ground truth was established using a requirements-light dataset approach, which is a documented design choice rather than an unstated methodology gap.
**My verdict:** DISAGREE
**Reasoning:** The finding's core claim is valid. The document says "Establish ground truth (human validation)" in the Phase Map and FR0 specifies "Expert reviewer (human, not LLM) examines each of 22 v3 Critical findings" with criteria including classification process, inter-rater agreement, and documented validation. However, the "requirements-light dataset" is a different dataset (the v1/light document) -- Phase 0 says it is "Complete (requirements-light dataset)" meaning ground truth was established using this dataset, not the v2 document. The finding asks who validated, what criteria, inter-rater reliability -- and FR0 does specify these things (expert reviewer, classification criteria, Cohen's kappa >= 0.6). So the finding partially mischaracterizes what the document specifies. On balance, the judge is mostly right that FR0 does specify methodology, though the finding raises a fair point about the "requirements-light dataset" label implying reduced rigor. Borderline, but judge verdict is defensible.

Actually, re-reading more carefully: the finding says "does not specify: who validated (domain expert, author, external reviewer?)." FR0 says "Expert reviewer (human, not LLM)" -- that specifies expert reviewer but not the specific qualifications. The finding also asks about "inter-rater reliability if multiple validators" -- FR0 specifies "If multiple reviewers: inter-rater agreement measured (Cohen's kappa >= 0.6)." So the document DOES address several of the finding's specific complaints. The judge's verdict (NOT_GENUINE) is defensible because the finding mischaracterizes the document's actual content.

**Final verdict:** AGREE

---

#### assumption-hunter-002
**Finding:** Assumes design doc content is in scope for eval tasks
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** FR-ARCH-2 explicitly states "document content delivered in Sample.input" and FR-ARCH-3 specifies the exact JSONL output format; the finding mischaracterizes what the document specifies.
**My verdict:** AGREE
**Reasoning:** The finding claims FR-ARCH-2 "never specifies where this content comes from, what format it's in, how long it is." But FR-ARCH-2 says "document content delivered in Sample.input" (delivery mechanism), FR-ARCH-3 specifies JSONL as output format, and the document describes design documents as the input. The context window concern is a legitimate implementation detail but not a design gap in the requirements. The judge correctly identifies that the finding mischaracterizes the document.

---

#### assumption-hunter-003
**Finding:** JSONL parsing failures conflated with detection failures
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-3 requires JSONL and states zero findings = format failure, but doesn't distinguish format failure from legitimate zero findings.
**My verdict:** AGREE
**Reasoning:** This is the same issue as success-validator-010. FR-ARCH-3 says "Zero findings parsed from any agent is treated as an output format failure, not zero findings found." This creates a genuine ambiguity: what if a well-designed document genuinely has no gaps? The document conflates two scenarios. The judge is correct.

---

#### assumption-hunter-004
**Finding:** Content hash collision risk unaddressed
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** FR-ARCH-4 is about "Ground Truth Refresh Cadence" and addresses when to refresh, not hash algorithm specifics. Hash algorithm is an implementation detail.
**My verdict:** AGREE
**Reasoning:** The finding is concerned about hash collisions (astronomically rare), whitespace-only changes, and hash validation on load. These are implementation details. FR-ARCH-4 requires a hash field to detect content changes; the specific algorithm choice is not a design gap. The judge correctly classifies this as implementation detail rather than requirements gap.

---

#### assumption-hunter-005
**Finding:** Cost budget assumes constant token usage
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-5 specifies budgets but doesn't define how they account for token usage variability from improved prompts, output variance, model updates, or ground truth expansion.
**My verdict:** DISAGREE
**Reasoning:** The judge overcorrects here. FR-ARCH-5 specifies budget *targets* with explicit cost reduction levers (Batch API, Haiku for mechanical scorers, reduce sample count). The budget is a constraint with documented mitigation strategies. The finding's four concerns are all hypothetical future changes: (1) longer system prompts = more tokens, (2) variable output length, (3) model pricing changes, (4) dataset expansion. These are operational concerns about future changes, not gaps in the current requirements. A budget target is not expected to forecast all future cost drivers. The judge's reasoning that "the document assumes constant token consumption" reads too much into a budget constraint -- budgets are targets, not predictions. This is the kind of overcorrection the prompt fix might introduce: treating any future uncertainty as a genuine gap.

---

#### assumption-hunter-006
**Finding:** Quality rubric scoring scale unbounded
**Judge verdict:** GENUINE
**Judge reasoning:** FR-QUALITY-1 specifies 1-5 scale with >= 3.5 average target but doesn't define averaging method, thresholds for individual dimensions, or linearity assumption.
**My verdict:** AGREE
**Reasoning:** The finding raises valid points. The rubric says "target aggregate quality score >= 3.5/5.0 average across all dimensions" but doesn't specify whether a single 1/5 should fail the finding regardless of other scores. The averaging vs. thresholding question is a real design ambiguity. This was one of the bias patterns the fix targeted (undefined terms in acceptance criteria), and the fix correctly allows this to be GENUINE.

---

#### assumption-hunter-007
**Finding:** LLM-as-judge grading cost model missing
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-5 specifies Phase 2 budget but FR-QUALITY-1 doesn't specify which model, how many API calls per finding, or single-shot vs multi-turn grading.
**My verdict:** AGREE
**Reasoning:** The finding correctly identifies that the Phase 2 budget ($2.00 per run) exists but the components that drive cost (model choice, calls per finding, grading protocol) are unspecified. FR-QUALITY-1 defines rubric dimensions but not the grading implementation. This is a genuine gap between the budget constraint and the implementation design.

---

#### assumption-hunter-008
**Finding:** Reviewer consensus logic unspecified
**Judge verdict:** GENUINE
**Judge reasoning:** Open Question #2 asks about deduplication but provides no operational definition of "same root cause."
**My verdict:** AGREE
**Reasoning:** Open Question #2 explicitly states: "If 3/5 reviewers independently flag the same root cause... should duplicates be deduplicated to one ground truth finding or kept as separate findings for each reviewer?" The document raises this as an open question but never defines "same root cause" operationally. The judge correctly identifies this as a genuine gap. The finding's observation about semantic equivalence testing is directly supported by the document's own open question.

---

#### assumption-hunter-009
**Finding:** Assumes reviewers produce findings synchronously
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Timeout handling, partial output, and rate limiting are operational/infrastructure concerns, not design flaws in the requirements.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-2 specifies the interface requirement (single-turn eval context without tools). The finding speculates about timeout behavior, partial output capture, and rate limiting -- these are infrastructure/operational concerns that don't represent gaps in the requirements document. The judge correctly classifies this.

---

#### assumption-hunter-010
**Finding:** Cost reduction levers lack priority rationale
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** The finding conflates three separate issues, and the claim about Haiku and "mechanical scorers" in Phase 1 is false.
**My verdict:** UNSURE
**Reasoning:** The judge's reasoning is muddled. The finding actually makes three claims: (1) cost lever ordering lacks rationale -- this is a fair point, the document says "in order of preference" without explaining why; (2) latency tradeoff of Batch API not addressed -- a valid concern; (3) Haiku for "mechanical scorers" assumes scorers exist in Phase 1. The judge says claim (3) is false because the document "clearly states Haiku is for 'mechanical scorers' in the cost reduction lever list." But the finding's point is that Phase 1 has no scorers yet (FR-QUALITY-1 is Phase 2), so listing Haiku for mechanical scorers is forward-looking. The judge's reasoning is incomplete and somewhat contradictory. However, the overall verdict (NOT_GENUINE) could be defensible because the cost levers are explicitly labeled as a prioritized list for when optimization is needed, not immediate requirements. Mixed signals.

---

#### assumption-hunter-999
**Finding:** Blind spot check: Assumption Hunter perspective
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Self-assessment of reviewer's blind spots, not a design gap in the document.
**My verdict:** AGREE
**Reasoning:** Meta-commentary, correctly classified.

---

### constraint-finder

#### constraint-finder-001
**Finding:** Ground truth validation budget and timeline missing
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** The finding speculates about expert costs based on assumptions not in the document. The $2000/month budget applies to eval infrastructure, not ground truth validation.
**My verdict:** AGREE
**Reasoning:** The finding calculates hypothetical costs ($150-300/hour expert rates) and concludes they consume 83-165% of the stated budget. But the document doesn't claim the $2000/month budget covers expert validation -- that budget is for eval infrastructure (API costs). The finding hallucinates a constraint by applying the eval budget to the validation phase. The judge correctly identifies this.

---

#### constraint-finder-002
**Finding:** Expert reviewer availability and qualification constraints unstated
**Judge verdict:** GENUINE
**Judge reasoning:** FR0 specifies "Expert reviewer (human, not LLM)" but leaves undefined qualifications, availability, conflict-of-interest rules, and fallback procedures.
**My verdict:** DISAGREE
**Reasoning:** The judge overcorrects here. FR0 does say "Expert reviewer (human, not LLM)" without specifying qualifications, but this is standard requirements practice -- specifying "expert" as a role without a job description is normal for a requirements document. The finding's concerns about (1) required qualifications, (2) availability constraints, (3) conflict of interest rules, (4) fallback procedures are all operational/staffing concerns, not design gaps. The finding also claims Cohen's kappa "implies multiple reviewers, multiplying cost" -- but the document says "If multiple reviewers," explicitly marking this as conditional. The finding treats a conditional clause as an implied requirement.

In the pre-fix analysis, the previous Opus review found this same finding (as constraint-finder-001, different numbering in a different eval run) and agreed with NOT_GENUINE, reasoning that "Expert recruitment cost and availability verification are operational details, not design requirements." The judge fix has now flipped this to GENUINE, which appears to be overcorrection -- treating operational/staffing concerns as design gaps.

---

#### constraint-finder-003
**Finding:** Cost per eval run target conflicts with token usage estimates
**Judge verdict:** GENUINE
**Judge reasoning:** NFR2.1.2 states <$0.50 while Success Criteria #7 says <$2.00, creating conflicting constraints. The cost calculation demonstrates the gap is material.
**My verdict:** AGREE
**Reasoning:** This is a real internal inconsistency. The light document's NFR1.2 says "Target <$0.50 per eval run (MVP)" while Success Criteria #7 says "Cost per eval run <$2.00 (revised from $0.50)." The revision was applied to Success Criteria but NOT to NFR1.2, leaving conflicting numbers in the document. The finding's token cost analysis, while somewhat speculative, demonstrates the $0.50 target may be infeasible. The judge correctly identifies the document inconsistency.

This was one of the pre-fix disagreements (the old judge called it NOT_GENUINE). The fix correctly flipped this.

---

#### constraint-finder-004
**Finding:** Token budget for review model calls not specified
**Judge verdict:** GENUINE
**Judge reasoning:** The document never explicitly defines input/output token limits per design doc or handling strategies for documents exceeding context windows.
**My verdict:** DISAGREE
**Reasoning:** The judge overcorrects. The document specifies that document content is delivered in Sample.input (FR-ARCH-2) and agents produce JSONL output (FR-ARCH-3). Token limits per finding are not a design requirement -- they're an implementation detail. The finding speculates about "15-20K input tokens" and mentions "200K budget" from the document end, but token budgets for individual API calls are not requirements-level concerns. The document appropriately specifies the interface (what goes in, what comes out) without constraining token-level implementation details.

---

#### constraint-finder-005
**Finding:** Regulatory and compliance constraints for API key handling unspecified
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Regulatory requirements (GDPR, SOC2, HIPAA) are not present in the document and cannot be evaluated without external context. NFR1.2 explicitly defers key rotation to Phase 1.
**My verdict:** AGREE
**Reasoning:** The finding introduces regulatory requirements (GDPR, SOC2, HIPAA, data residency, audit logging, breach response) that are not mentioned anywhere in either document. Whether these regulations apply depends on external context not available in the requirements. The judge correctly identifies that the finding introduces external constraints not grounded in the document.

---

#### constraint-finder-006
**Finding:** Dataset size constraints for git storage not calculated
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** The finding speculates about future Phase 2 expansion pushing dataset size past 1MB, but Phase 2 scope is deferred and the current MVP fits within the threshold.
**My verdict:** AGREE
**Reasoning:** NFR5.2 in the light document specifies the 1MB threshold with a clear bifurcation (git if <1MB, external with hash if >1MB). The finding calculates current dataset size (~660KB, within threshold) and then speculates about Phase 2 expansion pushing to 2-3MB. This is a hypothetical future concern about a deferred phase. The judge correctly identifies this as speculation about future growth, not a current design gap.

---

#### constraint-finder-007
**Finding:** MacBook Pro performance assumptions not validated
**Judge verdict:** GENUINE
**Judge reasoning:** NFR4.1 specifies <5 minutes but omits MacBook Pro specs, network latency assumptions, retry logic, and parallelization strategy.
**My verdict:** DISAGREE
**Reasoning:** The judge overcorrects. Performance targets without pre-specifying hardware configurations are standard requirements practice. "Completes in <5 minutes on MacBook Pro" is a testable acceptance criterion -- you run it and see if it passes. The finding's concerns about which MacBook model, network latency, retry logic, and parallel execution are all implementation variables that will be discovered empirically during testing. The previous Opus analysis agreed with NOT_GENUINE for an equivalent finding (constraint-finder-004), reasoning that "performance targets in acceptance criteria without pre-specifying hardware specs are standard practice." The fix flipped this to GENUINE, which is overcorrection.

---

#### constraint-finder-008
**Finding:** Inspect AI learning curve and documentation gaps not accounted for
**Judge verdict:** GENUINE
**Judge reasoning:** Phase 1 targets 1-week completion but FR3.1 acknowledges learning curve ("research Inspect AI Dataset/Sample format during Phase 1 design") without budgeting time for it.
**My verdict:** AGREE
**Reasoning:** FR3.1 acceptance criteria include "Dataset schema documented (research Inspect AI Dataset/Sample format during Phase 1 design)." This explicitly acknowledges that Inspect AI format research is unscoped work within Phase 1's timeline. The finding correctly identifies that the 1-week Phase 1 target includes research work without estimating it. The previous Opus analysis also agreed with GENUINE for this same pattern (constraint-finder-007).

---

#### constraint-finder-009
**Finding:** Baseline threshold (90% detection rate) not validated against ground truth sample size
**Judge verdict:** GENUINE
**Judge reasoning:** FR2.2 specifies 90% threshold on >= 15 findings, but the document doesn't address statistical validity or sample size adequacy.
**My verdict:** AGREE
**Reasoning:** The finding correctly identifies that 90% on 15 samples has wide confidence intervals (a single missed finding = 93%, two = 87%), making the threshold brittle. The document acknowledges thresholds are "provisional" but provides no acceptance criteria for validating whether the sample size supports the threshold. This is a real statistical gap in the requirements.

---

#### constraint-finder-010
**Finding:** CI/CD integration timeline and prerequisites not specified
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** CI/CD is explicitly deferred to Phase 3 (post-MVP) and the "Explicitly Deferred" section confirms this.
**My verdict:** AGREE
**Reasoning:** The document clearly states CI/CD is deferred. Phase 3 is "Not started" and explicitly out of scope. The finding speculates about implementation details for a phase with no requirements. Correctly classified.

---

#### constraint-finder-999
**Finding:** Blind spot check: Constraint Finder perspective
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Self-reflective meta-analysis, not a design gap identification.
**My verdict:** AGREE
**Reasoning:** Meta-commentary, correctly classified.

---

### problem-framer

#### problem-framer-001
**Finding:** Problem statement assumes eval framework exists
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** The document explicitly states v1 was written pre-implementation and implementation revealed failures. The document does not assume a working eval framework; it documents v1's failure and prescribes v2 corrections.
**My verdict:** AGREE
**Reasoning:** The finding claims the document "frames this as v2 corrections to a failed implementation, not as building the measurement system from scratch." But that IS what the document does -- and it's accurate framing. The document's Background section explains exactly what failed (skill-as-system-prompt pattern, interactive prompts instead of JSONL) and what v2 changes (per-reviewer tasks). This is transparent about the situation, not an assumption. The judge correctly identifies that the finding mischaracterizes the document's framing.

---

#### problem-framer-002
**Finding:** Root cause unclear: architecture mismatch vs output format
**Judge verdict:** GENUINE
**Judge reasoning:** The Background presents two root causes without clarifying which is primary or whether they're the same problem.
**My verdict:** AGREE
**Reasoning:** The Background section says "the skill-as-system-prompt pattern fails" (architecture) and then "the model produced interactive prompts instead of JSONL" (output format). FR-ARCH-3 reveals assumption-hunter used markdown. The finding correctly identifies the document doesn't clarify whether the root cause was wrong architecture, wrong output format, or both. This ambiguity could lead implementers to address only the format issue when the architecture issue might recur. Genuine gap.

---

#### problem-framer-003
**Finding:** Success criteria missing: what proves v2 solves the problem?
**Judge verdict:** GENUINE
**Judge reasoning:** The document says "testable at the component level" but provides no quantitative definition of what "testable" means. Phase 1 acceptance criteria focus on task existence, not regression/improvement validation.
**My verdict:** AGREE
**Reasoning:** The v2 addition says "The eval framework itself must be testable at the component level" without defining testability quantitatively. Phase 1's acceptance criteria are structural ("task exists," "JSONL parses," "make target runs") rather than outcome-oriented ("framework catches N% of regressions"). The finding correctly identifies this gap between the stated goal and the measurement criteria.

---

#### problem-framer-004
**Finding:** Impact scope unclear: who needs this and when?
**Judge verdict:** GENUINE
**Judge reasoning:** The document doesn't specify change frequency, who makes changes, what triggers changes, or what decisions depend on eval results.
**My verdict:** DISAGREE
**Reasoning:** The judge overcorrects. The problem statement establishes the need ("changes to skill prompts may improve, degrade, or have no effect -- we cannot tell which"), and the solution addresses it (eval framework with detection/precision metrics). The finding asks about operational workflow questions: (1) how often prompts change, (2) who changes them, (3) what triggers changes, (4) what decisions depend on results. These are usage context questions, not design gaps. A requirements document for an eval framework doesn't need to specify the change management process of the artifacts being evaluated. The framework's purpose is clear: measure effectiveness. Who uses it and when is operational context.

---

#### problem-framer-005
**Finding:** Circular dependency not explained as a root cause
**Judge verdict:** GENUINE
**Judge reasoning:** The document states "Blocking issue: Circular dependency" in Phase 0 and references it in Open Question 2, but never explains what the circular dependency was or how it was resolved.
**My verdict:** AGREE
**Reasoning:** Phase Map says Phase 0 blocking issue is "Circular dependency" with status "Complete." The light document's Problem Statement explains: "Ground truth validation is circular. We need verified design flaws to test detection capability, but we need detection capability to find design flaws." So the light document DOES explain the circular dependency. However, the v2 document references it without explaining it, and Phase 0's resolution is marked "Complete" without documenting the resolution. The v2 document is not self-contained on this point. The finding identifies a real gap in the v2 document's explanation, even if the light document partially addresses it.

---

#### problem-framer-006
**Finding:** Ground truth refresh trigger ambiguity
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-4 uses "changed significantly" and "updated substantially" without measurable thresholds.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-4 lists refresh triggers including "The reviewed requirements/design document updated substantially" and "Any reviewer agent prompt changed" (note: this one has NO qualifier). The finding focuses on the undefined terms "changed significantly" and "updated substantially." These are real design gaps -- undefined terms in requirements that different implementers would interpret differently. This was one of the bias patterns the judge fix targeted (undefined terms), and the fix correctly allows this to be GENUINE.

---

#### problem-framer-999
**Finding:** Blind spot check: Problem Framer perspective
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Meta-analysis raising legitimate questions but not identifying concrete design gaps.
**My verdict:** AGREE
**Reasoning:** Meta-commentary, correctly classified. However, the judge's reasoning is slightly flawed when it calls point (3) "a hallucinated constraint" and claims FR-ARCH-1 provides "detailed rationale" for per-reviewer decomposition. The finding questions whether per-finding-type decomposition would be better -- that's a design alternative, not a hallucinated constraint. But the overall verdict (NOT_GENUINE for a blind spot meta-finding) is correct regardless.

---

### scope-guardian

#### scope-guardian-001
**Finding:** Phase 1 scope boundary unclear: JSONL output fix vs. full per-reviewer eval
**Judge verdict:** GENUINE
**Judge reasoning:** Phase 1 is "In progress" with deliverables listed but no explicit mapping of which FR-ARCH requirements must be completed in Phase 1 vs. later phases.
**My verdict:** AGREE
**Reasoning:** The Phase Map lists Phase 1 deliverables as "Per-reviewer eval tasks, JSONL output fix, detection baseline." FR-ARCH-1 maps to per-reviewer tasks, FR-ARCH-3 maps to JSONL fix. But FR-ARCH-2 (eval-compatible interface), FR-ARCH-4 (ground truth refresh), and FR-ARCH-5 (cost budget) don't have clear Phase 1/Phase 2 assignments. The finding correctly identifies that the scope boundary between what's in Phase 1 and what's deferred is ambiguous for some requirements.

---

#### scope-guardian-002
**Finding:** Phase 1.5 scope undefined: multi-model comparison deliverables missing
**Judge verdict:** GENUINE
**Judge reasoning:** Phase 1.5 has a Phase Map entry but no corresponding functional requirements defining deliverables, metrics, or success criteria.
**My verdict:** AGREE
**Reasoning:** Phase 1.5 is listed as "Multi-model comparison (Sonnet vs Haiku), cost tracking" in the Phase Map but has no FR section defining what "multi-model comparison" means as a deliverable. FR8 and FR9 exist in the light document but are marked "Deferred to post-MVP." There's a gap between the Phase Map listing and the lack of requirements. Genuine.

---

#### scope-guardian-003
**Finding:** Phase 2 mock tools scope ambiguous: which Tier 2 tools?
**Judge verdict:** GENUINE
**Judge reasoning:** Phase 2 includes "mock tools (Tier 2)" but doesn't specify which tools need mock implementations.
**My verdict:** AGREE
**Reasoning:** The Phase Map says Phase 2 includes "mock tools (Tier 2)" without specifying which tools are in scope. The finding correctly identifies this ambiguity. The document references Tier 2 tools elsewhere but doesn't define which ones need mocking for Phase 2.

---

#### scope-guardian-004
**Finding:** Ground truth refresh scope unclear: what qualifies as 'substantial' document update?
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-4 uses "substantially" without defining criteria.
**My verdict:** AGREE
**Reasoning:** Same issue as problem-framer-006. FR-ARCH-4 uses "updated substantially" as a trigger without defining thresholds. This is an undefined term in a requirements document. Genuine gap.

---

#### scope-guardian-005
**Finding:** Phase 0 ground truth scope ambiguous: requirements-light dataset size sufficient?
**Judge verdict:** GENUINE
**Judge reasoning:** Phase Map marks Phase 0 as "Complete" but Open Question #3 asks if 10 Critical findings are sufficient, creating tension between completion status and unresolved adequacy questions.
**My verdict:** AGREE
**Reasoning:** The Phase Map says Phase 0 is "Complete (requirements-light dataset)" while Open Question #3 asks "10 validated Critical findings (requirements-light dataset) -- sufficient for Phase 1 detection baseline?" This is a real inconsistency: a completed phase with an unresolved question about whether its output is adequate. Genuine gap.

---

#### scope-guardian-006
**Finding:** Phase 4+ scope includes deferred experiment with no exit criteria
**Judge verdict:** GENUINE
**Judge reasoning:** Phase 4+ lists "Markdown vs JSONL output experiment" but FR-ARCH-3 mandates JSONL, creating a contradiction with no exit criteria for the experiment.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-3 explicitly states "The output format is a requirement, not an implementation choice." Phase 4+ then lists a "Markdown vs JSONL output experiment" that would question this requirement. The finding correctly identifies the contradiction and the lack of exit criteria for the experiment. Genuine.

---

#### scope-guardian-007
**Finding:** Out-of-scope list missing agent orchestration skill itself
**Judge verdict:** GENUINE
**Judge reasoning:** The document specifies per-reviewer agent eval tasks but doesn't state whether testing the orchestration skill itself is in Phase 1-2 scope or permanently deferred.
**My verdict:** AGREE
**Reasoning:** The v2 Background explains why the skill-as-system-prompt pattern failed and why per-reviewer decomposition is the solution. The "Explicitly Out of Scope" section defers "Orchestrate wrapper (decision pending, Issue #52)" but doesn't explicitly state whether orchestration-level testing is in scope for Phases 1-2. The finding correctly identifies this ambiguity. Genuine.

---

#### scope-guardian-008
**Finding:** Implicit scope expansion: FR-QUALITY-1 requires ground truth re-validation
**Judge verdict:** GENUINE
**Judge reasoning:** FR-QUALITY-1 says "Rubric validated against existing ground truth findings" but doesn't specify if this reopens Phase 0 scope or uses Phase 0 output as-is.
**My verdict:** AGREE
**Reasoning:** FR-QUALITY-1 acceptance criteria include "Rubric validated against existing ground truth findings before scoring new findings." This validation could mean (a) re-open Phase 0 to re-validate ground truth, or (b) use Phase 0 output as calibration data. The document doesn't clarify. This is a genuine scope ambiguity that could cause Phase 0 to reopen. Genuine.

---

#### scope-guardian-009
**Finding:** MVP boundary unclear: Phase 1 'non-zero accuracy' insufficient as done criteria
**Judge verdict:** GENUINE
**Judge reasoning:** "Produces non-zero accuracy" could mean 1% -- technically non-zero but not useful.
**My verdict:** AGREE
**Reasoning:** The Phase Map states Phase 1 is the "immediate target" and "Phases 2+ remain blocked until Phase 1 produces non-zero accuracy." But "non-zero" is an extremely low bar. The finding correctly identifies that this done criterion doesn't connect to the quality expectations defined elsewhere (FR-ARCH-5 cost budgets, FR-QUALITY-1 rubric). Genuine gap between the milestone definition and the quality standards.

---

#### scope-guardian-010
**Finding:** Post-review findings (v1-post-review-001) not explicitly in or out of scope
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-1 excludes post-review findings from per-reviewer ground truth but doesn't specify what happens to them. Open Question #1 asks about this but leaves it unresolved.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-4 says post-review findings are "stored separately... with 'discovery': 'implementation' field and excluded from per-reviewer task ground truth." But Open Question #1 asks "Should it be added to a separate 'implementation discovery' dataset?" -- treating the storage decision as unresolved while the acceptance criteria already specify separate storage. This is a real inconsistency between the requirements and open questions sections. Genuine.

---

#### scope-guardian-999
**Finding:** Blind spot check: Scope Guardian perspective
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Meta-commentary about possible blind spots, not identification of specific design gaps.
**My verdict:** AGREE
**Reasoning:** Meta-commentary, correctly classified. The judge's reasoning is mostly sound, though point (3) about "make target" is slightly off -- the finding's claim that the make target is implicit isn't fully wrong (the acceptance criterion says it must exist, but FR-ARCH-1 doesn't define who builds it or when). However, for a blind spot meta-finding, NOT_GENUINE is correct.

---

### success-validator

#### success-validator-001
**Finding:** Missing detection rate thresholds for Phase 1 eval tasks
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-1 specifies structural requirements but no detection rate or pass/fail thresholds for Phase 1.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-1 acceptance criteria are structural ("task function per reviewer," "system_message(load_agent_content())," "make reviewer-eval runs"). There's no threshold defining what detection rate constitutes success for Phase 1. The light document's FR2.2 mentions 90% detection rate as "provisional," but FR-ARCH-1 doesn't reference this. Genuine gap.

---

#### success-validator-002
**Finding:** No precision target specified for Phase 1
**Judge verdict:** GENUINE
**Judge reasoning:** Detection rate (recall) is implied by filtering, but precision is not specified as a Phase 1 requirement.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-1 filtering by `reviewer == agent_name` enables recall measurement, but no acceptance criterion specifies a precision target. The light document mentions 80% precision in FR2.2, but the v2 document's FR-ARCH requirements don't carry this forward. Genuine gap.

---

#### success-validator-003
**Finding:** Ground truth filtering acceptance criteria lacks validation method
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-1 says "Ground truth filtering excludes post-review findings" but provides no test method to verify the exclusion works.
**My verdict:** AGREE
**Reasoning:** The acceptance criterion specifies what should happen (exclude post-review findings) but not how to verify it works correctly. This is a testable requirement without a defined test. Genuine gap.

---

#### success-validator-004
**Finding:** Cost budget acceptance criteria unverifiable without implementation
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-5 acceptance criteria reference implementation artifacts ("make cost-report," "EvalLog metadata") that don't exist yet.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-5 acceptance criteria include "make cost-report reads eval logs" and "Eval run cost logged in EvalLog metadata" -- both reference specific implementation artifacts. The requirements define acceptance in terms of unbuilt components, making them unverifiable until implementation. This is a genuine design gap: the acceptance criteria depend on implementation rather than observable outcomes.

---

#### success-validator-005
**Finding:** Quality rubric target score lacks statistical validity specification
**Judge verdict:** GENUINE
**Judge reasoning:** FR-QUALITY-1 specifies >= 3.5/5.0 average but doesn't define sample size, variance, or confidence intervals.
**My verdict:** AGREE
**Reasoning:** The target aggregate score (>= 3.5/5.0) is defined without statistical parameters. A score of 3.5 on 2 findings is meaningfully different from 3.5 on 20 findings. The document doesn't address this. Genuine gap.

---

#### success-validator-006
**Finding:** Phase 1 completion definition unclear due to 'in progress' status
**Judge verdict:** GENUINE
**Judge reasoning:** Phase Map shows "In progress" without aggregated Phase 1 exit criteria.
**My verdict:** AGREE
**Reasoning:** Phase Map lists Phase 1 as "In progress" with deliverables and blocking issues, but there's no single statement of "Phase 1 is complete when X, Y, Z are all satisfied." Individual FRs have acceptance criteria, but there's no aggregation into Phase 1 exit criteria. Genuine gap -- the same finding pattern as scope-guardian-009.

---

#### success-validator-007
**Finding:** FR-ARCH-4 ground truth refresh procedure not testable
**Judge verdict:** GENUINE
**Judge reasoning:** "make validate re-runs if document hash differs" doesn't specify what "re-runs" means (human re-validation vs eval re-run).
**My verdict:** AGREE
**Reasoning:** FR-ARCH-4 acceptance criteria say "make validate re-runs if document hash differs" but "re-runs" is ambiguous. Does it re-run the human validation process (FR0) or the eval tasks (FR-ARCH-1)? These are very different operations with different cost, time, and process implications. Genuine ambiguity.

---

#### success-validator-008
**Finding:** Open question #1 (post-review findings) blocks Phase 1 completion
**Judge verdict:** GENUINE
**Judge reasoning:** Open Question #1 creates uncertainty about Phase 1 requirements scope if the answer is "yes, add to separate dataset."
**My verdict:** AGREE
**Reasoning:** The finding correctly identifies that an unanswered open question could expand Phase 1 scope. FR-ARCH-4 already specifies post-review findings are "stored separately" but Open Question #1 asks whether to add them to an "implementation discovery" dataset -- if yes, this implies new dataset infrastructure as a Phase 1 requirement. Genuine.

---

#### success-validator-009
**Finding:** No validation method for FR-ARCH-2 agent interface compatibility
**Judge verdict:** GENUINE
**Judge reasoning:** FR-ARCH-2 describes behavioral properties but no test method to verify agents work in both production and eval contexts.
**My verdict:** AGREE
**Reasoning:** FR-ARCH-2 requires agents function in both production (multi-turn, tools) and eval (single-turn, no tools) contexts "without modifications." The acceptance criteria describe properties (self-contained prompts, no tool instructions, JSONL output) but not how to test that both contexts actually work. This is a testability gap. Genuine.

---

#### success-validator-010
**Finding:** FR-ARCH-3 zero findings ambiguity
**Judge verdict:** GENUINE
**Judge reasoning:** "Zero findings parsed" = format failure conflicts with the valid case of a well-designed document producing zero legitimate findings.
**My verdict:** AGREE
**Reasoning:** Same issue as assumption-hunter-003. FR-ARCH-3 conflates two scenarios (format failure vs. genuine zero findings) without a mechanism to distinguish them. Genuine gap.

---

#### success-validator-999
**Finding:** Blind spot check: Success Validator perspective
**Judge verdict:** NOT_GENUINE
**Judge reasoning:** Self-reflective meta-question, not a specific design gap identification.
**My verdict:** AGREE
**Reasoning:** Meta-commentary, correctly classified.

---

## Accuracy Calculation

| Category | Count |
|---|---|
| AGREE | 43 |
| DISAGREE | 7 |
| UNSURE | 1 |
| Total | 51 |
| Accuracy (AGREE / (AGREE+DISAGREE)) | 86.0% |

### By verdict type
- GENUINE verdicts (36 total): 31 AGREE, 5 DISAGREE (86.1% agreement)
- NOT_GENUINE verdicts (15 total): 12 AGREE, 2 DISAGREE, 1 UNSURE (85.7% agreement)

### By reviewer
| Reviewer | AGREE | DISAGREE | UNSURE | Total |
|---|---|---|---|---|
| assumption-hunter | 8 | 2 | 1 | 11 |
| constraint-finder | 8 | 3 | 0 | 11 |
| problem-framer | 6 | 1 | 0 | 7 |
| scope-guardian | 11 | 0 | 0 | 11 |
| success-validator | 10 | 1 | 0 | 11 |

### By confidence band
- High-conf (>= 80): 27 AGREE, 4 DISAGREE, 0 UNSURE (87.1%)
- Low-conf (< 80): 16 AGREE, 3 DISAGREE, 1 UNSURE (84.2%)

---

## Disagreements Detail

### GENUINE verdicts I disagree with (judge overcorrected -- now too lenient)

#### 1. assumption-hunter-005 (judge: GENUINE, I say: NOT_GENUINE)
**Finding:** Cost budget assumes constant token usage.
**Problem:** FR-ARCH-5 specifies budget *targets* with explicit mitigation levers. The finding's four concerns (prompt growth, output variance, model pricing changes, ground truth expansion) are all hypothetical future changes. Budget targets are constraints, not predictions -- they don't need to forecast all cost drivers. Treating any future uncertainty as a design gap is too lenient.

#### 2. constraint-finder-002 (judge: GENUINE, I say: NOT_GENUINE)
**Finding:** Expert reviewer qualification and availability constraints unstated.
**Problem:** FR0 specifies "Expert reviewer (human, not LLM)" -- expert role without detailed job requirements is standard requirements practice. Availability constraints, conflict of interest rules, and fallback procedures are operational/staffing concerns, not design gaps. The conditional "If multiple reviewers" clause doesn't imply mandatory multiple reviewers. This was NOT_GENUINE in pre-fix run; the fix overcorrected.

#### 3. constraint-finder-004 (judge: GENUINE, I say: NOT_GENUINE)
**Finding:** Token budget for review model calls not specified.
**Problem:** Token limits per API call are implementation details, not design requirements. The document specifies the interface (document content in Sample.input, JSONL output) without needing to constrain token allocation per call. This is infrastructure-level detail.

#### 4. constraint-finder-007 (judge: GENUINE, I say: NOT_GENUINE)
**Finding:** MacBook Pro performance assumptions not validated.
**Problem:** Performance targets without hardware specs are standard practice. "<5 minutes on MacBook Pro" is testable as-is. The finding's concerns about model/year, network latency, retry logic, and parallelization are implementation variables, not requirements gaps. This was NOT_GENUINE in pre-fix; the fix overcorrected.

#### 5. problem-framer-004 (judge: GENUINE, I say: NOT_GENUINE)
**Finding:** Impact scope unclear: who needs this and when?
**Problem:** The problem statement establishes the need (can't measure effectiveness). The finding asks operational workflow questions (frequency, who, triggers, decisions). A requirements document for an eval framework doesn't need to specify the change management process of the artifacts being evaluated. These are usage context questions, not design gaps.

### NOT_GENUINE verdicts I disagree with (judge still too strict)

#### 6. assumption-hunter-001 (judge: NOT_GENUINE, I say: DISAGREE initially but changed to AGREE)
N/A -- I changed my mind during analysis and agreed with the judge.

#### 7. assumption-hunter-010 (judge: NOT_GENUINE, I say: UNSURE)
**Finding:** Cost reduction levers lack priority rationale.
**Problem:** The finding has three sub-claims with mixed validity. The judge's reasoning is muddled, neither fully addressing nor refuting the individual points. The overall verdict is defensible but the reasoning quality is poor.

---

## Systematic Patterns

### Pattern 1: Overcorrection toward GENUINE (new leniency bias)

The judge shifted from 9/51 GENUINE (18%) to 36/51 GENUINE (71%). This is a dramatic swing. Of the 36 GENUINE verdicts, I disagree with 5 (14% false-positive rate on GENUINE calls). The pre-fix judge had 0% false-positive on GENUINE calls (all 9 were correct).

The overcorrection pattern: the judge now treats implementation details, operational concerns, and hypothetical future scenarios as genuine design gaps. Specific overcorrection areas:
- **Operational/staffing concerns** treated as design gaps (constraint-finder-002: expert qualifications)
- **Implementation details** treated as requirements gaps (constraint-finder-004: token budgets, constraint-finder-007: hardware specs)
- **Future uncertainty** treated as current gaps (assumption-hunter-005: cost variability)
- **Usage context questions** treated as design gaps (problem-framer-004: who uses this)

### Pattern 2: NOT_GENUINE verdicts are now more accurate

Pre-fix: 29/42 NOT_GENUINE correct (69.0%).
Post-fix: 12/14 NOT_GENUINE correct (85.7%, excluding UNSURE).

The fix successfully addressed the previous problem of over-aggressively dismissing findings. The remaining NOT_GENUINE verdicts are mostly correct (blind spot checks, speculative findings, hallucinated constraints).

### Pattern 3: Undefined terms fix is well-targeted

The judge now correctly classifies undefined terms in acceptance criteria (e.g., "substantially," "non-zero accuracy") as GENUINE. This was the primary bias in the pre-fix judge. Findings like problem-framer-006, scope-guardian-004, and scope-guardian-009 are correctly GENUINE.

### Pattern 4: Reporting vs enforcement fix is well-targeted

The pre-fix judge conflated "report flags for optimization" with enforcement. The post-fix verdicts for scope-guardian-009 and success-validator-006 (cost budget enforcement) are now not in the sample (those specific IDs aren't in this run), but the principle appears to be applied correctly elsewhere.

### Pattern 5: scope-guardian findings are highly accurate

All 11 scope-guardian verdicts are correct (11/11 AGREE). This reviewer's findings are well-scoped to actual document gaps, and the judge handles them reliably.

### Pattern 6: constraint-finder findings have the most overcorrection

3 of 7 DISAGREE verdicts are constraint-finder findings. The constraint-finder produces findings about implementation details, operational concerns, and future scalability -- categories where the judge now overcorrects toward GENUINE.

---

## Key Question: Did the Fix Overcorrect?

**Yes, partially.** The fix corrected the right biases (undefined terms, reporting vs enforcement, assumption-questioning, factual verification) but introduced a new leniency pattern.

**What improved:**
- NOT_GENUINE accuracy rose from 69% to 86%
- The judge no longer dismisses legitimate challenges to undefined terms
- Factual errors appear reduced (no obvious "this doesn't exist in the document" errors when it does)
- Blind spot checks still correctly classified

**What overcorrected:**
- GENUINE accuracy dropped from 100% to 86% (5 false-GENUINE verdicts)
- The judge now accepts implementation details, operational concerns, and hypothetical future scenarios as genuine design gaps
- The balance shifted from "too strict" to "somewhat too lenient"

**Net assessment:**
- Overall accuracy: 86% (up from 74.5%)
- This passes the >= 80% gate for trusting the precision metric
- The bias shifted from "too many false NOT_GENUINE" to "some false GENUINE"
- Impact on precision metric: false GENUINE inflates precision (making reviewers look better than they are)
- This is the less dangerous direction of error -- overcounting genuine findings is better than undercounting them for a precision metric, because it means the measured precision is a lower bound on true precision

**Recommendation:** The judge is now accurate enough (86%) to trust the precision metric. The remaining overcorrection (5 false-GENUINE out of 36) means measured precision slightly understates the true false-positive rate. For the purposes of calibrating reviewer quality and detecting regressions, this is acceptable. If tighter precision measurement is needed later, add guidance distinguishing "implementation details" and "operational concerns" from "requirements-level design gaps."
