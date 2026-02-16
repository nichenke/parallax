# Assumption Hunter Review

## Findings

### Finding 1: Auto-Fix Step Assumes It Can Correctly Identify "Trivial" Changes
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Step 4: Auto-Fix (synthesis section)
- **Issue:** Design specifies auto-fix classifies findings as "typos in markdown, missing file extensions, broken internal links" and applies them automatically. This assumes the system can reliably distinguish trivial mechanical fixes from semantic changes. Example: "broken internal link" could mean (a) wrong file extension (trivial) or (b) wrong target document entirely (semantic). "Typo" could mean spelling error (trivial) or variable name that should be intentionally different (semantic). The design provides no validation mechanism beyond "conservative criteria" which is undefined.
- **Why it matters:** Auto-fixes modify source files and commit changes automatically. A misclassified "trivial" fix that changes meaning breaks the design. Git blame shows auto-fix commit obscuring who made the semantic decision. Worse: if auto-fix runs before human review (as specified in Step 4), user cannot reject bad auto-fixes—they're already applied and committed.
- **Suggestion:** Add validation requirements to auto-fix specification: (1) Define "conservative" with concrete examples and exclusion criteria, (2) Require that auto-fixes are presented as diffs for user approval before application, (3) Add rollback mechanism (separate git commit enables revert, but user must be told how), (4) Consider deferring all auto-fix to post-human-processing—user accepts findings first, then auto-fixable accepted findings are applied as batch. This prevents auto-fixing findings the user would reject.

### Finding 2: Git-Based Iteration Tracking Assumes Design Doc Lives in Git
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Output Artifacts ("Iteration history tracked by git"), Cross-Iteration Finding Tracking
- **Issue:** Design states "Iteration history tracked by git (each re-review is a new commit, diffs show what changed)" and "git diff integration: highlight changed sections to reviewers." This assumes the design document being reviewed is git-tracked. If user reviews a design doc that lives outside the repository (e.g., Google Doc exported to markdown, Confluence page converted to local file, design doc from different repo), git diff fails. No fallback specified.
- **Why it matters:** Requirements doc states this should be "applicable to work contexts." Many teams use Confluence, Notion, or Google Docs for design documents, not git-tracked markdown. If parallax:review only works for git-tracked docs, it excludes significant use cases. Additionally, cross-iteration tracking depends on git diff to detect changed sections—if diff isn't available, reviewers lose focus prioritization.
- **Suggestion:** Add input validation that checks whether design doc is git-tracked. If not: (1) Warn user that cross-iteration diff won't be available, (2) Fall back to file timestamp comparison or manual change notes from user, (3) Document git requirement as constraint, or (4) Implement text-based diff (compare iteration 1 file to iteration 2 file directly) as fallback.

### Finding 3: Stable Finding IDs Assume Section Headings Don't Change
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Cross-Iteration Finding Tracking ("Stable hash derived from section + issue content")
- **Issue:** Design specifies finding IDs as "stable hash derived from section + issue content." This assumes design doc section headings remain stable across iterations. If designer refactors "UX Flow" section into "User Workflow" and "State Management" between iterations, all findings anchored to "UX Flow" become orphaned—system treats them as resolved when they're actually just relocated. Hash-based IDs break when input text changes, even if semantic content is unchanged.
- **Why it matters:** Section refactoring is normal during design iteration. Improving document structure shouldn't invalidate finding tracking. Prior review (iteration 2) flagged this as Finding 7 (Critical) with suggestion for semantic matching, but design still specifies text hashing. If implemented as designed, cross-iteration tracking will produce false negatives (findings marked "resolved" when section renamed) and false positives (findings marked "new" when actually rephrased).
- **Suggestion:** Replace text-based hashing with semantic anchoring or LLM-based matching. Options: (1) Store section heading + offset position, fuzzy-match on re-review if heading changed, (2) Use LLM to semantically match new findings to prior findings ("Is this the same issue?"), (3) Hybrid: hash as first pass, LLM disambiguation when hash misses, (4) Allow manual finding ID assignment by reviewers for critical findings that need guaranteed cross-iteration tracking.

### Finding 4: Reviewer Prompt Context Assumes Single Iteration Per Session
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Reviewer Prompt Architecture ("Variable suffix: prior review summary if re-review")
- **Issue:** Design specifies reviewers receive "prior review summary (if re-review)" as context. This assumes re-review happens after user processes findings from prior iteration and updates design doc. If user runs review, sees findings, immediately revises design, and re-runs review within same session (common workflow during rapid iteration), "prior review summary" is the review from 5 minutes ago. Reviewer context grows with each iteration in a single session. After 3 rapid iterations, reviewers receive summaries from iterations 1, 2, and 3, consuming thousands of tokens for diminishing value.
- **Why it matters:** Rapid iteration is a common workflow ("fix Critical findings immediately, re-review before moving on"). Design doesn't specify how prior context is bounded when multiple iterations happen in quick succession. Token costs scale linearly with iteration count. After 5 iterations in one session, review becomes prohibitively expensive or exceeds context limits.
- **Suggestion:** Add prior context pruning rules to prompt architecture: (1) Include only most recent N iterations (e.g., 2), (2) Summarize older iterations rather than include verbatim, (3) For rapid iteration, include only findings from most recent run that remain unresolved, (4) Track token budget and warn user if prior context exceeds threshold.

### Finding 5: Async-First Architecture Assumes File System as Single Source of Truth
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** UX Flow (async-first), Finding 2 disposition from iteration 2
- **Issue:** Design specifies "review always writes artifacts to disk" as baseline, with interactive processing as "convenience layer." This assumes all state lives in files under `docs/reviews/<topic>/`. If user runs review on machine A, processes findings on machine B (different clone of repo), or collaborates with teammate who processes findings from their checkout, state diverges. File-based state requires that all participants operate on same filesystem or rigorously sync via git. No synchronization mechanism specified.
- **Why it matters:** Requirements emphasize "applicable to work contexts" and CLAUDE.md notes "this repo may be worked on from multiple machines." File-based state doesn't handle distributed workflows without additional tooling (git push/pull between every operation). If two users process findings in parallel, last write wins—earlier dispositions are silently lost.
- **Suggestion:** Either (1) Document single-user, single-machine constraint explicitly as MVP limitation, (2) Add conflict detection (check if summary.md has uncommitted changes before allowing processing), (3) Require git commit after each disposition batch, (4) Evaluate external state management (LangSmith annotation queues, as noted in iteration 2 Finding 44).

### Finding 6: Phase Classification Routing Assumes Single Phase Owns Each Finding
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Verdict Logic, Finding Phase Classification
- **Issue:** Verdict logic routes findings based on primary phase: survey/calibrate gap → escalate, design flaw → revise. This assumes each finding has a clear owner phase. Real design failures are multi-causal: missing research (survey) creates unstated assumption (calibrate) enabling flawed design (design). Iteration 2 Finding 6 flagged this (Critical severity), disposition accepted primary+contributing classification, but design still shows single-phase routing. If a finding is "design flaw (primary) caused by calibrate gap (contributing)," routing to design revision doesn't fix the upstream calibrate issue.
- **Why it matters:** Systemic failures require systemic fixes. If 30% of design findings trace to same calibrate gap (e.g., "missing failure mode requirements"), fixing each design finding individually is inefficient. Design acknowledges multi-causal reality ("When >30% of findings share a contributing phase, synthesizer flags systemic issue") but verdict logic doesn't use this for routing—it's informational only.
- **Suggestion:** Update verdict logic to treat contributing phases as escalation triggers. If any finding has calibrate/survey as contributing phase AND that phase appears in >20% of findings, verdict cannot be "proceed"—must be "escalate with systemic issue noted." User must acknowledge upstream gap before addressing downstream symptoms.

### Finding 7: Reviewer Tool Access Assumes Read Operations Are Side-Effect-Free
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Reviewer Capabilities (new section in iteration 3), iteration 2 Finding 33
- **Issue:** Design specifies reviewers have "read-only" file access and specific tools (git, gh, curl for Prior Art Scout). This assumes read operations have no side effects. But some "read" operations create state: `git status` is read-only, but running git commands creates `.git` lock files. `curl` fetching a URL may trigger server-side logging or rate limits. `gh api` calls count against API quotas. If 6 reviewers all run `gh search repos X`, that's 6 API calls per review—potentially hitting GitHub rate limits for unauthenticated requests (60/hour).
- **Why it matters:** Tools with quotas or side effects need coordination. If multiple reviewers independently query same external resource, they waste quota. If review runs in CI/CD (future automation), read operations that modify filesystem state can cause permission errors or lock conflicts.
- **Suggestion:** Add tool access constraints to design: (1) Specify which tools are quota-limited (gh, curl with external APIs), (2) Implement result caching—if Prior Art Scout searches GitHub for "design review tools," cache result for other reviewers, (3) Document side-effect assumptions (git commands may create temp files, external API calls count against quotas), (4) For CI/CD: ensure reviewers run with appropriate permissions and avoid lock file conflicts.

### Finding 8: Critical-First Mode Assumes Critical Findings Are Independent
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Step 5: Present Summary (Critical-first mode)
- **Issue:** Design offers "Critical-first" processing mode: "Address Critical findings only. Send source material back for rethink. Remaining findings processed in next pass." This assumes Critical findings can be processed independently without context from Important/Minor findings. But findings often have dependency chains: Critical finding "No authentication specified" depends on Important finding "API endpoints exposed externally." Processing Critical finding without seeing Important finding may lead to wrong fix (add auth when correct fix is "make internal-only").
- **Why it matters:** Out-of-context fixes waste time. User processes Critical finding, makes design decision, re-reviews, discovers Important finding that contradicts the decision. Must backtrack. Critical-first mode optimizes for iteration speed but may reduce fix quality by hiding necessary context.
- **Suggestion:** Add dependency detection to Critical-first workflow: (1) If Important/Minor findings relate to same design section as Critical finding, present them together, (2) Add "view related findings" option during Critical processing, (3) Synthesizer groups findings by affected subsystem/section, processes clusters together regardless of severity, (4) Document tradeoff: Critical-first is fast but may miss context, all-findings is slower but more comprehensive.

### Finding 9: Synthesizer Deduplication Assumes "Same Issue" Is Objectively Determinable
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Synthesis (deduplication responsibility)
- **Issue:** Synthesizer must "deduplicate—group findings flagged by multiple reviewers into single entries." Design doesn't specify how "same issue" is determined. This is a subjective judgment task. Example: Assumption Hunter flags "assumes users have admin rights" (calibrate gap), Edge Case Prober flags "no permission check in delete operation" (design flaw). Are these duplicates (both about permissions) or distinct (one is missing requirement, other is missing implementation)?
- **Why it matters:** Aggressive deduplication ("both about permissions → merge") loses important distinctions (requirement-level vs implementation-level). Conservative deduplication ("different wording → separate") floods user with near-duplicates. Iteration 2 Finding 40 flagged this but design still provides no heuristics—just responsibility assignment.
- **Suggestion:** Define deduplication criteria explicitly: (1) Findings are duplicates only if same section AND same root cause AND same suggested fix, (2) Findings about same topic but different phases are NOT duplicates—preserve as related but distinct, (3) Synthesizer groups related findings under common heading with cross-references ("Related: Finding 3 addresses requirement gap, Finding 7 addresses implementation") but counts them separately, (4) Provide examples of duplicate vs related in synthesizer prompt.

### Finding 10: Prompt Caching Assumes Stable Prefix Doesn't Change Between Iterations
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Reviewer Prompt Architecture (stable prefix for caching)
- **Issue:** Design structures prompts as "stable cacheable prefix (persona + methodology + output format + voice guidelines) + variable suffix (design artifact + requirements + prior summary)." This assumes stable prefix doesn't change across review iterations. But if user rejects findings as false positives and adds calibration rules to reviewer prompts ("Assumption Hunter: don't flag X as assumption, it's explicitly stated in requirements"), that modifies the stable prefix. Cache invalidates. Next review pays full input token cost.
- **Why it matters:** Reviewer calibration (learning loop from iteration 2 Finding 29 disposition, Compound Engineering pattern from iteration 2 Finding 46) requires modifying reviewer prompts based on false positive/negative feedback. Every calibration change invalidates cache. Cost optimization via caching conflicts with quality improvement via calibration. Design acknowledges "prompt changes to stable prefix invalidate cache" but doesn't address how to balance these competing needs.
- **Suggestion:** Separate calibration rules from stable prefix. Structure prompts as: (1) Stable prefix (persona, methodology, format—never changes), (2) Calibration rules (versioned, changes based on feedback), (3) Variable suffix (artifact being reviewed). Cache stable prefix. Include calibration rules in non-cached middle section. Track calibration rule version separately from prompt version. Cost increases linearly with calibration rule size, not prompt size.

### Finding 11: Verdict "Proceed" Assumes Accepted Findings Will Be Addressed
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Verdict Logic, Step 6: Wrap Up
- **Issue:** Verdict logic states "Only Important/Minor → proceed with noted improvements." This assumes user will actually address accepted findings before moving to next phase. But "proceed" means "move forward"—skill exits, user continues to implementation. No mechanism tracks whether accepted findings were addressed or just noted and forgotten. If user accepts 15 Important findings, gets "proceed" verdict, and moves to execution without fixing them, review provided no value.
- **Why it matters:** "Proceed with noted improvements" creates false sense of completeness. User thinks "review passed" when actually "review passed conditionally on fixing these 15 things." If improvements aren't tracked, they become technical debt. Design has no follow-up mechanism.
- **Suggestion:** Clarify verdict semantics: (1) "Proceed" means "design is acceptable as-is, improvements are optional," (2) Add "proceed-with-conditions" verdict for "must address these findings before implementation," (3) Track accepted findings as open work items (link to issue tracker, or create tasks file), (4) On next phase review (plan stage), check whether design-stage accepted findings were addressed.

### Finding 12: Topic Label Validation Assumes Alphanumeric Is Safe
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Skill Interface (topic label validation)
- **Issue:** Design specifies topic labels "validated against safe character set (alphanumeric, hyphens, underscores only)." This assumes these characters are safe for all filesystems and git branch names. Hyphens at start of filename on some systems are interpreted as command flags. Underscore-only filenames may be hidden. Very long alphanumeric strings (user provides 500-character topic) create filesystem path length issues.
- **Why it matters:** Topic label becomes folder name under `docs/reviews/<topic>/`. Edge cases: (1) topic starting with hyphen: `docs/reviews/-foo/` may cause issues with tools that interpret leading hyphen as flag, (2) very long topic exceeds filesystem path limit (typically 255 chars for filename, but full path limit is OS-dependent), (3) topic that matches git special refs (e.g., "HEAD") could cause confusion.
- **Suggestion:** Strengthen validation rules: (1) Require topic starts with alphanumeric (no leading hyphen/underscore), (2) Limit length (64 chars recommended, enforced maximum at 128), (3) Disallow reserved names (HEAD, master, main, refs), (4) Sanitize rather than reject—convert spaces to hyphens, lowercase, trim to length.

## Blind Spot Check

My focus on unstated assumptions means I primarily catch what the designer didn't say. What I may miss:

1. **Explicit bad decisions:** If the design states an assumption clearly but the assumption is wrong, I might not flag it—I look for *unstated* assumptions, not *incorrect stated* assumptions. Feasibility Skeptic or First Principles Challenger would catch this better.

2. **Implementation feasibility:** I identify assumptions about environment or dependencies, but whether those assumptions make implementation overly complex is outside my lens. Feasibility Skeptic covers this.

3. **Missing requirements entirely:** If the design assumes a requirement exists but the requirement was never written, I flag it as calibrate gap. But if the requirement is missing AND no one assumes it exists, I won't see it—Edge Case Prober or Requirement Auditor would catch gaps via "what's not covered?"

4. **User workflow assumptions:** I focused on technical assumptions (file system, git, tools, state management) but may have under-weighted assumptions about how users actually work (do they iterate rapidly? do they review in teams? do they context-switch mid-review?). These are assumptions about user behavior, not system behavior.

5. **Cost and performance assumptions:** I flagged quota/rate limit assumptions (Finding 7) but didn't deeply examine assumptions about cost tolerance, acceptable latency, or performance at scale. If the design assumes "6 reviewers in parallel completes in 60 seconds" but doesn't validate this, I may have missed it.

6. **Prior art and standards:** I don't focus on "are we reinventing existing solutions?" (that's Prior Art Scout's domain). I catch assumptions about whether something exists, but not whether we should build vs leverage.

The cross-reviewer synthesis should compensate for these blind spots—findings I miss should appear from other personas.
