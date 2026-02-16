# Review Summary: parallax-review-v1

**Date:** 2026-02-15
**Design:** docs/plans/2026-02-15-parallax-review-design.md
**Requirements:** docs/problem-statements/design-orchestrator.md
**Stage:** design
**Verdict:** revise

## Verdict Reasoning
Multiple Critical findings require design revision before implementation. Key issues: (1) parallel agent failure handling is unspecified, creating production failure risk; (2) interactive finding processing assumes real-time human availability, contradicting background automation requirements; (3) prompt caching architecture—a stated architectural convention—is not addressed in the design; (4) auto-fix requirement from problem statement is completely missing; (5) cross-iteration finding tracking mechanism is incomplete. Additionally, two Critical-severity findings challenge core design assumptions (discuss mode state management, phase classification errors). The design is sound in structure but incomplete in critical details. No escalation required—all findings are design-phase fixable.

## Finding Counts
- Critical: 8
- Important: 22
- Minor: 11
- Contradictions: 3

## Findings by Phase
- Survey gaps: 0
- Calibrate gaps: 5
- Design flaws: 30
- Plan concerns: 6

---

## Critical Findings

### Finding 1: Parallel Agent Failure Handling Unspecified
- **Severity:** Critical
- **Flagged by:** Assumption Hunter, Edge Case Prober, Feasibility Skeptic (3 reviewers)
- **Phase:** design
- **Section:** Step 2: Dispatch (parallel reviewer execution)
- **Issue:** The design dispatches 4-6 reviewer agents in parallel but provides no specification for handling agent failures (API timeout, rate limit, model error, prompt refusal, malformed output). No retry strategy, timeout threshold, or degraded-mode behavior defined.
- **Why it matters:** Partial failures in parallel execution are not edge cases—they're expected behavior in production (API rate limits, transient network errors, model capacity issues). Without a failure strategy, a single agent crash either blocks the entire review or produces incomplete findings that silently appear complete. During prototyping, this manifests as "skill hangs for 2 minutes then fails" requiring reactive debugging.
- **Suggestion:** Define comprehensive failure handling strategy: (1) Timeout per agent (suggested: 60-120s), (2) Retry failed agents with exponential backoff (1 retry recommended), (3) Proceed with partial results if minimum threshold met (suggested: 4/6 agents succeed), (4) Mark failed agents explicitly in summary ("5/6 reviewers completed, Feasibility Skeptic timed out"), (5) Allow user to re-run individual failed reviewers without redoing successful ones. Add schema validation layer before synthesis to catch malformed output and trigger retries vs fail-fast decisions.
- **Status:** accepted
- **Disposition note:** Always mark summary results as partial if not 100% of reviewers returned successfully.

### Finding 2: Interactive Processing Contradicts Background Automation Requirements
- **Severity:** Critical
- **Flagged by:** Assumption Hunter
- **Phase:** calibrate
- **Section:** Step 5: Process Findings (interactive one-at-a-time processing)
- **Issue:** The design requires "one at a time" interactive processing of findings with accept/reject/discuss, assuming the human is present at keyboard. No provision for async workflows (run review overnight, process findings the next morning). This directly contradicts CLAUDE.md's stated goal of "Claude-native background automation — Agent SDK + MCP + cron for long-running research" (track #6).
- **Why it matters:** If reviews can't be decoupled from human interaction, they can't run in background automation. This is a requirements-level constraint that should have been surfaced in calibrate phase—the skill cannot satisfy both "interactive processing" and "background automation" without async mode support.
- **Suggestion:** Decouple finding presentation from finding processing. Support two modes: (1) **Interactive** (current design) for real-time review, (2) **Async** where findings are written to disk and the user processes them in a later session. The summary.md format already supports this (dispositions updated incrementally), but the skill invocation contract doesn't acknowledge async mode exists. Make mode selection explicit in skill interface.
- **Status:** accepted
- **Disposition note:** Async is the default — review always writes artifacts to disk. Interactive mode reuses those same artifacts as a convenience layer. No separate "async mode" needed; it's the baseline.

### Finding 3: Prompt Caching Architecture Not Addressed
- **Severity:** Critical
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Missing (should be in Reviewer Prompt Architecture)
- **Issue:** Problem statement explicitly requires "Prompt structure for caching: System prompts should be structured as stable cacheable prefix (persona + methodology + output format) + variable suffix (the design being reviewed + iteration context). This is an architectural convention, not a feature — 90% input cost reduction on cache hits. Decide before building skills." The design doc has no prompt architecture section.
- **Why it matters:** This is an architectural decision that affects **how reviewer prompts are authored**. If prompts aren't structured for caching from the start, refactoring later invalidates all eval data. This is a design-time decision, not an implementation detail. Without this, the design is structurally complete but architecturally incomplete.
- **Suggestion:** Add a "Reviewer Prompt Architecture" section specifying: (1) Stable prefix structure (persona identity, methodology, output format rules), (2) Variable suffix (artifact being reviewed, requirements context, iteration number), (3) Explicit note that prompt changes to prefix invalidate cache and should be tracked. Document the prototyping tradeoff acknowledged in Finding 19 (Feasibility Skeptic): defer optimization until prompts stabilize, but design the structure now.
- **Status:** accepted

### Finding 4: Auto-Fix Requirement Completely Missing
- **Severity:** Critical
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** UX Flow, Synthesis
- **Issue:** Problem statement explicitly requires "After adversarial review, auto-fix trivial findings (typos, wrong file paths) and re-review" but the design has no auto-fix mechanism. The UX flow goes straight from synthesis to human processing with no auto-fixable classification or automated correction step.
- **Why it matters:** This is a must-have feature to reduce human review burden and a core value proposition of the orchestrator. Without it, humans must manually process obvious fixes like typos and path corrections, defeating automation value. This is a requirement coverage gap that should have been caught in design review checklist.
- **Suggestion:** Add an auto-fix step between synthesis and human processing. Synthesizer should classify findings as auto-fixable vs human-decision-required. Auto-fixable findings get applied automatically, design is re-reviewed, and only remaining findings are shown to human. Define criteria for "auto-fixable" conservatively in MVP (typos in markdown, missing file extensions, broken internal links) and expand based on eval data.
- **Status:** accepted
- **Disposition note:** Auto-fix step between synthesis and human processing. Git history must show auto-fixes as separate commit from human-reviewed changes, enabling async review of what was auto-applied.

### Finding 5: Cross-Iteration Finding Tracking Incomplete
- **Severity:** Critical
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Synthesis, UX Flow
- **Issue:** Problem statement requires "Track which findings have been addressed across iterations." Design tracks dispositions in summary.md but doesn't specify **how** the system knows whether Finding #3 from iteration 1 was resolved in iteration 2. No mechanism for linking findings across review runs or detecting when previously-flagged issues reappear.
- **Why it matters:** Without this, re-reviews require humans to manually cross-reference "did we fix the thing the Assumption Hunter flagged last time?" Edge Case Prober specifically flags this (Finding 6): reviewers have no memory of previous findings, may re-flag resolved issues if the fix wasn't clear, and won't focus extra scrutiny on newly-changed sections. Defeats automation value and creates reviewer fatigue.
- **Suggestion:** Add finding persistence mechanism—stable IDs for findings (e.g., hash of section + issue text), status field (open/addressed/rejected), cross-iteration diff in summary.md showing which findings from prior review are now resolved. Provide iteration context to reviewers: (1) Include previous summary.md in reviewer context ("last review flagged X, check if addressed"), (2) Highlight changed sections if possible (git diff), (3) Ask reviewers to explicitly note "previously flagged, now resolved" vs "new finding" vs "still an issue".
- **Status:** accepted
- **Disposition note:** Stable finding IDs, status tracking across iterations, prior summary fed to reviewers on re-review.

### Finding 6: "Discuss" Mode State Management Underspecified
- **Severity:** Critical
- **Flagged by:** Assumption Hunter, Edge Case Prober, Feasibility Skeptic, First Principles Challenger (4 reviewers)
- **Phase:** design
- **Section:** Step 5: Process Findings (Discuss interaction)
- **Issue:** The design describes "discuss" as "a first-class interaction: the user can explore a finding in depth, ask questions, challenge the reviewer's reasoning" while "the skill maintains its position in the finding queue and resumes after the discussion resolves." This requires: (1) suspending iteration through findings, (2) context-switching to conversational mode with a specific reviewer persona, (3) maintaining conversation history, (4) detecting when discussion is resolved, (5) resuming iteration from exact finding, (6) preserving accept/reject/discuss outcomes across all findings. No specification for: who the user discusses with (original reviewer? all reviewers? mediator agent?), how conversation terminates, depth limits, what constitutes "resolved," what happens if discussion reveals the finding is actually three separate findings.
- **Why it matters:** This is a complex stateful interaction pattern (modal UI: finding iteration mode vs discussion mode inside a CLI skill) that doesn't map cleanly to Claude Code's execution model. State transitions are ambiguous. Feasibility Skeptic estimates this will consume 30-50% of implementation time for a feature that's not testable with existing test cases (Second Brain session had findings but no discussion transcripts). Without termination criteria, a single finding discussion could consume unbounded tokens or drift off-topic.
- **Suggestion:** Multiple reviewers suggest different approaches. **Feasibility Skeptic (strongest case):** MVP should be accept/reject only. "Discuss" becomes: user rejects a finding with a note, that note becomes input to the next review cycle (treating it as calibration data). This is testable, doesn't require modal state management, delivers same outcome. Add true discussion mode in v2 if eval data shows rejected findings aren't being addressed. **First Principles Challenger:** Specify the discussion protocol—discussion with original reviewer only, time-boxed to 3 turns, must end with revised severity or withdrawn finding; OR discussion invokes a "mediator" agent with access to all reviewer contexts. **Edge Case Prober:** Add discussion boundaries—max turn count per finding (5 exchanges), explicit "resolve and decide" command to exit, show context reminder at each turn, allow user to defer decision.
- **Status:** accepted
- **Disposition note:** Cut "discuss" from MVP. Replace with reject-with-note — rejection note becomes calibration input to next review cycle. Evaluate adding real discussion mode in v2 if eval data shows rejected findings aren't being addressed.

### Finding 7: Phase Classification Errors Could Route to Wrong Pipeline Stage
- **Severity:** Critical
- **Flagged by:** Edge Case Prober, First Principles Challenger
- **Phase:** design
- **Section:** Finding Phase Classification, Verdict Logic
- **Issue:** The synthesizer classifies findings by pipeline phase (survey gap, calibrate gap, design flaw, plan concern), but phase classification is a judgment call that could be wrong. Misclassifying a design flaw as a "calibrate gap" would escalate unnecessarily, restarting requirements when the design just needs a fix. Misclassifying a calibrate gap as a "design flaw" would attempt to patch a broken requirement instead of fixing it upstream. First Principles Challenger notes deeper issue: real design flaws are multi-causal (missing requirement enabled bad assumption which led to infeasible design). Single-phase classification forces a false choice.
- **Why it matters:** The entire value proposition of finding classification is routing errors to the phase that failed. If classification is unreliable, the system wastes time (false escalation) or produces bad designs (missed escalation). This is the core novel contribution per CLAUDE.md—if it's broken, the tool has no advantage over manual review. Edge Case Prober: "If 5 findings all trace back to survey gaps, the signal is 'stop and do real research,' not 'fix these 5 isolated gaps.'"
- **Suggestion:** **Edge Case Prober:** Add classification confidence and validation: (1) Reviewers suggest phase in their findings (they have most context), synthesizer reconciles disagreements, (2) Include classification reasoning in summary ("Classified as calibrate gap because requirements don't address failure mode X"), (3) Allow user to override classification during finding processing, (4) Track classification errors in eval framework to tune synthesizer prompts. **First Principles Challenger:** Classify findings by primary and contributing phases. A finding can be "design flaw (primary) caused by calibrate gap (contributing)." This enables two actions: immediate (fix the design) and systemic (revisit requirements for this pattern). Add aggregate analysis: if >30% of findings share a common root cause, escalate with "systemic issue detected."
- **Status:** accepted
- **Disposition note:** Both suggestions accepted. (1) Reviewers suggest phase in their findings, synthesizer reconciles disagreements with reasoning. User can override. (2) Classify by primary + contributing phases — "design flaw (primary) caused by calibrate gap (contributing)." Systemic issue detection when >30% share root cause. Track classification accuracy in eval framework.

### Finding 8: Verdict Logic Ambiguous with Severity Ranges
- **Severity:** Critical (conservatively escalated from Important due to impact on core workflow)
- **Flagged by:** Edge Case Prober, Feasibility Skeptic, Requirement Auditor
- **Phase:** design
- **Section:** Synthesis (severity ranges), Verdict Logic
- **Issue:** The synthesizer reports severity ranges when reviewers disagree ("Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic") but the verdict logic uses "any Critical finding → revise." This creates ambiguity: is a finding with range "Critical-to-Important" treated as Critical (blocks proceed) or Important (allows proceed)? Feasibility Skeptic identifies deeper problem: verdict must be computed before user processes findings (Step 4 presents verdict before Step 5 processes findings), but contradictory severity ratings can't be resolved until findings are processed. Who decides?
- **Why it matters:** Inconsistent verdict logic undermines trust. Without normalization, verdict logic is ambiguous—does "revise" trigger on any single reviewer flagging Critical, or require consensus? Current design punts this to the human, reducing automation value. If the synthesizer picks highest severity (conservative), you'll get false escalations. If it picks lowest (optimistic), you'll miss real issues. The UX flow (verdict → process findings) conflicts with the need to resolve contradictions before computing verdict.
- **Suggestion:** **Edge Case Prober:** Clarify severity range handling: (1) Use highest severity in range for verdict logic (conservative: any reviewer says Critical → treat as Critical), (2) Explicitly state rule in summary, (3) Allow user to override severity during finding processing. **Requirement Auditor:** Either implement severity normalization (consensus-based, or weighted by persona authority), or update verdict logic to handle severity disagreements explicitly (e.g., "any reviewer flags Critical → revise, unless majority disagrees"). **Feasibility Skeptic:** Contradictions trigger mandatory discussion before verdict is computed, OR contradictory findings are bucketed as "Important" (middle ground) and flagged for user attention first, OR reorder UX (present findings → user processes → synthesizer computes verdict based on accepted findings).
- **Status:** accepted
- **Disposition note:** Conservative — use highest severity in range for verdict logic. If false escalations become a problem, investigate per-agent prompt tuning first, then severity normalization as fallback. User can override during processing.

---

## Important Findings

### Finding 9: "Review Stage" Input Assumes Orchestrator Context But Claims Standalone Use
- **Severity:** Important
- **Flagged by:** Assumption Hunter
- **Phase:** calibrate
- **Section:** Skill Interface, Pipeline Integration
- **Issue:** The skill input contract requires "Review stage — one of: requirements, design, plan" which implies the skill knows where it sits in a linear pipeline. But the design also claims the skill can be "invoked by the orchestrator or directly by the user" and that each skill is "independently useful." If a user manually invokes `parallax:review` on a design doc, how do they know which stage to specify? The design doesn't explain. If the stage input is wrong (user says "design" but artifact is actually a plan), wrong personas activate and review is low-quality.
- **Why it matters:** This is a calibration gap—the requirements say skills are independently useful but the interface assumes orchestrator context. Without stage detection or clear guidance, the skill isn't as standalone as claimed.
- **Suggestion:** Either (1) Make stage detection automatic (analyze the artifact to infer whether it's a requirements doc, design doc, or plan—acknowledge this is hard and may require user override), or (2) Provide clear user-facing guidance ("How to choose review stage: if your doc includes implementation commands, use `plan`; if it includes architecture diagrams, use `design`; if it's MoSCoW lists, use `requirements`").
- **Status:** accepted
- **Disposition note:** Real gap but low-urgency for MVP — we're the only user and know the stage. Add guidance text to skill interface later. Auto-detection is YAGNI.

### Finding 10: Topic Label Input Has No Validation or Collision Handling
- **Severity:** Important
- **Flagged by:** Assumption Hunter, Edge Case Prober
- **Phase:** design
- **Section:** Skill Interface, Step 1: Invoke, Output Artifacts
- **Issue:** The design requires a "topic label for the review folder" but doesn't specify constraints (allowed characters? max length? what if it contains `/` or `..`?). Doesn't specify what happens if `docs/reviews/<topic>/` already exists from a prior review (silent overwrite? error? timestamp suffix?). Edge Case Prober notes that re-running with same topic before committing the first review loses the first review's data.
- **Why it matters:** Without validation, a malicious or accidental topic like `../../secrets` could write review files outside the intended directory. Without collision handling, re-running silently overwrites previous review (losing iteration history) or fails with cryptic filesystem error. The design claims "iteration history tracked by git" but doesn't explain whether iterations share one folder (overwrite files) or create new folders.
- **Suggestion:** (1) Validate topic label against safe character set (alphanumeric, hyphens, underscores only), (2) Specify collision behavior: append timestamp suffix (`topic-2026-02-15-143022/`), prompt user to confirm overwrite, or auto-increment (`topic-v2/`). Edge Case Prober suggests timestamped folders as cleanest solution.
- **Status:** accepted
- **Disposition note:** Sanitize topic label (alphanumeric, hyphens, underscores only) + timestamped folders for collision handling. Simple safety fix.

### Finding 11: Cost Budget or Token Limit Not Specified
- **Severity:** Important
- **Flagged by:** Assumption Hunter, Edge Case Prober, Feasibility Skeptic
- **Phase:** calibrate
- **Section:** Entire design, especially "Optimal number of personas per stage"
- **Issue:** The design acknowledges cost as an eval question ("Cost per review run") but the skill interface and verdict logic have no cost ceiling or visibility. Feasibility Skeptic provides rough math: 6 reviewers × (3000 token system prompt + 2000 token design doc + 1500 token requirements) × Sonnet pricing ≈ $0.50-1.00 per review cycle. Tuning 6 personas across 20 iterations = $10-20. One test case with 3 review cycles = $1.50-3.00. A single poorly-scoped review (e.g., reviewing CLAUDE.md itself) could consume 10-20% of monthly budget.
- **Why it matters:** CLAUDE.md specifies $2000/month budget with $150-400/month projected API spend. Without cost visibility or caps, users can't make informed go/no-go decisions. Edge Case Prober notes that users want to know cost before committing to a 6-agent review.
- **Suggestion:** Add optional `max_cost` parameter to skill invocation (e.g., "abort if estimated cost exceeds $X"). Show estimated cost before dispatch ("This review will cost approximately $12 based on input token count × 6 agents"). Log actual cost in summary.md for budget tracking. Specify whether cost estimation uses prompt caching assumptions (which reduce cost 90% on cache hits but require stable prompts).
- **Status:** accepted
- **Disposition note:** Cost estimation is hard pre-prototype. Log actual cost per run in JSONL output and iterate. Pre-dispatch estimates and caps come after we have empirical cost data.

### Finding 12: Git Commit Strategy Undefined for Multi-Artifact Reviews
- **Severity:** Important
- **Flagged by:** Assumption Hunter, Edge Case Prober, Feasibility Skeptic
- **Phase:** design
- **Section:** Step 6: Wrap Up, Output Artifacts
- **Issue:** The design states "All artifacts committed to git" but doesn't specify: one commit containing all reviewer outputs + summary, or separate commits per reviewer, or only summary committed? Commit message format? User approval required (CLAUDE.md Git Safety Protocol: "NEVER commit changes unless the user explicitly asks")? Feasibility Skeptic notes git tracking is "clever but fragile"—assumes clean working directory, no concurrent work on other files, user wants review iterations in commit history (vs separate branch or scratch directory).
- **Why it matters:** Requirements doc emphasizes "Git commits per iteration. Full history, diffable artifacts" and "ADR-style finding documentation." But if all 6 reviewer files + summary in one blob commit, diffing across iterations is noisy. If each reviewer is separate commit, git history has 7 commits per review run (hard to navigate). The design hasn't reconciled "full history" with usability. Auto-committing on user's behalf is invasive if they're mid-feature-development.
- **Suggestion:** **Assumption Hunter:** Specify commit strategy explicitly. Recommended: Single commit per review run containing all artifacts, with structured commit message: `parallax:review — [topic] — [verdict] ([N] findings)`. User confirms before commit (per Git Safety Protocol). Optionally, support `--auto-commit` flag for automation workflows. **Feasibility Skeptic:** Reviews write to timestamped folder and skill offers to commit at the end ("Review complete. Commit these artifacts? [y/n]"). Alternatively, use dedicated review branch (auto-created, never merged) to isolate review commits from main work.
- **Status:** accepted
- **Disposition note:** Partly addressed by Finding 4 (auto-fixes get separate commit for async review). Review artifacts: single commit per review run, user confirms. Auto-fix changes: separate commit. Two distinct commits per cycle enables clean async review of what was auto-applied vs human-reviewed.

### Finding 13: Synthesizer Role Contradicts "Purely Editorial" Constraint
- **Severity:** Important
- **Flagged by:** Assumption Hunter, Feasibility Skeptic, First Principles Challenger
- **Phase:** design
- **Section:** Synthesis (responsibilities and "zero judgment" statement)
- **Issue:** The design states the Synthesizer has "zero judgment" and "does NOT override or adjust reviewer severity ratings." But the Synthesizer must: (1) deduplicate findings (requires judging whether two findings are "the same issue"), (2) group contradictions (requires recognizing when reviewers address same topic with opposing positions), (3) classify findings by phase (requires understanding boundary between phases—is "missing error handling" a design flaw or plan concern?). All three require semantic judgment. First Principles Challenger: "This is judgment work disguised as editorial work."
- **Why it matters:** If deduplication is too aggressive, it collapses distinct issues into one finding, losing nuance. If too conservative, it floods user with near-duplicates. If synthesizer can't override phase classifications when reviewers disagree, contradictory phase tags make verdict logic ambiguous. The role definition conflicts with the responsibilities.
- **Suggestion:** **Assumption Hunter:** Acknowledge that deduplication is a judgment call and specify the threshold. Options: (1) Conservative (deduplicate only if findings reference exact same section and similar wording), (2) Aggressive (deduplicate if findings address same design decision even if different failure modes), (3) Compromise (preserve separate findings but group related ones under common heading). Include excerpts from each reviewer's version when deduplicating. **Feasibility Skeptic:** Synthesizer is judgmental on phase classification (remove "purely editorial" constraint), OR phase classification is separate agent/step with explicit reasoning. **First Principles Challenger:** Reframe as "adversarial consolidator" whose job is to find patterns and tensions individuals can't see, OR split into mechanical aggregator (no judgment) + meta-reviewer (analyzes aggregate for emergent patterns).
- **Status:** accepted
- **Disposition note:** Reframe synthesizer as judgment-exercising role (not "purely editorial"). Smoke test confirmed: escalated Finding 8 severity. Honest role definition is prerequisite for good prompt engineering. Part of Task 8.

### Finding 14: Large Finding Counts Overwhelm Interactive Processing
- **Severity:** Important
- **Flagged by:** Edge Case Prober, Feasibility Skeptic
- **Phase:** design
- **Section:** Step 5: Process Findings (All findings mode), Test case validation (Second Brain Design)
- **Issue:** The design supports processing "every finding one by one" but doesn't address scale. Second Brain test case produced 40+ findings across 3 reviews. Processing one-at-a-time in interactive CLI means 40+ prompts of "Finding 23: [title]. Accept, reject, or discuss?" This is a 10-15 minute manual process. If design triggers "revise" and re-review, you're processing findings again (some duplicates, some new). Design provides "critical-first" mode to mitigate but it's optional—users may not know to use it.
- **Why it matters:** UX assumes review is a checkpoint, but 40-finding reviews turn it into a slog. Users will start auto-accepting to get through queue, defeating purpose of adversarial review. Causes decision fatigue and error-prone processing (user may rush through later findings or abandon review).
- **Suggestion:** Add smart defaults and batching: (1) Auto-suggest critical-first mode when finding count > 15, (2) Allow bulk operations ("accept all Minor findings," "accept all from [persona]," "reject findings in [section]"), (3) Group related findings for batch decision ("these 5 findings all say the same thing, accept all?"), (4) Support "defer" to skip findings and return later. **Feasibility Skeptic:** Add filtering ("show me only feasibility concerns," "show only Critical/Important").
- **Status:** accepted
- **Disposition note:** JSONL format enables this naturally — jq filters by severity/persona/phase without LLM tokens. Bulk ops and filtering become CLI one-liners rather than custom UX.

### Finding 15: No Progress Indication for Long-Running Reviews
- **Severity:** Important
- **Flagged by:** Edge Case Prober
- **Phase:** design
- **Section:** Step 2: Dispatch, Step 3: Synthesize
- **Issue:** Running 6 reviewers in parallel with large design docs could take minutes. User sees "Running 6 reviewers in parallel..." but no indication of progress, completion estimates, or which reviewers have finished. Per-reviewer time variance (Prior Art Scout may need web search, Assumption Hunter may finish in 30 seconds) means total time is unpredictable.
- **Why it matters:** Long-running operations without progress feedback feel broken. Users may interrupt process thinking it's stuck, wasting tokens and time.
- **Suggestion:** Stream progress updates as reviewers complete ("Assumption Hunter: done [1/6]", "Edge Case Prober: done [2/6]"). Show elapsed time. Consider timeout per reviewer (e.g., 120 seconds max).
- **Status:** accepted
- **Disposition note:** Stream completion as reviewers finish. Straightforward UX improvement.

### Finding 16: Contradictions Presented Without Resolution Guidance
- **Severity:** Important
- **Flagged by:** Edge Case Prober, Requirement Auditor
- **Phase:** design
- **Section:** Synthesis (Contradictions section), Summary Format
- **Issue:** When reviewers disagree, the synthesizer presents both positions with "user resolves" but provides no framework for resolution. User must decide between conflicting technical opinions without guidance on which reviewer's lens is more relevant to this specific tension. Example: Feasibility Skeptic says "too complex, use SQLite," Prior Art Scout says "don't reinvent, use Postgres." Both valid from their lenses—which wins depends on context user may not have.
- **Why it matters:** Contradictions are high-value findings (surface real design tensions), but dumping them on user without structure creates decision paralysis. Requirement Auditor notes current design leaves this to ad-hoc user decision.
- **Suggestion:** **Edge Case Prober:** Enhance contradiction presentation: (1) Surface underlying tension explicitly ("tradeoff: simplicity vs leveraging existing tools"), (2) Include relevant context from design/requirements that might resolve it, (3) Suggest tie-breaking criteria ("if timeline < 1 week, favor simplicity"), (4) Allow user to request deeper analysis from both reviewers before deciding. **Requirement Auditor:** Add contradiction resolution options to UX flow: (1) Accept one position and reject the other, (2) Request debate (both reviewers present arguments, user decides), (3) Mark as "both valid" (design decision depends on unstated constraint, document the tradeoff).
- **Status:** accepted
- **Disposition note:** Synthesizer should surface underlying tension explicitly and suggest tie-breaking criteria. Low frequency (3/41 in smoke test) so low urgency, but high value when it occurs.

### Finding 17: Re-Review After Revisions May Produce Identical Findings
- **Severity:** Important
- **Flagged by:** Edge Case Prober
- **Phase:** design
- **Section:** Step 6: Wrap Up (revise flow), Iteration Loops
- **Issue:** When verdict is "revise," user updates design and re-runs `parallax:review`. Reviewers have no memory of previous findings or what changed. They may re-flag same issues if fix wasn't clear, or miss new issues introduced by revision.
- **Why it matters:** Re-review waste: if user addressed a finding but reviewer can't tell (fix was subtle or in different section), same finding reappears, frustrating user. Also, reviewers won't focus extra scrutiny on newly-changed sections where bugs are most likely.
- **Suggestion:** Provide iteration context to reviewers: (1) Include previous summary.md in reviewer context ("last review flagged X, check if addressed"), (2) Highlight changed sections if possible (git diff), (3) Ask reviewers to explicitly note "previously flagged, now resolved" vs "new finding" vs "still an issue", (4) Track finding IDs across iterations to auto-detect duplicates.
- **Status:** accepted
- **Disposition note:** Covered by Finding 5 disposition — stable finding IDs + prior summary fed to reviewers on re-review addresses this directly.

### Finding 18: Scope Mismatch — Requirement Refinement Expected
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** calibrate
- **Section:** Entire design
- **Issue:** Problem statement title is "Design Orchestrator" and describes full pipeline including requirement refinement (MoSCoW, anti-goals, success criteria) as critical phase. This design only covers `parallax:review` and explicitly defers requirement refinement. Design satisfies the review skill, not the orchestrator problem statement.
- **Why it matters:** If requirement is "orchestrator," this design is incomplete. If requirement is "review skill," then problem statement is over-scoped and should be split. Currently testing against wrong requirements.
- **Suggestion:** Either (1) split problem statement into separate docs for `parallax:review` and `parallax:orchestrate`, or (2) treat this design as phase 1 of multi-phase orchestrator design and explicitly scope what's in/out for this iteration.
- **Status:** accepted
- **Disposition note:** True by design — we explicitly chose to build review first as prototype. This design is phase 1 of the orchestrator. Document the scope boundary in the design doc.

### Finding 19: Prompt Caching Creates Painful Iteration Tradeoff
- **Severity:** Important
- **Flagged by:** Feasibility Skeptic
- **Phase:** design
- **Section:** Prompt structure for caching (problem statement requirement, design implied)
- **Issue:** Design commits to prompt caching as "architectural convention" with 90% cost reduction, but reviewer personas need continuous tuning during prototyping. Every prompt change invalidates cache prefix, making optimization counterproductive during the phase where you need fast iteration. You'll either (a) lock prompts prematurely to preserve cache hits (degrading review quality), or (b) iterate prompts freely and burn through budget on cache misses during 10-20 prototype cycles needed to tune 6-9 personas.
- **Why it matters:** Problem statement acknowledges this (customization-04) but design doesn't resolve the tension. This is a real constraint that will manifest during implementation.
- **Suggestion:** Defer prompt caching optimization until reviewer prompts stabilize (post-MVP). Use versioned prompt structure where cache-friendly prefix is separate from tunable instructions, but don't optimize for cache hits until eval data shows prompts converging. Budget for full-price API calls during prototyping ($200-400/mo allows ~20-40 full reviews with 6 Sonnet agents). **Note:** This is complementary to Finding 3 (Prompt Caching Architecture Not Addressed)—Finding 3 requires designing the structure now, this finding suggests deferring optimization of that structure until post-MVP.
- **Status:** accepted
- **Disposition note:** Duplicate of Finding 3 disposition — design the cache-friendly structure now, defer optimization until prompts stabilize. Already decided.

### Finding 20: Self-Consumption Mechanism Missing
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement says "Self-consuming: Parallax should use its own document chain as input to its own review tasks. The artifacts are the context that makes adversarial review effective." Design has no mechanism for feeding prior review artifacts back into the review process.
- **Why it matters:** Iteration 2 reviewers can't reference iteration 1 findings to check whether concerns were addressed. Valuable context is lost. Especially important for Requirement Auditor (did design address the gap we flagged?) and First Principles Challenger (did revision actually fix the framing issue?).
- **Suggestion:** Add to skill interface: optional prior review summary as input. Reviewer prompts should reference prior findings when present. Synthesizer should explicitly note which prior findings are now resolved vs still open.
- **Status:** accepted
- **Disposition note:** Covered by Finding 5 disposition — prior summary as reviewer input, stable IDs for tracking resolution across iterations.

### Finding 21: CLI Tooling Requirements Missing
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement specifies "CLI-first" as tooling principle and lists specific CLI tools (`gh`, `jq`, `git`, `curl`, `inspect`). Design has no tooling section and doesn't specify which tools reviewers or synthesizer use.
- **Why it matters:** If reviewers need to check prior art (Prior Art Scout), search codebases (survey phase context), or validate assumptions (Assumption Hunter), they need tooling. Design doesn't specify whether these capabilities exist or how they're accessed.
- **Suggestion:** Add "Reviewer Capabilities" section specifying: (1) which CLI tools are available to each persona (e.g., Prior Art Scout gets `gh` for searching repos, `curl` for fetching docs), (2) whether reviewers can invoke subagents for research, (3) what the tool access boundary is (read-only vs write).
- **Status:** accepted
- **Disposition note:** Valid — specify reviewer tool access in Task 8 prompt iteration. Per-persona tool boundaries belong in the stable prompt prefix.

### Finding 22: Codex Portability Not Addressed
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement requires "Portability sanity check script: Build a simple script early that runs a parallax skill on both Claude Code and Codex CLI and diffs the output quality. Goal: catch Claude-specific assumptions before they're baked in." Design doesn't address portability or testing on Codex.
- **Why it matters:** If reviewer prompts use Claude-specific features (extended thinking mode, artifact rendering, MCP tools), skill won't work on Codex. Testing this early is cheaper than refactoring later.
- **Suggestion:** Add to prototype scope: portability validation task. Run the 6 reviewer personas on same design doc using both Claude and Codex, diff the findings. Document any Claude-specific assumptions discovered.
- **Status:** deferred
- **Disposition note:** Defer to eval phase. Post-prototype concern — run portability check after prompts stabilize.

### Finding 23: Output Voice Guidelines Missing
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Per-Reviewer Output Format
- **Issue:** Problem statement specifies detailed output voice requirements ("direct and engineer-targeted," "lead with verdict," "no hedging language," "SRE-style framing"). Design specifies output **format** (markdown structure) but not output **voice** (how findings should be written).
- **Why it matters:** Without voice guidelines in reviewer prompts, different personas will use different tones (some hedging, some direct). Inconsistent output quality reduces trust in findings.
- **Suggestion:** Add voice guidelines to "Per-Reviewer Output Format" section and specify that these rules are part of stable prompt prefix. Example rules: "Use active voice. Lead with impact, then evidence. No hedging ('might', 'could', 'possibly'). Quantify blast radius where possible."
- **Status:** accepted
- **Disposition note:** Part of Task 8 prompt iteration. Voice guidelines go in stable prompt prefix per Finding 3 caching architecture.

### Finding 24: Document Chain RFC Mechanism Undefined
- **Severity:** Important
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement says "The pipeline naturally produces a chain: problem statement → requirements → design → review findings → plan. This chain consolidates into something RFC-like." Design produces individual artifacts but has no consolidation mechanism.
- **Why it matters:** If artifacts aren't consolidated, users must manually assemble context from multiple files when sharing designs for human review. Reduces portability of design decisions.
- **Suggestion:** Add to synthesis step: RFC consolidation task. After review converges, synthesizer produces single markdown file combining: (1) original requirements, (2) design decisions, (3) review findings + dispositions, (4) final approved design. This becomes the shareable artifact.
- **Status:** accepted
- **Disposition note:** Nice-to-have, defer. JSONL + markdown rendering may naturally produce this — consolidated view becomes a render target rather than a separate mechanism.

### Finding 25: Design vs Requirements Contradiction Not Handled
- **Severity:** Important
- **Flagged by:** Edge Case Prober
- **Phase:** design
- **Section:** Requirement Auditor persona, Input contract
- **Issue:** Requirement Auditor checks if design satisfies requirements, but design doesn't specify what happens if the *requirements themselves* are contradictory or impossible to satisfy together. Design can't fix this—it's upstream—but review may not surface it clearly.
- **Why it matters:** Contradictory requirements are a calibrate-phase failure, not design-phase failure. If requirements say "must be zero-latency" and "must run on free tier," no design can satisfy both. Reviewer should escalate immediately, but design doesn't explicitly call this out as distinct failure mode.
- **Suggestion:** Add explicit check: Requirement Auditor should flag requirement-level contradictions as automatic escalate (calibrate gap, severity Critical). Don't attempt design iteration—requirements need fixing first.
- **Status:** accepted
- **Disposition note:** Small prompt addition to Requirement Auditor — auto-escalate requirement contradictions as calibrate gap (Critical). No architectural change. Additionally: research "The Algorithm" engineering workflow (delete before optimize — never optimize a requirement or process step that shouldn't exist). Apply this principle both to parallax's own pipeline AND as a reviewer lens. Reviewers should ask "should this requirement exist at all?" before checking if the design satisfies it.

### Finding 26: Personas Solve Coverage, Not Adversarial Review
- **Severity:** Important
- **Flagged by:** First Principles Challenger
- **Phase:** calibrate
- **Section:** Reviewer Personas
- **Issue:** The 6 design-stage personas (Assumption Hunter, Edge Case Prober, etc.) are scoped by domain (what to look for) but not by stance (what to defend or attack). This produces comprehensive coverage but weak adversarial tension. Real adversarial review requires incompatible worldviews: "move fast and prove it works" vs "move carefully and prove it's safe." Personas can all be right simultaneously—they're additive, not adversarial.
- **Why it matters:** Hypothesis is "multiple perspectives catch gaps," but personas are designed as non-overlapping inspectors. You'll catch more bugs but won't challenge the design's core premise. Most valuable finding is "this whole approach is wrong," and none of these personas are incentivized to say that (except First Principles Challenger, outvoted 5-to-1).
- **Suggestion:** Redesign personas as adversarial pairs with opposing incentives. Examples: "Ship Fast" (minimize complexity, defer edge cases) vs "Ship Right" (demand completeness, block on unknowns). "User-Centric" (optimize for end-user experience) vs "Operator-Centric" (optimize for maintainability). Force them to argue. Best findings will come from resolving their contradictions, not from independent checklists. **Note:** This is a significant architectural change that challenges the core persona design. May be better suited for post-prototype iteration based on eval data.
- **Status:** accepted
- **Disposition note:** Prioritize in early eval — don't wait for full eval framework. Test at least a couple of adversarial personas (stance-based, not just domain-based) against current coverage-based personas on same artifact. Need eval data to show whether adversarial pairs produce higher-value findings. If pairs outperform, may not need as many total personas.

### Finding 27: Prototype Defers Highest-Leverage Phase
- **Severity:** Important
- **Flagged by:** First Principles Challenger
- **Phase:** plan
- **Section:** Prototype Scope
- **Issue:** Prototype builds design-stage review but defers requirements and plan stages. Problem statement explicitly calls out requirements refinement as "single biggest design quality lever" and identifies spec drift (design-to-plan divergence) as major pain point. Prototype will validate persona mechanics but won't test core hypothesis: does adversarial review at requirements-time prevent downstream design failures?
- **Why it matters:** Building design-stage review first is natural (familiar domain) but risks building the wrong thing. If requirements review is highest-leverage phase, prototyping design review teaches you about subagent orchestration but nothing about whether pipeline actually works. You'll have battle-tested personas for a phase that might not matter.
- **Suggestion:** Prototype requirements-stage review first, or in parallel. Use real past project where bad requirements led to design failures (Second Brain is candidate). Validate that adversarial review at requirements-time would have caught the issues. Then build design-stage review knowing it's solving the right problem. Alternatively: accept that you're prototyping orchestration mechanics (not value hypothesis) and defer validation to eval framework.
- **Status:** accepted
- **Disposition note:** Known tradeoff, already made. We're prototyping orchestration mechanics with design review. Value hypothesis validation (does requirements-stage review prevent downstream failures?) comes in eval phase with real test cases.

### Finding 28: "Proceed" Verdict Lacks Quality Bar
- **Severity:** Important
- **Flagged by:** First Principles Challenger
- **Phase:** design
- **Section:** Verdict Logic
- **Issue:** A "proceed" verdict means "only Important/Minor findings" but provides no guidance on how many Important findings are acceptable. Is a design with 20 Important findings better than one with 2? Does it matter if they're all in same category (e.g., all edge cases deferred) vs spread across categories?
- **Why it matters:** Without quality threshold, "proceed" becomes "no Critical findings" which is very low bar. Real designs will accumulate Important findings that individually seem acceptable but collectively indicate design is undercooked. User has no framework to decide "this is good enough" vs "we need another iteration."
- **Suggestion:** Define quality budget. Examples: (1) Hard cap (no more than N Important findings total). (2) Weighted score (Critical = -10, Important = -2, must be net positive after accepts). (3) Category limits (no more than 3 Important findings in any single persona's domain, signals blind spot). Make this configurable but provide sensible default.
- **Status:** deferred
- **Disposition note:** Defer to eval phase. Need empirical data on finding distributions before designing a quality budget formula. Premature to pick thresholds without seeing real review outputs across test cases.

### Finding 29: Reviewer Calibration Feedback Loop Not Designed
- **Severity:** Important
- **Flagged by:** First Principles Challenger
- **Phase:** calibrate
- **Section:** Open Questions, Problem Statement "Correction Compounding"
- **Issue:** Design mentions "reject findings as feedback for reviewer tuning" and problem statement describes correction compounding (false positives/negatives become calibration rules). But there's no design for how this feedback is captured, who analyzes it, or how prompts are updated. This is a core value proposition (reviewers improve over time) with no implementation plan.
- **Why it matters:** Without calibration loop, rejected findings are lost signal. Over time, users will learn which reviewers produce noise and ignore them (defeating multi-perspective benefit). Eval framework can measure quality, but if there's no mechanism to feed that back into prompts, system won't improve.
- **Suggestion:** Design the calibration artifact. Minimal version: `docs/reviews/<topic>/calibration-notes.md` where skill logs rejected findings with user's reason. After N reviews, a calibration skill analyzes patterns and suggests prompt updates. Or integrate with eval framework: every review run is also an eval, findings are graded, and low-accuracy reviewers trigger prompt revision tasks.
- **Status:** deferred
- **Disposition note:** Defer to eval phase. JSONL output with disposition data naturally captures the signal (rejected findings + notes). Calibration analysis comes after enough review runs to see patterns.

### Finding 30: Inspect AI Already Provides Multi-Agent Review Orchestration
- **Severity:** Important
- **Flagged by:** Prior Art Scout
- **Phase:** design
- **Section:** Reviewer Personas, Pipeline Integration
- **Issue:** The design builds custom parallel reviewer dispatch, finding consolidation, and severity classification. Inspect AI (already listed as eval framework) has built-in multi-agent orchestration, finding deduplication, scoring normalization, and agent comparison features. This is being reimplemented rather than leveraged.
- **Why it matters:** Inspect AI is MIT-licensed, actively maintained (UK AISI project), supports Claude + Codex, and has 100+ pre-built evals including multi-agent patterns. Building custom orchestration means maintaining code for agent dispatch, result collection, retries, timeout handling. Design claims "evaluate LangGraph when limits are hit" but doesn't evaluate whether Inspect AI already provides what's being built.
- **Suggestion:** Prototype reviewer personas as Inspect AI solvers with custom system prompts. Use Inspect's `multi_agent` pattern for parallel dispatch and `scorer` API for finding consolidation. Reserve custom orchestration only if Inspect's patterns prove insufficient. This positions parallax:review as prompt engineering (the novel contribution) rather than orchestration infrastructure (already solved). See: https://inspect.ai-safety-institute.org.uk/multi-agent.html
- **Status:** accepted
- **Disposition note:** Evaluate Inspect AI as implementation substrate during eval phase. Aligns with CLAUDE.md: BUILD adversarial review (novel), LEVERAGE mature frameworks. Novel contribution is persona prompts + phase classification, not orchestration plumbing.

---

## Minor Findings

### Finding 31: Empty Design Docs May Produce No Findings
- **Severity:** Minor
- **Flagged by:** Edge Case Prober
- **Phase:** design
- **Section:** Step 2: Dispatch
- **Issue:** If user provides very short or incomplete design doc (e.g., "TODO: write design"), reviewers may struggle to produce meaningful findings. They might hallucinate issues, return "insufficient detail" meta-findings, or produce empty output.
- **Why it matters:** Garbage in, garbage out. Running full 6-agent review on stub design wastes tokens and produces confusing output. User expects actionable findings, not "this design is too short to review."
- **Suggestion:** Add pre-flight check: (1) Validate design doc length (e.g., min 500 words or 10 headings), (2) If too short, return early with "design incomplete, minimum review threshold not met", (3) Alternatively, shift reviewers into "incompleteness audit" mode (flag missing sections rather than reviewing content).
- **Status:** pending

### Finding 32: Git Commit Failures Could Lose Review Artifacts
- **Severity:** Minor (downgraded from Important—while data loss is serious, git failures are rare in practice and workarounds exist)
- **Flagged by:** Edge Case Prober
- **Phase:** plan
- **Section:** Step 6: Wrap Up
- **Issue:** Design assumes git commit will succeed, but git operations can fail (detached HEAD, merge conflicts, repo in bad state, disk full). If commit fails after review completes, review artifacts exist on disk but aren't tracked, risking loss on cleanup or confusion about which review is "official."
- **Why it matters:** Review artifacts are valuable (especially after 6-agent runs consuming significant tokens). Losing them due to git failure is bad UX and data loss. Silent failure is worse—user thinks review is saved but it's not.
- **Suggestion:** Add git operation validation: (1) Check git status before review starts (warn if repo is dirty or detached), (2) After writing review artifacts, explicitly commit and check success, (3) If commit fails, warn user and explain how to manually commit from `docs/reviews/<topic>/`, (4) Consider writing artifacts even if git is unavailable (graceful degradation).
- **Status:** pending

### Finding 33: No Token/Cost Visibility During Review
- **Severity:** Minor
- **Flagged by:** Edge Case Prober
- **Phase:** design
- **Section:** Step 2: Dispatch, Step 3: Synthesize
- **Issue:** Running 6 agents in parallel on large design docs could consume significant tokens. Design doesn't show cost estimates before running or actual token usage after completion.
- **Why it matters:** Budget-conscious users may want to know cost before committing to 6-agent review. Post-run token reporting helps tune reviewer prompts (identify verbose reviewers) and validates cost assumptions.
- **Suggestion:** Add cost visibility: (1) Estimate token cost before dispatch based on design doc size and reviewer count, (2) Report actual token usage and cost per reviewer in summary, (3) Track cumulative cost across iterations for same topic, (4) Warn if estimated cost exceeds threshold (e.g., $1+ for single review). **Note:** This overlaps with Finding 11 (Cost Budget Not Specified) but focuses specifically on visibility during execution rather than overall budgeting.
- **Status:** pending

### Finding 34: Blind Spot Checks May Produce Noise
- **Severity:** Minor
- **Flagged by:** Assumption Hunter, Edge Case Prober, Feasibility Skeptic, Requirement Auditor
- **Phase:** design
- **Section:** Per-Reviewer Output Format (Blind Spot Check)
- **Issue:** Each reviewer ends with "Blind Spot Check" where they ask "what might I have missed?" This could produce duplicate findings (reviewer flags X in Findings, then flags "I might have missed X" in blind spot check), meta-findings ("I'm not a security expert so I might have missed security issues" without actionable detail), or hedged non-findings. Design describes this as "self-error-detection" (valuable in theory) but provides no specification for how this freeform text is used.
- **Why it matters:** If blind spot checks are never surfaced to user or acted upon, they're pure overhead (token cost, no value). If they *are* valuable, they should be first-class output in summary.md. Feasibility Skeptic: "untestable—how do you know if a blind spot check is useful?" Design doc flags this as "empirical question for eval framework" but doesn't specify fallback if it's noise.
- **Suggestion:** **Assumption Hunter:** Specify whether blind spot checks are: (1) Included in summary.md under dedicated section, (2) Used by Synthesizer to identify coverage gaps and suggest additional reviewers, or (3) Informational only (written to individual reviewer files for eval/tuning, not shown to user). Clarify whether they count as findings (with severity/phase) or just freeform reflection. **Edge Case Prober:** Test empirically with clear removal criteria: If blind spot checks produce <10% novel findings across 10 test reviews, remove them. Alternatively, move to separate optional section (not mixed with findings). **Feasibility Skeptic:** Make optional in output format and run A/B tests during eval: same reviewers with/without blind spot prompts. Compare finding coverage. Don't commit to it in prototype.
- **Status:** pending

### Finding 35: Product Strategist Missing from Design Stage
- **Severity:** Minor
- **Flagged by:** Assumption Hunter
- **Phase:** design
- **Section:** Requirements Stage personas, Design Stage personas
- **Issue:** Design specifies Product Strategist persona active during requirements review ("Will anyone actually use this? How do we know it worked?"), but when reviewing a *design* doc, none of the 6 active personas check whether design actually delivers user value or includes measurable success criteria. Requirement Auditor checks "coverage gaps" but is focused on requirement compliance, not product strategy.
- **Why it matters:** A design can satisfy all stated requirements while still being wrong solution (over-engineered, wrong user workflow, unmeasurable outcomes). Requirements doc emphasizes "outcome-focused" as single biggest design quality lever, but design-stage review doesn't enforce this.
- **Suggestion:** Either (1) Add PM-focused question to one of existing design-stage personas (e.g., First Principles Challenger asks "Does this design optimize for outcomes or just check requirement boxes?"), or (2) Activate Product Strategist in design stage as well (making it 7 personas, not 6). Acknowledge the tradeoff (cost/time vs coverage).
- **Status:** pending

### Finding 36: Persona Count Justification Weak
- **Severity:** Minor
- **Flagged by:** Requirement Auditor, Feasibility Skeptic
- **Phase:** design
- **Section:** Reviewer Personas
- **Issue:** Design says "9 total personas, 4-6 active per stage. Optimal count is empirical question for eval framework—this is starting hypothesis." No justification for **why** these specific personas or why 4-6 is the hypothesis. Feasibility Skeptic questions whether requirements stage needs 4-5 reviewers (requirements docs typically shorter/less complex than designs).
- **Why it matters:** Without rationale, unclear whether this is over-engineered (too many personas, overlapping concerns) or under-engineered (missing key perspectives). Eval results will be hard to interpret.
- **Suggestion:** **Requirement Auditor:** Add brief rationale for each persona (what blind spot does it cover that others miss?) and for 4-6 count hypothesis (based on prior art research? intuition? cost constraints?). **Feasibility Skeptic:** Start requirements stage with 3 reviewers (Requirement Auditor, Product Strategist, First Principles Challenger). If eval data shows you're missing critical requirement gaps, add more. Scale up based on evidence.
- **Status:** pending

### Finding 37: Stage-Specific Persona Activation Not Validated
- **Severity:** Minor
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Persona Activation Matrix
- **Issue:** Activation matrix shows which personas are active per stage (e.g., Assumption Hunter active in requirements & design, not plan). No justification for **why** specific personas are excluded from specific stages.
- **Why it matters:** If Assumption Hunter would catch plan-stage assumptions (e.g., "assumes this API exists"), excluding it is a gap. If not, exclusion is correct. No rationale provided.
- **Suggestion:** Add column to activation matrix: "Why not active?" for each excluded persona-stage pair. Example: "Assumption Hunter not in plan stage—implementation assumptions caught by Code Realist instead."
- **Status:** pending

### Finding 38: Review Stage Parameter Not Future-Proof
- **Severity:** Minor
- **Flagged by:** Requirement Auditor
- **Phase:** design
- **Section:** Skill Interface
- **Issue:** Input contract specifies `review stage` as "one of: requirements, design, plan" but only design stage implemented in prototype. If new stages added later (e.g., post-execution retrospective review), the enum changes.
- **Why it matters:** Minor versioning concern—clients invoking skill will need to update when new stages added.
- **Suggestion:** Document stage enum as extensible in skill interface section. Consider using `stage: string` parameter with validation rather than hardcoded enum, or version the skill (parallax:review v1 = design only, v2 = all stages).
- **Status:** pending

### Finding 39: Git Tracking Assumes Single-Branch Workflow
- **Severity:** Minor
- **Flagged by:** First Principles Challenger
- **Phase:** design
- **Section:** Output Artifacts
- **Issue:** "Iteration history tracked by git (each re-review is new commit, diffs show what changed)" assumes all iterations happen on single branch. Real workflows often involve design exploration in branches (Option A vs Option B) with review findings informing which to merge.
- **Why it matters:** If user is comparing two design approaches and reviews both, git history will show two interleaved commit sequences. Diffs will compare iterations within a branch (useful) but not branches against each other (also useful).
- **Suggestion:** Support explicit design comparison mode: review two design docs against same requirements, produce comparative summary ("Design A has stronger feasibility, Design B has better edge case handling"). Or document the limitation and defer to manual branching strategies.
- **Status:** pending

### Finding 40: Model Tiering Not Tested
- **Severity:** Minor
- **Flagged by:** Feasibility Skeptic
- **Phase:** design
- **Section:** Prototype scope, cost strategy
- **Issue:** Design assumes Sonnet for all reviewers but doesn't test whether Haiku is sufficient for any personas. Requirement Auditor (mechanical checklist matching) and Edge Case Prober (boundary condition enumeration) might work fine on Haiku at 1/10th the cost.
- **Why it matters:** Budgeting for worst-case when you could be testing model tiering empirically. If Haiku catches 80%+ of same issues for mechanical reviewers, model tiering drops per-review cost by 30-40%.
- **Suggestion:** Run first prototype review with all-Sonnet (validates quality bar), then run ablation test with Haiku for 2-3 personas and compare finding quality. This is low-risk empirical validation (single test case, manual comparison) that pays for itself in 10-20 review cycles.
- **Status:** pending

### Finding 41: LangSmith Provides Ready-Made Finding Classification and Human-In-The-Loop Review
- **Severity:** Minor (downgraded from Important—valuable optimization but not blocking for prototype)
- **Flagged by:** Prior Art Scout
- **Phase:** design
- **Section:** Synthesis, UX Flow
- **Issue:** Synthesizer agent and interactive finding processing (accept/reject/discuss) are being custom-built. LangSmith (already in tooling budget) provides dataset annotation, human feedback collection, finding tagging by phase/severity, and web UI for accept/reject/comment workflows. This is production-grade infrastructure for exactly this use case.
- **Why it matters:** Building custom finding queue, disposition tracking, and "discuss" conversation threading is complex UI/UX work. LangSmith's human review UI is battle-tested, supports team collaboration, integrates with LangChain/LangGraph. 5k traces/month free tier covers months of prototyping.
- **Suggestion:** Evaluate LangSmith's annotation UI for finding processing. Each reviewer run becomes trace, findings become tags, human disposition (accept/reject) becomes feedback. If UI works, skill becomes thin wrapper that launches reviews and posts results to LangSmith for human processing. Reserve custom implementation if LangSmith's UI/workflow doesn't fit.
- **Status:** pending

---

## Contradictions

### Contradiction 1: Synthesizer Role Definition
- **Reviewers:** Assumption Hunter, Feasibility Skeptic, First Principles Challenger
- **Position A (Assumption Hunter):** Synthesizer should acknowledge deduplication is a judgment call and specify threshold (conservative vs aggressive). Deduplication requires semantic interpretation.
- **Position B (Feasibility Skeptic):** Synthesizer should be explicitly judgmental on phase classification, or phase classification should be a separate agent/step. Remove "purely editorial" constraint.
- **Position C (First Principles Challenger):** Reframe Synthesizer as "adversarial consolidator" whose job is finding patterns and tensions individuals can't see, OR split into two roles: mechanical aggregator (no judgment) + meta-reviewer (analyzes aggregate for emergent patterns).
- **Why this matters:** All three reviewers agree the "purely editorial, zero judgment" constraint is dishonest given the responsibilities (deduplication, phase classification, contradiction surfacing). They disagree on the solution. This affects prompt engineering for the Synthesizer agent and determines whether it's one agent or two.
- **Status:** pending

### Contradiction 2: "Discuss" Mode Implementation
- **Reviewers:** Feasibility Skeptic (strongest position: cut it from MVP), First Principles Challenger (specify protocol), Edge Case Prober (add boundaries), Assumption Hunter (specify exit conditions)
- **Position A (Feasibility Skeptic):** MVP should be accept/reject only. "Discuss" becomes: user rejects finding with note, that note becomes input to next review cycle. Add true discussion mode in v2 if eval data shows rejected findings aren't being addressed. This is testable, doesn't require modal state management, delivers same outcome.
- **Position B (First Principles Challenger):** Specify the discussion protocol now. Options: discussion with original reviewer only (time-boxed to 3 turns, must end with revised severity or withdrawn finding), OR discussion invokes "mediator" agent with access to all reviewer contexts, OR discussion creates sub-review where all reviewers re-examine just this finding with user's clarifications.
- **Position C (Edge Case Prober/Assumption Hunter):** Keep "discuss" mode but add explicit boundaries: max turn count per finding (5 exchanges), explicit "resolve and decide" command to exit discussion, show context reminder at each turn, allow user to defer decision.
- **Why this matters:** This is a major implementation decision. Feasibility Skeptic estimates "discuss" will consume 30-50% of implementation time for an untestable feature (no test case includes discussion transcripts). First Principles Challenger calls it "the most novel and potentially valuable interaction mode" but "underspecified and high-risk." The choice affects scope, timeline, and risk profile of the prototype.
- **Status:** pending

### Contradiction 3: Persona Design Philosophy
- **Reviewers:** First Principles Challenger vs implicit design assumption
- **Position A (First Principles Challenger):** Personas should be redesigned as adversarial pairs with opposing incentives (Ship Fast vs Ship Right, User-Centric vs Operator-Centric). Force them to argue. Best findings come from resolving contradictions, not independent checklists. Current personas are "additive, not adversarial."
- **Position B (Implicit design assumption):** Current personas are scoped by domain (what to look for) providing comprehensive coverage. Non-overlapping inspectors catch more bugs through diverse perspectives.
- **Why this matters:** This challenges the core architecture of the reviewer personas. First Principles Challenger argues the hypothesis is "multiple perspectives catch gaps" but current design produces coverage, not adversarial tension. Most valuable finding is "this whole approach is wrong" and current personas aren't incentivized to say that. This would require significant rework of persona definitions and likely change the persona count. However, it may be better suited for post-prototype iteration based on eval data (YAGNI principle).
- **Status:** pending

---

## Analysis Notes

### Deduplication Summary
- **Parallel agent failure handling:** 3 reviewers (Assumption Hunter, Edge Case Prober, Feasibility Skeptic) flagged this with near-identical framing. Consolidated as Finding 1.
- **Discuss mode complexity:** 4 reviewers (Assumption Hunter, Edge Case Prober, Feasibility Skeptic, First Principles Challenger) flagged this with different emphasis. Consolidated as Finding 6 with contradiction (Contradiction 2) capturing the different solutions.
- **Synthesizer "purely editorial" contradiction:** 3 reviewers (Assumption Hunter, Feasibility Skeptic, First Principles Challenger) flagged this. Consolidated as Finding 13 with contradiction (Contradiction 1) capturing different framings.
- **Severity range ambiguity:** 3 reviewers (Edge Case Prober, Feasibility Skeptic, Requirement Auditor) flagged this. Consolidated as Finding 8 (escalated to Critical due to verdict logic impact).
- **Cost/budget concerns:** 3 reviewers (Assumption Hunter, Edge Case Prober, Feasibility Skeptic) flagged this from different angles. Split into Finding 11 (overall cost budget) and Finding 33 (runtime visibility).
- **Blind spot checks:** 4 reviewers flagged this with consensus that it's empirical/unvalidated. Consolidated as Finding 34.

### Calibrate Gaps (5 findings)
These represent mismatches between problem statement requirements and design scope, or requirements-level constraints not addressed:
- Finding 2: Interactive processing contradicts background automation requirements
- Finding 9: Review stage input assumes orchestrator context but claims standalone use
- Finding 11: Cost budget not specified (requirements doc mentions budget extensively)
- Finding 18: Scope mismatch—requirement refinement expected
- Finding 26: Personas solve coverage, not adversarial review (calibration of what "adversarial" means)
- Finding 29: Reviewer calibration feedback loop not designed (problem statement requirement)

### Plan Concerns (6 findings)
These are implementation/testing concerns that should be addressed during plan phase:
- Finding 22: Codex portability not addressed
- Finding 27: Prototype defers highest-leverage phase
- Finding 32: Git commit failures could lose review artifacts
- Finding 40: Model tiering not tested

### Highest Consensus Findings
Findings flagged by 3+ reviewers (strong signal):
1. **Finding 1** (Parallel agent failure handling) - 3 reviewers
2. **Finding 6** (Discuss mode) - 4 reviewers
3. **Finding 8** (Severity ranges/verdict logic) - 3 reviewers
4. **Finding 12** (Git commit strategy) - 3 reviewers
5. **Finding 13** (Synthesizer role) - 3 reviewers
6. **Finding 34** (Blind spot checks) - 4 reviewers

### Novel Contributions vs Build-vs-Buy
Prior Art Scout (Finding 30) identifies that Inspect AI provides multi-agent orchestration infrastructure that's being rebuilt. This is important leverage opportunity but doesn't invalidate the design—the novel contribution is finding classification (routing errors to failed phase) and persona prompt engineering, not the orchestration mechanics. Recommend evaluating Inspect AI as implementation substrate rather than building custom orchestration.
