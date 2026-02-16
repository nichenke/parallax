# Requirement Auditor Review

## Coverage Matrix

| Requirement | Addressed? | Design Section | Notes |
|---|---|---|---|
| Multi-phase process orchestration (brainstorm → design → review → iterate → plan → execute) | Partial | Pipeline Integration, Prototype Scope | Design review phase only. Survey, calibrate, plan, execute phases acknowledged but not designed. |
| Adversarial review with multiple agents | Yes | Reviewer Personas (6 design-stage) | 6 personas for design stage, 4 for requirements stage, 5 for plan stage. Parallel dispatch specified. |
| Consolidate findings automatically | Yes | Synthesis | Synthesizer deduplicates, classifies by phase, surfaces contradictions. Judgment acknowledged. |
| Track findings across iterations | Partial | Cross-Iteration Finding Tracking | Disposition accepted, mechanism acknowledged, but stable ID generation and status tracking unspecified. |
| Human checkpoints at decision points | Yes | UX Flow (Step 5-6), Pipeline Integration | Interactive processing with accept/reject, verdict determines proceed/revise/escalate. |
| Finding classification by pipeline phase | Yes | Finding Phase Classification | Primary + contributing phase classification specified. Systemic issue detection (>30% threshold) added. |
| Requirement refinement (MoSCoW, anti-goals, success criteria) | No | Prototype Scope | Explicitly deferred. "Build later" section acknowledges Product Strategist persona for requirements stage. Calibration gap. |
| Design-plan consistency check | No | None | Requirements doc pain point #3. Not addressed in design review scope. Plan stage deferred. |
| Auto-fix trivial findings | Partial | Step 4 (Auto-Fix) | Added to UX Flow after v1 disposition. Criteria specified (typos, links, paths), separate commit strategy. Implementation added in v2 sync. |
| Iterate until review converges | Partial | UX Flow, Verdict Logic | Re-review flow specified, but no stopping criteria or "good enough" threshold. Can iterate indefinitely. |
| Document decision history (ADR-style) | Yes | Summary Format (Finding Dispositions), UX Flow Step 6 | Accept/reject with notes captured in summary.md. Rejection notes feed calibration. |
| Structured requirement refinement prevents skipped requirements | No | None | Problem statement core thesis. Parallax:calibrate skill not designed. First Principles Challenge (Finding 12). |
| Self-error-detecting (classify finding by phase that failed) | Yes | Finding Phase Classification, Verdict Logic | Core novel contribution. Survey/calibrate/design/plan classification routes to correct upstream phase. |
| Parallel review execution with failure handling | Yes | Parallel Agent Failure Handling | Timeout (60-120s), retry (1x), partial results (4/6 threshold), transparency, selective re-run, schema validation. |
| Prompt caching for cost reduction | Partial | Reviewer Prompt Architecture | Section added in v2 sync. Stable prefix + variable suffix structure specified. Cache optimization deferred post-MVP. |
| Git-based iteration tracking | Yes | Output Artifacts, UX Flow Step 6 | Review artifacts in docs/reviews/<topic>/, git commit per review run. Diffs show iteration changes. |
| CLI-first tooling | Partial | None explicitly | Requirements doc lists gh/jq/git/curl. Reviewer capabilities section added in v2 sync, but tool access per persona still unspecified. |
| Model tiering (Haiku/Sonnet/Opus) for cost optimization | No | None | Requirements doc and CLAUDE.md specify this. Not designed. All reviewers use Sonnet by default. |
| Async-first architecture (artifacts to disk, interactive as convenience) | Yes | UX Flow, Step 2 disposition | Established in v2 sync. All reviewers write to disk. Interactive processing optional. |
| Output voice (active, SRE-style, engineer-targeted) | Yes | Output Voice Guidelines | Added to Per-Reviewer Output Format in v2 sync. Part of stable prompt prefix. |
| Reviewer persona coverage (optimal count empirical) | Partial | Reviewer Personas, Open Questions | 6 design-stage personas specified. Optimal count flagged as eval question. No validation criteria. |
| Anti-goals should be explicit | No | None | Requirements doc section on requirement refinement. Not addressed. Calibrate skill deferred. |
| Correction compounding (false negatives/positives → calibration rules) | No | None | Requirements doc "Iteration Loops" section. Learning loop not designed. Deferred to Phase 3+ per CLAUDE.md. |
| Findings challenge assumptions → escalate | Yes | Reviewer Personas (Requirement Auditor auto-escalates contradictions), Verdict Logic | Requirement contradictions → calibrate gap (Critical) → escalate. |
| Test cases: Second Brain Design | No | Prototype Scope | Mentioned as validation target. Not run. Smoke test only (self-review). |
| Portability (Codex + Claude) | No | None | Requirements doc: portability sanity check script. Not designed. |
| Cost per review run tracking | No | Open Questions | Acknowledged as eval question. No instrumentation specified. Cost logging mentioned in Prototype Scope as JSONL feature. |
| Reviewer tool access (read-only) | Partial | Reviewer Capabilities | Section added in v2 sync. Tool boundaries specified generically. Per-persona assignments unspecified. |

## Findings

### Finding 1: Documentation Debt Resolved — V1 Dispositions Now in Design
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Entire design doc (multiple sections updated)
- **Issue:** V2 review flagged 10 accepted findings from iteration 1 not reflected in design doc (Critical severity, systemic issue). Between v2 and v3, 23 dispositions were synced. Spot-checking key sections: (1) Prompt caching architecture now specified in "Reviewer Prompt Architecture," (2) Auto-fix step added to UX Flow Step 4, (3) Cross-iteration tracking section expanded with finding IDs + status + prior context, (4) Phase classification updated to primary+contributing, (5) Severity range handling in verdict logic, (6) Output voice guidelines added to Per-Reviewer Output Format, (7) Reviewer capabilities section added, (8) Synthesizer role updated (judgment acknowledged). All major v2 documentation debt resolved.
- **Why it matters:** Design doc is now synchronized with accepted decisions from iteration 1. This resolves the systemic issue flagged in v2.
- **Suggestion:** No action. Documentation debt cleared. Remaining gaps are unimplemented features, not missing documentation.

### Finding 2: JSONL Format Still Not Designed
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Output Artifacts, Per-Reviewer Output Format, Summary Format
- **Issue:** V2 review flagged JSONL format as Critical (Finding 9, 4 reviewers consensus). Disposition notes reference JSONL as canonical format. MEMORY.md states "decided but not yet implemented." Design doc sync added cross-iteration tracking and finding IDs but still specifies only markdown output. No JSONL schema, no field definitions, no migration path. Lines 319-320 mention "JSONL output enables jq-based filtering" but no structure specified.
- **Why it matters:** This is the largest structural decision not documented. Finding IDs (line 248), status tracking (line 249), filtering by severity/persona/phase (line 320), cost logging (line 323)—all depend on structured output. Markdown format doesn't support stable IDs or machine-processable fields. Building markdown-first then migrating later means rewriting file I/O, parsing, and potentially invalidating iteration 1-2 data.
- **Suggestion:** Add JSONL schema section specifying structure even if implementation deferred. Minimal schema: `{finding_id, reviewer, severity, phase_primary, phase_contributing, section, issue, why_it_matters, suggestion, iteration_status, disposition, disposition_note}`. Specify: (1) reviewers output markdown (unchanged for MVP), (2) synthesizer converts to JSONL as canonical storage, (3) summary.md is markdown rendering of JSONL for human reading, (4) finding IDs generated during JSONL conversion, (5) tools consume JSONL via jq. Or: acknowledge markdown is permanent and JSONL is deferred indefinitely.

### Finding 3: Requirement for "Structured Requirement Refinement" Not Addressed
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Section:** Prototype Scope (deferred), Problem Statement
- **Issue:** Requirements doc pain point #5: "No structured requirement refinement—we jumped from 'interesting idea' to 'write the design' without formally prioritizing must-have vs nice-to-have. A major feature was dropped late, after significant design work." Requirements doc explicitly states "Outcome-focused—define what success looks like before defining how to get there. This has been the single biggest design quality lever in practice." First Principles Finding 12 from v2 notes "The real problem is 'skipping requirements refinement,' not 'lack of review automation.'" Design prototypes design-stage review. Requirement refinement (parallax:calibrate) deferred to "Build later."
- **Why it matters:** You're building a solution to catch design flaws when the requirements doc identifies preventing those flaws (via requirements review) as the highest-leverage intervention. Building design review first means you'll discover during testing that it catches symptoms, not root causes. V2 review already surfaced this (Finding 10: circularity, Finding 12: wrong problem framed).
- **Suggestion:** Either (1) prototype requirements-stage review first (4 personas: Assumption Hunter, Requirement Auditor, First Principles, Prior Art Scout, Product Strategist), validate it catches requirement-level errors that prevent design failures, then build design review as extension, OR (2) explicitly reframe problem statement as "validate orchestration mechanics" prototype (not value hypothesis test) and accept that requirements review hypothesis is untested. Current framing claims to solve a problem the design doesn't address.

### Finding 4: Cross-Iteration Finding IDs Still Unspecified
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Cross-Iteration Finding Tracking (lines 244-252)
- **Issue:** Section added in v2 sync. Line 248: "Finding IDs: Stable hash derived from section + issue content. Enables cross-iteration diff." But hash generation algorithm unspecified. V2 Assumption Hunter Finding 7 noted text-hash brittleness: minor wording changes break tracking. Same design concern evolving across iterations produces different hashes, treated as unrelated findings. Section acknowledges the mechanism but doesn't specify it.
- **Why it matters:** Finding persistence is the entire value of cross-iteration tracking. Without stable ID specification, implementation will produce brittle hashes (wording changes → false new findings) or inconsistent IDs (manual assignment → errors). When Finding 3 from iteration 1 reappears in iteration 2, system must detect it.
- **Suggestion:** Specify ID generation in design. Options from v2 Finding 7 + Finding 15: (1) Semantic hash (section + first 100 chars of issue, normalized), (2) Section-based anchoring (section + reviewer + iteration, dedupe by overlap), (3) LLM-based semantic matching (synthesizer asks "which prior findings does this match?"), (4) Hybrid (auto-hash with manual override). Recommend LLM semantic matching for MVP—synthesizer already exercises judgment, matching is natural extension.

### Finding 5: Multi-Causal Phase Classification Routing Not Operationalized
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Finding Phase Classification (lines 153-161), Verdict Logic (lines 163-169)
- **Issue:** Lines 161 note "Findings classified by primary phase (most actionable fix) and optional contributing phase (upstream cause)." Lines 161: "When >30% share contributing phase, synthesizer flags systemic issue." But verdict logic (lines 163-169) only uses primary phase for routing. V2 Assumption Hunter Finding 6 notes: if finding is "design flaw (primary) caused by calibrate gap (contributing)," system routes to design revision when it should escalate to calibrate. Contributing phase documented but not operationalized.
- **Why it matters:** Multi-causal classification was accepted in v1 Finding 7 disposition specifically to catch systemic upstream failures. Current verdict logic defeats this—user revises design when requirements are broken. Wastes iteration cycles.
- **Suggestion:** Update verdict logic to treat contributing phases as escalation signals. Add rule: "If any finding has calibrate gap (contributing) or survey gap (contributing), verdict includes systemic escalation warning. User must acknowledge upstream issue before proceeding." Alternatively: if >30% of findings share contributing phase, force escalate regardless of primary classifications.

### Finding 6: Model Tiering Strategy Missing
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** None (should be in Reviewer Personas or cost section)
- **Issue:** Requirements doc: "Model tiering: Haiku for simple evals, Sonnet for review agents, Opus sparingly for adversarial deep analysis." CLAUDE.md cost strategy relies on model tiering. Design specifies Sonnet for all reviewers (line 62 table note: "all use model: sonnet"). No architecture for per-persona model configuration. V2 Requirement Auditor Finding 38 flagged this.
- **Why it matters:** Cost optimization. If Haiku works for mechanical reviewers (Edge Case Prober, Prior Art Scout for search), per-review cost drops 30-40%. Without design-level specification, model becomes hardcoded implementation detail rather than configurable parameter. Eval framework can't test model variants.
- **Suggestion:** Add model configuration subsection. Specify: (1) default model per stage (Sonnet for design), (2) model parameter per persona (allows empirical testing), (3) configuration via persona definition (not hardcoded), (4) eval framework tests Haiku for mechanical personas vs Sonnet baseline.

### Finding 7: Auto-Fix Git Safety Concerns Unresolved
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** UX Flow Step 4 (Auto-Fix, lines 276-278)
- **Issue:** Lines 276-278: "Auto-fixable findings (typos in markdown, missing file extensions, broken internal links) applied automatically. Auto-fixes committed as separate git commit from human-reviewed changes." V2 Edge Case Prober Finding 20 flagged this conflicts with Git Safety Protocol ("NEVER commit changes unless user explicitly asks"). Auto-fix modifies design doc before user sees findings. If user has unrelated edits, auto-fix commit includes them. If user wants to reject auto-fixes, they can't—already applied.
- **Why it matters:** Auto-fix as described is invasive. Modifies source files without user approval. Step 4 (auto-fix) happens before Step 5 (user processes findings), so user can't reject bad auto-fixes. Separate commit impossible if auto-fixes intermixed with user changes between review start and completion.
- **Suggestion:** Revise auto-fix workflow. Options: (1) auto-fixes presented as suggested changes (diff format), user approves before application, (2) auto-fixes applied to copy of design doc (user merges if approved), (3) auto-fixes deferred to post-human-processing (user accepts/rejects findings, then auto-fixable accepted findings applied as batch), (4) conservative criteria (whitespace/formatting only) with explicit approval. Recommend option 3: auto-fix only accepted findings, not all findings.

### Finding 8: No Stopping Criteria for Re-Review Iteration Loop
- **Severity:** Important
- **Phase:** calibrate (primary)
- **Section:** Verdict Logic, UX Flow (revise path)
- **Issue:** Line 170: "`revise` = fix the design and re-review." No exit condition. If iteration 2 produces new Critical findings (different from iteration 1), user revises. Iteration 3 produces more. When does it stop? When findings = 0 (unrealistic)? When no new Critical findings? When user decides "good enough"? V2 Edge Case Prober Finding 24 flagged this.
- **Why it matters:** Without convergence criteria, reviews iterate indefinitely. Real designs have tradeoffs—edge cases deferred, Important findings accepted as constraints. Current design treats all Critical findings as blockers with no framework for "acceptable risk, proceed anyway."
- **Suggestion:** Add review convergence criteria. Options: (1) explicit threshold ("2 consecutive iterations with no new Critical findings"), (2) allow user override ("proceed despite Critical findings" with justification required), (3) track iteration count, flag if >3, (4) add "defer" disposition for out-of-scope findings accepted by user. Recommend option 2: user can override verdict with required note.

### Finding 9: Requirements-Stage Review Deferred But Problem Statement Says It's Highest Leverage
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Section:** Prototype Scope (lines 314-330), Requirements doc (lines 99-103)
- **Issue:** Requirements doc lines 99-103: "Outcome-focused—define what success looks like before defining how to get there. This has been the single biggest design quality lever in practice: missing a critical angle during requirements means the design optimizes for the wrong thing." Design builds design-stage review as prototype. Requirements-stage review (with Product Strategist persona) deferred to "Build later" (lines 325-327). V2 First Principles Finding 10 notes this is circular: building design review to validate orchestration when problem statement identifies requirement refinement as root cause.
- **Why it matters:** If requirements review is actually highest leverage (per requirements doc), spending weeks tuning design-stage personas validates mechanics but misses value hypothesis. You'll build battle-tested infrastructure for the wrong problem. Test case validation (Second Brain) may show design review catches symptoms while requirement errors remain uncaught.
- **Suggestion:** Reframe prototype scope. Either (1) build requirements-stage review first (4 personas including Product Strategist), test against historical requirement docs that led to design failures, validate hypothesis, then extend to design stage, OR (2) make explicit: "This prototype validates orchestration mechanics (parallel agents, synthesis, finding processing, iteration tracking), not value hypothesis. Requirements review is acknowledged as higher leverage but deferred pending orchestration validation." Current framing claims to solve problem it doesn't address.

### Finding 10: Verdict Computed Before Findings Processed
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** UX Flow Step 4 (Present Summary), Verdict Logic
- **Issue:** UX flow: Step 3 synthesize → Step 4 present verdict → Step 5 process findings. Verdict based on all findings, but Step 5 may reject findings as false positives. If user rejects 3 of 5 Critical findings in Step 5, the "revise" verdict from Step 4 should become "proceed." Design doesn't specify whether verdict recomputed. V2 Feasibility Skeptic Finding 43 flagged this.
- **Why it matters:** Presenting provisional verdict wastes cycles. User sees "revise" (5 Critical), processes findings for 20 minutes, rejects 4 Critical as invalid. Should have been "proceed" verdict. User took action (started revising design) based on wrong signal.
- **Suggestion:** Recompute verdict after finding processing based on accepted findings only. Show provisional verdict in Step 4 ("Based on all findings: revise. Processing findings may change this."), final verdict in Step 6 after processing completes. Alternatively: eliminate provisional verdict, show finding counts only, let user process first then compute verdict.

### Finding 11: "Critical-First" Mode Orphans Non-Critical Findings
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** UX Flow Step 5 (Processing modes, lines 280-286)
- **Issue:** Lines 282-284: "Critical-first: Address Critical findings only. Send source material back for rethink. Remaining findings processed in next pass." User processes Critical, revises design, re-reviews. Iteration 2 produces new findings. User processes Critical-first again. Important/Minor from iteration 1 never processed—orphaned. After 3 iterations, 40+ unprocessed findings accumulated. V2 Edge Case Prober Finding 25.
- **Why it matters:** Critical-first designed for fast iteration but creates technical debt. Eventually user must process orphaned findings or accept valuable feedback discarded. No mechanism tracks which findings carried forward unprocessed vs obsoleted by design changes.
- **Suggestion:** Add orphaned finding management. Specify: (1) after Critical-first processing, synthesizer marks remaining findings "deferred to next iteration," (2) on re-review, synthesizer reconciles prior deferred findings with new findings (mark as resolved/persists/new), (3) after revise loop converges, prompt user to process accumulated deferred findings before final proceed. Track deferred finding count in summary.

### Finding 12: Test Cases Not Run — Second Brain Validation Missing
- **Severity:** Important
- **Phase:** design (primary), plan (contributing)
- **Section:** Prototype Scope (Validate with, lines 332-334)
- **Issue:** Lines 332-334: "Validate with: Second Brain Design test case (3 reviews, 40+ findings in the original session)." MEMORY.md shows only smoke test run (self-review of parallax:review design). Second Brain test case—real project with known design flaws—not executed. V2 Feasibility Skeptic Finding 54.
- **Why it matters:** Self-review validates orchestration works but weak for quality validation. Second Brain case is the test that matters: did implemented system catch the same 40+ issues manual process found? Without this, design approval is premature—you don't know if reviewers catch real design flaws.
- **Suggestion:** Run Second Brain test case before marking design approved. Use findings to validate: (1) personas catch real design flaws, (2) finding counts comparable to manual review, (3) severity calibration sensible, (4) phase classification routes correctly. If test reveals failures, update design. Alternatively: acknowledge this is post-approval validation and Second Brain test will inform iteration 4 refinements.

### Finding 13: CLI Tool Access Per Persona Still Unspecified
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Reviewer Capabilities (lines 253-258)
- **Issue:** Section added in v2 sync (lines 253-258). Line 257: "Tool access boundaries specified in stable prompt prefix per persona. Specific tool assignments empirical question for eval framework—start with baseline access and expand based on observed reviewer needs." Requirements doc lists specific CLI tools (gh, jq, git, curl). Section acknowledges tool access but defers specifics to eval. Which reviewers get which tools?
- **Why it matters:** Some personas need tools to perform their function. Prior Art Scout searches existing solutions (needs gh, curl, web search). Assumption Hunter validates assumptions (needs grep for codebase checks). Without per-persona specification, prompt authors must guess or over-provision (security risk).
- **Suggestion:** Add per-persona tool access table to design. Minimal specification: (1) all reviewers: Read (design/requirements), (2) Prior Art Scout: gh, curl, WebSearch, (3) Assumption Hunter: grep, jq for config validation, (4) all reviewers: read-only, no write access. Note: specific assignments tuned via eval, this is baseline.

### Finding 14: Multi-User Disposition Workflows Not Addressed
- **Severity:** Minor
- **Phase:** design (primary), calibrate (contributing)
- **Section:** UX Flow (assumes single human), Finding 2 disposition (async-first)
- **Issue:** Async-first architecture (lines 261, disposition from v1 Finding 2) correctly decouples review execution from human availability. But finding disposition workflow assumes single human. CLAUDE.md states "useful beyond personal infra, applicable to work contexts." Work contexts have teams. If three engineers process same summary.md, last writer wins. No support for finding assignment or collaborative review. V2 Assumption Hunter Finding 4.
- **Why it matters:** Teams need multi-user disposition tracking. Current design: Alice accepts findings 1-5, Bob reviews 6-10 simultaneously, both write summary.md, one overwrites the other. Or: team wants to discuss Finding 12 before disposition—no workflow for "flagged for team discussion."
- **Suggestion:** Document single-user limitation in design. Add to summary.md format: dispositions include reviewer name + timestamp (enables detecting conflicts). Or: defer to LangSmith which has built-in team annotation UI (v2 Prior Art Scout Finding 44). For MVP, acknowledge limitation: "Multi-user workflows deferred. Summary.md dispositions are last-writer-wins. For team review, use external tooling (LangSmith, GitHub PR comments on summary.md)."

### Finding 15: Cost Per Review Run Still Not Tracked
- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Open Questions (line 346), Prototype Scope (line 323)
- **Issue:** Line 346: "Cost per review run and whether model tiering is worth quality tradeoff" flagged as eval question. Line 323 notes "cost logging per review run in JSONL output." But after smoke test + v2 validation run (55 findings), actual cost data should exist. How much did v2 review cost? Token counts? Was cost within budget?
- **Why it matters:** Budget $2000/month, $150-400 projected API spend. Unknown costs make iteration risky. If review costs $5 (10x estimate), you can afford 30-60 reviews/month. If $0.20 (5x under), hundreds. Without data, flying blind on burn rate. Two review runs completed, no cost logging.
- **Suggestion:** Instrument next review run (iteration 3, this review) with token/cost logging. Capture: (1) input tokens per reviewer, (2) output tokens per reviewer, (3) synthesizer tokens, (4) total cost at Sonnet pricing, (5) cache hit rate if enabled. Log to summary metadata or separate cost file. Use data to validate budget assumptions and inform model tiering decisions.

### Finding 16: Rejection Note Processing Unspecified
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** UX Flow Step 6 (Process Findings, lines 288-290), Finding 6 disposition
- **Issue:** Lines 289-290: "Reject with note—finding is wrong or not applicable. Rejection note becomes calibration input to next review cycle." V1 Finding 6 disposition cut "discuss" mode, replaced with reject-with-note. Where are rejection notes stored? Who reads them? What format? V2 Edge Case Prober Finding 17 flagged this.
- **Why it matters:** Reject-with-note is now primary mechanism for disputed findings and capturing design decisions. Without schema or processing specified, notes are write-only (captured but never used). If note says "This assumes REST architecture, we're event-driven," how does that context reach reviewers who need it?
- **Suggestion:** Add rejection note schema to summary.md format. Specify: (1) rejected findings section with disposition notes, (2) prior review summary includes "Previously rejected findings and why" (fed to reviewers on re-review), (3) synthesizer checks if rejected findings reappear and surfaces to user, (4) rejection notes feed reviewer calibration (when same false positive recurs, update prompt).

### Finding 17: Prompt Versioning Strategy Missing
- **Severity:** Minor
- **Phase:** plan (primary), design (contributing)
- **Section:** Reviewer Prompt Architecture (lines 225-242)
- **Issue:** Lines 225-242 specify prompt structure (stable prefix + variable suffix) for caching. Line 241: "Prompt changes to stable prefix invalidate cache and should be tracked as versioned changes." But no version tracking mechanism specified. Task 8 updated prompts (smoke test → iteration), but how are prompt versions tracked? Can iteration 1 findings be compared to iteration 2 if prompts changed? V2 Feasibility Skeptic Finding 53.
- **Why it matters:** Eval framework depends on comparing review quality across iterations. If Assumption Hunter prompt changes between iteration 1 and 2, finding differences could be due to prompt changes (not design improvements). Can't distinguish "design improved" from "prompts got better" or "prompts regressed."
- **Suggestion:** Version reviewer prompts explicitly. Each prompt file includes version header (or git commit SHA). Summary.md records prompt versions used. When comparing iterations, note prompt version changes. If major prompt refactor needed, increment version, treat findings as non-comparable to prior versions.

### Finding 18: Timestamped Folders Break Git Diff Workflow
- **Severity:** Minor
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Skill Interface (topic label, lines 22-24), Requirements (git diffing)
- **Issue:** Lines 23-24: "Collision handling: timestamped folders for iteration separation." But requirements doc: "Git commits per iteration. Full history, diffable artifacts" and "diffs show what changed." If each iteration creates timestamped folder (`docs/reviews/topic-2026-02-15-143022/`), git diff between iterations compares different file paths—useless. Lose iteration diffing, core design goal. V2 Edge Case Prober Finding 19.
- **Why it matters:** Timestamped folders solve collision but break diffability. Contradiction between disposition and requirement.
- **Suggestion:** Revise collision handling. Options: (1) single folder per topic, overwrite on re-review, rely on git history for diffs (collision = overwrite), (2) timestamped folders + symlink `docs/reviews/topic-latest/` pointing to most recent, synthesizer produces diff report, (3) nested structure `docs/reviews/topic/iteration-1/`. Recommend option 1: overwrite + git history.

### Finding 19: Async Mode Is Not Actually Background Execution
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** UX Flow, Finding 2 disposition
- **Issue:** V1 Finding 2 disposition: "Async is default—review writes artifacts to disk." This describes batch execution (run, write files, exit), not async workflow (background execution, resume later). True async: (1) review runs without blocking terminal, (2) user closes session and resumes later, (3) state persists across sessions. Current design has none. V2 Feasibility Skeptic Finding 42.
- **Why it matters:** Background automation (CLAUDE.md track #6) requires true async. If review takes 5 minutes, that's 5 minutes terminal occupancy. "Async" framing in disposition is misleading—it's file-based output (good) but not background execution (required for automation).
- **Suggestion:** Distinguish execution mode (sync/async) from output mode (interactive/file-based). Current design: sync execution, file-based output with optional interactive processing. For true async: (1) skill supports `--background` flag, (2) finding processing session-independent, (3) re-running skill on same topic detects in-progress review and shows status. Defer true async to post-MVP but document distinction.

## Blind Spot Check

What might I have missed given my assigned focus?

**Coverage-over-quality bias:** I validated that requirements are addressed (coverage) but didn't deeply evaluate whether the approaches are sufficient (quality). Example: cross-iteration tracking is "addressed" but the LLM semantic matching suggestion may be unreliable at scale—I didn't challenge that.

**Assumed requirements are correct:** I checked design against requirements but didn't question whether requirements themselves are right. First Principles challenges (requirement refinement as highest leverage, adversarial naming misalignment) suggest problem framing may be off. Requirement Auditor should catch this per auto-escalation rule—requirements contradictory or incomplete should escalate to calibrate.

**Implementation realism:** I flagged features as "addressed" when specified in design but didn't assess buildability. Example: systemic issue detection (>30% threshold) is specified but may be too subjective for reliable implementation.

**Leverage opportunities:** I noted missing features (model tiering, cost tracking) but didn't fully evaluate v2 Prior Art Scout findings suggesting 80% of infrastructure already exists in Inspect AI, LangGraph, LangSmith, Braintrust. If mature frameworks solve this, "requirement not addressed" may not matter—solution exists, just not built here.

**JSONL as showstopper:** Finding 2 rated Critical, but is it? Markdown works for MVP per MEMORY.md. JSONL absence blocks structured finding IDs, jq filtering, cross-iteration diff—but LLM semantic matching could work without stable IDs. May be Important, not Critical. Severity reflects stated decision ("JSONL is canonical format") more than technical necessity.
