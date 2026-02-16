# Review Summary: parallax-review-v1 (Iteration 2)

**Date:** 2026-02-15
**Design:** docs/plans/2026-02-15-parallax-review-design.md
**Requirements:** docs/problem-statements/design-orchestrator.md
**Stage:** design
**Verdict:** revise
**Reviewers:** 6/6 completed

## Changes from Prior Review

**Iteration 1 (prior review):** 41 findings (8C/22I/11M), all processed with dispositions
**Iteration 2 (this review):** 55 findings (15C/28I/12M)

### Key Observations

**Documentation debt detected as systemic issue:** 67% of Requirement Auditor's findings (10 of 15) are "accepted prior findings not yet reflected in design doc." This is a **process finding**, not a design flaw—the decisions were good (Task 8 implemented them in prompts/code), but the design doc wasn't updated in parallel. Root cause: design doc treated as static artifact rather than living spec.

**Prior findings addressed in implementation:**
- Finding 2 (Async workflows) → Task 8 established async-first architecture
- Finding 3 (Reviewer output compliance) → Schema validation added to prompts
- Finding 4 (Topic label validation) → Sanitization implemented
- Finding 5 (Discuss mode) → Cut from MVP, replaced with reject-with-note
- Finding 7 (Synthesizer role) → Reframed as judgment-exercising (not "purely editorial")
- Finding 9 (Git commit strategy) → Single commit per review + auto-fix as separate commit
- Finding 10 (Product Strategist missing) → Acknowledged, persona activation unchanged
- Finding 12 (Review stage input) → Acknowledged as low-priority for MVP
- Finding 1 (Parallel failure) → Partial resolution (timeout/retry logic in prompts, not design)

**Prior findings that persisted or escalated:**
- Finding 4 (Auto-fix) → Still missing from design (Critical, 2 reviewers)
- Finding 5 (Cross-iteration tracking) → Still incomplete (Critical, 4 reviewers)
- Finding 3 (Prompt caching) → Still not specified (Critical, 2 reviewers)
- Finding 6 (Phase classification) → Disposition accepted but design not updated (Important, 2 reviewers)
- Finding 8 (Severity ranges) → Disposition accepted but design not updated (Important)

**New findings introduced by iteration:**
- **Critical:** Requirement versioning/drift (Assumption Hunter Finding 1), Multi-causal phase classification routing (Assumption Hunter Finding 2), Text-hash finding ID brittleness (Assumption Hunter Finding 3), Design-vs-implementation gap (Feasibility Skeptic Finding 1), JSONL format missing (Feasibility Skeptic Finding 2, Edge Case Prober Finding 12)
- **Important:** Requirements drift detection (Assumption Hunter Finding 4), JSONL schema design (Assumption Hunter Finding 5), Verdict timing (Assumption Hunter Finding 6), Multi-user workflows (Assumption Hunter Finding 4), Reject-with-note processing (Edge Case Prober Finding 3), Auto-fix git safety (Edge Case Prober Finding 6)

**Cross-reviewer consensus (3+ reviewers flagged same issue):**
- Design doc out of sync with implementation (4 reviewers: Assumption Hunter, Edge Case Prober, Requirement Auditor, First Principles)
- JSONL format mentioned in dispositions but not in design (3 reviewers: Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic)
- Cross-iteration finding ID stability undefined (3 reviewers: Assumption Hunter, Edge Case Prober, Requirement Auditor)

**First Principles challenges to core framing:**
- Finding 1: Building design review to validate orchestration hypothesis is circular (Critical)
- Finding 2: "Adversarial review" is misnamed—this is comprehensive coverage, not opposition (Critical)
- Finding 3: Real problem is "skipping requirements," not "lack of review automation" (Critical)

**Prior Art Scout findings (leverage vs build):**
- Finding 1: Inspect AI multi-agent patterns already solve orchestration (Critical)
- Finding 2: LangGraph solves stateful workflow and human-in-the-loop gates (Critical)
- Finding 3: LangSmith annotation UI solves finding processing UX (Important)
- Finding 4: Braintrust LLM-as-judge solves severity normalization (Important)
- Finding 6: Compound Engineering is exact prior art for learning loop (Important)
- Finding 7: adversarial-spec demonstrates multi-LLM debate pattern (Important)

### Systemic Patterns

**Build vs Leverage imbalance:** Prior Art Scout identifies mature solutions exist for 80% of what's being custom-built (orchestration, state management, annotation UI, severity scoring). CLAUDE.md says "BUILD adversarial review (novel), LEVERAGE mature frameworks" but design custom-builds infrastructure. Novel contribution (finding classification, persona prompts) is 20% of implementation surface area.

**Design-first vs prototype-first tension:** Feasibility Skeptic Finding 1 notes design was written post-implementation (11 commits already exist). This explains documentation debt—design is rationalizing what was built, not specifying what to build. Standard practice: design review before implementation.

**Multi-causal finding classification:** Multiple reviewers (Assumption Hunter Finding 2, First Principles Finding 4, Edge Case Prober Finding 8) note that phase classification assumes single root cause, but real failures are multi-causal. Disposition for Finding 7 (iteration 1) accepted primary+contributing classification, but design not updated.

## Verdict Reasoning

**Verdict: revise**

Multiple Critical findings require design doc updates before marking as approved:

1. **Documentation debt (systemic):** 10 accepted findings from iteration 1 implemented in code but not reflected in design doc. Design is authoritative spec—if out of sync, it's wrong.
2. **JSONL format:** Decided per MEMORY.md, referenced in multiple dispositions, completely missing from design. This is structural (affects storage, parsing, finding IDs) not cosmetic.
3. **Cross-iteration tracking:** Stable finding IDs, status tracking, prior summary context—all accepted in iteration 1, none specified in design doc.
4. **Auto-fix mechanism:** Explicitly required by problem statement, disposition accepted in iteration 1, still not in design.
5. **Prompt caching architecture:** Stated as architectural convention (not optional) in requirements, still not specified in design.

**Why revise instead of proceed:** These aren't new discoveries requiring redesign—they're accepted decisions not yet documented. Remediation is writing, not rearchitecting. 1-2 hours to update design doc with accepted decisions.

**Why not escalate:** No calibrate gaps that block design-level fixes. First Principles challenges (Findings 1-3) are valid critiques of problem framing, but they're exploratory (should be evaluated empirically in prototype) not blocking (must fix before building). Prior Art Scout leverage opportunities (Inspect AI, LangGraph) should be evaluated during implementation, not redesigned before building.

**Quality gate:** Next iteration should show iteration 1 accepted findings incorporated into design doc, JSONL schema specified, cross-iteration tracking designed, auto-fix step documented.

## Finding Counts

- **Critical:** 15 (up from 8)
- **Important:** 28 (up from 22)
- **Minor:** 12 (up from 11)
- **Contradictions:** 0 (down from 3—prior contradictions resolved via dispositions)

## Findings by Phase

- **Survey gaps:** 0
- **Calibrate gaps:** 7 (problem framing, requirements drift, build-vs-leverage decisions)
- **Design flaws:** 38 (mostly documentation debt + new iteration-introduced concerns)
- **Plan concerns:** 7 (portability, cost tracking, test validation)

## Critical Findings

### Finding 1: Accepted Critical Findings Not Yet Reflected in Design Doc
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Entire design doc (multiple sections need updates)
- **Issue:** Prior review produced 8 Critical findings, all accepted by user with disposition notes. Task 8 updated agent prompts and skill code, but the design doc was not updated to reflect these decisions. Specifically: Finding 3 (prompt caching architecture), Finding 4 (auto-fix mechanism), Finding 5 (cross-iteration tracking), Finding 6 (discuss mode cut from MVP), Finding 7 (phase classification by primary+contributing), Finding 8 (severity range handling). The design doc still describes "discuss" mode (cut), doesn't specify auto-fix step (added), doesn't include prompt architecture section (required).
- **Why it matters:** The design doc is the authoritative specification for implementation. If it doesn't reflect accepted design decisions, it's out of date and future implementers (or eval framework) will build the wrong thing. This is documentation debt that invalidates the design-as-spec. Git commits show code/prompts were updated, but design doc wasn't.
- **Suggestion:** Update design doc to reflect all accepted Critical findings. Add sections: (1) "Prompt Architecture" (Finding 3—caching structure), (2) "Auto-Fix Step" in synthesis section (Finding 4), (3) "Cross-Iteration Tracking Mechanism" (Finding 5), (4) Remove or mark "discuss" mode as future/deferred (Finding 6), (5) Update "Finding Phase Classification" to specify primary+contributing phases (Finding 7), (6) Update "Verdict Logic" to clarify severity range handling (Finding 8).
- **Fixability:** human-decision
- **Status:** pending

### Finding 2: Auto-Fix Requirement Still Not Designed
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Synthesis, UX Flow (missing auto-fix step)
- **Issue:** Prior review Finding 4 flagged "Auto-fix requirement completely missing" (Critical severity). User accepted with disposition: "Auto-fix step between synthesis and human processing. Git history must show auto-fixes as separate commit from human-reviewed changes, enabling async review of what was auto-applied." Design doc still shows synthesis → human processing flow with no auto-fix step. No specification for: (1) how findings are classified as auto-fixable, (2) what criteria define "auto-fixable", (3) which agent performs auto-fixes, (4) how fixes are validated before applying, (5) commit strategy.
- **Why it matters:** Explicitly required by problem statement and flagged Critical in prior review. User accepted it as required. Without this, humans must manually process obvious fixes (typos, broken links, path corrections), defeating automation value. The disposition note specifies a key architectural decision (separate commits for async review) that's not in the design.
- **Suggestion:** Add "Auto-Fix" section to design specifying: (1) Classification criteria (conservative MVP: typos in markdown, missing file extensions, broken internal links, path corrections), (2) Auto-fix agent responsibilities (apply fixes, write updated design to disk, commit separately), (3) Validation (re-run subset of reviewers on auto-fixed sections), (4) UX flow update: synthesis → auto-fix → commit auto-fixes → human processing → commit human-reviewed changes. Two distinct commits per cycle enables async review transparency.
- **Fixability:** human-decision
- **Status:** pending

### Finding 3: Cross-Iteration Finding Tracking Mechanism Still Incomplete
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor, Assumption Hunter, Edge Case Prober
- **Section:** Synthesis, UX Flow, Output Artifacts
- **Issue:** Prior review Finding 5 flagged "Cross-iteration finding tracking incomplete" (Critical). User accepted with disposition: "Stable finding IDs, status tracking across iterations, prior summary fed to reviewers on re-review." Design doc still has no mechanism for: (1) generating stable finding IDs (hash of section + issue? manual tagging?), (2) storing finding status across iterations (open/addressed/rejected), (3) feeding prior summary to reviewers, (4) detecting which findings from iteration N are resolved in iteration N+1.
- **Why it matters:** Requirements doc explicitly states "Track which findings have been addressed across iterations." Without this, re-reviews waste human time cross-referencing. Edge Case Prober notes reviewers won't focus scrutiny on changed sections where bugs are likely. Disposition specifies the solution but design doesn't implement it.
- **Suggestion:** Add "Finding Persistence Mechanism" section specifying: (1) Finding ID generation (semantic hash or LLM-based matching across iterations—see Assumption Hunter Finding 3 for hash brittleness concerns), (2) Status field in summary.md (open/addressed/rejected/partial), (3) Reviewer context update: include prior summary.md in reviewer prompts, (4) Synthesizer cross-iteration diff: "Iteration 2 resolved Findings 1, 3, 5 from Iteration 1. Findings 2, 4 remain open. 8 new findings," (5) Git diff integration: highlight changed sections to reviewers.
- **Fixability:** human-decision
- **Status:** pending

### Finding 4: Prompt Caching Architecture Still Not Specified
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Missing (should be "Reviewer Prompt Architecture" section)
- **Issue:** Prior review Finding 3 flagged "Prompt caching architecture not addressed" (Critical). Requirements doc states "Prompt structure for caching: System prompts should be structured as stable cacheable prefix + variable suffix. This is an architectural convention, not a feature—90% input cost reduction on cache hits. Decide before building skills." Design doc has no prompt architecture section. Task 8 prompt iteration happened but design doc has no specification.
- **Why it matters:** This affects how reviewer prompts are written. If prompts aren't structured for caching from start, refactoring later invalidates eval data. Cost strategy in CLAUDE.md explicitly relies on prompt caching for 90% cost reduction—this is architectural, not optional.
- **Suggestion:** Add "Reviewer Prompt Architecture" section specifying: (1) Stable prefix structure (persona identity, focus areas, methodology, output format rules, voice guidelines), (2) Variable suffix structure (design artifact, requirements context, prior review summary if re-review, iteration number), (3) Cache boundary (where prefix ends, suffix begins), (4) Prompt versioning (changes to prefix invalidate cache, track prompt version in output metadata), (5) Prototyping tradeoff acknowledgment (defer cache optimization until prompts stabilize post-MVP, but design structure now).
- **Fixability:** human-decision
- **Status:** pending

### Finding 5: Requirement Versioning Assumptions Unvalidated
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Agents (all 7 agent prompts, especially reviewer personas)
- **Issue:** All agent prompts reference requirements documents and design artifacts as inputs, but assume these artifacts remain semantically stable across iterations. The design supports re-reviews after revision, but agent prompts contain no mechanism to detect or handle requirement drift (requirements doc changed between iteration 1 and iteration 2). If requirements change mid-iteration, reviewers comparing "design v2 vs requirements v2" have no context that requirements themselves moved, creating false "design now satisfies requirement X" signals when requirement X was actually relaxed.
- **Why it matters:** In real design workflows, adversarial review findings often trigger requirement clarification ("we need to specify what happens at scale" → requirement gets added). Next review cycle operates against updated requirements, but reviewers can't distinguish "design improved" from "requirement lowered the bar." This breaks finding classification—a previously-Critical finding resolved by changing the requirement should escalate to calibrate, not mark as "design fixed."
- **Suggestion:** Add requirement versioning to review contract. Options: (1) Timestamp or hash requirements doc, reviewers note which version they reviewed against, synthesizer flags requirement changes across iterations, (2) Git-based diff: pass `git diff` of requirements to reviewers on re-review ("requirements changed: added failure mode section, relaxed latency constraint"), (3) Require explicit user confirmation when re-reviewing with modified requirements.
- **Fixability:** human-decision
- **Status:** pending

### Finding 6: Reviewer Personas Assume Linear Causality for Phase Classification
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Assumption Hunter
- **Section:** Finding Phase Classification, Per-Reviewer Output Format
- **Issue:** Reviewers classify findings by single primary phase (survey/calibrate/design/plan) with optional contributing phase, but the classification schema assumes each finding has a clear root cause in one pipeline phase. Real design failures are multi-causal: missing research (survey) leads to unstated assumption (calibrate gap) which enables flawed design (design) that's hard to implement (plan). The design forces reviewers to pick one primary phase when the finding actually indicates systemic failure across multiple phases. Prior review Finding 7 acknowledged this and added contributing phase classification, but contributing phase is secondary metadata—verdict logic and escalation routing use only primary phase.
- **Why it matters:** If a finding is "design flaw (primary) caused by calibrate gap (contributing)," the system routes to design revision when it should escalate to calibrate. The multi-causal nature is documented but not operationalized in routing logic.
- **Suggestion:** Revise verdict logic to treat contributing phases as escalation triggers. Rule: If any finding has "calibrate gap (contributing)" or "survey gap (contributing)", verdict cannot be "proceed"—even if primary phase is design. User must acknowledge the systemic issue before moving forward. Alternatively, synthesizer should aggregate contributing phases: if >30% of findings share same contributing phase, that phase failed and requires re-work regardless of primary classifications.
- **Fixability:** human-decision
- **Status:** pending

### Finding 7: Cross-Iteration Finding Tracking Assumes Text Stability
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Synthesis (cross-iteration tracking, Finding 5 from prior review)
- **Issue:** Prior review Finding 5 added stable finding IDs "e.g., hash of section + issue text" for tracking findings across iterations. Hash-based IDs break when finding text is refined without changing substance. Example: Iteration 1 flags "Parallel agent dispatch has no retry logic" (hash: abc123). Designer adds retries. Iteration 2 reviewer writes "Parallel agent retry logic lacks exponential backoff" (hash: def456). These are the same design concern evolving, but hash IDs treat them as unrelated findings.
- **Why it matters:** Finding persistence mechanism from Finding 5 relies on exact text matching (via hashing) which is brittle. Reviewers naturally rephrase findings, especially when design improves partially. User sees "12 new findings" when actually "8 are refinements of prior findings, 4 are truly new." Defeats the purpose of iteration tracking.
- **Suggestion:** Replace text hashing with semantic fingerprinting or section-based anchoring. Options: (1) Anchor findings to design doc section headings (stable across iterations if structure doesn't change), track as "Section: Parallel Dispatch, Reviewer: Edge Case Prober, Iteration: 2" and deduplicate by section+reviewer, (2) LLM-based semantic matching: synthesizer compares new findings to prior findings and flags semantic overlap, (3) Hybrid: hash section+severity+reviewer as coarse ID, manual user confirmation when hashes don't match but section overlaps.
- **Fixability:** human-decision
- **Status:** pending

### Finding 8: Design vs Implementation Reality Gap
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** Entire design document
- **Issue:** The design document describes a system that was already implemented (11 commits on feature/parallax-review branch). This review is examining a design artifact that may not match what was actually built. Standard practice: design review happens before implementation, not after. The test case (smoke test against own design doc) validates the orchestration works but doesn't validate that the implementation matches this design spec.
- **Why it matters:** Design documents written post-implementation are rationalizations, not blueprints. They tend to gloss over implementation complexities. Without seeing the actual implementation code, this review may be validating an idealized description rather than buildable reality. If the implementation diverged from this design during development, findings here are academic.
- **Suggestion:** Include implementation artifacts (code snippets, actual agent prompts, error handling logic) in design reviews when the design is written after the fact. Better: run design review before implementation, use findings to improve the design, then implement. Alternative: treat this as a "design extraction" doc (documenting what was built) and review it for completeness/accuracy rather than feasibility.
- **Fixability:** human-decision
- **Status:** pending

### Finding 9: JSONL Output Format Missing from Design
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Feasibility Skeptic, Edge Case Prober, Requirement Auditor, Assumption Hunter
- **Section:** Output Artifacts, Per-Reviewer Output Format, Summary Format
- **Issue:** MEMORY.md states "JSONL as canonical output format—decided but not yet implemented. Current markdown works for MVP." The design document specifies only markdown output format with no mention of JSONL structure, schema, or migration path. Disposition notes reference JSONL enabling features (Finding 14: "JSONL format enables this naturally—jq filters by severity/persona/phase"), but the design has zero specification for what that looks like.
- **Why it matters:** JSONL vs markdown is not a trivial format change—it affects how findings are identified (stable IDs), how dispositions are tracked (structured fields vs prose), how tools consume review output (jq vs grep), and whether reviews are machine-processable. This is the largest structural decision not documented in the design. If JSONL is the decided format, the markdown output format section is describing throwaway scaffolding, not the actual system.
- **Suggestion:** Either (1) add JSONL schema specification to design (finding format, summary format, disposition tracking), or (2) acknowledge markdown is MVP and JSONL is v2, specifying migration path (parsers that convert markdown findings to JSONL, or dual output during transition). Clarify whether "markdown works for MVP" means "markdown is sufficient for prototype testing" (acceptable) or "we'll keep markdown indefinitely" (conflicts with JSONL decision).
- **Fixability:** human-decision
- **Status:** pending

### Finding 10: Building Design Review to Validate Orchestration Hypothesis is Circular
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** First Principles Challenger
- **Section:** Prototype Scope, Problem Statement framing
- **Issue:** The problem statement says "requirement refinement has been the single biggest design quality lever in practice" and identifies requirements gaps as the root cause of design failures. The design prototypes design-stage review to validate "orchestration mechanics," then defers requirements review to eval phase. This tests the wrong hypothesis. You're building a skill to catch design flaws when the real problem is preventing those flaws by catching requirement errors earlier.
- **Why it matters:** If requirements review is actually the highest-leverage phase, you'll spend weeks tuning design-stage personas and discover during eval that they're solving a symptom, not the root cause. You'll have battle-tested infrastructure for the wrong problem. The design explicitly acknowledges this tension but treats it as an acceptable tradeoff rather than a red flag that the problem framing itself may be wrong.
- **Suggestion:** Reframe the problem as "validate that multi-perspective review catches errors single-perspective review misses" and test at requirements stage first. Use a real past project where bad requirements led to design failures. Run requirements review, compare findings to what actually went wrong, validate the hypothesis. If requirements review works, then design/plan reviews are lower-risk extensions. Alternatively: accept that this is a "build to learn orchestration mechanics" prototype (not a value hypothesis test) and make that explicit in scope.
- **Fixability:** human-decision
- **Status:** pending

### Finding 11: "Adversarial Review" is Misnamed—This is Comprehensive Coverage, Not Opposition
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Flagged by:** First Principles Challenger
- **Section:** Reviewer Personas, core hypothesis
- **Issue:** The design claims "adversarial multi-agent design review" as the core differentiator, but the 6 design-stage personas are scoped by domain (what to look for), not by stance (what to oppose). Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout can all be right simultaneously—they're examining different parts of the design. True adversarial review requires incompatible worldviews forced to reconcile: "ship fast and prove it works" vs "ship safely and prove it won't break." Prior review flagged this (Finding 26) and disposition was "prioritize in early eval" but the design hasn't changed.
- **Why it matters:** If the core hypothesis is "adversarial tension surfaces design flaws," but personas produce additive findings (more inspectors = more coverage), you're not testing the hypothesis. You're testing whether comprehensive review is better than single review—which is obviously true but not novel. The Mitsubishi adversarial debate AI uses opposing models arguing for incompatible conclusions, not parallel models inspecting different domains. Your design is closer to code review checklists (security + performance + style + correctness) than to adversarial debate.
- **Suggestion:** Either (a) rename this "comprehensive multi-perspective review" and acknowledge that adversarial tension is deferred to post-prototype iteration, or (b) redesign 2-3 personas as true adversaries with opposing success criteria. Example pairs: "Optimizer" (minimize complexity, ship fast, defer edge cases) vs "Hardener" (demand robustness, block on unknowns). "User-Centric" (optimize for end-user experience even if it complicates implementation) vs "Operator-Centric" (optimize for maintainability even if UX suffers). Force them to argue and require human to resolve contradictions.
- **Fixability:** human-decision
- **Status:** pending

### Finding 12: The Real Problem is "Skipping Requirements Refinement," Not "Lack of Review Automation"
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Flagged by:** First Principles Challenger
- **Section:** Problem Statement, Desired Workflow
- **Issue:** Problem statement says "No structured requirement refinement—we jumped from 'interesting idea' to 'write the design' without formally prioritizing must-have vs nice-to-have." The desired workflow shows a `calibrate` phase with MoSCoW prioritization, anti-goals, success criteria, and a human checkpoint. The pain points all trace back to skipped or underspecified requirements. Yet the design builds review automation. This treats the symptom (unreviewed designs have flaws) not the cause (teams skip requirements).
- **Why it matters:** If the real problem is "teams skip requirements refinement because it's effortful and the value isn't obvious until later," then automating design review doesn't solve it—it just moves the problem downstream. You'll catch design flaws adversarially but still miss requirement-level errors until they compound into implementation failures.
- **Suggestion:** Reframe the problem as "requirement refinement is skipped because the ROI isn't obvious" and build `parallax:calibrate` first. Make it a 5-minute interaction that takes a user's initial idea and produces MoSCoW prioritization + anti-goals + testable success criteria. Then run a design session with calibrate output and compare to historical designs without it. If calibrate reduces downstream errors, it proves its own value and solves the "skipped phase" problem.
- **Fixability:** human-decision
- **Status:** pending

### Finding 13: Inspect AI Multi-Agent Patterns Already Solve Orchestration Architecture
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing—build vs leverage decision should have been explicit)
- **Flagged by:** Prior Art Scout
- **Section:** Entire design—Reviewer Personas, Synthesis, UX Flow, Pipeline Integration
- **Issue:** The design custom-builds parallel reviewer dispatch, finding consolidation, retry logic, timeout handling, and result aggregation. Inspect AI (already in tooling budget, MIT license, supports Claude + Codex) provides `multi_agent` pattern with handoff primitives, agent-as-tool composition, built-in retry/timeout, and trace collection. The design doc states "evaluate LangGraph when limits are hit" but doesn't evaluate whether Inspect AI already provides what's being built.
- **Why it matters:** Building custom orchestration means maintaining code for agent dispatch, result collection, retries, timeout handling, progress tracking, cost estimation, and failure recovery. This is 40-60% of the implementation surface area. Inspect AI is production-grade infrastructure (UK AI Safety Institute project), actively maintained, and designed specifically for multi-agent LLM evaluation. Using Inspect positions parallax:review as domain-specific prompt engineering (the novel contribution) rather than infrastructure work (already solved). CLAUDE.md explicitly says "LEVERAGE Inspect AI" but design doesn't reference it.
- **Suggestion:** Evaluate Inspect AI as the implementation substrate. Prototype reviewer personas as Inspect solvers with custom system prompts. Use Inspect's `multi_agent` pattern for parallel dispatch, `scorer` API for finding consolidation, and trace collection for cost tracking. Reserve custom orchestration only if Inspect's patterns prove insufficient after prototyping.
- **Fixability:** human-decision
- **Status:** pending

### Finding 14: LangGraph Solves Stateful Workflow and Human-in-the-Loop Gates
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Prior Art Scout
- **Section:** UX Flow (human checkpoints), Interactive Finding Processing, Iteration Loops
- **Issue:** The design describes stateful workflows (process findings one-at-a-time, maintain disposition state, resume after discussion, track cross-iteration finding history) and human approval gates (verdict → human processing → wrap up) but custom-builds the state management. LangGraph (already in tooling budget, MIT license) is specifically designed for stateful, controllable AI workflows with built-in graph-based state management, conditional transitions, human-in-the-loop pause points, and persistent memory across sessions. Problem statement explicitly lists LangGraph as "natural fit for pipeline control" but design doesn't address it.
- **Why it matters:** State management for "discuss" mode (Finding 6 in prior review, flagged Critical by 4 reviewers) is estimated at 30-50% of implementation time. LangGraph provides this as a core primitive: workflows pause for human input, context persists, and conversation resumes from exact state. Additionally, cross-iteration finding tracking (Finding 5 in prior review, Critical) requires persistent state across review runs—LangGraph's state graphs support this natively. Custom state management in a CLI skill is complex and error-prone. LangGraph is battle-tested production infrastructure with 20k+ stars.
- **Suggestion:** Evaluate LangGraph for the skill's control flow. Model the review process as a state graph: dispatch reviewers (parallel) → synthesize findings (sequential) → human processing loop (conditional, stateful) → wrap up. Use LangGraph's `interrupt` for human approval gates and `state` for finding disposition tracking. If LangGraph proves too heavyweight for a single skill, defer to orchestrator phase (where pipeline state is essential).
- **Fixability:** human-decision
- **Status:** pending

### Finding 15: Cross-Iteration Finding ID Stability Not Specified
- **Severity:** Critical
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 5 disposition (cross-iteration tracking), Synthesis
- **Issue:** Disposition note for prior Finding 5 specifies "stable finding IDs, status tracking across iterations, prior summary fed to reviewers on re-review." The mechanism for generating stable IDs is unspecified in the design. If finding IDs are based on hash of section + issue text, minor wording changes between iterations break tracking. If IDs are reviewer-assigned, reviewers may not maintain consistency. If auto-incremented per topic, findings from different iterations can't be cross-referenced.
- **Why it matters:** Cross-iteration tracking is the entire value proposition of Finding 5's resolution. Without stable ID specification in the design, implementation will either produce brittle hashes (false negatives—treated as new when actually same issue) or require manual ID assignment (error-prone, defeats automation). When a finding reappears in iteration 2, the system must detect "this is Finding 3 from iteration 1" to show status history.
- **Suggestion:** Add to design doc: ID generation algorithm specification. Options: (1) Semantic hash (section + first 100 chars of issue, normalized for whitespace/punctuation), (2) Reviewer-assigned with strict format rules (`AH-001` = Assumption Hunter finding 1), (3) Hybrid (auto-hash with reviewer override for cross-iteration linking), (4) Use LLM to match findings semantically. Document hash collision handling. For MVP, recommend semantic matching via LLM (Synthesizer asks "which prior findings does this match?" when processing each new finding).
- **Fixability:** human-decision
- **Status:** pending

## Important Findings

### Finding 16: Prior Summary Context May Exceed Token Limits on Long Review Chains
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 5 disposition (prior summary fed to reviewers), Cross-iteration context
- **Issue:** Each reviewer receives "prior summary" as context on re-review. If design goes through 5 iterations with 30+ findings each, prior summary grows to 10k+ tokens. With 6 reviewers each receiving full prior context + design doc + requirements, token usage explodes. After 3-4 iterations, input context could exceed model limits or consume entire prompt caching budget.
- **Why it matters:** Long review chains are exactly the scenario where cross-iteration tracking is most valuable (complex designs requiring multiple refinement passes). But feeding all prior history to all reviewers on every iteration is unsustainable. Iteration 5 would be significantly more expensive than iteration 1, with no cost ceiling specified in the design.
- **Suggestion:** Add to design: prior context pruning strategy. Options: (1) Reviewers receive only their own prior findings + high-severity findings from other reviewers (not full summary), (2) Prior findings marked "resolved" are summarized rather than included verbatim, (3) Hard cap on prior context (e.g., most recent 2 iterations only), (4) Use finding IDs to reference prior context by ID rather than full text.
- **Fixability:** human-decision
- **Status:** pending

### Finding 17: "Reject-with-Note" Disposition Has No Schema or Processing
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 6 disposition (reject-with-note), Step 5: Process Findings
- **Issue:** Finding 6 disposition replaces "discuss" mode with "reject-with-note—rejection note becomes calibration input to next review cycle." What happens to these notes is unspecified in the design. Where are they stored? Who reads them? What format? If note says "This finding assumes wrong architecture, we're using event-driven not REST," how does that context reach the reviewers who need it?
- **Why it matters:** Reject-with-note is now the primary mechanism for handling disputed findings and capturing design decisions. Without schema or processing specified in the design, notes become write-only data (captured but never used). Calibration value is lost.
- **Suggestion:** Add to design: rejection note schema and processing flow. Specify: (1) Notes stored in summary.md under each rejected finding, (2) Rejected findings + notes included in prior summary sent to reviewers on re-review (separate section: "Previously rejected findings and why"), (3) Synthesizer checks if rejected findings reappear and surfaces to user, (4) Rejection notes feed into calibration loop.
- **Fixability:** human-decision
- **Status:** pending

### Finding 18: Async-Default Mode Has No Resumption Specification
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 2 disposition (async is default), UX Flow
- **Issue:** Finding 2 disposition states "Async is the default—review always writes artifacts to disk. Interactive mode reuses those same artifacts as a convenience layer." This means: (1) Review runs overnight, writes findings to disk, (2) User processes findings next morning. But the design doesn't specify how resumption works. If user closes terminal after review completes, how do they invoke "process findings from docs/reviews/topic-12345/"?
- **Why it matters:** Async mode is the baseline architecture per disposition note, but there's no interface specification in the design for the second half of the workflow (processing pre-written findings). Users will run reviews overnight, come back the next day, and have no clear path to "pick up where review left off."
- **Suggestion:** Add to design: resumption interface specification. Options: (1) `parallax:review --resume <topic>` loads findings from existing review folder and enters processing mode, (2) Skill checks on invocation whether target topic already has unprocessed findings and prompts user, (3) Document that summary.md tracks processing state (findings with no disposition = unprocessed) and skill uses this to resume.
- **Fixability:** human-decision
- **Status:** pending

### Finding 19: Timestamped Folder Collision Handling Breaks Git Diff Workflow
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 10 disposition (timestamped folders), Output Artifacts, Requirements (git diffing across iterations)
- **Issue:** Finding 10 disposition specifies "timestamped folders for collision handling" (e.g., `docs/reviews/topic-2026-02-15-143022/`). But requirements doc emphasizes "Git commits per iteration. Full history, diffable artifacts" and "diffs show what changed." If each iteration creates a new timestamped folder, git diff between iterations compares completely different file paths—useless. You lose iteration diffing, which was a core design goal.
- **Why it matters:** Timestamped folders solve collision problem but break diffability. The disposition note contradicts the requirement. This is a calibrate gap (requirement for git-based iteration tracking conflicts with timestamp-based collision handling).
- **Suggestion:** Revise disposition or update design to resolve contradiction. Options: (1) Single folder per topic, overwrite files on re-review, rely on git history for iteration tracking (diffs work, collision handled by overwrite), (2) Timestamped folders but add symlink `docs/reviews/topic-latest/` pointing to most recent, and synthesizer produces diff report comparing current iteration to prior, (3) Nested iteration structure: `docs/reviews/topic/iteration-1/`, `docs/reviews/topic/iteration-2/`.
- **Fixability:** human-decision
- **Status:** pending

### Finding 20: Auto-Fix Git Commit May Overwrite User's Unrelated Changes
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 4 disposition (auto-fix as separate commit), Step 6: Wrap Up
- **Issue:** Finding 4 disposition specifies "Auto-fix step between synthesis and human processing. Git history must show auto-fixes as separate commit." Auto-fixes modify the design doc on disk, then commit those changes. But if user has made other edits to the design doc between starting the review and processing findings, auto-fix commit includes unrelated changes. Worse: if auto-fix step runs before user sees findings, it modifies the file before user can reject the fixes.
- **Why it matters:** Auto-fix as described is invasive—modifies source files automatically without user approval. Conflicts with Git Safety Protocol ("NEVER commit changes unless user explicitly asks"). If auto-fix is applied before user processing, user can't reject bad auto-fixes. If applied after, separate commit is impossible (human changes intermixed).
- **Suggestion:** Revise auto-fix workflow in design. Options: (1) Auto-fixes presented to user as suggested changes (patch/diff format), user approves before application, (2) Auto-fixes applied to copy of design doc, not original (user merges if approved), (3) Auto-fixes deferred to post-human-processing (user accepts/rejects findings, then auto-fixable accepted findings are applied as batch), (4) Conservative auto-fix criteria (only formatting/whitespace, no semantic changes) with explicit user approval.
- **Fixability:** human-decision
- **Status:** pending

### Finding 21: Interactive Processing State Loss on Crash or Interruption
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Step 5: Process Findings (interactive mode), Summary.md updates
- **Issue:** User processes findings one-by-one in interactive mode (accept/reject/note). If terminal crashes, network drops, or user interrupts (Ctrl-C) mid-processing, what's the state? Design says summary.md is updated with dispositions, but doesn't specify when—after each finding (incremental save) or at the end of processing (batch save)?
- **Why it matters:** If dispositions are saved only at end, crash loses all progress (user must re-process 41 findings from scratch). If saved incrementally, partial processing is recoverable, but interrupted processing leaves summary.md in partial state. On resume, does skill start from first unprocessed finding, or does user have to track manually?
- **Suggestion:** Specify in design: incremental state persistence. (1) summary.md updated after each finding disposition (crash-safe), (2) On resume (user re-invokes skill on same topic), skill detects partial processing and offers to continue from last processed finding, (3) Add finding index/ID to dispositions so resume position is unambiguous.
- **Fixability:** human-decision
- **Status:** pending

### Finding 22: Synthesizer Phase Classification Disagreements Not Reconciled
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 7 disposition (reviewers suggest phase, synthesizer reconciles), Synthesis responsibilities
- **Issue:** Finding 7 disposition specifies "Reviewers suggest phase in their findings, synthesizer reconciles disagreements with reasoning." What happens when reconciliation is ambiguous? Example: Assumption Hunter flags "assumes X" (calibrate gap), Edge Case Prober flags "doesn't handle X" (design flaw). Same issue, different phase classification. Synthesizer must pick one or classify as both (primary + contributing). If reviewers disagree 3-to-2, does majority win? Consensus rule unspecified in design.
- **Why it matters:** Phase classification drives verdict logic (calibrate gap → escalate, design flaw → revise). Wrong classification wastes time or produces bad designs. If synthesizer has no tie-breaking rule, it either makes arbitrary decisions (bad) or punts every disagreement to user as contradiction (defeats automation).
- **Suggestion:** Add to design: phase reconciliation rules. Specify: (1) When reviewers disagree, use primary + contributing classification (both recorded, action is based on primary), (2) Primary phase = most common suggestion from reviewers (majority vote), (3) If tied, escalate conservatively (calibrate > design > plan), (4) Synthesizer includes reasoning in summary, (5) User can override during processing.
- **Fixability:** human-decision
- **Status:** pending

### Finding 23: "Systemic Issue Detection" Threshold Arbitrary and Untested
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 7 disposition (systemic issue detection when >30% share root cause)
- **Issue:** Finding 7 disposition adds "systemic issue detection when >30% of findings share a common root cause." The 30% threshold is arbitrary (why not 25%? 40%?). "Share a common root cause" is subjective—how does synthesizer determine this? If 12/41 findings trace to "missing error handling," is that 29% (not systemic) or does it round to 30% (systemic)?
- **Why it matters:** If threshold is too low, every review triggers false systemic escalations. If too high, real systemic issues are missed. Root cause attribution is judgment-heavy work requiring semantic analysis. Synthesizer must either have taxonomy of root causes or perform ad-hoc clustering, both error-prone and not specified in design.
- **Suggestion:** Either add systemic detection specification to design or defer to post-MVP. If implemented, design must specify: (1) Root cause taxonomy (explicit categories like "missing requirements," "unstated assumptions"), (2) Reviewers tag findings with root cause category, (3) Threshold configurable per topic, (4) Systemic issue detection is advisory, not automatic escalation. Alternatively, start with manual pattern detection until eval data shows automated detection is reliable.
- **Fixability:** human-decision
- **Status:** pending

### Finding 24: No Guidance on When to Stop Re-Reviewing
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Verdict Logic, UX Flow (revise iteration loop)
- **Issue:** Design specifies `revise` verdict triggers re-review after user updates design. But there's no exit condition. If iteration 2 produces new Critical findings (different from iteration 1), user revises again. Iteration 3 produces more findings. When does the loop end? When findings count reaches zero (unrealistic)? When no new Critical findings appear? When user manually decides "good enough"?
- **Why it matters:** Without stopping criteria in the design, reviews can iterate indefinitely. Real designs have tradeoffs—some edge cases are deferred intentionally, some Important findings are accepted as constraints. Current design treats all Critical findings as blockers but provides no framework for "this Critical finding is acceptable risk, proceed anyway."
- **Suggestion:** Add to design: review convergence criteria. Options: (1) Explicit "good enough" threshold (e.g., "2 consecutive iterations with no new Critical findings"), (2) Allow user to override verdict ("proceed despite Critical findings" with required justification), (3) Track iteration count and flag if >3 iterations, (4) Add "defer" disposition for findings user accepts as out-of-scope.
- **Fixability:** human-decision
- **Status:** pending

### Finding 25: "Critical-First" Mode Orphans Non-Critical Findings Across Iterations
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Step 4: Present Summary (Critical-first mode), Finding processing
- **Issue:** Critical-first mode processes only Critical findings, then user revises design and re-reviews. Iteration 2 produces new findings (some overlap with prior Important/Minor from iteration 1, some new). User processes Critical-first again. Important findings from iteration 1 are never processed—orphaned. After 3 iterations of Critical-first, there may be 40+ unprocessed Important findings spanning multiple iterations.
- **Why it matters:** Critical-first is designed for fast iteration, but it creates accumulating technical debt of unprocessed findings. Eventually user must process all orphaned findings or accept that valuable feedback was discarded. No mechanism in the design tracks which findings are carried forward unprocessed vs which are obsoleted by design changes.
- **Suggestion:** Add to design: orphaned finding management for Critical-first workflow. Specify: (1) After Critical-first processing, synthesizer marks remaining findings as "deferred to next iteration," (2) On re-review, synthesizer reconciles prior deferred findings with new findings, (3) After revise loop converges, user is prompted to process accumulated deferred findings, (4) Alternative: Critical-first mode includes Important findings related to same root cause as Critical findings.
- **Fixability:** human-decision
- **Status:** pending

### Finding 26: JSONL Format Noted But Not Specified in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober, Requirement Auditor
- **Section:** Finding 14 disposition (JSONL format enables filtering), Output Artifacts
- **Issue:** Finding 14 disposition states "JSONL format enables this naturally—jq filters by severity/persona/phase." But design doc specifies markdown output format throughout. JSONL mentioned in MEMORY.md as "decided but not yet implemented." No schema, field definitions, or migration path specified in design.
- **Why it matters:** Multiple disposition notes reference JSONL as solution. If JSONL is core output format, it should be in the design. If it's deferred, disposition notes shouldn't reference it as solved. Current ambiguity makes implementation unclear—should MVP implement JSONL or markdown?
- **Suggestion:** Add to design: output format specification. Either (1) Add JSONL output format section with schema, specify markdown is human-readable rendering of JSONL, OR (2) Update disposition notes to clarify JSONL is post-MVP enhancement, markdown is baseline for prototype. Specify migration path if format changes.
- **Fixability:** human-decision
- **Status:** pending

### Finding 27: Parallel Review Execution May Hit Rate Limits
- **Severity:** Important
- **Phase:** plan (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Step 2: Dispatch (6 reviewers in parallel)
- **Issue:** Dispatching 6 reviewers in parallel means 6 simultaneous API calls to Claude. If user is running multiple reviews concurrently (e.g., testing on 4 test cases in parallel), that's 24 simultaneous requests. Rate limits may be hit, causing some reviewers to fail with 429 errors.
- **Why it matters:** Finding 1 (parallel agent failure handling) from prior review was marked RESOLVED with retry logic, but retrying rate limit errors with exponential backoff could add 30-60 seconds to review time. If rate limit is persistent, all retries fail and review completes with partial results. Design doesn't specify whether parallel execution is configurable.
- **Suggestion:** Add to design: rate limit awareness. Specify: (1) Make parallelism configurable (default 6, user can set to 3 or 1 for serial execution), (2) Implement request pacing (stagger reviewer dispatch by 1-2 seconds), (3) Document rate limit failures in summary and suggest reducing parallelism if frequent, (4) For batch API mode (future), this is non-issue.
- **Fixability:** human-decision
- **Status:** pending

### Finding 28: Async-First Architecture Assumes Single Human Reviewer
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Assumption Hunter
- **Section:** UX Flow, Finding 2 disposition from prior review
- **Issue:** Prior review Finding 2 established "async is the default—review always writes artifacts to disk, interactive mode is convenience layer." This correctly decouples review execution from human availability, but the finding disposition workflow still assumes single human making accept/reject decisions. In team contexts, multiple people may want to process findings asynchronously, discuss as a group, or delegate finding review. Current design has no multi-user support or finding assignment.
- **Why it matters:** CLAUDE.md states this is "useful beyond personal infra, applicable to work contexts." Work contexts have teams. If three engineers all run `parallax:review --process-findings` on the same summary.md, last writer wins. No support for "Alice accepted findings 1-5, Bob is reviewing 6-10, Carol flagged 11 for team discussion."
- **Suggestion:** Add multi-user disposition tracking to summary.md format. Minimal version: dispositions include reviewer name + timestamp. Skill checks for existing dispositions before allowing overwrites. Or defer to LangSmith which has built-in team annotation features. Document the single-user limitation if multi-user is out of scope for MVP.
- **Fixability:** human-decision
- **Status:** pending

### Finding 29: JSONL Format Deferred But Not Designed
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Output Artifacts, Per-Reviewer Output Format
- **Issue:** Multiple prior findings reference JSONL as canonical output format. MEMORY.md states "JSONL as canonical output format—decided but not yet implemented. Current markdown works for MVP." Design doc specifies only markdown format. No schema definition for JSONL, no migration path from markdown to JSONL, no specification of how JSONL and markdown coexist.
- **Why it matters:** Building markdown-first then migrating to JSONL later requires either (1) rewriting all file I/O and parsing logic, or (2) maintaining two output formats indefinitely. JSONL schema decisions affect storage, parsing, and UI layer. Deferring implementation is fine (YAGNI), but deferring design means the markdown format may bake in assumptions that conflict with JSONL needs.
- **Suggestion:** Add lightweight JSONL schema section to design doc specifying planned structure (even if implementation is deferred). Minimal version: one JSON object per finding with keys `{id, reviewer, severity, phase, section, issue, why_it_matters, suggestion, iteration_status, disposition}`. Specify whether markdown is transitional or permanent. Clarify whether "JSONL format" means reviewers output JSON or synthesizer converts markdown findings to JSONL.
- **Fixability:** human-decision
- **Status:** pending

### Finding 30: Verdict Logic Assumes Findings Are Independent
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Assumption Hunter
- **Section:** Verdict Logic, Synthesis
- **Issue:** Verdict logic states "Any Critical finding → revise." This treats findings as independent boolean flags, but findings often have dependency relationships. Example: Finding A (Critical) "No authentication specified" and Finding B (Minor) "Session timeout should be configurable"—if you fix A by deciding "this is internal-only, no auth needed," then B becomes irrelevant. Conversely, cluster of 5 Minor findings all in same subsystem may signal "this subsystem is underdesigned" which should block proceed.
- **Why it matters:** Verdict logic doesn't account for finding relationships, clusters, or dependencies. User must mentally model these relationships during processing, reducing automation value.
- **Suggestion:** Defer verdict computation until after user processes findings (reorder UX flow), OR make verdict preliminary. Synthesizer could add relational analysis: "Findings 3, 7, 12 all relate to error handling subsystem. Addressing Finding 3 may resolve the others." User processes findings, system recomputes verdict based on accepted findings.
- **Fixability:** human-decision
- **Status:** pending

### Finding 31: Discuss Mode Still in Design Doc Despite Being Cut
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Step 5: Process Findings, UX Flow
- **Issue:** Prior review Finding 6 (Critical, 4 reviewers) was accepted with disposition: "Cut 'discuss' from MVP. Replace with reject-with-note." Design doc still describes discuss mode as "first-class interaction" in Step 5: Accept / Reject / Discuss. Should be Accept / Reject (with note).
- **Why it matters:** Design doc is the spec. If it says discuss mode exists, implementers will build it or be confused why code doesn't match spec. This is documentation debt from the disposition decision.
- **Suggestion:** Update Step 5: Process Findings to remove discuss mode. Replace with: "For each finding, presented one at a time: (1) Accept—finding is valid, will address; (2) Reject (with note)—finding is wrong or not applicable, note becomes feedback for reviewer tuning and calibration input to next review cycle." Add note: "Full discussion mode deferred to v2 pending eval data on whether reject-with-note addresses finding quality concerns."
- **Fixability:** auto-fixable
- **Status:** pending

### Finding 32: Primary + Contributing Phase Classification Not in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Finding Phase Classification
- **Issue:** Prior review Finding 7 (Critical, 2 reviewers) accepted dual classification: "Classify by primary + contributing phases—'design flaw (primary) caused by calibrate gap (contributing).' Systemic issue detection when >30% share root cause." Design doc still shows single-phase classification with no mention of primary+contributing dual classification or systemic issue detection threshold.
- **Why it matters:** Phase classification is the core novel contribution per CLAUDE.md. If design doesn't implement the accepted classification refinement, it's less effective at routing multi-causal findings.
- **Suggestion:** Update "Finding Phase Classification" section to specify: (1) Each finding has primary phase (where to route) and optional contributing phase (systemic pattern to track), (2) Format: "Phase: design (primary), calibrate (contributing)", (3) Synthesizer analyzes aggregate: if >30% of findings share contributing phase, flag systemic issue, (4) Reviewers suggest phase in findings, synthesizer reconciles disagreements with reasoning, (5) User can override classification during processing.
- **Fixability:** human-decision
- **Status:** pending

### Finding 33: CLI Tooling for Reviewers Still Unspecified
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Missing (should be "Reviewer Capabilities" or "Tooling" section)
- **Issue:** Requirements doc emphasizes "CLI-first" and lists specific tools (`gh`, `jq`, `git`, `curl`). Prior review Finding 21 (Important, accepted). Disposition: "Specify reviewer tool access in Task 8 prompt iteration. Per-persona tool boundaries belong in stable prompt prefix." Design doc has no tooling section.
- **Why it matters:** Some reviewer personas need tools to perform their function. Prior Art Scout searches for existing solutions (needs `gh`, `curl`). Without tool specification, reviewers are limited to what's in the design doc text, missing real-world validation.
- **Suggestion:** Add "Reviewer Capabilities" section specifying tool access per persona: (1) All reviewers: Read tool for design/requirements artifacts, git for checking repo structure, (2) Prior Art Scout: `gh` for GitHub search, `curl` for fetching external docs, web search, (3) Assumption Hunter: `grep` for codebase validation, `jq` for config inspection, (4) Tool access boundary: read-only, no write operations.
- **Fixability:** human-decision
- **Status:** pending

### Finding 34: Voice Guidelines Not Documented in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Per-Reviewer Output Format
- **Issue:** Requirements doc specifies detailed output voice requirements ("direct and engineer-targeted," "no hedging language," "SRE-style framing"). Prior review Finding 23 (Important, accepted). Disposition: "Part of Task 8 prompt iteration. Voice guidelines go in stable prompt prefix." Task 8 added voice rules to agent prompts. Design doc still only specifies output format (markdown structure), not voice rules.
- **Why it matters:** Design doc is authoritative spec. If voice guidelines are only in prompts but not documented in design, future prompt updates might drop them. Voice rules are part of prompt caching prefix (per Finding 3 disposition), so they're architecturally important to document.
- **Suggestion:** Add "Voice Guidelines" subsection to "Per-Reviewer Output Format" specifying: (1) Active voice—lead with impact, then evidence, (2) No hedging, (3) Quantify blast radius where possible, (4) SRE-style framing for severity, (5) Engineer-targeted audience. Note: these rules are part of stable prompt prefix per prompt caching architecture.
- **Fixability:** human-decision
- **Status:** pending

### Finding 35: Requirement for "Should This Exist?" Lens Not in Design
- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Flagged by:** Requirement Auditor
- **Section:** Reviewer Personas (Requirement Auditor specifically)
- **Issue:** Prior review Finding 25 accepted user disposition requesting addition of "The Algorithm" engineering workflow lens (delete before optimize). Disposition: "Reviewers should ask 'should this requirement exist at all?' before checking if design satisfies it." Task 8 prompt updates included this for Requirement Auditor. Design doc doesn't mention this lens.
- **Why it matters:** This is a high-value review lens that prevents gold-plating and catches YAGNI violations. User explicitly requested it as design principle. It's in the prompt now but not documented in the design as part of reviewer methodology.
- **Suggestion:** Update Requirement Auditor persona description to include: "Before checking coverage or contradictions, first evaluates whether each requirement should exist at all. Flags requirements that add complexity without clear value as calibrate gaps." Add note in general review methodology: "All reviewers apply 'delete before optimize' lens—never optimize or critique something that should be deleted entirely."
- **Fixability:** human-decision
- **Status:** pending

### Finding 36: Synthesizer Role Still Called "Purely Editorial" in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor, First Principles Challenger
- **Section:** Synthesis
- **Issue:** Prior review Finding 13 (Important, 3 reviewers). Disposition: "Reframe synthesizer as judgment-exercising role (not 'purely editorial'). Smoke test confirmed: escalated Finding 8 severity. Part of Task 8." Task 8 updated synthesizer prompt. Design doc still says "Its role is purely editorial—zero judgment on content or severity."
- **Why it matters:** Design doc contradicts implementation and prior disposition. Synthesizer exercises judgment on deduplication, phase classification, and finding aggregation. Disposition accepted this, prompts updated, but design not updated.
- **Suggestion:** Update Synthesis section to remove "purely editorial" and "zero judgment" language. Replace with: "Synthesizer exercises judgment on finding consolidation, phase classification, and pattern detection. It does not override individual reviewer severity ratings or add its own findings, but does reconcile disagreements and surface emergent patterns that individual reviewers cannot see."
- **Fixability:** auto-fixable
- **Status:** pending

### Finding 37: JSONL Output Format Mentioned in Dispositions But Not in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Output Artifacts, Summary Format
- **Issue:** Multiple prior review finding dispositions reference JSONL as canonical output format. Finding 14 disposition: "JSONL format enables this naturally—jq filters by severity/persona/phase." Finding 24 disposition: "JSONL + markdown rendering may naturally produce this." MEMORY.md notes "JSONL as canonical output format—decided but not yet implemented." Design doc specifies only markdown output format. No mention of JSONL.
- **Why it matters:** If JSONL is the intended canonical format, design should specify it (even if deferred to post-MVP). Current design commits to markdown as output format with no migration path to structured data. Multiple features depend on it. Requirements doc emphasizes CLI-first tooling, which naturally works better with JSONL (jq for filtering/processing) than markdown.
- **Suggestion:** Add JSONL to output format section as post-MVP enhancement: "Current prototype uses markdown for human readability. Post-MVP, structured JSONL output with markdown rendering layer enables: (1) stable finding IDs (JSON id field), (2) CLI-based filtering/processing (jq by severity/persona/phase), (3) bulk finding operations, (4) cross-iteration diff without LLM parsing. Markdown remains primary interface, JSONL becomes underlying data format."
- **Fixability:** human-decision
- **Status:** pending

### Finding 38: Model Tiering Strategy Mentioned in Requirements But Not Designed
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Requirement Auditor
- **Section:** Missing (should be in cost/architecture section)
- **Issue:** Requirements doc and CLAUDE.md specify model tiering as cost strategy: "Haiku for simple evals, Sonnet for review agents, Opus sparingly for adversarial deep analysis." Prior review Finding 40 suggests testing Haiku for mechanical reviewers. Design doc specifies Sonnet for all reviewers but has no model tiering architecture or configuration mechanism.
- **Why it matters:** Cost optimization via model tiering could reduce per-review cost 30-40% if Haiku works for mechanical personas. Without design-level specification, this becomes implementation detail rather than architectural decision.
- **Suggestion:** Add "Model Configuration" subsection to design specifying: (1) Default model per stage (Sonnet for design-stage review), (2) Model parameter per persona (allows empirical testing of Haiku for mechanical reviewers), (3) Configuration via skill parameter or persona definition file (not hardcoded), (4) Eval framework tests model variants.
- **Fixability:** human-decision
- **Status:** pending

### Finding 39: No "Minimum Viable Reviewer Set" Validation
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Feasibility Skeptic
- **Section:** Reviewer Personas (6 design-stage personas)
- **Issue:** Design specifies 6 reviewers for design stage but provides no evidence that all 6 are necessary or that this set is sufficient. Prior Art Scout and First Principles Challenger have significant overlap. Edge Case Prober and Feasibility Skeptic both examine "what could go wrong." No analysis of coverage overlap or diminishing returns per additional reviewer.
- **Why it matters:** Each reviewer adds cost and coordination overhead. If 3 reviewers catch 80% of findings, running 6 is low ROI. Problem statement acknowledges this is empirical but doesn't specify how you'd validate minimum viable set during prototyping.
- **Suggestion:** Run coverage analysis during first 3-5 review cycles. For each finding, tag which reviewer(s) flagged it. Identify: (1) reviewers that consistently flag unique findings (high value, keep), (2) reviewer pairs with >50% overlap (consolidate or choose one), (3) finding categories no reviewer consistently catches (missing persona). Start with 3 core reviewers, add one at a time, measure incremental value.
- **Fixability:** human-decision
- **Status:** pending

### Finding 40: Synthesis Consolidation Heuristics Undefined
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** Synthesis (deduplication, contradiction detection)
- **Issue:** Synthesizer must "deduplicate" findings and "surface contradictions" but design provides no heuristics for how. When do two findings count as "the same issue"? Same section + similar keywords? Same root cause? Same suggested fix? When do two findings count as "contradictory" vs "complementary concerns about same area"?
- **Why it matters:** Aggressive deduplication loses nuance and reduces finding count artificially. Conservative deduplication floods user with near-duplicates. Inconsistent consolidation across review runs makes iteration comparison unreliable. The synthesizer's judgment directly affects verdict and user experience.
- **Suggestion:** Define explicit consolidation rules in synthesizer prompt: (1) Deduplicate only if findings reference exact same section AND same root cause (conservative baseline), (2) Group related findings under common heading but preserve as separate entries with cross-references, (3) Flag potential duplicates for user decision rather than auto-consolidating. Track deduplication decisions in summary.
- **Fixability:** human-decision
- **Status:** pending

### Finding 41: Phase Classification as Multi-Label Problem
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** Finding Phase Classification, Verdict Logic
- **Issue:** Design treats phase classification as single-label (each finding is survey gap OR calibrate gap OR design flaw OR plan concern) but disposition note for Finding 7 acknowledges multi-label reality ("design flaw (primary) caused by calibrate gap (contributing)"). The summary format has "Findings by Phase" section with counts but doesn't specify how multi-label findings are counted.
- **Why it matters:** If 30% of findings are multi-causal, single-label classification is lossy and verdict logic becomes ambiguous. Misclassification wastes cycles.
- **Suggestion:** Specify whether classification is single-label or multi-label in "Finding Phase Classification" section. If multi-label: (1) Define primary vs contributing semantics, (2) Update summary format to show multi-label data, (3) Update verdict logic (escalate on primary phase = survey/calibrate, track systemic patterns separately). If single-label: resolve contradiction in Finding 7 disposition note.
- **Fixability:** human-decision
- **Status:** pending

### Finding 42: Async Mode Is Not Actually Async
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** UX Flow, Finding 2 disposition note
- **Issue:** Finding 2 disposition states "Async is the default—review always writes artifacts to disk." This describes batch execution (run review, write files, exit), not async workflow (run review in background, process findings hours later). True async requires: (1) review runs without blocking user's terminal, (2) user can close session and resume later, (3) finding processing state persists across sessions. Current design has none of this.
- **Why it matters:** Background automation (CLAUDE.md track #6) requires true async. If review takes 5 minutes, that's 5 minutes of terminal occupancy. User can't work on other tasks during review. The "async" framing in disposition note is misleading—it's really "file-based output" (good) but not "background execution" (required for automation track).
- **Suggestion:** Distinguish between execution mode (sync/async) and output mode (interactive/file-based). Current design: sync execution, file-based output with optional interactive processing. For true async: (1) skill supports `--background` flag, (2) finding processing is session-independent, (3) re-running skill on same topic detects in-progress review and offers to show status or abort. Defer true async to post-MVP but document the distinction.
- **Fixability:** human-decision
- **Status:** pending

### Finding 43: Verdict Computed Before Findings Processed
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** Verdict Logic, UX Flow Step 4 (Present Summary)
- **Issue:** UX flow shows verdict presented to user in Step 4 before findings are processed in Step 5, but verdict depends on severity ratings that may be wrong (false positives). If user rejects 3 Critical findings as invalid in Step 5, the "revise" verdict from Step 4 should retroactively become "proceed." Design doesn't specify whether verdict is recomputed after finding processing or remains unchanged.
- **Why it matters:** Presenting an incorrect verdict wastes cycles. User sees "revise" (based on 5 Critical findings), spends 20 minutes processing findings, rejects 4 of the Critical findings as false positives. Should have been different verdict.
- **Suggestion:** Recompute verdict after finding processing completes, based on accepted findings only. Show provisional verdict in Step 4, final verdict in Step 6 after processing. Alternatively: eliminate provisional verdict entirely, show finding counts and let user decide verdict after processing.
- **Fixability:** human-decision
- **Status:** pending

### Finding 44: LangSmith Annotation UI Solves Finding Processing UX
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Prior Art Scout
- **Section:** Step 5: Process Findings, Interactive Finding Processing, Summary Format (dispositions)
- **Issue:** The design custom-builds interactive finding processing (accept/reject/discuss one-at-a-time in CLI) with disposition tracking in markdown. LangSmith (already in tooling budget, 5k traces/month free tier) provides production-grade annotation queues with web UI for human feedback, finding tagging by severity/phase, accept/reject/comment workflows, team collaboration, and historical disposition tracking.
- **Why it matters:** Custom CLI-based finding processing has UX limitations: no async mode (user must be present), no filtering/batching, no collaboration, no historical view. LangSmith's annotation UI supports: async review, filtering, batch operations, team collaboration, and integration with LangChain/LangGraph traces.
- **Suggestion:** Evaluate LangSmith's annotation queues for finding processing. Each reviewer run becomes a trace, findings become annotations, human disposition becomes feedback. Skill writes findings to LangSmith, user processes them in the web UI (async-first), and skill reads back dispositions to update summary.md. If UI/workflow doesn't fit parallax's needs, fall back to custom implementation.
- **Fixability:** human-decision
- **Status:** pending

### Finding 45: Braintrust LLM-as-Judge Solves Severity Normalization
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Prior Art Scout
- **Section:** Synthesis (severity ranges, deduplication), Verdict Logic
- **Issue:** The design describes synthesizer responsibilities (deduplicate findings, reconcile severity ranges, classify by phase) but treats it as a custom prompt engineering problem. Braintrust (already in tooling budget, 1M spans/10k scores free tier) is specifically designed for LLM-as-judge evaluation with autoevals library for scoring, chain-of-thought reasoning for severity assessment, and configurable scorers for classification tasks.
- **Why it matters:** Synthesizer must: (1) judge if two findings are "the same issue" (semantic similarity + deduplication threshold), (2) reconcile severity ranges when reviewers disagree (consensus scoring), (3) classify findings by phase (multi-class classification with reasoning). All three are LLM-as-judge tasks. Custom implementation means writing prompts, managing model calls, handling edge cases.
- **Suggestion:** Evaluate Braintrust for synthesis logic. Each reviewer output becomes a trace. Scorers classify findings (deduplication scorer identifies duplicates via semantic similarity, severity scorer reconciles ranges via consensus voting, phase scorer assigns pipeline phase via chain-of-thought classification). Synthesizer becomes a Braintrust experiment that runs scorers and produces summary.md from results.
- **Fixability:** human-decision
- **Status:** pending

### Finding 46: Promptfoo Adversarial Testing Is Exact Prior Art for Reviewer Personas
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Flagged by:** Prior Art Scout
- **Section:** Reviewer Personas, Open Questions (optimal persona count)
- **Issue:** The design defines 6-9 reviewer personas with adversarial lenses and flags persona tuning as an empirical question for the eval framework. Promptfoo (already in tooling budget, open source, 10k probes/month free) is specifically designed for adversarial LLM testing with 50+ vulnerability types, automated probe generation, OWASP LLM Top 10 coverage, and plugin-based test strategies.
- **Why it matters:** Reviewer personas are adversarial probes applied to design artifacts rather than LLM outputs, but the underlying pattern is identical. Using Promptfoo's patterns accelerates persona development and validates against industry standards.
- **Suggestion:** Study Promptfoo's adversarial testing architecture before finalizing reviewer personas. Map parallax personas to Promptfoo vulnerability types. Evaluate whether Promptfoo's test generation patterns can accelerate persona prompt development. Consider contributing parallax-specific probes back to Promptfoo.
- **Fixability:** human-decision
- **Status:** pending

### Finding 47: Compound Engineering Is Exact Prior Art for Learning Loop
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Flagged by:** Prior Art Scout
- **Section:** Problem Statement "Correction Compounding", Reviewer Calibration Feedback Loop (prior Finding 29)
- **Issue:** Problem statement describes "correction compounding" where false negatives/positives become permanent calibration rules in reviewer prompts, creating a learning loop that improves over time. EveryInc's Compound Engineering plugin (8.9k stars, production use at Every) implements exactly this pattern: Plan → Work → Review → Compound → Repeat, where the Review step captures learnings and the Compound step feeds them back into the system.
- **Why it matters:** Compound Engineering demonstrates that reviewer learning loops are viable and valuable in production. This validates parallax's hypothesis but also shows parallax is reinventing a mature pattern. Additionally, Compound Engineering's 15 review agents are all implementation-focused (code review), whereas parallax targets design review—complementary domains, not competitors.
- **Suggestion:** Study Compound Engineering's learning loop implementation before building parallax's calibration mechanism. Key questions: (1) How do they capture learnings from review cycles? (2) How do they structure calibration data? (3) What's their prompt update workflow? (4) Do they version prompts? Consider: propose collaboration where parallax contributes design-stage reviewers to Compound Engineering.
- **Fixability:** human-decision
- **Status:** pending

### Finding 48: adversarial-spec Demonstrates Multi-LLM Debate Pattern
- **Severity:** Important
- **Phase:** design (primary)
- **Flagged by:** Prior Art Scout
- **Section:** Reviewer Personas (prior Finding 26: adversarial pairs), Contradictions (synthesis)
- **Issue:** The design uses parallel personas with domain-scoped lenses (coverage-based). Prior review Finding 26 (Important, accepted) suggested adversarial pairs with opposing incentives (stance-based) to force genuine debate. adversarial-spec (zscole, 487 stars) implements exactly this: multi-LLM debate where models critique each other iteratively until consensus, with explicit skepticism of early consensus and model personas defending different positions.
- **Why it matters:** adversarial-spec validates that stance-based adversarial review (multiple agents arguing) produces better outcomes than coverage-based review (multiple agents inspecting). Their approach: Claude drafts spec → opponents critique → synthesize → revise → repeat. The key insight: debate surfaces gaps better than independent inspection.
- **Suggestion:** Read adversarial-spec source code and methodology. Key patterns to study: (1) How do they frame opponent critiques? (2) How do they detect consensus vs genuine disagreement? (3) How many debate rounds? (4) Same model with different personas, or different models? (5) Synthesis logic? Use these answers to inform parallax's persona design (Finding 26 implementation).
- **Fixability:** human-decision
- **Status:** pending

## Minor Findings

### Finding 49: Requirements Doc as Input May Be Stale or Mismatch Design
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Skill Interface (Requirements artifact input), Reviewer personas (Requirement Auditor)
- **Issue:** Skill accepts "Requirements artifact" as file path, but design doesn't specify validation that requirements are current or match the design being reviewed. If user points to wrong requirements doc, reviewers audit design against incorrect requirements, producing irrelevant findings.
- **Why it matters:** Garbage in, garbage out. Requirement Auditor would flag "design violates requirement X" when design was intentionally scoped differently. Low probability but high impact when it occurs.
- **Suggestion:** Add to design: input validation specification. Options: (1) Check that requirements doc and design doc reference each other (cross-link check), (2) Include metadata in requirements/design (version, date, topic) and validate consistency, (3) Show user a preview/confirmation before dispatching reviewers, (4) If validation fails, prompt user to confirm override.
- **Fixability:** human-decision
- **Status:** pending

### Finding 50: Re-Review Diff Highlighting Unspecified
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 17 disposition (highlight changed sections via git diff)
- **Issue:** Prior Finding 17 disposition suggests "Highlight changed sections if possible (git diff)" as part of iteration context fed to reviewers. How this is presented is unspecified in the design. If full git diff is included in reviewer context, it adds 1k+ tokens per reviewer (expensive). If diff summary is included, reviewers don't see what specifically changed. If reviewers are told to use git diff themselves, that's tool access not specified in design.
- **Why it matters:** Reviewers focusing scrutiny on changed sections (where bugs are most likely) is high-value. But unspecified implementation could be expensive (full diff bloats tokens), incomplete (summary too vague), or impossible (reviewers lack git access).
- **Suggestion:** Add to design: diff presentation specification for re-review. Options: (1) Include section-level change summary in reviewer context ("Sections modified since iteration 1: Architecture, UX Flow, Synthesis"), (2) Full diff available on request, (3) Use line-level diff markers in design doc, (4) Defer to post-MVP if token cost is prohibitive. For MVP, recommend option 1.
- **Fixability:** human-decision
- **Status:** pending

### Finding 51: Reviewer Tool Access Noted But Design Unchanged
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Finding 21 disposition (specify reviewer tool access), Reviewer capabilities
- **Issue:** Prior Finding 21 disposition states "Valid—specify reviewer tool access in Task 8 prompt iteration. Per-persona tool boundaries belong in the stable prompt prefix." But Task 8 is implementation/prompt tuning, not design. If tool access is architectural (which tools reviewers can use affects what they can verify), it should be in the design.
- **Why it matters:** Tool access affects review quality and security boundaries. If reviewers have read-write tool access, they could modify files accidentally. If they have no tool access, they can't verify assumptions.
- **Suggestion:** Add to design: "Reviewer Capabilities" section. Specify: (1) All reviewers have read-only file access, (2) Prior Art Scout additionally has `curl`, `gh`, (3) No reviewers have write access or ability to execute code, (4) Tool access specified in reviewer prompt prefix.
- **Fixability:** human-decision
- **Status:** pending

### Finding 52: Verdict "Escalate" Has No UX Specification
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Edge Case Prober
- **Section:** Verdict Logic (escalate path), Step 6: Wrap Up
- **Issue:** Design says "If escalate: skill tells user which upstream phase to revisit and why, then exits." No specification of what "tells user" means in the design. Is it a message in summary.md? A separate escalation report? An interactive prompt?
- **Why it matters:** Escalate is a critical path (fundamental design issue requires upstream fix). If escalation message is buried in summary.md, user may miss it. Needs clear signaling specified in design.
- **Suggestion:** Add to design: escalation UX specification. Specify: (1) summary.md includes prominent escalation section at top, (2) Escalation message includes: which phase to revisit, which findings triggered escalation, suggested next steps, (3) In interactive mode, escalation pauses processing and prompts user to confirm, (4) In async mode, escalation verdict is in summary.md header.
- **Fixability:** human-decision
- **Status:** pending

### Finding 53: Reviewer Prompt Versioning Strategy Missing
- **Severity:** Minor
- **Phase:** plan (primary), design (contributing)
- **Flagged by:** Feasibility Skeptic
- **Section:** Reviewer Personas, prompt iteration (Task 8)
- **Issue:** Task 8 completed "prompt iteration from smoke test" with 8 files updated across 3 commits. This means reviewer prompts changed based on findings. But design doesn't specify how prompt versions are tracked or how old review results remain comparable to new review results. If Assumption Hunter's prompt changes significantly between iteration 1 and iteration 2 of reviewing the same design, finding differences could be due to prompt changes (not design improvements).
- **Why it matters:** Eval framework depends on comparing review quality across iterations. If you can't distinguish "design improved" from "prompts got better at finding issues" or "prompts got worse and missed things," eval data is noisy.
- **Suggestion:** Version reviewer prompts explicitly. Each prompt file includes version header. Summary.md records prompt versions used for each review run. When comparing review iterations, note prompt version changes. If major prompt refactor needed, increment version and treat findings as non-comparable to prior versions.
- **Fixability:** human-decision
- **Status:** pending

### Finding 54: Second Brain Test Case Not Actually Run
- **Severity:** Minor
- **Phase:** design (primary), plan (contributing)
- **Flagged by:** Feasibility Skeptic
- **Section:** Prototype Scope ("Validate with: Second Brain Design test case")
- **Issue:** Design claims validation will use "Second Brain Design test case (3 reviews, 40+ findings in the original session)" but Memory.md shows only one test case actually run: smoke test against the parallax:review design doc itself. The Second Brain test case (real project with known design flaws and review findings) hasn't been executed against the implemented system.
- **Why it matters:** Self-review (reviewing parallax:review's own design doc) is useful for dogfooding but weak for validation. The Second Brain case is the validation that matters—did the implemented review system catch the same 40+ issues the manual process found?
- **Suggestion:** Run Second Brain test case before finalizing this design doc as "approved." Use findings to validate: (1) reviewer personas catch real design flaws, (2) finding counts are comparable to manual review, (3) severity calibration is sensible, (4) phase classification routes issues correctly. If test reveals failures, update design before marking approved.
- **Fixability:** human-decision
- **Status:** pending

### Finding 55: Cost Per Review Run Unknown
- **Severity:** Minor
- **Phase:** plan (primary)
- **Flagged by:** Feasibility Skeptic
- **Section:** Open Questions ("Cost per review run")
- **Issue:** Design acknowledges cost as eval question but after 11 commits of implementation including a smoke test run, actual cost data should exist. How much did the smoke test cost? What was token count per reviewer? Did prompt caching work? Was cost within budget assumptions?
- **Why it matters:** Budget is $2000/month with $150-400 projected API spend. Unknown costs make iteration risky. If smoke test cost $5 (10x estimate), you can afford ~30-60 reviews/month. If it cost $0.20 (5x under estimate), you can afford hundreds. Without data, you're flying blind on burn rate.
- **Suggestion:** Instrument next review run with token/cost logging. Capture: (1) input tokens per reviewer, (2) output tokens per reviewer, (3) synthesizer tokens, (4) total cost at Sonnet pricing, (5) cache hit rate if caching enabled. Log to review summary or separate cost tracking file. Use data to validate budget assumptions.
- **Fixability:** human-decision
- **Status:** pending

## Auto-Fixable Findings

### Finding 56: Discuss Mode References Should Be Removed
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Synthesizer
- **Section:** Step 5: Process Findings, UX Flow
- **Issue:** Finding 31 notes design doc still describes discuss mode despite disposition cutting it from MVP. This is straightforward documentation cleanup—search for "discuss" references and either remove or mark as "deferred to v2."
- **Suggestion:** Global find-replace: remove "discuss" from Step 5 options, update any UX flow references to two-option workflow (accept/reject with note), add deferred note if discuss mode is mentioned elsewhere.
- **Fixability:** auto-fixable
- **Status:** pending

### Finding 57: "Purely Editorial" References Should Be Removed
- **Severity:** Minor
- **Phase:** design (primary)
- **Flagged by:** Synthesizer
- **Section:** Synthesis section
- **Issue:** Finding 36 notes design doc still uses "purely editorial" and "zero judgment" language for synthesizer role despite Task 8 reframing this. Straightforward text replacement.
- **Suggestion:** Replace "purely editorial" with "judgment-exercising" and update role description to acknowledge semantic interpretation responsibilities.
- **Fixability:** auto-fixable
- **Status:** pending

## Contradictions

No contradictions in this iteration. All contradictions from iteration 1 were resolved via disposition notes.

## Analysis Notes

### Cross-Reviewer Consensus (3+ reviewers)

**Highest consensus findings (4+ reviewers):**
1. **JSONL format missing** (Finding 9) - Feasibility Skeptic, Edge Case Prober, Requirement Auditor, Assumption Hunter
2. **Design doc out of sync with implementation** (Finding 1) - Implied by all reviewers noting documentation debt

**Strong consensus (3 reviewers):**
1. **Cross-iteration finding tracking** (Finding 3) - Requirement Auditor, Assumption Hunter, Edge Case Prober
2. **Prompt caching architecture missing** (Finding 4) - Requirement Auditor (+ prior review consensus)

### Deduplication Summary

- **JSONL format:** Consolidated from 4 separate findings (Assumption Hunter Finding 5, Edge Case Prober Finding 12, Requirement Auditor Finding 14/37, Feasibility Skeptic Finding 2) into single Critical finding (Finding 9)
- **Cross-iteration tracking:** Consolidated from 3 findings (Assumption Hunter Finding 3/7, Edge Case Prober Finding 1, Requirement Auditor Finding 3)
- **Documentation debt:** Pervasive pattern noted by Requirement Auditor (Finding 1 as meta-finding), confirmed by multiple reviewers

### Systemic Issues

**Documentation debt (67% of Requirement Auditor findings):** 10 of 15 findings from Requirement Auditor are "accepted prior findings not reflected in design doc." Root cause: design doc treated as static artifact rather than living spec. Remediation: 1-2 hours to update design doc with accepted decisions from iteration 1.

**Build vs Leverage imbalance (Prior Art Scout findings):** 6 of 14 Prior Art Scout findings (Findings 13-14, 44-48) identify mature frameworks solving 80% of what's being custom-built. Novel contribution (finding classification, persona prompts) is 20% of implementation surface area but design commits to building 100%. Evaluate Inspect AI, LangGraph, LangSmith, Braintrust during implementation phase before committing to custom infrastructure.

**Multi-causal phase classification:** Assumption Hunter Finding 2/6, First Principles Finding 4, Edge Case Prober Finding 8, Feasibility Skeptic Finding 41 all note phase classification assumes single root cause when real failures are multi-causal. Iteration 1 Finding 7 disposition accepted primary+contributing classification but design not updated.
