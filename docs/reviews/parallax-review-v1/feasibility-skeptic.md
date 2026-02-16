# Feasibility Skeptic Review

## Changes from Prior Review

This is a re-review of the same design document after 8 commits of implementation and prompt iteration work. Prior review identified 41 findings (8 Critical, 22 Important, 11 Minor). Key areas I flagged:

**Previously flagged, now resolved:**
- Finding 1 (Parallel agent failure handling) — partially addressed by implementation experience, though formal retry/timeout strategy still undefined
- Finding 6 ("Discuss" mode complexity) — resolved by cutting from MVP, replaced with reject-with-note pattern
- Finding 8 (Verdict logic with severity ranges) — resolved by conservative highest-severity rule
- Finding 11 (Cost budget/token limits) — addressed via JSONL logging for empirical data collection
- Finding 13 (Synthesizer role contradiction) — resolved by honest role definition (judgment-exercising, not "purely editorial")
- Finding 19 (Prompt caching iteration tradeoff) — acknowledged and deferred to post-stabilization

**Still open issues:**
- Finding 4 (Auto-fix requirement missing) — no implementation added
- Finding 5 (Cross-iteration finding tracking) — no stable ID system implemented
- Finding 14 (Large finding count UX) — JSONL helps but bulk operations not yet built
- Finding 30 (Inspect AI as orchestration substrate) — evaluation deferred

**New findings in this review:**
All findings below are new — they emerged from examining the design with fresh eyes after seeing implementation reality.

## Complexity Assessment

**Overall complexity:** Medium-High

This design is buildable but more complex than it appears. The surface simplicity ("dispatch 6 agents, consolidate findings") hides state management challenges, error handling gaps, and UX coordination costs.

**Riskiest components:**
1. **Interactive finding processing state machine** — Even with "discuss" mode cut, managing accept/reject/defer across 20-40 findings with resume capability is complex CLI state management. One interruption (user hits Ctrl-C at finding 23) requires careful state persistence.
2. **Synthesizer judgment reliability** — Deduplication and phase classification require semantic understanding that may be inconsistent across review runs. Misclassification of a single Critical finding (design flaw vs calibrate gap) triggers wrong workflow (patch vs escalate).
3. **Review-to-review consistency** — Without stable finding IDs or cross-iteration context, re-reviews become repetitive human work. Reviewers have no memory, users must manually track "did we fix that thing?"

**Simplification opportunities:**
1. **Cut interactive processing entirely** — All reviews write to disk. User processes findings with external tools (text editor, jq). Skill becomes pure generation, zero state management. Add interactive wrapper later if needed.
2. **Single-phase prototype** — Build only the review execution + file output. Defer verdict logic, finding classification, and interactive processing until you have 5-10 review runs to validate the data model.
3. **Hardcode 3 core reviewers** — Assumption Hunter, Requirement Auditor, Feasibility Skeptic. This covers 70% of value (requirements coverage, assumption validation, complexity check) at 50% cost. Add specialized reviewers empirically based on missed findings.

## Findings

### Finding 1: Design vs Implementation Reality Gap
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Entire design document
- **Issue:** The design document describes a system that was already implemented (11 commits on feature/parallax-review branch). This review is examining a design artifact that may not match what was actually built. Standard practice: design review happens before implementation, not after. The test case (smoke test against own design doc) validates the orchestration works but doesn't validate that the implementation matches this design spec.
- **Why it matters:** Design documents written post-implementation are rationalizations, not blueprints. They tend to gloss over implementation complexities ("reviewers run in parallel" — how? with what error handling? what happens when one hangs?). Without seeing the actual implementation code, this review may be validating an idealized description rather than buildable reality. If the implementation diverged from this design during development, findings here are academic.
- **Suggestion:** Include implementation artifacts (code snippets, actual agent prompts, error handling logic) in design reviews when the design is written after the fact. Better: run design review before implementation, use findings to improve the design, then implement. Alternative: treat this as a "design extraction" doc (documenting what was built) and review it for completeness/accuracy rather than feasibility.
- **Iteration status:** New

### Finding 2: JSONL Output Format Missing from Design
- **Severity:** Critical
- **Phase:** design (primary), plan (contributing)
- **Section:** Output Artifacts, Per-Reviewer Output Format, Summary Format
- **Issue:** Memory.md states "JSONL as canonical output format — decided but not yet implemented. Current markdown works for MVP." The design document specifies only markdown output format with no mention of JSONL structure, schema, or migration path. Disposition notes reference JSONL enabling features (Finding 14: "JSONL format enables this naturally — jq filters by severity/persona/phase"), but the design has zero specification for what that looks like.
- **Why it matters:** JSONL vs markdown is not a trivial format change — it affects how findings are identified (stable IDs), how dispositions are tracked (structured fields vs prose), how tools consume review output (jq vs grep), and whether reviews are machine-processable. This is the largest structural decision not documented in the design. If JSONL is the decided format, the markdown output format section is describing throwaway scaffolding, not the actual system. Implementing markdown carefully is wasted effort.
- **Suggestion:** Either (1) add JSONL schema specification to design (finding format, summary format, disposition tracking), or (2) acknowledge markdown is MVP and JSONL is v2, specifying migration path (parsers that convert markdown findings to JSONL, or dual output during transition). Clarify whether "markdown works for MVP" means "markdown is sufficient for prototype testing" (acceptable) or "we'll keep markdown indefinitely" (conflicts with JSONL decision).
- **Iteration status:** New

### Finding 3: No "Minimum Viable Reviewer Set" Validation
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Reviewer Personas (6 design-stage personas)
- **Issue:** Design specifies 6 reviewers for design stage but provides no evidence that all 6 are necessary or that this set is sufficient. Prior Art Scout and First Principles Challenger have significant overlap (both question whether you're solving the right problem / reinventing existing solutions). Edge Case Prober and Feasibility Skeptic both examine "what could go wrong" (one from input boundary perspective, one from implementation complexity perspective). No analysis of coverage overlap or diminishing returns per additional reviewer.
- **Why it matters:** Each reviewer adds cost (API calls, synthesis complexity, user processing time) and coordination overhead (deduplication, contradiction resolution). If 3 reviewers catch 80% of findings, running 6 is low ROI. Conversely, if critical gaps exist (security review completely missing from design stage), 6 may be insufficient. Problem statement acknowledges this is empirical ("optimal number is eval question") but doesn't specify how you'd validate minimum viable set during prototyping.
- **Suggestion:** Run coverage analysis during first 3-5 review cycles. For each finding, tag which reviewer(s) flagged it. Identify: (1) reviewers that consistently flag unique findings (high value, keep), (2) reviewer pairs with >50% overlap (consolidate or choose one), (3) finding categories no reviewer consistently catches (missing persona). Start with 3 core reviewers (Assumption Hunter, Requirement Auditor, Feasibility Skeptic as suggested in Simplification Opportunities), add one specialized reviewer at a time, measure incremental value. Don't commit to 6 without data.
- **Iteration status:** New

### Finding 4: Synthesis Consolidation Heuristics Undefined
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Synthesis (deduplication, contradiction detection)
- **Issue:** Synthesizer must "deduplicate" findings and "surface contradictions" but design provides no heuristics for how. When do two findings count as "the same issue"? Same section + similar keywords? Same root cause? Same suggested fix? When do two findings count as "contradictory" vs "complementary concerns about same area"? Example from prior review: Finding 11 (cost budget) and Finding 33 (cost visibility) were split as distinct findings, but both address cost concerns. That was a deduplication judgment call with no documented rule.
- **Why it matters:** Aggressive deduplication (collapse anything related) loses nuance and reduces finding count artificially. Conservative deduplication (only exact matches) floods user with near-duplicates. Inconsistent consolidation across review runs makes iteration comparison unreliable ("did finding count drop because we fixed things or because synthesizer deduplicated more aggressively?"). The synthesizer's judgment directly affects verdict (Critical finding count) and user experience (40 findings vs 25 after deduplication).
- **Suggestion:** Define explicit consolidation rules in synthesizer prompt: (1) Deduplicate only if findings reference exact same section AND same root cause (conservative baseline), (2) Group related findings under common heading but preserve as separate entries with cross-references ("See also Finding 5, Finding 12"), (3) Flag potential duplicates for user decision rather than auto-consolidating. Track deduplication decisions in summary ("5 findings consolidated from 8 reviewer flags"). Test consolidation quality in first few review runs, tune heuristics based on false merges.
- **Iteration status:** New

### Finding 5: Phase Classification as Multi-Label Problem
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Finding Phase Classification, Verdict Logic
- **Issue:** Design treats phase classification as single-label (each finding is survey gap OR calibrate gap OR design flaw OR plan concern) but disposition note for Finding 7 acknowledges multi-label reality ("design flaw (primary) caused by calibrate gap (contributing)"). The summary format has "Findings by Phase" section with counts (survey gaps: N, calibrate gaps: N, etc.) but doesn't specify how multi-label findings are counted. Does "design flaw (primary), calibrate gap (contributing)" increment both counters? Just primary? How does verdict logic handle this?
- **Why it matters:** If 30% of findings are multi-causal (realistic for complex design flaws), single-label classification is lossy and verdict logic becomes ambiguous. Example: finding is "design assumes API exists (assumption) because requirements didn't specify integration constraints (calibrate gap)." Primary phase is design (fix the assumption), but systemic issue is calibrate (requirements should have caught this). Verdict logic says "calibrate gap at any severity → escalate" but if it's tagged as design-primary, you'll iterate the design instead of escalating. Misclassification wastes cycles.
- **Suggestion:** Specify whether classification is single-label or multi-label in "Finding Phase Classification" section. If multi-label: (1) Define primary vs contributing semantics (primary = phase to revisit, contributing = systemic pattern to track), (2) Update summary format to show multi-label data (separate "Primary Phase" and "Contributing Factors" sections), (3) Update verdict logic (escalate on primary phase = survey/calibrate, track systemic patterns separately). If single-label: resolve contradiction in Finding 7 disposition note (pick primary only, log contributing factors in finding detail but don't formalize them).
- **Iteration status:** New

### Finding 6: Async Mode Is Not Actually Async
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** UX Flow, Finding 2 disposition note
- **Issue:** Finding 2 disposition states "Async is the default — review always writes artifacts to disk. Interactive mode reuses those same artifacts as a convenience layer. No separate 'async mode' needed; it's the baseline." This describes batch execution (run review, write files, exit), not async workflow (run review in background, process findings hours later). True async requires: (1) review runs without blocking user's terminal, (2) user can close session and resume later, (3) finding processing state persists across sessions. Current design has none of this — it writes files but still blocks during review execution and expects interactive processing immediately after.
- **Why it matters:** Background automation (CLAUDE.md track #6: "Agent SDK + MCP + cron for long-running research") requires true async. If review takes 5 minutes to run 6 agents, that's 5 minutes of terminal occupancy. User can't work on other tasks during review, can't trigger review and come back tomorrow. The "async" framing in disposition note is misleading — it's really "file-based output" (good) but not "background execution" (required for automation track).
- **Suggestion:** Distinguish between execution mode (sync/async) and output mode (interactive/file-based). Current design: sync execution, file-based output with optional interactive processing. For true async: (1) skill supports `--background` flag (launches reviewers as background jobs, skill exits immediately, user polls for completion or gets notification), (2) finding processing is session-independent (summary.md includes URL or file path for resuming processing, state persisted to disk), (3) re-running skill on same topic detects in-progress review and offers to show status or abort. Defer true async to post-MVP but document the distinction to avoid confusion.
- **Iteration status:** New

### Finding 7: Verdict Computed Before Findings Processed
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Verdict Logic, UX Flow Step 4 (Present Summary)
- **Issue:** UX flow shows verdict presented to user in Step 4 before findings are processed in Step 5, but verdict depends on severity ratings that may be wrong (false positives). If user rejects 3 Critical findings as invalid in Step 5, the "revise" verdict from Step 4 should retroactively become "proceed." Design doesn't specify whether verdict is recomputed after finding processing or remains unchanged. Finding 8 disposition says "User can override severity during processing" but doesn't specify what happens to verdict when severity changes.
- **Why it matters:** Presenting an incorrect verdict wastes cycles. User sees "revise" (based on 5 Critical findings), spends 20 minutes processing findings, rejects 4 of the Critical findings as false positives, and is left with 1 actual Critical finding. Should have been "revise" but for different reasons. Or user sees "proceed" (no Critical findings), processes findings, realizes an Important finding should have been Critical, but workflow already said "proceed" so they ignore it. Verdict is a key decision signal; if it's computed prematurely and not updated, it's unreliable.
- **Suggestion:** Recompute verdict after finding processing completes, based on accepted findings only. Show provisional verdict in Step 4 ("Provisional verdict: revise [based on 5 Critical findings, subject to your review]"), final verdict in Step 6 after processing ("Final verdict: proceed [4 Critical findings rejected, 1 accepted and addressed]"). Alternatively: eliminate provisional verdict entirely, show finding counts and let user decide verdict after processing.
- **Iteration status:** New

### Finding 8: No Rollback Plan for Bad Implementations
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Prototype Scope, implementation commits
- **Issue:** The feature/parallax-review branch has 11 commits implementing this design. If this review identifies Critical design flaws requiring rework, what's the rollback strategy? Git revert? New branch? Archive and restart? The design document doesn't address "what if the design is wrong after implementation?" which is meta-level irony (building a design review tool without reviewing its own design first).
- **Why it matters:** Sunk cost fallacy is real. With 11 commits of implementation work, there's psychological pressure to accept the design as-is and work around flaws rather than rearchitect. If a finding reveals fundamental design error (e.g., "synthesizer can't reliably deduplicate findings, need different architecture"), the response may be "too late, already built, let's patch it" instead of "let's fix the design and rebuild correctly." This is especially risky for a tool whose value proposition is catching design flaws early.
- **Suggestion:** Adopt "prototype is disposable" mindset. If this review finds Critical design flaws, archive the current implementation as learning reference, write updated design doc, and rebuild. Alternatively: acknowledge that review-after-implementation is validation (confirming the built system matches needs) rather than true design review (catching flaws before building). In that case, focus findings on "does the implementation match the design?" and "is the design complete?" rather than "should this be built differently?"
- **Iteration status:** New

### Finding 9: Reviewer Prompt Versioning Strategy Missing
- **Severity:** Important
- **Phase:** plan (primary), design (contributing)
- **Section:** Reviewer Personas, prompt iteration (Task 8)
- **Issue:** Task 8 completed "prompt iteration from smoke test" with 8 files updated across 3 commits. This means reviewer prompts changed based on findings. But design doesn't specify how prompt versions are tracked or how old review results remain comparable to new review results. If Assumption Hunter's prompt changes significantly between iteration 1 and iteration 2 of reviewing the same design, finding differences could be due to prompt changes (not design improvements).
- **Why it matters:** Eval framework depends on comparing review quality across iterations. If you can't distinguish "design improved" from "prompts got better at finding issues" or "prompts got worse and missed things," eval data is noisy. Cross-iteration finding tracking (Finding 5 from prior review) requires stable finding IDs, but if prompts change, same logical issue may be phrased differently (breaking ID matching). Prompt caching (Finding 3 from prior review) requires stable prompt prefix, but iteration requires prompt changes.
- **Suggestion:** Version reviewer prompts explicitly. Each prompt file includes version header (`# Assumption Hunter v1.2 — 2026-02-15`). Summary.md records prompt versions used for each review run (`Assumption Hunter: v1.2, Edge Case Prober: v1.1`). When comparing review iterations, note prompt version changes. If major prompt refactor needed, increment version and treat findings as non-comparable to prior versions. Alternatively: adopt immutable prompt strategy (prompts locked after first production use, improvements go into new personas rather than changing existing ones).
- **Iteration status:** New

### Finding 10: Second Brain Test Case Not Actually Run
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Prototype Scope ("Validate with: Second Brain Design test case")
- **Issue:** Design claims validation will use "Second Brain Design test case (3 reviews, 40+ findings in the original session)" but Memory.md shows only one test case actually run: smoke test against the parallax:review design doc itself. The Second Brain test case (real project with known design flaws and review findings) hasn't been executed against the implemented system.
- **Why it matters:** Self-review (reviewing parallax:review's own design doc) is useful for dogfooding but weak for validation. You're testing whether the tool can review itself, not whether it catches real design flaws in domain problems. The Second Brain case is the validation that matters — did the implemented review system catch the same 40+ issues the manual process found? Did it catch different issues? This is the eval that shows whether the tool works. Without it, you've built a tool, tested that it runs, but not validated that it produces value.
- **Suggestion:** Run Second Brain test case before finalizing this design doc as "approved." Use findings to validate: (1) reviewer personas catch real design flaws (not just generic concerns), (2) finding counts are comparable to manual review (not 10x higher or lower), (3) severity calibration is sensible (Critical findings actually are critical), (4) phase classification routes issues correctly (design flaws vs calibrate gaps). If test reveals failures, update design before marking approved.
- **Iteration status:** New

### Finding 11: Cost Per Review Run Unknown
- **Severity:** Important
- **Phase:** plan (primary)
- **Section:** Open Questions ("Cost per review run")
- **Issue:** Design acknowledges cost as eval question but after 11 commits of implementation including a smoke test run, actual cost data should exist. How much did the smoke test cost? What was token count per reviewer? Did prompt caching work? Was cost within budget assumptions ($0.50-1.00 per review from Finding 11 in prior review)? Memory.md shows extensive work (6 reviewer outputs, synthesizer run, finding processing) but no cost data captured.
- **Why it matters:** Budget is $2000/month with $150-400 projected API spend. Unknown costs make iteration risky. If smoke test cost $5 (10x estimate), you can afford ~30-60 reviews/month. If it cost $0.20 (5x under estimate), you can afford hundreds. Without data, you're flying blind on burn rate. Especially critical for eval phase where you'll run many review iterations.
- **Suggestion:** Instrument next review run with token/cost logging. Capture: (1) input tokens per reviewer (design doc + requirements + system prompt), (2) output tokens per reviewer, (3) synthesizer tokens, (4) total cost at Sonnet pricing, (5) cache hit rate if caching enabled. Log to review summary or separate cost tracking file. Use data to validate budget assumptions and inform model tiering decisions (Finding 40 from prior review: test Haiku for some personas).
- **Iteration status:** New

### Finding 12: UX Friction Log Has No Feedback Loop
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Memory.md reference to UX friction log
- **Issue:** Memory.md mentions "UX friction log: docs/research/ux-friction-log.md — 'UX note:' convention for capturing observations" with 7 entries added during smoke test session. This is excellent practice (capture pain points during real use), but design doc has no mechanism for feeding UX findings back into design improvements. Friction log is write-only.
- **Why it matters:** UX friction compounds. If 7 friction points emerged in one smoke test session, each future review session will hit the same friction until addressed. Without prioritization framework (which friction points block workflows vs annoy?), log becomes complaint repository rather than improvement backlog.
- **Suggestion:** Add UX friction review to wrap-up process. After every N review runs (suggest N=3), analyze friction log, prioritize top 3 issues by impact, file as design improvements. Categorize friction as: (1) fixable with prompt tuning (reviewer output format issues), (2) requires UX flow changes (interactive processing problems), (3) requires architecture changes (state management complexity). Address category 1 immediately, defer 2-3 to planned improvements.
- **Iteration status:** New

## Blind Spot Check

Given my focus on buildability and simplification, I likely underweight:

**Correctness I'm not checking:** I'm not validating that the 6 chosen personas actually cover the design review space effectively. First Principles Challenger (Finding 26 from prior review) argues personas solve coverage, not adversarial review — they're not incentivized to challenge the core premise. I didn't assess whether a different persona set (adversarial pairs, stance-based rather than domain-based) would produce higher-value findings. That's a calibrate-phase question about whether we're solving the right problem.

**User value I'm not measuring:** I'm focused on implementation complexity but not asking "does this tool actually improve design quality?" The Second Brain test case (Finding 10) would answer that, but I'm flagging its absence rather than speculating on outcome. If the tool catches the same issues human reviewers catch, it's automation (saves time). If it catches different issues, it's augmentation (improves outcomes). If it misses critical issues or floods with false positives, it's net-negative (wastes time on noise). I don't have data to assess which.

**Long-term maintainability:** I'm evaluating MVP complexity but not post-MVP evolution costs. If reviewer prompts need continuous tuning (correction compounding, calibration loops), the maintenance burden grows over time. If prompt versioning causes eval comparability issues (Finding 9), technical debt accumulates. Feasibility Skeptic lens is "can you build this?" but doesn't assess "can you maintain this for 6-12 months as requirements evolve?"

**Integration complexity beyond this skill:** This design is scoped to parallax:review in isolation, but it's meant to plug into a larger pipeline (parallax:orchestrate calling review as a gate between phases). I'm not evaluating how this skill's outputs (verdict, finding classifications, review artifacts) integrate with upstream/downstream skills. That's a systems architecture concern that Requirement Auditor or (in plan-stage review) Systems Architect would catch.
