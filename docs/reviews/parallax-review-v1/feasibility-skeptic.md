# Feasibility Skeptic Review

## Complexity Assessment
**Overall complexity:** High  
**Riskiest components:**  
1. Parallel subagent orchestration with finding synthesis  
2. Interactive finding processing workflow (accept/reject/discuss state machine)  
3. Prompt engineering for 9 distinct reviewer personas with non-overlapping focus  

**Simplification opportunities:**  
- Start with 3 reviewers instead of 6 (Assumption Hunter, Requirement Auditor, Feasibility Skeptic covers 80% of value)  
- Cut "discuss" mode from MVP — accept/reject is sufficient for validation  
- Sequential execution instead of parallel (slower but simpler state management)  

---

## Critical Findings

### Finding 1: Prompt Caching Architecture Creates a Painful Tradeoff
- **Severity:** Critical
- **Phase:** design
- **Section:** Prompt structure for caching (problem statement lines 96-97, design doc implied)
- **Issue:** The design commits to prompt caching as "an architectural convention, not a feature" with 90% cost reduction, but reviewer personas need continuous tuning during prototyping. Every prompt change invalidates the cache prefix, making the optimization counterproductive during the exact phase where you need fast iteration. You're architecting for production cost optimization before you know if the reviewers work.
- **Why it matters:** You'll either (a) lock prompts prematurely to preserve cache hits, degrading review quality, or (b) iterate prompts freely and burn through your budget on cache misses during the 10-20 prototype cycles needed to tune 6-9 personas. The problem statement acknowledges this (customization-04) but the design doesn't resolve the tension.
- **Suggestion:** Defer prompt caching architecture until reviewer prompts stabilize (post-MVP). Use a versioned prompt structure where the cache-friendly prefix is separate from the tunable instructions, but don't optimize for cache hits until eval data shows prompts converging. Budget for full-price API calls during prototyping ($200-400/mo allows ~20-40 full reviews with 6 Sonnet agents).

### Finding 2: "Discuss" Mode is a State Management Nightmare
- **Severity:** Critical
- **Phase:** design
- **Section:** Step 5: Process Findings (lines 220-226)
- **Issue:** The design describes "discuss" as "a first-class interaction: the user can explore a finding in depth, ask questions, challenge the reviewer's reasoning" while "the skill maintains its position in the finding queue and resumes after the discussion resolves." This requires: (1) suspending iteration through findings, (2) context-switching to conversational mode with a specific reviewer persona, (3) maintaining conversation history, (4) detecting when the discussion is resolved, (5) resuming iteration from the exact finding, (6) preserving accept/reject/discuss outcomes across all findings. This is a complex stateful interaction pattern that doesn't map cleanly to Claude Code's skill execution model.
- **Why it matters:** You're building a modal UI (finding iteration mode vs discussion mode) inside a CLI skill. The state transitions are ambiguous: how does the system know the discussion is over? What if the user asks a question unrelated to the current finding? What if they want to reference a different finding during discussion? This will consume 30-50% of implementation time for a feature that's not testable with your existing test cases (the Second Brain session had findings but no discussion transcripts).
- **Suggestion:** MVP should be accept/reject only. "Discuss" becomes: user rejects a finding with a note, that note becomes input to the next review cycle (treating it as calibration data for the reviewer). This is testable, doesn't require modal state management, and delivers the same outcome (user challenges finding, reviewer refines on next pass). Add true discussion mode in v2 if eval data shows rejected findings aren't being addressed.

### Finding 3: No Clear Failure Mode for Synthesizer Contradictions
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis responsibilities (lines 123-136) and verdict logic (lines 147-153)
- **Issue:** The synthesizer is "purely editorial" and surfaces contradictions without resolving them, but the verdict logic requires a binary decision (proceed/revise/escalate). What happens when Assumption Hunter flags something as Critical (design-breaking) and Feasibility Skeptic flags the same issue as Minor (easily mitigated)? The design says "report the range" and "user resolves," but the verdict must trigger before the user processes findings (Step 4 presents the verdict before Step 5 processes findings one-by-one). Who decides if contradictory severity ratings trigger "revise"?
- **Why it matters:** If the synthesizer picks the highest severity (conservative), you'll get false escalations that waste user time. If it picks the lowest (optimistic), you'll miss real issues. If it defers to the user, the verdict is meaningless because the user hasn't reviewed findings yet. The UX flow is verdict → process findings, but contradictions can't be resolved until findings are processed.
- **Suggestion:** Contradictions trigger a mandatory "discuss" step before verdict is computed, OR contradictory findings are always bucketed as "Important" (middle ground) and flagged for user attention first. Alternatively, reorder UX: present findings → user processes → synthesizer computes verdict based on accepted findings. This inverts the flow but makes the verdict meaningful.

---

## Important Findings

### Finding 4: Six Parallel Sonnet Agents is $0.50-1.00 Per Review
- **Severity:** Important
- **Phase:** design
- **Section:** Prototype scope (6 reviewers), cost strategy (Sonnet for review agents)
- **Issue:** Rough math: 6 reviewers × (3000 token system prompt + 2000 token design doc + 1500 token requirements) × Sonnet input pricing + (6 × 1000 token output average) × Sonnet output pricing ≈ $0.30-0.50 input + $0.20-0.50 output = $0.50-1.00 per review cycle. Tuning 6 personas across 20 iterations = $10-20. One test case with 3 review cycles = $1.50-3.00. Your prototype budget supports this, but you're one scope expansion away from pain (adding plan stage with 5 reviewers, running reviews on 4 test cases, etc.).
- **Why it matters:** The design assumes Sonnet for all reviewers but doesn't test whether Haiku is sufficient for any personas. Requirement Auditor (mechanical checklist matching) and Edge Case Prober (boundary condition enumeration) might work fine on Haiku at 1/10th the cost. You're budgeting for worst-case when you could be testing model tiering empirically.
- **Suggestion:** Run the first prototype review with all-Sonnet (validates quality bar), then run an ablation test with Haiku for 2-3 personas and compare finding quality. If Haiku catches 80%+ of the same issues for mechanical reviewers, model tiering drops per-review cost by 30-40%. This is low-risk empirical validation (single test case, manual comparison) that pays for itself in 10-20 review cycles.

### Finding 5: Interactive Finding Processing Doesn't Scale to 40+ Findings
- **Severity:** Important
- **Phase:** design
- **Section:** Test case validation (Second Brain Design, 40+ findings), Step 5: Process Findings (one-at-a-time interaction)
- **Issue:** The Second Brain test case produced 40+ findings across 3 reviews. Processing findings one-at-a-time in an interactive CLI workflow means 40+ prompts of "Finding 23: [title]. Accept, reject, or discuss?" This is a 10-15 minute manual process for a single review cycle. If the design triggers "revise" and re-review, you're processing findings again (some duplicates, some new). The design acknowledges this with "critical-first" mode, but that just defers the problem.
- **Why it matters:** The UX assumes review is a checkpoint, but 40-finding reviews turn it into a slog. Users will start auto-accepting to get through the queue, defeating the purpose of adversarial review. The design doesn't provide batch operations (accept all Minor, reject all from Prior Art Scout, etc.) or filtering (show me only feasibility concerns).
- **Suggestion:** Add bulk operations to the finding processor: "accept all Minor," "accept all from [persona]," "reject findings in [section]," "show only Critical/Important." Still supports one-at-a-time for careful review, but gives the user control over granularity. This is a 10-line enhancement to the processing loop that makes 40-finding reviews tractable.

### Finding 6: Git Tracking of Review Iterations is Clever But Fragile
- **Severity:** Important
- **Phase:** design
- **Section:** Output artifacts (lines 32-45), iteration tracking (CLAUDE.md)
- **Issue:** The design commits every review cycle to git ("iteration history tracked by git, diffs show what changed"). This is elegant when it works: `git diff HEAD~1 docs/reviews/second-brain/assumption-hunter.md` shows exactly what the Assumption Hunter found differently in iteration 2. But it assumes: (1) the user runs reviews from a clean working directory (no uncommitted changes), (2) reviews don't conflict with concurrent work on other files, (3) the user wants review iterations in their commit history (vs a separate branch or scratch directory), (4) the review folder structure is stable across iterations (renaming a persona breaks diffs).
- **Why it matters:** If the user is mid-feature-development and runs a design review, the review artifacts get mixed into their working changes. Auto-committing on their behalf is invasive (what if they didn't want that commit message?). Not auto-committing means manually reminding them to commit after every review, breaking the "automated" flow. This is a git workflow assumption that may not match real usage.
- **Suggestion:** Reviews write to a timestamped folder (`docs/reviews/<topic>/<timestamp>/`) and the skill offers to commit at the end ("Review complete. Commit these artifacts? [y/n]"). User controls when/if it enters git history. Diffs are still possible via folder comparison. Alternatively, use a dedicated review branch (auto-created, never merged) to isolate review commits from main work.

### Finding 7: Synthesizer "Purely Editorial" Conflicts With Phase Classification
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis responsibilities (lines 123-136), finding phase classification (lines 138-146)
- **Issue:** The synthesizer is "purely editorial — zero judgment on content or severity" but must classify findings by phase (survey gap / calibrate gap / design flaw / plan concern). Phase classification is inherently judgmental: deciding whether "missing error handling" is a design flaw (the design should have specified it) vs a plan concern (the design is fine, the plan should implement it) requires understanding the boundary between phases. Different reviewers may flag the same issue with different phase tags.
- **Why it matters:** If the synthesizer can't override phase classifications, contradictory phase tags make the verdict logic ambiguous (is it escalate or revise?). If the synthesizer can override phase tags, it's no longer "purely editorial." The role definition conflicts with the responsibility.
- **Suggestion:** Either (a) synthesizer is judgmental on phase classification (remove "purely editorial" constraint), or (b) reviewers don't tag phase, and phase classification is a separate agent/step that runs after synthesis with explicit reasoning. Option (a) is simpler. Option (b) is more auditable but adds another agent to the pipeline.

---

## Minor Findings

### Finding 8: Blind Spot Check is Unvalidated Fluff
- **Severity:** Minor
- **Phase:** design
- **Section:** Per-reviewer output format (lines 116-118)
- **Issue:** Each reviewer ends with "What might I have missed given my assigned focus?" This is metacognitive self-reflection, which sounds good but is untestable. How do you know if a blind spot check is useful? If a reviewer says "I might have missed performance concerns because I focused on security," did that help you catch a performance issue, or is it just hedging?
- **Why it matters:** The design doc itself flags this as an open question ("whether blind spot checks produce actionable findings or noise"). You're building it into the output format before you know if it works. If it turns out to be noise, you've trained 6-9 personas to produce a useless section.
- **Suggestion:** Make blind spot checks optional in the output format and run A/B tests during eval: same reviewers with/without blind spot prompts. Compare finding coverage. If reviewers with blind spot prompts don't catch meaningfully more issues, cut it. If they do, keep it. Don't commit to it in the prototype.

### Finding 9: No Handling for Reviewer Agent Failures
- **Severity:** Minor
- **Phase:** plan
- **Section:** Step 2: Dispatch (parallel agent execution)
- **Issue:** The design dispatches 6 reviewers in parallel and synthesizes their output. What happens if one agent times out, hits a rate limit, or returns malformed output? Does the synthesis wait indefinitely? Does it proceed with 5/6 reviewers? Does it retry the failed agent?
- **Why it matters:** Parallel execution introduces partial failure modes. You're optimizing for the happy path (all agents succeed) without specifying degraded-mode behavior. During prototyping this will manifest as "the skill hangs for 2 minutes then fails" and you'll debug it reactively.
- **Suggestion:** Document the failure policy: timeout per agent (60s?), retry once on failure, synthesize with partial results if 4/6 agents succeed (note missing perspectives in summary). This is 5 lines of policy that prevents debugging sessions later.

### Finding 10: Requirements Stage May Not Need 4-5 Personas
- **Severity:** Minor
- **Phase:** design
- **Section:** Requirements stage persona matrix (lines 61-69)
- **Issue:** The design allocates 4-5 reviewers to requirements stage (Assumption Hunter, Requirement Auditor, First Principles Challenger, Prior Art Scout, Product Strategist). Requirements docs are typically shorter and less complex than design docs. Running 5 adversarial reviewers on a 1-page MoSCoW prioritization feels like overkill — you'll get redundant findings ("is this really Must-have?" flagged by 3 different personas).
- **Why it matters:** Over-reviewing requirements burns budget and time without proportional quality gain. The problem statement emphasizes outcome-focused requirements, but 5 reviewers doesn't make requirements more outcome-focused, it makes processing slower.
- **Suggestion:** Start requirements stage with 3 reviewers (Requirement Auditor, Product Strategist, First Principles Challenger). If eval data shows you're missing critical requirement gaps, add more. You can always scale up, but you can't get back time spent processing redundant findings.

---

## Blind Spot Check

**What I might have missed:**
- **User experience assumptions:** I focused on implementation complexity but didn't challenge whether the CLI skill interaction model is the right fit for this workflow. A web UI or even a batch mode ("review this, email me the summary") might be more appropriate for 40-finding reviews.
- **Integration complexity:** I didn't deeply probe how this skill composes with existing superpowers skills (brainstorming, writing-plans). If those skills output artifacts in a different format or location, integration is harder than the design suggests.
- **Testing strategy:** I flagged cost and complexity risks but didn't question whether the Second Brain test case is representative. If that test case is an outlier (40 findings is unusually high), the design may be over-optimized for an edge case.
- **Alternatives to parallel agents:** I accepted the parallel persona approach as given. A sequential "pass the baton" model (one reviewer critiques, next reviewer critiques the critique) might catch deeper issues with simpler orchestration.
