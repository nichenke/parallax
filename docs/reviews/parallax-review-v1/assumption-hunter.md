# Assumption Hunter Review

## Changes from Prior Review

Prior review found 41 total findings (8 Critical, 22 Important, 11 Minor). I contributed 12 findings in that review. Status of my prior findings after implementation (Tasks 1-8):

**Previously flagged, now resolved:**
- Finding 2 (Interactive processing contradicts background automation) — Task 8 established async-first architecture, interactive mode is convenience layer
- Finding 3 (Reviewer output compliance) — Schema validation added to agent prompts in Task 8
- Finding 4 (Topic label validation) — Task 8 added sanitization (alphanumeric, hyphens, underscores only)
- Finding 5 (Discuss mode depth limits) — Task 8 cut discuss mode from MVP, replaced with reject-with-note
- Finding 7 (Synthesizer "purely editorial" contradiction) — Task 8 reframed synthesizer as judgment-exercising role
- Finding 9 (Git commit strategy) — Task 8 clarified single commit per review run, user confirms, auto-fix gets separate commit

**Previously flagged, still an issue:**
- Finding 6 (Phase classification contradicts verdict logic) — Partially addressed but see Finding 2 below (multi-causal phase classification routing not operationalized)
- Finding 8 (Cost budget not specified) — Acknowledged, deferred to empirical data collection
- Finding 10 (Product Strategist missing from design stage) — Persona activation unchanged, still a gap
- Finding 12 (Review stage input assumes orchestrator context) — Acknowledged as low-priority for MVP, guidance text deferred

**New findings in this review:** 8 new findings identified below.

## Findings

### Finding 1: Prompt Iterations Assume Stable Requirements Context
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Agents (all 7 agent prompts, especially reviewer personas)
- **Issue:** All agent prompts reference requirements documents and design artifacts as inputs, but assume these artifacts remain semantically stable across iterations. The design supports re-reviews after revision, but agent prompts contain no mechanism to detect or handle requirement drift (requirements doc changed between iteration 1 and iteration 2). If requirements change mid-iteration, reviewers comparing "design v2 vs requirements v2" have no context that requirements themselves moved, creating false "design now satisfies requirement X" signals when requirement X was actually relaxed.
- **Why it matters:** In real design workflows, adversarial review findings often trigger requirement clarification ("we need to specify what happens at scale" → requirement gets added). Next review cycle operates against updated requirements, but reviewers can't distinguish "design improved" from "requirement lowered the bar." This breaks finding classification — a previously-Critical finding resolved by changing the requirement should escalate to calibrate, not mark as "design fixed."
- **Suggestion:** Add requirement versioning to review contract. Options: (1) Timestamp or hash requirements doc, reviewers note which version they reviewed against, synthesizer flags requirement changes across iterations, (2) Git-based diff: pass `git diff` of requirements to reviewers on re-review ("requirements changed: added failure mode section, relaxed latency constraint"), (3) Require explicit user confirmation when re-reviewing with modified requirements ("Requirements changed since last review. Proceed with new requirements or revert?").
- **Iteration status:** New finding

### Finding 2: Reviewer Personas Assume Linear Causality for Phase Classification
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Section:** Finding Phase Classification, Per-Reviewer Output Format
- **Issue:** Reviewers classify findings by single primary phase (survey/calibrate/design/plan) with optional contributing phase, but the classification schema assumes each finding has a clear root cause in one pipeline phase. Real design failures are multi-causal: missing research (survey) leads to unstated assumption (calibrate gap) which enables flawed design (design) that's hard to implement (plan). The design forces reviewers to pick one primary phase when the finding actually indicates systemic failure across multiple phases.
- **Why it matters:** Prior review Finding 7 (accepted) acknowledged this: "real design flaws are multi-causal" and added contributing phase classification. But contributing phase is secondary metadata — verdict logic and escalation routing use only primary phase. If a finding is "design flaw (primary) caused by calibrate gap (contributing)," the system routes to design revision when it should escalate to calibrate. The multi-causal nature is documented but not operationalized in routing logic.
- **Suggestion:** Revise verdict logic to treat contributing phases as escalation triggers. Rule: If any finding has "calibrate gap (contributing)" or "survey gap (contributing)", verdict cannot be "proceed" — even if primary phase is design. User must acknowledge the systemic issue before moving forward. Alternatively, synthesizer should aggregate contributing phases: if >30% of findings share same contributing phase, that phase failed and requires re-work regardless of primary classifications.
- **Iteration status:** Still an issue (Finding 6 from prior review only partially addressed)

### Finding 3: Cross-Iteration Finding Tracking Assumes Text Stability
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Synthesis (cross-iteration tracking, Finding 5 from prior review)
- **Issue:** Prior review Finding 5 (accepted) added stable finding IDs "e.g., hash of section + issue text" for tracking findings across iterations. Hash-based IDs break when finding text is refined without changing substance. Example: Iteration 1 flags "Parallel agent dispatch has no retry logic" (hash: abc123). Designer adds retries. Iteration 2 reviewer writes "Parallel agent retry logic lacks exponential backoff" (hash: def456). These are the same design concern evolving, but hash IDs treat them as unrelated findings. System reports first finding "resolved" and second as "new" when it's actually "still an issue, refined."
- **Why it matters:** Finding persistence mechanism from Finding 5 relies on exact text matching (via hashing) which is brittle. Reviewers naturally rephrase findings, especially when design improves partially. User sees "12 new findings" when actually "8 are refinements of prior findings, 4 are truly new." Defeats the purpose of iteration tracking (knowing what changed vs what's new).
- **Suggestion:** Replace text hashing with semantic fingerprinting or section-based anchoring. Options: (1) Anchor findings to design doc section headings (stable across iterations if structure doesn't change), track as "Section: Parallel Dispatch, Reviewer: Edge Case Prober, Iteration: 2" and deduplicate by section+reviewer, (2) LLM-based semantic matching: synthesizer compares new findings to prior findings and flags semantic overlap ("This appears related to Finding 3 from iteration 1, has it been addressed or is this a new concern?"), (3) Hybrid: hash section+severity+reviewer as coarse ID, manual user confirmation when hashes don't match but section overlaps.
- **Iteration status:** New finding

### Finding 4: Async-First Architecture Assumes Single Human Reviewer
- **Severity:** Important
- **Phase:** design (primary), calibrate (contributing)
- **Section:** UX Flow, Finding 2 disposition from prior review
- **Issue:** Prior review Finding 2 established "async is the default — review always writes artifacts to disk, interactive mode is convenience layer." This correctly decouples review execution from human availability, but the finding disposition workflow still assumes single human making accept/reject decisions. In team contexts (common for design review), multiple people may want to process findings asynchronously, discuss as a group, or delegate finding review (senior reviews Critical, junior reviews Minor). Current design has no multi-user support or finding assignment.
- **Why it matters:** CLAUDE.md states this is "useful beyond personal infra, applicable to work contexts." Work contexts have teams. If three engineers all run `parallax:review --process-findings` on the same summary.md, last writer wins (dispositions overwrite). No support for "Alice accepted findings 1-5, Bob is reviewing 6-10, Carol flagged 11 for team discussion." This is a calibration gap — requirements don't specify single-user vs team workflows, design assumes single-user.
- **Suggestion:** Add multi-user disposition tracking to summary.md format. Minimal version: dispositions include reviewer name + timestamp ("Finding 1: accepted by alice@example.com at 2026-02-15T14:32Z"). Skill checks for existing dispositions before allowing overwrites. Or defer to LangSmith (Finding 41 from prior review) which has built-in team annotation features. Document the single-user limitation if multi-user is out of scope for MVP.
- **Iteration status:** New finding

### Finding 5: JSONL Format Deferred But Not Designed
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Output Artifacts, Per-Reviewer Output Format
- **Issue:** Multiple prior findings reference JSONL as canonical output format (Finding 14 disposition: "JSONL format enables this naturally — jq filters by severity/persona/phase without LLM tokens"). MEMORY.md states "JSONL as canonical output format — decided but not yet implemented. Current markdown works for MVP." Design doc specifies only markdown format. No schema definition for JSONL, no migration path from markdown to JSONL, no specification of how JSONL and markdown coexist (is markdown rendered from JSONL, or are they parallel formats?).
- **Why it matters:** Building markdown-first then migrating to JSONL later requires either (1) rewriting all file I/O and parsing logic, or (2) maintaining two output formats indefinitely. JSONL schema decisions (nested vs flat, per-finding files vs single file, embedded disposition state vs separate) affect storage, parsing, and UI layer. Deferring implementation is fine (YAGNI), but deferring design means the markdown format may bake in assumptions that conflict with JSONL needs.
- **Suggestion:** Add lightweight JSONL schema section to design doc specifying planned structure (even if implementation is deferred). Minimal version: one JSON object per finding with keys `{id, reviewer, severity, phase, section, issue, why_it_matters, suggestion, iteration_status, disposition}`. Specify whether markdown is transitional (replaced by JSONL) or permanent (JSONL is internal, markdown is human-readable export). Clarify whether "JSONL format" means reviewers output JSON (breaking current markdown reviewer prompts) or synthesizer converts markdown findings to JSONL (adding conversion layer).
- **Iteration status:** New finding

### Finding 6: Verdict Logic Assumes Findings Are Independent
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Verdict Logic, Synthesis
- **Issue:** Verdict logic states "Any Critical finding → revise (or escalate if survey/calibrate gap). Only Important/Minor → proceed." This treats findings as independent boolean flags (presence of Critical triggers revise), but findings often have dependency relationships. Example: Finding A (Critical) "No authentication specified" and Finding B (Minor) "Session timeout should be configurable" — if you fix A by deciding "this is internal-only, no auth needed," then B becomes irrelevant. Conversely, cluster of 5 Minor findings all in same subsystem may signal "this subsystem is underdesigned" which should block proceed even with no Critical findings.
- **Why it matters:** Prior review Finding 28 (deferred) raised this as quality budget concern ("Is 20 Important findings better than 2?"). Verdict logic doesn't account for finding relationships, clusters, or dependencies. User must mentally model these relationships during processing, reducing automation value. Edge Case Prober's disposition note for Finding 7 anticipated this: if >30% share root cause, escalate — but verdict is computed before user processes findings, so root cause analysis can't inform verdict.
- **Suggestion:** Defer verdict computation until after user processes findings (reorder UX flow), OR make verdict preliminary ("Preliminary verdict: revise. Processing findings may change this if clusters or dependencies are discovered"). Synthesizer could add relational analysis: "Findings 3, 7, 12 all relate to error handling subsystem. Addressing Finding 3 may resolve the others." User processes findings, system recomputes verdict based on accepted findings.
- **Iteration status:** New finding

### Finding 7: Reviewer Prompts Assume English-Language Artifacts
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Skill Interface, Reviewer Personas
- **Issue:** Skill interface specifies "design artifact — markdown document" and "requirements artifact — markdown document" but all reviewer prompts (voice rules, output format examples) assume English. No specification for handling non-English design docs, mixed-language docs (code examples in one language, prose in another), or internationalization. Agent prompts include phrases like "lead with impact" and "no hedging ('might', 'could', 'possibly')" which are English-specific linguistic patterns.
- **Why it matters:** CLAUDE.md says "useful beyond personal infra, applicable to work contexts" and design targets senior+ engineers (global audience). Non-English design docs are common in non-US engineering teams. If a Japanese team provides design doc in Japanese, reviewers will either (1) fail to parse it, (2) review poorly due to language mismatch, or (3) auto-translate and lose nuance. This is a design assumption worth stating even if out-of-scope for MVP.
- **Suggestion:** Document English-only assumption explicitly in Skill Interface section ("MVP supports English-language artifacts only. Non-English documents may produce low-quality reviews."). Alternatively, add language detection and localized reviewer voice rules (defer to post-MVP). Minimal fix: add to reviewer prompts "If artifact language is not English, note this limitation in Blind Spot Check."
- **Iteration status:** New finding

### Finding 8: Test Case Validation Assumes Availability of Original Artifacts
- **Severity:** Minor
- **Phase:** plan (primary)
- **Section:** Prototype Scope, Test Cases (Second Brain Design)
- **Issue:** Design specifies validation using Second Brain Design test case ("3 reviews, 40+ findings in the original session"). CLAUDE.md confirms this test case is from nichenke/openclaw (private repo). Prototype development happens in public parallax repo. No specification of whether test case artifacts (design docs, requirements, original review findings) will be copied to parallax repo, anonymized, or referenced externally.
- **Why it matters:** If test case artifacts remain in private repo, public contributors can't reproduce validation results or iterate on test cases. If copied without anonymization, may leak proprietary context. If anonymized, may lose fidelity (design flaws specific to OpenClaw context may not reproduce in sanitized version).
- **Suggestion:** Specify test case artifact handling: (1) Extract and anonymize Second Brain test case into `docs/test-cases/second-brain-anonymized/` with design doc, requirements, and expected findings, (2) Document what was anonymized and what fidelity was lost, (3) Validate that anonymized version still produces comparable finding counts/types, or (4) Use only public test cases for open-source validation (claude-ai-customize from local repo, if it can be open-sourced).
- **Iteration status:** New finding

## Blind Spot Check

Given my focus on unstated assumptions, I may have missed:

1. **Performance assumptions** — I didn't examine whether the design assumes reviews complete in reasonable time. If a design doc is 10,000 words, running 6 Sonnet agents in parallel might take 5+ minutes. Are there timeout assumptions baked into UX expectations?

2. **Prompt token limits** — I flagged language assumptions but not token limit assumptions. If design doc + requirements doc + system prompt + prior review summary exceeds model context window, what happens? Does the design assume all inputs fit in context?

3. **Git workflow assumptions beyond single-branch** — Finding 39 from prior review flagged single-branch workflow, but I didn't examine assumptions about git state. Does the design assume clean working directory, or can reviews run with uncommitted changes present?

4. **Filesystem assumptions** — Design writes to `docs/reviews/<topic>/`. I didn't check assumptions about filesystem permissions, disk space, or path length limits (Windows MAX_PATH). Topic label sanitization (Finding 4 from prior review, now resolved) may not cover all edge cases.

5. **Model-specific behavior assumptions** — Finding 22 from prior review (Codex portability, deferred) flagged this, but I didn't examine assumptions specific to Claude's behavior. Do reviewer prompts assume extended thinking mode, or artifact rendering, or specific formatting capabilities that might not work on other models?

6. **Delete-before-optimize principle** — Added to Requirement Auditor's prompt in Task 8 as "should this exist at all?" check. I didn't evaluate whether all design elements passed this test. Some findings may be optimizing something that should be deleted entirely.

These gaps are better covered by Edge Case Prober (performance/limits), Feasibility Skeptic (implementation complexity), and Prior Art Scout (portability). My adversarial lens centers on "what's assumed without stating," and I've focused on semantic/logical assumptions over technical/environmental ones.
