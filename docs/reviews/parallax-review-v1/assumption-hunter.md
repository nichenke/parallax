# Assumption Hunter Review

## Findings

### Finding 1: Parallel Dispatch Without Failure Handling
- **Severity:** Critical
- **Phase:** design
- **Section:** Step 2: Dispatch (line 206-207)
- **Issue:** The design states "dispatches reviewer agents in parallel (4-6 depending on stage)" but provides no specification for what happens if one or more agents fail, timeout, or produce malformed output. The UX only describes the success path ("User sees status").
- **Why it matters:** In a multi-agent parallel execution, partial failures are not edge cases — they're expected behavior. Without a failure strategy, a single agent crash blocks the entire review, or worse, proceeds with incomplete findings that appear complete.
- **Suggestion:** Specify failure modes explicitly: (1) Retry count per agent, (2) Whether to proceed with N-1 findings if one agent fails, (3) How to surface partial results to the user ("5 of 6 reviewers completed"), (4) Timeout values, (5) What constitutes a malformed reviewer output that should trigger a retry vs fail-fast.

### Finding 2: "Interactive Finding Processing" Assumes Real-Time Human Availability
- **Severity:** Critical
- **Phase:** calibrate
- **Section:** Step 5: Process Findings (line 221-227)
- **Issue:** The design requires "one at a time" interactive processing of findings with accept/reject/discuss. This assumes the human is sitting at the keyboard waiting for the review to complete. No provision for async workflows (run review overnight, process findings the next morning).
- **Why it matters:** This directly contradicts CLAUDE.md's stated goal of "Claude-native background automation — Agent SDK + MCP + cron for long-running research" (track #6). If reviews can't be decoupled from human interaction, they can't run in background automation.
- **Suggestion:** Decouple finding presentation from finding processing. Support two modes: (1) **Interactive** (current design), (2) **Async** where findings are written to disk and the user processes them in a later session. The summary.md format already supports this (dispositions updated incrementally), but the skill invocation contract doesn't acknowledge async mode exists.

### Finding 3: Unstated Assumption About Reviewer Output Compliance
- **Severity:** Important
- **Phase:** design
- **Section:** Per-Reviewer Output Format (line 99-118), Synthesis (line 123-136)
- **Issue:** The design assumes reviewers will produce well-formed markdown with the exact schema specified (Severity, Phase, Section, Issue, etc.). No validation, no error handling if a reviewer invents new severity levels, omits required fields, or uses freeform text instead of structured findings.
- **Why it matters:** The Synthesizer's deduplication, phase classification, and severity reporting logic all depend on parseable structured output. If reviewer output isn't validated, synthesis fails silently or produces garbage. LLMs are stochastic — even with good prompts, they occasionally produce malformed output.
- **Suggestion:** Add schema validation step after each reviewer completes. Either (1) Validate and retry the agent if output is malformed, or (2) Mark that reviewer's output as "unparseable" and exclude it from synthesis (with user notification). Specify which fields are strictly required vs optional.

### Finding 4: "Topic Label" Input Has No Validation or Collision Handling
- **Severity:** Important
- **Phase:** design
- **Section:** Skill Interface (line 21), Step 1: Invoke (line 200-204)
- **Issue:** The design requires a "topic label for the review folder" but doesn't specify constraints (allowed characters? max length? what if it contains `/` or `..`?). It also doesn't specify what happens if `docs/reviews/<topic>/` already exists from a prior review.
- **Why it matters:** Without validation, a malicious or accidental topic like `../../secrets` could write review files outside the intended directory. Without collision handling, re-running a review with the same topic either silently overwrites the previous review (losing iteration history) or fails with a cryptic filesystem error.
- **Suggestion:** (1) Validate topic label against a safe character set (alphanumeric, hyphens, underscores only), (2) Specify collision behavior: append timestamp suffix (`topic-2026-02-15-143022/`), prompt user to confirm overwrite, or auto-increment (`topic-v2/`). The design claims "iteration history tracked by git" but doesn't explain whether iterations share one folder (overwrite files) or create new folders.

### Finding 5: "Discuss" Mode Has No Depth Limit or Exit Strategy
- **Severity:** Important
- **Phase:** design
- **Section:** Step 5: Process Findings, "Discuss is a first-class interaction" (line 226)
- **Issue:** The design allows the user to "explore a finding in depth, ask questions, challenge the reviewer's reasoning" but provides no specification for how the discussion terminates, whether there's a conversation depth limit, or what happens if the discussion never reaches a resolution.
- **Why it matters:** An unbounded conversation consumes context window, API costs, and user time. Without a forcing function to resolve the discussion, the finding queue stalls indefinitely. The design states "the skill maintains its position in the finding queue and resumes after the discussion resolves" but doesn't define what "resolves" means.
- **Suggestion:** Specify discussion exit conditions: (1) User explicitly chooses accept/reject/defer after the discussion, (2) Maximum conversation turns (e.g., 5 back-and-forth exchanges), (3) Ability to defer a finding ("mark for later review") and move to the next one. Also specify whether discussed findings are logged separately (ADR-style rationale for why the finding was accepted/rejected).

### Finding 6: Phase Classification Logic Contradicts Verdict Logic
- **Severity:** Critical
- **Phase:** design
- **Section:** Finding Phase Classification (line 138-146), Verdict Logic (line 148-153)
- **Issue:** The Finding Phase Classification table states that survey/calibrate gaps should "Go back to research" / "Revisit requirements." The Verdict Logic states "Survey or calibrate gap at any severity → `escalate`". But the design never specifies what `escalate` actually does — does it terminate the skill immediately, or does it still process all findings first? If survey gaps are found in finding #2 of 40, does the user process findings 3-40 or does the skill exit immediately?
- **Why it matters:** This is a critical UX decision that affects whether users see the full scope of the problem before restarting upstream. If the skill exits on first escalation, users can't assess whether the design has one foundational issue or twenty. If it processes all findings first, the `escalate` verdict is just a label, not a gate.
- **Suggestion:** Make the escalation behavior explicit: "If any survey/calibrate findings are detected, the skill marks verdict as `escalate` but continues processing all findings. At Step 6 wrap-up, if verdict is `escalate`, the skill presents all findings for informational review but does not allow accept/reject (since the design will be discarded anyway). User is told which upstream phase to revisit."

### Finding 7: "Synthesizer is Purely Editorial" But Must Make Judgment Calls
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis (line 123-136), specifically "zero judgment on content or severity"
- **Issue:** The design states the Synthesizer has "zero judgment" and "does NOT override or adjust reviewer severity ratings." But the Synthesizer must deduplicate findings, which requires judging whether two findings are "the same issue" or different issues. It must also group contradictions, which requires recognizing when reviewers are addressing the same topic with opposing positions. Both require semantic judgment.
- **Why it matters:** If deduplication is too aggressive, it collapses distinct issues into one finding, losing important nuance. If deduplication is too conservative, it floods the user with near-duplicates. The design hasn't acknowledged this tension or specified how aggressive the deduplication should be.
- **Suggestion:** Acknowledge that deduplication is a judgment call and specify the threshold. Options: (1) "Deduplicate only if findings reference the exact same section and use similar wording" (conservative), (2) "Deduplicate if findings address the same design decision, even if they identify different failure modes" (aggressive), (3) "Always preserve separate findings but group related ones under a common heading" (compromise). Also specify whether the Synthesizer includes excerpts from each reviewer's version when deduplicating.

### Finding 8: No Cost Budget or Token Limit Specified
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Entire design, especially "Optimal number of personas per stage" (line 271)
- **Issue:** The design acknowledges cost as an eval question ("Cost per review run", line 274) but the skill interface and verdict logic have no cost ceiling. A 6-agent review on a 50-page design doc could consume thousands of tokens per agent. The design provides no escape hatch if a review run exceeds budget.
- **Why it matters:** CLAUDE.md specifies a $2000/month budget with $150-400/month projected API spend. A single poorly-scoped review (e.g., reviewing CLAUDE.md itself with 6 agents) could consume 10-20% of the monthly budget. Without cost visibility or caps, users can't make informed go/no-go decisions.
- **Suggestion:** Add optional `max_cost` parameter to skill invocation (e.g., "abort if estimated cost exceeds $X"). Show estimated cost before dispatch ("This review will cost approximately $12 based on input token count × 6 agents"). Log actual cost in summary.md for budget tracking. Specify whether cost estimation uses prompt caching assumptions (which reduce cost 90% on cache hits but require stable prompts).

### Finding 9: Git Commit Strategy Undefined for Multi-Artifact Reviews
- **Severity:** Important
- **Phase:** design
- **Section:** Step 6: Wrap Up (line 228-234), "All artifacts committed to git" (line 234)
- **Issue:** The design states "All artifacts committed to git" but doesn't specify whether this is one commit containing all reviewer outputs + summary, or separate commits per reviewer, or only the summary is committed. It also doesn't specify the commit message format or whether the user approves the commit.
- **Why it matters:** The requirements doc emphasizes "Git commits per iteration. Full history, diffable artifacts" and "ADR-style finding documentation." But if all 6 reviewer files + summary are in one blob commit, diffing across iterations is noisy. If each reviewer is a separate commit, the git history has 7 commits per review run (hard to navigate). The design hasn't reconciled "full history" with usability.
- **Suggestion:** Specify commit strategy explicitly. Recommended: Single commit per review run containing all artifacts, with structured commit message: `parallax:review — [topic] — [verdict] ([N] findings)`. User confirms before commit (since CLAUDE.md states "NEVER commit changes unless the user explicitly asks" in Git Safety Protocol). Optionally, support `--auto-commit` flag for automation workflows.

### Finding 10: Requirements Stage Adds "Product Strategist" But Design Stage Review Has No PM Lens
- **Severity:** Minor
- **Phase:** design
- **Section:** Requirements Stage personas (line 60-70), Design Stage personas (line 49-58)
- **Issue:** The design specifies that Product Strategist persona is active during requirements review ("Will anyone actually use this? How do we know it worked?"), but when reviewing a *design* doc, none of the 6 active personas check whether the design actually delivers user value or includes measurable success criteria. The Requirement Auditor checks "coverage gaps" but is focused on requirement compliance, not product strategy.
- **Why it matters:** A design can satisfy all stated requirements while still being the wrong solution (over-engineered, wrong user workflow, unmeasurable outcomes). The requirements doc emphasizes "outcome-focused" as the single biggest design quality lever, but the design-stage review doesn't enforce this.
- **Suggestion:** Either (1) Add a PM-focused question to one of the existing design-stage personas (e.g., First Principles Challenger asks "Does this design optimize for outcomes or just check requirement boxes?"), or (2) Activate Product Strategist in design stage as well (making it 7 personas, not 6). Acknowledge the tradeoff (cost/time vs coverage).

### Finding 11: "Blind Spot Check" Output Is Unstructured and Unprocessed
- **Severity:** Minor
- **Phase:** design
- **Section:** Per-Reviewer Output Format (line 117-118), Blind Spot Check description (line 120)
- **Issue:** Each reviewer produces a "Blind Spot Check" section where they ask "what might I have missed?" The design describes this as "self-error-detection" but provides no specification for how this freeform text is used. Is it included in the synthesis? Shown to the user? Used to invoke additional reviewers? Or is it just reviewer introspection that gets written to disk and ignored?
- **Why it matters:** If blind spot checks are never surfaced to the user or acted upon, they're pure overhead (token cost, no value). If they *are* valuable, they should be a first-class output in summary.md. The design hasn't committed to either position.
- **Suggestion:** Specify whether blind spot checks are: (1) Included in summary.md under a dedicated section, (2) Used by the Synthesizer to identify coverage gaps and suggest additional reviewers, or (3) Informational only (written to individual reviewer files for eval/tuning purposes, not shown to user). Also clarify whether blind spot checks count as findings (with severity/phase) or are just freeform reflection.

### Finding 12: "Review Stage" Input Assumes Linear Pipeline but Design Claims Standalone Use
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Skill Interface (line 20), Pipeline Integration (line 236-246)
- **Issue:** The skill input contract requires "Review stage — one of: requirements, design, plan" which implies the skill knows where it sits in a linear pipeline. But the design also claims the skill can be "invoked by the orchestrator or directly by the user" and that each skill is "independently useful." If a user manually invokes `parallax:review` on a design doc, how do they know which stage to specify? The design doesn't explain.
- **Why it matters:** If the stage input is wrong (user says "design" but the artifact is actually a plan), the wrong personas activate and the review is low-quality. If the user has to guess, the skill isn't as standalone as claimed. This is a calibration gap — the requirements say skills are independently useful but the interface assumes orchestrator context.
- **Suggestion:** Either (1) Make stage detection automatic (analyze the artifact to infer whether it's a requirements doc, design doc, or plan), or (2) Provide clear user-facing guidance ("How to choose review stage: if your doc includes implementation commands, use `plan`; if it includes architecture diagrams, use `design`; if it's MoSCoW lists, use `requirements`"). Acknowledge that auto-detection is hard and may require user override.

## Blind Spot Check

What might I have missed given my focus on unstated assumptions?

1. **Prompt engineering details** — I focused on what the design assumes about inputs/outputs, but not whether the persona prompts themselves are well-crafted. The requirements doc mentions "Instruction Sharpener / Position Mapper" for prompt authoring, but the design doesn't specify how sharp these prompts need to be or how they'll be tested. This is likely covered by the eval framework (track #5), but it's a dependency I didn't flag.

2. **Contradiction resolution mechanics** — I flagged that the Synthesizer surfaces contradictions but doesn't pick winners, but I didn't challenge whether the user is equipped to resolve them. If Assumption Hunter says a finding is Critical and Feasibility Skeptic says it's Minor, what information does the user need to adjudicate? The design assumes the user has enough context from the reviewer files, but doesn't specify whether contradictions include excerpts or just pointer.

3. **Security review absence** — The requirements doc mentions "security review (sub)" as part of the design phase, but the design-stage persona list has no security-focused reviewer. Prior Art Scout might catch insecure dependencies, but no one is checking for auth bypass, injection risks, or secrets management. This might be intentional (security review is a separate skill), but it's an assumption the design doesn't state.

4. **Model-specific behavior** — The design assumes all reviewers produce similar-quality output, but CLAUDE.md mentions model tiering (Haiku/Sonnet/Opus) and Codex portability. If different personas use different models (e.g., Haiku for simple personas, Opus for deep analysis), does that introduce bias in severity ratings? The design hasn't acknowledged this as a variable.
