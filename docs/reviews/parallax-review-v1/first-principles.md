# First Principles Review

## Changes from Prior Review
All prior findings from the smoke test review were addressed through prompt iteration (Tasks 8). Key changes:
- **Finding 2 (Discuss mode)**: Resolved — discuss mode cut from MVP, replaced with reject-with-note
- **Finding 1 (Synthesizer role)**: Resolved — reframed as judgment-exercising role (not "purely editorial")
- **Finding 3 (Phase classification)**: Resolved — primary + contributing phases implemented
- **Finding 5 (Prototype defers highest-leverage phase)**: Acknowledged as known tradeoff

Several design improvements implemented:
- Voice rules added to all reviewer prompts
- Cross-iteration context mechanism designed (prior summary fed to reviewers)
- Topic validation and collision handling specified
- Auto-fix step added between synthesis and human processing

**New findings in this review**: Examining whether the problem framing, scope, and core assumptions are correct after the iteration.

## Problem Reframe

**Core problem as I would state it from scratch:**

Design artifacts produced by AI coding assistants contain flaws invisible to single-perspective review. The highest-leverage intervention is catching requirement-level errors before design begins, but teams skip formal requirement refinement and jump straight to design. When reviews happen, they treat all findings as same-phase fixes rather than routing errors back to the phase that failed.

**How this differs from the design's framing:**

The design correctly identifies multi-perspective review as the mechanism and finding classification as the differentiator. However, it frames the problem as "orchestrating the full pipeline" (research → requirements → design → plan → execution) but builds only the middle piece (design review). This creates a mismatch: the stated problem is pipeline orchestration, but the actual solution is a review skill. The design acknowledges this ("Prototype Scope" explicitly scopes design-stage only) but doesn't justify **why design review is the right starting point** when the requirements doc explicitly says "requirement refinement has been the single biggest design quality lever."

If I started from zero, I would either: (a) build requirements review first to validate the highest-leverage hypothesis, or (b) reframe the problem statement as "multi-perspective design review" and defer orchestration entirely.

## Findings

### Finding 1: Building Design Review to Validate Orchestration Hypothesis is Circular
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Prototype Scope, Problem Statement framing
- **Issue:** The problem statement says "requirement refinement has been the single biggest design quality lever in practice" and identifies requirements gaps as the root cause of design failures (Finding 2 in problem statement: "review findings revealed design flaws that should have been caught during research phase before design was written"). The design prototypes design-stage review to validate "orchestration mechanics," then defers requirements review to eval phase. This tests the wrong hypothesis. You're building a skill to catch design flaws when the real problem is preventing those flaws by catching requirement errors earlier.
- **Why it matters:** If requirements review is actually the highest-leverage phase, you'll spend weeks tuning design-stage personas and discover during eval that they're solving a symptom, not the root cause. You'll have battle-tested infrastructure for the wrong problem. The design explicitly acknowledges this tension (Finding 27 from prior review: "Prototype defers highest-leverage phase") but treats it as an acceptable tradeoff rather than a red flag that the problem framing itself may be wrong.
- **Suggestion:** Reframe the problem as "validate that multi-perspective review catches errors single-perspective review misses" and test at requirements stage first. Use a real past project where bad requirements led to design failures (Second Brain is candidate—problem statement says "review findings revealed design flaws that should have been caught during research phase"). Run requirements review, compare findings to what actually went wrong, validate the hypothesis. If requirements review works, then design/plan reviews are lower-risk extensions. If it doesn't work, you learn that before building 9 personas across 3 stages. Alternatively: accept that this is a "build to learn orchestration mechanics" prototype (not a value hypothesis test) and make that explicit in scope.
- **Iteration status:** New finding

### Finding 2: "Adversarial Review" is Misnamed—This is Comprehensive Coverage, Not Opposition
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Section:** Reviewer Personas, core hypothesis
- **Issue:** The design claims "adversarial multi-agent design review" as the core differentiator, but the 6 design-stage personas are scoped by domain (what to look for), not by stance (what to oppose). Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout can all be right simultaneously—they're examining different parts of the design. True adversarial review requires incompatible worldviews forced to reconcile: "ship fast and prove it works" vs "ship safely and prove it won't break." The prior review flagged this (Finding 26: "Personas solve coverage, not adversarial review") and disposition was "prioritize in early eval" but the design hasn't changed.
- **Why it matters:** If the core hypothesis is "adversarial tension surfaces design flaws," but personas produce additive findings (more inspectors = more coverage), you're not testing the hypothesis. You're testing whether comprehensive review is better than single review—which is obviously true but not novel. The Mitsubishi adversarial debate AI (cited in problem statement as validation) uses **opposing models arguing for incompatible conclusions**, not parallel models inspecting different domains. Your design is closer to code review checklists (security + performance + style + correctness) than to adversarial debate.
- **Why it matters (continued):** This affects prompt engineering strategy. Coverage-based personas need non-overlapping domains and clear checklist prompts. Adversarial personas need opposing incentives and debate protocols. You're building the former while claiming the latter. The most valuable finding from adversarial review is "this whole approach is wrong, here's a better framing"—and that requires a reviewer **incentivized to challenge the entire design**, not just find gaps in it. First Principles Challenger is scoped this way, but outvoted 5-to-1 by domain inspectors.
- **Suggestion:** Either (a) rename this "comprehensive multi-perspective review" and acknowledge that adversarial tension is deferred to post-prototype iteration, or (b) redesign 2-3 personas as true adversaries with opposing success criteria. Example pairs: "Optimizer" (minimize complexity, ship fast, defer edge cases) vs "Hardener" (demand robustness, block on unknowns). "User-Centric" (optimize for end-user experience even if it complicates implementation) vs "Operator-Centric" (optimize for maintainability even if UX suffers). Force them to argue and require human to resolve contradictions. Test whether adversarial pairs produce higher-value findings than independent inspectors. This is a significant architectural change, but it's the stated hypothesis.
- **Iteration status:** Previously flagged (Finding 26), still an issue

### Finding 3: The Real Problem is "Skipping Requirements Refinement," Not "Lack of Review Automation"
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Section:** Problem Statement, Desired Workflow
- **Issue:** Problem statement says "No structured requirement refinement—we jumped from 'interesting idea' to 'write the design' without formally prioritizing must-have vs nice-to-have." The desired workflow shows a `calibrate` phase with MoSCoW prioritization, anti-goals, success criteria, and a human checkpoint. The pain points all trace back to skipped or underspecified requirements (Finding 2: "design flaws that should have been caught during research phase," Finding 4: "open questions carried forward unresolved," Finding 5: "no structured requirement refinement"). Yet the design builds review automation. This treats the symptom (unreviewed designs have flaws) not the cause (teams skip requirements).
- **Why it matters:** If the real problem is "teams skip requirements refinement because it's effortful and the value isn't obvious until later," then automating design review doesn't solve it—it just moves the problem downstream. You'll catch design flaws adversarially but still miss requirement-level errors until they compound into implementation failures. The solution to "we skipped requirements" isn't "review designs better," it's "make requirements refinement so obviously valuable and low-friction that you can't skip it."
- **Suggestion:** Reframe the problem as "requirement refinement is skipped because the ROI isn't obvious" and build `parallax:calibrate` first. Make it a 5-minute interaction that takes a user's initial idea and produces MoSCoW prioritization + anti-goals + testable success criteria. Then run a design session **with calibrate output** and compare to historical designs **without it**. Measure: (1) time to stable design (fewer revision cycles?), (2) design review finding severity (fewer Critical findings?), (3) implementation failures (fewer spec-wrong escalations?). If calibrate reduces downstream errors, it proves its own value and solves the "skipped phase" problem. If it doesn't, you learn that requirements refinement isn't actually the lever you thought it was.
- **Iteration status:** New finding

### Finding 4: Finding Classification Assumes Single Root Cause, But Real Failures are Multi-Causal
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Finding Phase Classification, Verdict Logic
- **Issue:** The synthesizer classifies each finding as "survey gap," "calibrate gap," "design flaw," or "plan concern" with single-phase routing. Prior review flagged this (Finding 7: "Phase classification errors could route to wrong pipeline stage") and disposition accepted primary + contributing phase classification. But the design still treats findings as single-phase failures. Real design failures are multi-causal: a missing requirement (calibrate gap) enables a bad assumption (design flaw) which leads to an infeasible plan (plan concern). Classifying this as "design flaw" and fixing the design papers over the upstream requirement gap. Classifying it as "calibrate gap" and restarting requirements fixes the root cause but discards valid design work.
- **Why it matters:** Single-phase classification forces a false choice: fix the immediate symptom or restart the whole pipeline. Multi-causal classification enables two actions: immediate (fix the design flaw) and systemic (note the requirement gap for next project or major revision). This affects verdict logic—if 30% of design flaws trace back to a single missing requirement, the signal is "pause and fix requirements" not "fix these 5 design symptoms individually." The prior review disposition acknowledges this ("systemic issue detection when >30% share root cause") but the design hasn't incorporated it.
- **Suggestion:** Implement the accepted disposition from Finding 7: classify by primary + contributing phases, add aggregate analysis to synthesis step, escalate when systemic patterns detected. Update verdict logic: if multiple design flaws share a common calibrate-gap root cause, escalate with "systemic requirement issue detected—recommend revisiting calibrate phase" rather than "revise design 5 times."
- **Iteration status:** Previously flagged (Finding 7), disposition accepted but not incorporated into design doc

### Finding 5: "Purely Editorial" Synthesizer is Impossible Given Its Responsibilities
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis section, line 124
- **Issue:** Design still says "A Synthesizer agent consolidates reviewer output. Its role is purely editorial—zero judgment on content or severity." Prior review flagged this (Finding 13) and disposition was "reframe as judgment-exercising role" as part of Task 8 prompt iteration. The design doc text was not updated to reflect this decision.
- **Why it matters:** The design doc is inconsistent with implemented decisions. If prompt iteration already reframed the Synthesizer (which Finding 13 disposition confirms), the design should match. Leaving "purely editorial" in the doc misleads future readers and contradicts the prompt engineering work already done.
- **Suggestion:** Update design doc to match Task 8 implementation: "A Synthesizer agent consolidates reviewer output. Its role requires judgment—deduplication, phase classification, and contradiction surfacing all involve semantic interpretation and decision-making. It does NOT add its own findings or override individual reviewer severity ratings without justification."
- **Iteration status:** Previously flagged (Finding 13), resolved in implementation but not in design doc

### Finding 6: Stage Parameter Assumes Linear Pipeline, But Real Design is Iterative
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Skill Interface, Pipeline Integration
- **Issue:** The skill input contract requires "Review stage—one of: requirements, design, plan" assuming a linear pipeline (survey → calibrate → design → plan → execute). Prior review flagged this as "assumes orchestrator context" (Finding 9). Real design workflows are iterative: you write a design, review catches a requirement gap, you revise requirements, re-review requirements, update design, re-review design. The stage parameter doesn't capture "which iteration of which stage" or "re-reviewing requirements after design failed." Pipeline Integration diagram shows one review gate per phase, but iteration loops mean multiple review runs per phase.
- **Why it matters:** If a user runs `parallax:review stage=design` twice (once pre-revision, once post-revision), the skill has no context that this is iteration 2. Cross-iteration tracking (Finding 5 from prior review) partially addresses this (prior summary fed to reviewers), but the stage parameter itself is ambiguous. More importantly, the linear pipeline framing conflicts with the stated design philosophy ("Findings that challenge key assumptions or constraints trigger a full design cycle restart rather than incremental fixes"). Restart means going back to calibrate, running `stage=requirements`, then `stage=design` again—but these aren't new stages, they're iteration 2 of the same stages.
- **Suggestion:** Either (a) add iteration count to skill interface (`stage=design, iteration=2`) and track this explicitly in summary.md, or (b) drop the stage parameter and infer it from artifact structure (e.g., detect MoSCoW lists → requirements, detect architecture diagrams → design). Option (b) aligns with Finding 9 disposition ("auto-detection is YAGNI for MVP, we're the only user") but conflicts with long-term portability (other users won't know stage conventions). Option (a) is more explicit but adds interface complexity. Alternatively: acknowledge that "stage" is actually "artifact type" (what are we reviewing?) not "pipeline position" (where are we in the workflow?) and rename it for clarity.
- **Iteration status:** New finding (related to prior Finding 9)

### Finding 7: Test Cases Don't Validate Core Hypothesis
- **Severity:** Important
- **Phase:** plan (primary), calibrate (contributing)
- **Section:** Prototype Scope validation, Test Cases (CLAUDE.md)
- **Issue:** Design says "Validate with: Second Brain Design test case (3 reviews, 40+ findings in the original session)." The core hypothesis is "multi-perspective review catches gaps single-perspective review misses." But Second Brain test case had 3 serial reviews by different humans (security, design, implementation), not parallel multi-perspective reviews. Testing parallax:review on Second Brain validates "can the skill produce findings?" not "do multiple perspectives catch more than single perspective?" To validate the hypothesis, you need a design that had single-perspective review (or no review) **and subsequently failed**, then show that parallax:review would have caught the failure.
- **Why it matters:** Without counterfactual validation (what would single review have missed?), you can't prove multi-perspective adds value. You'll know the skill runs and produces findings, but not whether those findings are net-new compared to baseline (human single reviewer or no review). The problem statement identifies specific failure modes (Second Brain: dimension mismatch, wrong file paths, spec drift). To validate, you need to show: (1) which findings would have been caught by single reviewer (baseline), (2) which findings required multiple perspectives (value-add), (3) whether those value-add findings prevented real failures.
- **Suggestion:** Restructure test validation: (1) Run parallax:review on Second Brain design doc, (2) Classify findings as "would human reviewer catch this?" vs "requires specific persona lens," (3) Cross-reference against actual failures (dimension mismatch, spec drift—did reviewers flag these?). This produces eval data showing which personas added value. Alternatively: find a historical design that had no review, failed during implementation, and test whether parallax:review would have caught the errors. If no such test case exists, acknowledge that core hypothesis validation is deferred to eval framework (not prototype scope).
- **Iteration status:** New finding

### Finding 8: Output Voice Guidelines Don't Match Development Philosophy
- **Severity:** Minor
- **Phase:** design
- **Section:** Per-Reviewer Output Format, voice rules in CLAUDE.md
- **Issue:** CLAUDE.md says "Output Voice: direct and engineer-targeted, lead with verdict, no hedging language, SRE-style framing: blast radius, rollback path, confidence level." The design's Per-Reviewer Output Format specifies structure (markdown headings, severity field, etc.) but not voice. Prior review flagged this (Finding 23) and disposition was "part of Task 8 prompt iteration—voice guidelines go in stable prompt prefix." But the design doc doesn't reference SRE framing or specify voice rules.
- **Why it matters:** If the design doc is the specification for how reviewers should write findings, and voice rules are a stated requirement, they should appear in the design. This is a documentation gap, not an implementation gap (assuming Task 8 prompts include voice rules as disposition states).
- **Suggestion:** Add a "Voice Rules" subsection to "Per-Reviewer Output Format" specifying: "Active voice. Lead with impact, then evidence. No hedging ('might', 'could', 'possibly'). Quantify blast radius where possible. SRE-style framing: what's the failure mode, what's the blast radius, what's the mitigation." Reference this in stable prompt prefix architecture (Finding 3 from prior review).
- **Iteration status:** Previously flagged (Finding 23), resolved in prompts but not in design doc

### Finding 9: Prototype Scope Should Include "Not Building" List
- **Severity:** Minor
- **Phase:** design
- **Section:** Prototype Scope
- **Issue:** "Prototype Scope" lists what to build now vs later, but doesn't list what **not** to build (anti-scope). Prior review findings include multiple "deferred to eval" decisions (auto-fix detail, quality budget, calibration loop, model tiering, portability validation). These are anti-goals for the prototype—explicitly out of scope. CLAUDE.md development philosophy emphasizes "YAGNI ruthlessly" but the design doesn't make the YAGNI boundary explicit.
- **Why it matters:** Without anti-scope, future implementers (or the user revisiting this later) don't know which omissions are oversights vs deliberate deferrals. This creates scope creep risk ("why didn't we build auto-fix detail?" → "oh, Finding 4 said defer it, but that's not in prototype scope section").
- **Suggestion:** Add "**Explicitly deferred (not in prototype):**" subsection to Prototype Scope listing: auto-fix implementation (Finding 4 disposition: write to disk, iterate in v2), quality budget (Finding 28 disposition: need empirical data first), calibration feedback loop (Finding 29 disposition: JSONL captures signal, analysis comes later), model tiering (Finding 40 disposition: all-Sonnet for MVP, test Haiku in ablation), portability validation (Finding 22 disposition: defer to eval phase), LangGraph/Inspect AI evaluation (Finding 30 disposition: evaluate as implementation substrate post-prototype).
- **Iteration status:** New finding

### Finding 10: "Zero Judgment on Content or Severity" Contradicts "Report Severity Ranges"
- **Severity:** Minor
- **Phase:** design
- **Section:** Synthesis, line 127-134
- **Issue:** Design says Synthesizer has "zero judgment on content or severity" (line 124) but also "Report severity ranges—when reviewers rate the same issue differently, report the range ('Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic'), don't editorialize" (line 130). Detecting that two findings are "the same issue" rated differently requires judging whether they address the same underlying problem—that's content judgment. Prior review Finding 13 disposition resolved this ("reframe as judgment-exercising role") but design text still contains the contradiction.
- **Why it matters:** Same issue as Finding 5—design doc text doesn't match implemented decisions. Minor because it's documentation hygiene, not architectural flaw.
- **Suggestion:** Remove "zero judgment" statement, replace with disposition-aligned text: "The Synthesizer exercises judgment on deduplication, phase classification, and severity range reporting, but does NOT add its own findings or override reviewer severity without justification."
- **Iteration status:** Previously flagged (Finding 13), resolved in prompts but design doc text still contradictory

## Blind Spot Check

What might I have missed given my focus on fundamentals?

**Operational concerns I didn't examine:**
- Error handling for parallel agent failures (prior review Finding 1 covered this—accepted, mark partial if not 100% reviewers succeed)
- Progress indication during long-running reviews (prior review Finding 15)
- Git failure modes (prior review Finding 32)
- Cost estimation and visibility (prior review Finding 11, 33)

These are practical implementation details other reviewers flagged. My focus on "are we solving the right problem?" means I didn't validate whether the solution is buildable, only whether it's the right solution.

**Eval framework design:**
I didn't examine how the eval framework will validate review quality. If the core hypothesis is "multi-perspective catches more than single perspective," the eval must measure finding quality (precision/recall), not just finding count. Other reviewers likely covered this.

**Integration with existing skills:**
I didn't examine how this integrates with superpowers plugin's brainstorming/planning skills. Prior Art Scout likely examined this (Finding 30: Inspect AI integration).

**User experience during interactive processing:**
I didn't examine UX details for accept/reject flow, finding presentation, or batch operations. Edge Case Prober and Feasibility Skeptic likely covered this (Finding 14: large finding counts overwhelm processing).

My blind spot is **practical feasibility and user experience**—I focus on "is the problem framing right?" not "will this work in production?" That's by design (my role), but it means other reviewers' findings on implementation risk, UX friction, and operational concerns are critical complements.
