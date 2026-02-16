# Edge Case Prober Review

## Findings

### Finding 1: No handling for reviewer agent failures
- **Severity:** Critical
- **Phase:** design
- **Section:** Step 2: Dispatch (parallel reviewer execution)
- **Issue:** The design dispatches 4-6 reviewer agents in parallel but doesn't specify what happens if one or more agents fail (API timeout, rate limit, model error, prompt refusal). A single agent failure could block the entire review or produce incomplete findings.
- **Why it matters:** In production, partial failures are common (API rate limits, transient network errors, model capacity issues). If one reviewer fails, the user sees "Running 6 reviewers in parallel..." with no result, or worse — gets an incomplete synthesis that silently excludes a critical perspective.
- **Suggestion:** Define failure handling strategy: (1) Retry failed agents with exponential backoff, (2) Mark failed agents in summary ("5/6 reviewers completed, Feasibility Skeptic timed out"), (3) Allow user to re-run individual failed reviewers without redoing successful ones, (4) Set timeout threshold and surface degraded mode explicitly.

### Finding 2: Unbounded review time with no progress indication
- **Severity:** Important
- **Phase:** design
- **Section:** Step 2: Dispatch, Step 3: Synthesize
- **Issue:** Running 6 reviewers in parallel with potentially large design docs could take minutes. User sees "Running 6 reviewers in parallel..." but no indication of progress, completion estimates, or which reviewers have finished.
- **Why it matters:** Long-running operations without progress feedback feel broken. Users may interrupt the process thinking it's stuck, wasting tokens and time. Per-reviewer time variance (Prior Art Scout may need web search, Assumption Hunter may finish in 30 seconds) means total time is unpredictable.
- **Suggestion:** Stream progress updates as reviewers complete ("Assumption Hunter: done [1/6]", "Edge Case Prober: done [2/6]"). Show elapsed time. Consider timeout per reviewer (e.g., 120 seconds max).

### Finding 3: No protection against reviewer hallucination or malformed output
- **Severity:** Important
- **Phase:** design
- **Section:** Per-Reviewer Output Format, Step 3: Synthesize
- **Issue:** The design assumes reviewers will produce well-formed markdown with the expected structure (### Finding N, severity, phase, etc.). If a reviewer produces malformed output, the synthesizer may fail to parse findings or misclassify them.
- **Why it matters:** LLMs occasionally produce off-format output (especially under pressure, with large context, or at high temperature). A single malformed finding can break synthesis, leaving the user with raw reviewer output and no consolidated summary.
- **Suggestion:** Add validation layer before synthesis: (1) Parse each reviewer output against expected schema, (2) Flag malformed findings with severity "unknown" and phase "parse-failed", (3) Include parse errors in summary for debugging, (4) Allow synthesis to proceed with partial data rather than hard fail.

### Finding 4: Synthesizer contradictions escalate to user with no resolution guidance
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis, Summary Format (Contradictions section)
- **Issue:** When reviewers disagree, the synthesizer presents both positions with "user resolves" but provides no framework for resolution. The user must decide between conflicting technical opinions without guidance on which reviewer's lens is more relevant to this specific tension.
- **Why it matters:** Contradictions are high-value findings (they surface real design tensions), but dumping them on the user without structure creates decision paralysis. Example: Feasibility Skeptic says "too complex, use SQLite," Prior Art Scout says "don't reinvent, use Postgres." Both are valid from their lenses — which wins depends on context the user may not have.
- **Suggestion:** Enhance contradiction presentation: (1) Surface the underlying tension explicitly ("tradeoff: simplicity vs leveraging existing tools"), (2) Include relevant context from design/requirements that might resolve it, (3) Suggest tie-breaking criteria ("if timeline < 1 week, favor simplicity"), (4) Allow user to request deeper analysis from both reviewers before deciding.

### Finding 5: Discuss mode has no conversation termination criteria
- **Severity:** Important
- **Phase:** design
- **Section:** Step 5: Process Findings (Discuss interaction)
- **Issue:** The design allows "full back-and-forth conversation" during Discuss mode but doesn't specify how the conversation ends. No depth limit, no token budget, no explicit "resolve" command. A single finding discussion could consume unbounded tokens or drift off-topic.
- **Why it matters:** Unconstrained conversation can become circular ("but what about...", "yes, but...") or waste tokens on tangents. Without explicit termination, the user may forget they're in Discuss mode for Finding 3 of 40 and lose track of the review workflow.
- **Suggestion:** Add discussion boundaries: (1) Max turn count per finding discussion (e.g., 5 exchanges), (2) Explicit "resolve and decide" command to exit discussion and make accept/reject choice, (3) Show context reminder ("Discussing Finding 3/40: [title]") at each turn, (4) Allow user to defer decision ("skip for now, come back later").

### Finding 6: Re-review after revisions may produce identical findings
- **Severity:** Important
- **Phase:** design
- **Section:** Step 6: Wrap Up (revise flow), Iteration Loops
- **Issue:** When verdict is "revise," the user updates the design and re-runs `parallax:review`. The reviewers have no memory of previous findings or what was changed. They may re-flag the same issues if the fix wasn't clear, or miss new issues introduced by the revision.
- **Why it matters:** Re-review waste: if the user addressed a finding but the reviewer can't tell (because the fix was subtle or in a different section), the same finding reappears, frustrating the user. Also, reviewers won't focus extra scrutiny on newly-changed sections where bugs are most likely.
- **Suggestion:** Provide iteration context to reviewers: (1) Include previous summary.md in reviewer context ("last review flagged X, check if addressed"), (2) Highlight changed sections if possible (git diff), (3) Ask reviewers to explicitly note "previously flagged, now resolved" vs "new finding" vs "still an issue", (4) Track finding IDs across iterations to auto-detect duplicates.

### Finding 7: Empty or trivial design docs may produce no findings
- **Severity:** Minor
- **Phase:** design
- **Section:** Step 2: Dispatch
- **Issue:** If the user provides a very short or incomplete design doc (e.g., "TODO: write design"), reviewers may struggle to produce meaningful findings. They might hallucinate issues, return "insufficient detail" meta-findings, or produce empty output.
- **Why it matters:** Garbage in, garbage out. Running a full 6-agent review on a stub design wastes tokens and produces confusing output. The user expects actionable findings, not "this design is too short to review."
- **Suggestion:** Add pre-flight check: (1) Validate design doc length (e.g., min 500 words or 10 headings), (2) If too short, return early with "design incomplete, minimum review threshold not met", (3) Alternatively, shift reviewers into "incompleteness audit" mode (flag missing sections rather than reviewing content).

### Finding 8: Severity ranges create ambiguity in verdict logic
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis (severity ranges), Verdict Logic
- **Issue:** The synthesizer reports severity ranges when reviewers disagree ("Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic") but the verdict logic uses "any Critical finding → revise." This creates ambiguity: is a finding with range "Critical-to-Important" treated as Critical (blocks proceed) or Important (allows proceed)?
- **Why it matters:** Inconsistent verdict logic undermines trust. If a finding is Critical to one reviewer but Important to another, and the verdict is "revise," the user doesn't know if they can negotiate it down or if it's a hard blocker. Worse, if the synthesizer picks the lower severity to avoid conservatism, real critical issues may be downgraded.
- **Suggestion:** Clarify severity range handling: (1) Use highest severity in range for verdict logic (conservative: any reviewer says Critical → treat as Critical), (2) Explicitly state rule in summary, (3) Allow user to override severity during finding processing (downgrade Critical to Important if they judge the lower severity is correct).

### Finding 9: Finding phase classification errors could route to wrong pipeline stage
- **Severity:** Critical
- **Phase:** design
- **Section:** Finding Phase Classification, Verdict Logic
- **Issue:** The synthesizer classifies findings by pipeline phase (survey gap, calibrate gap, design flaw, plan concern), but phase classification is a judgment call that could be wrong. Misclassifying a design flaw as a "calibrate gap" would escalate unnecessarily, restarting requirements when the design just needs a fix. Misclassifying a calibrate gap as a "design flaw" would attempt to patch a broken requirement instead of fixing it upstream.
- **Why it matters:** The entire value proposition of finding classification is routing errors to the phase that failed. If classification is unreliable, the system wastes time (false escalation) or produces bad designs (missed escalation). This is the core novel contribution — if it's broken, the tool has no advantage over manual review.
- **Suggestion:** Add classification confidence and validation: (1) Reviewers suggest phase in their findings (they have the most context), synthesizer reconciles disagreements, (2) Include classification reasoning in summary ("Classified as calibrate gap because requirements don't address failure mode X"), (3) Allow user to override classification during finding processing, (4) Track classification errors in eval framework to tune synthesizer prompts.

### Finding 10: No handling for design vs requirements contradiction
- **Severity:** Important
- **Phase:** design
- **Section:** Requirement Auditor persona, Input contract
- **Issue:** Requirement Auditor checks if design satisfies requirements, but the design doesn't specify what happens if the *requirements themselves* are contradictory or impossible to satisfy together. The design can't fix this — it's upstream — but the review may not surface it clearly.
- **Why it matters:** Contradictory requirements are a calibrate-phase failure, not a design-phase failure. If the requirements say "must be zero-latency" and "must run on free tier," no design can satisfy both. The reviewer should escalate immediately, but the design doesn't explicitly call this out as a distinct failure mode.
- **Suggestion:** Add explicit check: Requirement Auditor should flag requirement-level contradictions as automatic escalate (calibrate gap, severity Critical). Don't attempt design iteration — requirements need fixing first.

### Finding 11: Git commit failures could lose review artifacts
- **Severity:** Important
- **Phase:** plan
- **Section:** Step 6: Wrap Up ("All artifacts committed to git")
- **Issue:** The design assumes git commit will succeed, but git operations can fail (detached HEAD, merge conflicts, repo in bad state, disk full). If commit fails after review completes, the review artifacts exist on disk but aren't tracked, risking loss on cleanup or confusion about which review is "official."
- **Why it matters:** Review artifacts are valuable (especially after 6-agent runs consuming significant tokens). Losing them due to git failure is bad UX and data loss. Silent failure is worse — user thinks review is saved but it's not.
- **Suggestion:** Add git operation validation: (1) Check git status before review starts (warn if repo is dirty or detached), (2) After writing review artifacts, explicitly commit and check success, (3) If commit fails, warn user and explain how to manually commit from `docs/reviews/<topic>/`, (4) Consider writing artifacts even if git is unavailable (graceful degradation).

### Finding 12: Topic label collision overwrites previous reviews
- **Severity:** Minor
- **Phase:** design
- **Section:** Output Artifacts (docs/reviews/<topic>/)
- **Issue:** If the user runs `parallax:review` twice with the same topic label, the second run overwrites the first review's files in `docs/reviews/<topic>/`. The design relies on git history to track iterations, but the working directory only shows the latest review.
- **Why it matters:** If the user re-reviews with the same topic before committing the first review, the first review is lost (unless they manually saved it elsewhere). Even with git commits, navigating history to compare review N vs review N+1 is cumbersome.
- **Suggestion:** Add iteration tracking to topic folder: (1) Append timestamp or iteration number to folder name (`docs/reviews/<topic>-20260215-1/`), or (2) Use subdirectories (`docs/reviews/<topic>/iteration-1/`, `iteration-2/`), or (3) Warn user if topic folder exists and prompt to confirm overwrite.

### Finding 13: Large finding counts overwhelm interactive processing
- **Severity:** Important
- **Phase:** design
- **Section:** Step 5: Process Findings (All findings mode)
- **Issue:** The design supports processing "every finding one by one" but doesn't address scale. If a design has 40+ findings (observed in test case "Second Brain Design"), walking through all of them interactively could take 30+ minutes and cause decision fatigue.
- **Why it matters:** The test cases explicitly include a session with 40+ findings. Interactive processing of that volume is painful and error-prone (user may rush through later findings or abandon the review). The design provides "critical-first" mode to mitigate this, but it's optional — users may not know to use it.
- **Suggestion:** Add smart defaults and batching: (1) Auto-suggest critical-first mode when finding count > 15, (2) Allow bulk operations ("accept all Minor findings from Assumption Hunter"), (3) Group related findings for batch decision ("these 5 findings all say the same thing, accept all?"), (4) Support "defer" to skip findings and return later.

### Finding 14: No cost or token usage visibility during review
- **Severity:** Minor
- **Phase:** design
- **Section:** Step 2: Dispatch, Step 3: Synthesize
- **Issue:** Running 6 agents in parallel on large design docs could consume significant tokens (thousands of input tokens per reviewer, especially with prompt caching disabled on first run). The design doesn't show cost estimates before running or actual token usage after completion.
- **Why it matters:** Budget-conscious users may want to know the cost before committing to a 6-agent review, especially for large designs or when iterating multiple times. Post-run token reporting helps tune reviewer prompts (identify verbose reviewers) and validates cost assumptions.
- **Suggestion:** Add cost visibility: (1) Estimate token cost before dispatch based on design doc size and reviewer count, (2) Report actual token usage and cost per reviewer in summary, (3) Track cumulative cost across iterations for the same topic, (4) Warn if estimated cost exceeds threshold (e.g., $1+ for a single review).

### Finding 15: Blind spot checks may duplicate findings or add noise
- **Severity:** Minor
- **Phase:** design
- **Section:** Per-Reviewer Output Format (Blind Spot Check)
- **Issue:** Each reviewer ends with a "Blind Spot Check" where they explicitly ask "what might I have missed?" This could produce duplicate findings (reviewer flags X in Findings, then flags "I might have missed X" in blind spot check), meta-findings ("I'm not a security expert so I might have missed security issues" — but there's a separate security reviewer), or noise ("I might have missed performance concerns" without actionable detail).
- **Why it matters:** The blind spot check is self-error-detection, which is valuable in theory. In practice, it may just produce hedged non-findings that clutter the summary or confuse the synthesizer. The design says this is an "empirical question for the eval framework" but doesn't specify fallback if it's noise.
- **Suggestion:** Test blind spot checks empirically, with clear removal criteria: (1) If blind spot checks produce <10% novel findings across 10 test reviews, remove them, (2) Alternatively, move blind spot checks to a separate optional section (not mixed with findings), (3) Train synthesizer to ignore meta-findings ("I might have missed X") and only surface actionable blind spot findings.

## Blind Spot Check

**What might I have missed given my focus on edge cases and failure modes?**

1. **Happy path usability issues:** I focused on what breaks, not on whether the happy path is intuitive or efficient. The interactive finding processing may have UX friction even when everything works (e.g., no undo for accept/reject decisions, no finding search/filter, no summary export).

2. **Persona prompt engineering quality:** I reviewed the design structure but didn't deeply analyze whether the reviewer personas will actually produce diverse, high-quality findings. Prompt quality is "the product" per the problem statement — if persona prompts are weak, the entire system produces garbage. This is a calibrate/plan concern (requirements state persona engineering matters, plan should validate prompts).

3. **Integration with superpowers skills:** The design mentions leveraging `dispatching-parallel-agents` from superpowers but doesn't specify the integration boundary. If superpowers APIs change or have undocumented constraints, the integration could break in unexpected ways. This is a feasibility concern (build vs leverage tradeoff).

4. **Synthesizer computational limits:** I flagged reviewer failures but didn't consider synthesizer failure modes. If the synthesizer receives 40 findings across 6 reviewers (240 items to consolidate), it may hit context limits, produce incomplete deduplication, or timeout. This is an edge case within synthesis itself.

5. **Eval framework dependency:** Several findings suggest "track this in eval framework" or "tune via eval," but the eval framework doesn't exist yet (it's a future skill). The design has no fallback if eval-driven tuning isn't ready when parallax:review ships. This is a sequencing/dependency risk.
