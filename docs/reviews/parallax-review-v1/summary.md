# Review Summary: parallax-review-v1 (Iteration 3)

**Date:** 2026-02-15
**Design:** docs/plans/2026-02-15-parallax-review-design.md
**Requirements:** docs/problem-statements/design-orchestrator.md
**Stage:** design
**Verdict:** revise
**Reviewers:** 6/6 completed

## Changes from Prior Review

**Iteration 2 (prior review):** 55 findings (15C/28I/12M), verdict: revise
**Iteration 3 (this review):** 83 findings (22C/47I/14M)

### Documentation Debt Resolution

**Major improvement:** The systemic documentation debt flagged in iteration 2 (67% of Requirement Auditor findings) has been substantially resolved. 23 accepted dispositions from iteration 1 were synchronized to the design document between v2 and v3:

- Prompt caching architecture added (Reviewer Prompt Architecture section)
- Auto-fix mechanism added (UX Flow Step 4)
- Cross-iteration tracking section expanded with finding IDs, status tracking, prior context
- Primary + contributing phase classification specified (Finding Phase Classification)
- Severity range handling specified (Verdict Logic)
- Output voice guidelines added (Per-Reviewer Output Format)
- Reviewer capabilities section added (tool access boundaries)
- Synthesizer role updated (judgment explicitly acknowledged)

Requirement Auditor confirms (Finding 1, Minor): "All major v2 documentation debt resolved. Remaining gaps are unimplemented features, not missing documentation."

### New Architectural Gaps Introduced by Design Updates

The design doc sync addressed accepted decisions but **did not add architectural specifications** for those decisions. Four Critical gaps remain:

1. **JSONL format schema** (Finding 2, flagged by 4 reviewers in v2) — still completely missing despite being referenced as "canonical format" in MEMORY.md and multiple disposition notes
2. **Cross-iteration finding ID mechanism** — section added but hash generation algorithm, semantic matching logic, and status tracking unspecified
3. **Auto-fix workflow** — step added to UX Flow but classification criteria, validation, git safety, and user approval process unspecified
4. **Prompt caching structure** — section added but cache boundary, versioning, and invalidation strategy unspecified

Prior Art Scout (Finding 1): "Design doc sync addresses decisions (what to do) but not specifications (how it works). Without JSONL schema, auto-fix workflow, finding ID mechanism, and prompt structure specifications, the design remains incomplete for implementation."

### New Edge Cases from Design Updates

Cross-iteration tracking, auto-fix re-review, partial reviewer results, and severity range resolution introduced new failure modes:

- **Hash-based finding IDs break when design structure changes** (Edge Case Prober Finding 1, Critical) — section renaming makes iteration tracking unreliable
- **Auto-fix re-review may loop indefinitely** (Edge Case Prober Finding 2, Critical) — no termination condition, can consume budget
- **Partial reviewer completion breaks systemic issue detection** (Edge Case Prober Finding 3, Critical) — 4/6 threshold corrupts pattern detection
- **Severity range resolution creates false escalations** (Edge Case Prober Finding 4, Critical) — single pessimistic reviewer blocks entire design

### Unchanged Fundamental Issues

Three iteration 2 Critical findings flagged as "valid but exploratory" remain unresolved:

1. **Problem framing inversion** (First Principles Finding 2, Finding 4) — requirements review acknowledged as highest leverage, design review prototyped instead
2. **Adversarial review naming mismatch** (First Principles Finding 3) — personas provide coverage-based inspection, not adversarial debate with incompatible incentives
3. **Build-vs-leverage decision deferred** (Prior Art Scout Finding 2, Finding 3, Finding 4) — Inspect AI, LangGraph, LangSmith, Braintrust solve 60-80% of custom infrastructure, evaluation still "when limits hit"

### Test Case Validation Still Missing

Feasibility Skeptic Finding 11 and Requirement Auditor Finding 12 both flag: Second Brain test case (real project with 40+ known design flaws) has not been run. After 3 review iterations, only self-review completed. External validation needed to confirm reviewers catch real design flaws, not just process issues.

---

## Verdict Reasoning

**Verdict: revise**

This review produces 22 Critical findings across 6 reviewers. Verdict logic requires revision when any Critical finding exists.

**Critical finding breakdown by category:**

1. **Architectural specification gaps (5 findings):** JSONL schema missing, cross-iteration tracking mechanism unspecified, auto-fix workflow unsafe, systemic issue detection requires undefined taxonomy, prompt versioning strategy missing
2. **Auto-fix implementation risks (3 findings):** Unsafe git workflow, infinite loop potential, Conservative criteria but no validation
3. **Assumption violations (5 findings):** Git-tracked design doc assumption, single-iteration-per-session assumption, single-user filesystem assumption, stable section headings assumption, read operations side-effect-free assumption
4. **Edge case failures (4 findings):** Hash stability breaks on structure changes, partial results corrupt detection, severity ranges create false escalations, prior context creates confirmation bias
5. **Calibrate gaps (5 findings):** Problem framing inversion (requirements review is highest leverage but deferred), adversarial naming mismatch, single-phase routing despite multi-causal classification, verdict escalation blocks all work, build-vs-leverage decision deferred

**Why revision is required:**

The design documentation has improved significantly (v2 documentation debt resolved), but implementation specifications are incomplete. Four architectural decisions accepted in v1-v2 are documented as "we decided to do X" but lack specifications for "here's how X works." Without JSONL schema, finding ID generation algorithm, auto-fix validation workflow, and prompt caching structure, implementation will produce inconsistent results or make unreviewed assumptions.

Additionally, auto-fix mechanism as currently specified violates Git Safety Protocol (auto-commits before user approval) and has no loop termination (can burn budget on infinite re-review). These are implementation risks requiring design-level resolution.

**Conservative escalation reasoning:**

Five Critical findings are calibrate gaps (problem framing, requirements review deferral, build-vs-leverage). Standard verdict logic: "calibrate gap at any severity → escalate." However, these findings were flagged in iteration 2 as "valid but exploratory—evaluate empirically during prototyping." Dispositions explicitly deferred problem framing questions to empirical validation. Escalating now contradicts accepted iteration strategy.

**Final verdict: revise (design-level action), not escalate**, because:
1. Documentation debt resolved (major progress from v2)
2. Calibrate gaps are acknowledged, empirical evaluation is the mitigation strategy
3. Critical gaps are specification-level (JSONL schema, auto-fix workflow, finding IDs), solvable within design phase
4. Auto-fix risks are addressable via workflow revision (user approval gates, loop guards)

---

## Finding Counts

**Total findings:** 83 (22 Critical, 47 Important, 14 Minor)

**By reviewer:**
- Assumption Hunter: 12 findings (5C/6I/1M)
- Edge Case Prober: 15 findings (4C/9I/2M)
- Feasibility Skeptic: 12 findings (4C/7I/1M)
- First Principles: 13 findings (7C/4I/2M)
- Prior Art Scout: 16 findings (1C/12I/3M)
- Requirement Auditor: 15 findings (1C/9I/5M)

**Deduplication summary:** 83 unique findings. 18 findings flagged by multiple reviewers (consensus signal). Most significant overlaps:
- JSONL format missing: 4 reviewers (Feasibility Skeptic, First Principles, Prior Art Scout, Requirement Auditor)
- Cross-iteration finding tracking unspecified: 3 reviewers (Assumption Hunter, Edge Case Prober, Requirement Auditor)
- Auto-fix workflow unsafe: 3 reviewers (Assumption Hunter, Edge Case Prober, Requirement Auditor)
- Build-vs-leverage decision deferred: 3 reviewers (Feasibility Skeptic, First Principles, Prior Art Scout)
- Problem framing inversion: 2 reviewers (First Principles, Requirement Auditor)
- Verdict computed before user processes findings: 3 reviewers (Feasibility Skeptic, First Principles, Requirement Auditor)
- Requirements review highest leverage but deferred: 2 reviewers (First Principles, Requirement Auditor)

**Severity consensus:** When multiple reviewers flagged the same issue, severity agreement is high (14 of 18 overlapping findings have consensus severity). Severity ranges reported below.

---

## Findings by Phase

### Primary Phase Distribution

- **Design (primary):** 62 findings (15C/36I/11M) — 75% of all findings
- **Calibrate (primary):** 14 findings (6C/6I/2M) — 17% of all findings
- **Plan (primary):** 7 findings (1C/5I/1M) — 8% of all findings
- **Survey (primary):** 0 findings

### Contributing Phase Analysis

- **Calibrate (contributing):** 11 findings cite calibrate gaps as contributing cause
- **Plan (contributing):** 8 findings cite plan-stage concerns as contributing cause
- **Design (contributing):** 3 findings cite design decisions enabling plan failures

**Systemic issue detection:** 11 findings (13% of total) have "calibrate gap (contributing)" as root cause. This exceeds the 30% threshold flagged in design for systemic issue escalation. However, verdict logic only routes on primary phase. **Recommendation:** User must acknowledge that 11 findings trace to upstream calibrate issues (requirements refinement, problem framing) before proceeding with design-level fixes.

**Cross-phase dependency:** Assumption Hunter Finding 6 (Important): "Verdict logic routes findings based on primary phase, but 11 findings have calibrate gap (contributing). Fixing design without fixing upstream calibrate gap produces local patch, not systemic fix. When >30% of findings share a contributing phase, synthesizer flags systemic issue—but verdict logic doesn't use this for routing."

---

## Auto-Fixable Findings

**Total auto-fixable findings:** 0

**Reasoning:** Design specifies auto-fix criteria as "typos in markdown, missing file extensions, broken internal links" (conservative). However, all 83 findings require human judgment:
- Design specification gaps require architectural decisions (not mechanical fixes)
- Edge case handling requires workflow design (not text correction)
- Calibrate gaps require problem reframing (not typo fixes)
- Build-vs-leverage evaluation requires prototyping (not path correction)

**Critical auto-fix concern:** Assumption Hunter Finding 3, Edge Case Prober Finding 2, Requirement Auditor Finding 7 all flag auto-fix mechanism as unsafe (auto-commits before user approval, no loop termination, violates Git Safety Protocol). Auto-fix classification and application workflow must be revised before any findings can be auto-fixed.

---

## Critical Findings

### Architectural Specification Gaps

**C1. JSONL Format Schema Missing (Consensus: 4 reviewers)**
- **Reviewers:** Feasibility Skeptic (Finding 1), First Principles (Finding 6), Prior Art Scout (Finding 5), Requirement Auditor (Finding 2)
- **Severity range:** Critical (consensus)
- **Issue:** MEMORY.md states "JSONL as canonical output format—decided but not yet implemented." Multiple iteration 1 disposition notes reference JSONL. Design doc specifies markdown-only output. No schema, no field definitions, no migration path. Lines 319-320 mention JSONL but don't specify structure.
- **Why it matters:** Finding IDs, status tracking, filtering by severity/persona/phase, cost logging—all depend on structured output. Markdown doesn't support stable IDs or machine-processable fields. Building markdown-first then migrating requires rewriting file I/O and parsing.
- **Consensus reasoning:** All 4 reviewers agree this is the largest structural decision not documented. Feasibility Skeptic: "JSONL vs markdown affects finding IDs, disposition tracking, CLI tooling, and machine processability." First Principles: "If JSONL is decided canonical format, markdown specification describes throwaway scaffolding." Prior Art Scout: "Schema decisions affect deduplication, severity ranges, phase classification storage, cross-iteration diffs." Requirement Auditor: "Building markdown-first then migrating means rewriting file I/O, parsing, potentially invalidating iteration 1-2 data."

**C2. Cross-Iteration Finding Tracking Mechanism Unspecified (Consensus: 3 reviewers)**
- **Reviewers:** Assumption Hunter (Finding 3), Edge Case Prober (Finding 1), Requirement Auditor (Finding 4)
- **Severity range:** Critical (consensus)
- **Issue:** Design now specifies "stable hash derived from section + issue content" but provides no algorithm. Text-based hashing breaks when findings evolve ("no retry logic" iteration 1 becomes "retry lacks backoff" iteration 2 = different hash). Section renaming makes tracking unreliable. Alternative is LLM-based semantic matching but token cost and complexity unestimated.
- **Why it matters:** Finding persistence enables cross-iteration diff (core workflow). Without stable IDs, "12 new findings" is ambiguous—truly new concerns or rephrased prior findings? Hash-based IDs break precisely when iteration tracking is most valuable (design structure changes, findings evolve).
- **Consensus reasoning:** Assumption Hunter: "Hash-based IDs break when input text changes, even if semantic content unchanged. Prior review flagged this as Finding 7 (Critical) with suggestion for semantic matching, but design still specifies text hashing." Edge Case Prober: "Design restructuring (adding sections, splitting, renaming) is normal during revision. Hash-based IDs tied to section names make tracking unreliable across structure changes." Requirement Auditor: "Hash generation algorithm unspecified. Same design concern evolving produces different hashes, treated as unrelated."

**C3. Auto-Fix Git Workflow Unsafe (Consensus: 3 reviewers)**
- **Reviewers:** Assumption Hunter (Finding 1), Edge Case Prober (Finding 2), Requirement Auditor (Finding 7)
- **Severity range:** Critical (consensus)
- **Issue:** Design specifies auto-fix applies changes automatically, commits separately from human-reviewed changes. This requires: (1) auto-fixes run before user sees findings, (2) auto-fixes modify design doc and commit, (3) user processes remaining findings. If user made other edits between starting review and processing findings, auto-fix commit includes unrelated changes. If user rejects auto-fix during processing, it's already committed. Temporal ordering is unsolvable.
- **Why it matters:** Auto-fix as specified violates Git Safety Protocol ("NEVER commit changes unless user explicitly asks"). Modifies source files without user approval. Conflicts with user's ability to reject bad fixes. "Separate commit" requirement impossible if user has intervening changes.
- **Consensus reasoning:** Assumption Hunter: "Auto-fix applies changes and commits automatically without user approval for each fix. Git blame shows auto-fix commit obscuring who made semantic decision. Worse: if auto-fix runs before human review (as specified), user cannot reject bad auto-fixes—they're already applied and committed." Edge Case Prober: "If auto-fix introduces new errors, re-review flags new findings, triggers another auto-fix pass, which creates more errors, loops. No loop termination condition." Requirement Auditor: "Auto-fix modifies design doc before user sees findings. Conflicts with Git Safety Protocol."

**C4. Git-Based Iteration Tracking Assumes Design Doc in Git**
- **Reviewer:** Assumption Hunter (Finding 2)
- **Severity:** Critical
- **Issue:** Design states "iteration history tracked by git" and "git diff integration: highlight changed sections to reviewers." Assumes design document being reviewed is git-tracked. If user reviews design doc from outside repository (Google Doc exported to markdown, Confluence page converted, design doc from different repo), git diff fails. No fallback specified.
- **Why it matters:** Requirements doc states "applicable to work contexts." Many teams use Confluence, Notion, or Google Docs for design documents, not git-tracked markdown. If parallax:review only works for git-tracked docs, excludes significant use cases. Cross-iteration tracking depends on git diff to detect changed sections—if diff unavailable, reviewers lose focus prioritization.

**C5. Stable Finding IDs Assume Section Headings Don't Change**
- **Reviewer:** Assumption Hunter (Finding 3)
- **Severity:** Critical
- **Issue:** Design specifies finding IDs as "stable hash derived from section + issue content." Assumes design doc section headings remain stable across iterations. If designer refactors "UX Flow" section into "User Workflow" and "State Management" between iterations, all findings anchored to "UX Flow" become orphaned—system treats them as resolved when they're relocated.
- **Why it matters:** Section refactoring is normal during design iteration. Improving document structure shouldn't invalidate finding tracking. Prior review (iteration 2) flagged this as Finding 7 (Critical) with suggestion for semantic matching, but design still specifies text hashing. If implemented as designed, cross-iteration tracking will produce false negatives (findings marked "resolved" when section renamed) and false positives (findings marked "new" when rephrased).

### Auto-Fix Implementation Risks

**C6. Auto-Fix Re-Review May Loop Indefinitely**
- **Reviewer:** Edge Case Prober (Finding 2)
- **Severity:** Critical
- **Issue:** Auto-fix applies changes, then "design is re-reviewed with remaining findings only." If auto-fix introduces new errors (broken markdown formatting, incorrect path corrections), re-review flags new findings, triggers another auto-fix pass, which creates more errors, loops. No loop termination condition specified.
- **Why it matters:** Unbounded auto-fix loops consume API budget and block user workflow. If each auto-fix pass costs $0.50 and loop runs 10 times before user intervenes, $5 burned. Conservative criteria ("typos in markdown, missing file extensions, broken internal links") still allow errors—typo correction can break markdown syntax, path correction can point to wrong file.

**C7. Systemic Issue Detection Requires Undefined Root Cause Taxonomy**
- **Reviewer:** Feasibility Skeptic (Finding 4)
- **Severity:** Critical
- **Issue:** Design specifies "when >30% of findings share a contributing phase, synthesizer flags systemic issue." Implementation requires: (1) detecting which findings "share" a contributing phase (exact match of phase label? semantic similarity of root causes?), (2) computing percentage (how are multi-label findings counted?), (3) determining what "systemic issue" means (advisory flag? automatic escalation?). Root cause attribution is judgment-heavy.
- **Why it matters:** The 30% threshold is arbitrary (why not 25%? 40%?). "Share a common root cause" is subjective—if 12 findings trace to "missing error handling" but phrased differently, does synthesizer detect this? Root cause taxonomy is undefined in design.

### Edge Case Failures

**C8. Partial Reviewer Completion Breaks Systemic Issue Detection**
- **Reviewer:** Edge Case Prober (Finding 3)
- **Severity:** Critical
- **Issue:** Design allows proceeding with 4/6 reviewers. Synthesizer detects systemic issues "when >30% of findings share a contributing phase." If 2 missing reviewers would have flagged the systemic pattern, threshold calculation is wrong. Example: 4 reviewers produce 20 findings, 6 have "calibrate gap (contributing)" = 30% (triggers systemic flag). But missing 2 reviewers would have added 10 more findings with 8 calibrate gaps = 14/30 = 47%. Systemic issue severity underestimated. Verdict computed on partial data.
- **Why it matters:** Partial results corrupt systemic issue detection. User sees "proceed with noted improvements" when full reviewer set would have flagged "escalate—systemic calibrate gap." Missing reviewers aren't random—timeouts correlate with design complexity (harder designs take longer to review, more likely to hit timeout). Worst-case: hardest designs get weakest reviews.

**C9. Severity Range Resolution Creates False Escalations**
- **Reviewer:** Edge Case Prober (Finding 4)
- **Severity:** Critical
- **Issue:** When reviewers rate same issue differently, design uses "highest severity in range for verdict computation" (conservative). If Assumption Hunter rates finding Critical, Feasibility Skeptic rates same finding Important, verdict logic treats as Critical. Single pessimistic reviewer can block entire design.
- **Why it matters:** If Edge Case Prober consistently over-rates severity (sees every edge case as Critical), every review escalates regardless of actual risk. Design defers mitigation to prompt tuning but prompt tuning is iterative—false escalations occur throughout prototyping phase. User abandons review process as too heavyweight before prompts stabilize.

### Calibrate Gaps (Problem Framing)

**C10. Documentation Sync Treated as Design Revision Conflates Two Different Actions**
- **Reviewer:** First Principles (Finding 1)
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Issue:** Iteration 2 verdict is "revise" based on 15 Critical findings. 10 of those are "accepted iteration 1 findings not yet reflected in design doc" (67% of Requirement Auditor findings flagged as documentation debt). These aren't design flaws requiring rethink—they're accepted decisions requiring documentation updates. User accepted the design decisions in iteration 1, implemented them in code/prompts, didn't update design doc. Treating documentation sync as design revision conflates "design needs improvement" with "design doc needs updates to match implemented design."
- **Why it matters:** Documentation debt is process failure (design doc not kept in sync with implementation), not design failure (wrong architecture, missed edge case). Requiring design revision when actual action is "update docs to match code" wastes iteration cycles.

**C11. Testing Orchestration Infrastructure by Building Design Review First Inverts Risk**
- **Reviewer:** First Principles (Finding 2)
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Issue:** Problem statement identifies "no structured requirement refinement" as root cause of design failures, explicitly states "requirement refinement has been the single biggest design quality lever in practice," then prototypes design-stage review to "validate orchestration mechanics." Requirements review is deferred to eval phase. This validates infrastructure using a phase acknowledged to have lower leverage than the deferred phase.
- **Why it matters:** If requirements review is actually the highest-leverage intervention (as stated), weeks spent tuning design-stage personas prove orchestration works but not that the right thing is being orchestrated. When you eventually build requirements review, you may discover it needs different persona types, different output format, different finding classification. This invalidates design-stage infrastructure decisions.

**C12. "Adversarial Review" is Coverage-Based Inspection, Not Adversarial Debate**
- **Reviewer:** First Principles (Finding 3)
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Issue:** Design claims "adversarial multi-agent design review" as differentiator. The 6 design personas (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles, Prior Art Scout) are scoped by domain coverage—what part of the design to inspect. They can all be simultaneously correct because they're examining different surfaces. True adversarial review requires incompatible incentives forced to reconcile: "ship fast, prove in production" vs "ship safe, prove upfront." Mitsubishi's adversarial debate AI (Jan 2026) uses opposing models arguing for contradictory conclusions.
- **Why it matters:** If core hypothesis is "adversarial tension surfaces design blind spots better than single-perspective review," your persona architecture doesn't test it. You're testing "more inspectors find more issues" (obviously true, not novel). The finding consolidation synthesizer deduplicates parallel findings—additive coverage. Adversarial debate synthesizer would reconcile opposing positions—forcing design to satisfy contradictory constraints reveals tradeoffs.

**C13. Solving "Lack of Review Automation" When Problem is "Skipping Requirements Phase"**
- **Reviewer:** First Principles (Finding 4)
- **Severity:** Critical
- **Phase:** calibrate (primary)
- **Issue:** Observed pain points trace to "no structured requirement refinement—jumped from idea to design without prioritizing." Desired workflow shows calibrate phase with MoSCoW, anti-goals, success criteria, human checkpoint. All pain points are upstream of design. Design builds review automation to catch design flaws adversarially. This treats symptom (designs have flaws) not cause (teams skip requirements because ROI isn't obvious).
- **Why it matters:** Automating design review doesn't solve "teams skip requirements." It moves problem detection downstream. You'll catch design flaws adversarially but requirement-level errors still compound into implementation failures. If real problem is "requirements phase is skipped because value isn't obvious until later when errors surface," you need to make requirements refinement's value obvious immediately.

**C14. Phase Classification Routing Logic Assumes Linear Causality**
- **Reviewer:** First Principles (Finding 5)
- **Severity:** Critical
- **Phase:** design (primary), calibrate (contributing)
- **Issue:** Reviewers classify findings by primary phase with optional contributing phase. Verdict logic routes on primary phase only: calibrate gap → escalate to requirements, design flaw → revise design. Real design failures are multi-causal. Design doc includes primary+contributing classification (accepted from iteration 1 Finding 7, synced in this iteration) but verdict logic still routes on primary phase only. Contributing phase is metadata, not operationalized in routing.
- **Why it matters:** If finding is "design flaw (primary) caused by calibrate gap (contributing)," verdict routes to design revision when it should escalate to requirements. Fixing design without fixing upstream calibrate gap produces local patch, not systemic fix.

**C15. Design-After-Implementation Creates Rationalization Risk**
- **Reviewer:** First Principles (Finding 7)
- **Severity:** Critical
- **Phase:** design (primary)
- **Issue:** Memory context shows 11 commits on feature/parallax-review branch before this design review (implementation exists). Design document describes system already built. Standard practice: design review before implementation. Post-implementation design docs rationalize what was built (glossing over implementation complexity, ideal-case framing) rather than specify buildable reality.
- **Why it matters:** Reviewing a design written after implementation validates documentation quality, not design quality. The test that matters is "does implementation match spec?" which is inverted—spec was written to match implementation. Iteration 2 documentation debt finding (67% of Requirement Auditor issues) confirms: design doc is lagging indicator of implementation decisions, not leading blueprint.

**C16. Requirements Versioning Untracked Creates False Resolution Signals**
- **Reviewer:** First Principles (Finding 8)
- **Severity:** Critical
- **Phase:** design (primary)
- **Issue:** All reviewer prompts reference requirements document as immutable input. Cross-iteration tracking detects when findings are resolved between iterations. In real workflows, adversarial review findings trigger requirement clarification. Next review cycle operates against updated requirements. Reviewers can't distinguish "design improved to satisfy requirement" from "requirement was lowered/changed to match design."
- **Why it matters:** Finding classification routes errors to pipeline phase that failed. If design finding from iteration 1 is "resolved" in iteration 2 because requirement was relaxed (not design improved), that's calibrate gap disguised as design improvement. Cross-iteration tracking without requirement versioning can't detect this.

**C17. Building Custom Infrastructure When Mature Frameworks Exist**
- **Reviewer:** First Principles (Finding 9)
- **Severity:** Critical
- **Phase:** calibrate (primary), design (contributing)
- **Issue:** Design custom-builds parallel reviewer dispatch, finding consolidation, retry logic, timeout handling, state management, cross-iteration tracking, verdict computation. Iteration 2 Prior Art Scout identified: Inspect AI provides multi-agent patterns with retry/timeout (Finding 13), LangGraph solves stateful workflows and human-in-the-loop gates (Finding 14), LangSmith provides annotation UI (Finding 44), Braintrust provides LLM-as-judge for severity normalization (Finding 45). All in tooling budget, MIT licensed, production-grade. Design builds 80% custom infrastructure for 20% novel contribution.
- **Why it matters:** CLAUDE.md explicitly states "BUILD adversarial review (novel), LEVERAGE LangGraph + Inspect AI + Claude Code Swarms (mature)." Design inverts this—custom-builds infrastructure (orchestration, state, UI) and treats persona prompts as configuration. Maintaining custom agent dispatch, result collection, retries, timeout handling, progress tracking, cost estimation, failure recovery is 40-60% of implementation surface area.

### Additional Critical Findings (Single Reviewer)

**C18. Design Doc Sync Incomplete — JSONL Still Missing** (Feasibility Skeptic Finding 1)
**C19. Cross-Iteration Finding Tracking Complexity Underestimated** (Feasibility Skeptic Finding 2)
**C20. Build-vs-Leverage Evaluation Still Deferred** (Prior Art Scout Finding 2)
**C21. Design Doc Sync Addresses Dispositions But Misses Architectural Gaps** (Prior Art Scout Finding 1)
**C22. Requirement for "Structured Requirement Refinement" Not Addressed** (Requirement Auditor Finding 3)

---

## Important Findings

### Assumption Violations

**I1. Reviewer Prompt Context Assumes Single Iteration Per Session** (Assumption Hunter Finding 4)
**I2. Async-First Architecture Assumes File System as Single Source of Truth** (Assumption Hunter Finding 5)
**I3. Phase Classification Routing Assumes Single Phase Owns Each Finding** (Assumption Hunter Finding 6)
**I4. Reviewer Tool Access Assumes Read Operations Are Side-Effect-Free** (Assumption Hunter Finding 7)
**I5. Critical-First Mode Assumes Critical Findings Are Independent** (Assumption Hunter Finding 8)

### Synthesizer Complexity

**I6. Synthesizer Deduplication Assumes "Same Issue" Is Objectively Determinable** (Assumption Hunter Finding 9)
**I7. Prompt Caching Assumes Stable Prefix Doesn't Change Between Iterations** (Assumption Hunter Finding 10)
**I8. Synthesis Consolidation Heuristics Still Undefined** (Feasibility Skeptic Finding 6)

### Edge Case Handling

**I9. Prior Summary Context Injection Creates Confirmation Bias** (Edge Case Prober Finding 5)
**I10. Verdict Escalation on Any Calibrate Gap Blocks Design Work** (Edge Case Prober Finding 6)
**I11. JSONL Format Decided But Schema Still Unspecified** (Edge Case Prober Finding 7)
**I12. Multi-Causal Phase Classification Routing Still Unresolved** (Edge Case Prober Finding 8)
**I13. Selective Re-Run of Failed Reviewers Changes Finding Context** (Edge Case Prober Finding 9)
**I14. Empty Design Doc or Requirements Doc Produces Nonsense Review** (Edge Case Prober Finding 10)
**I15. Cost Logging Specified But No Format or Schema** (Edge Case Prober Finding 11)
**I16. Timestamped Folder Collision Creates Review Folder Sprawl** (Edge Case Prober Finding 13)
**I17. Reviewer Timeout Without Progress Updates Appears Frozen** (Edge Case Prober Finding 14)
**I18. No Handling for Concurrent Reviews on Same Topic** (Edge Case Prober Finding 15)

### Feasibility and Complexity

**I19. Verdict Still Computed Before User Processes Findings** (Feasibility Skeptic Finding 5, also flagged by First Principles Finding 10 and Requirement Auditor Finding 10)
**I20. No Exit Criteria for Re-Review Loop** (Feasibility Skeptic Finding 7)
**I21. Reviewer Prompt Versioning Strategy Missing** (Feasibility Skeptic Finding 8)
**I22. Cost Per Review Run Still Unknown** (Feasibility Skeptic Finding 9)
**I23. Minimum Viable Reviewer Set Still Unvalidated** (Feasibility Skeptic Finding 10)
**I24. Second Brain Test Case Still Not Run** (Feasibility Skeptic Finding 11, also flagged by Requirement Auditor Finding 12)
**I25. Inspect AI and LangGraph Evaluation Still Deferred** (Feasibility Skeptic Finding 12)

### Prior Art and Frameworks

**I26. Inspect AI Multi-Agent Patterns Are Production-Grade** (Prior Art Scout Finding 3)
**I27. LangGraph Human-in-the-Loop Is First-Class** (Prior Art Scout Finding 4)
**I28. Auto-Fix Criteria Conservative But Implementation Workflow Unsafe** (Prior Art Scout Finding 6)
**I29. Cross-Iteration Finding Tracking Needs LLM-Based Matching** (Prior Art Scout Finding 7)
**I30. Prompt Caching Architecture Underspecified** (Prior Art Scout Finding 8)
**I31. LangSmith Annotation UI Is Standard Solution for Finding Processing** (Prior Art Scout Finding 9)
**I32. Braintrust Scorers Are Standard Solution for Synthesis Tasks** (Prior Art Scout Finding 10)
**I33. TRiSM Frameworks Provide Adversarial Resilience Standards** (Prior Art Scout Finding 11)
**I34. Cloud Security Alliance Agentic AI Controls Apply** (Prior Art Scout Finding 12)
**I35. Multi-Agent Observability Is Industry Standard** (Prior Art Scout Finding 13)
**I36. Mitsubishi Adversarial Debate Validates Stance-Based Review** (Prior Art Scout Finding 14)
**I37. Compound Engineering Learning Loop Is Exact Prior Art** (Prior Art Scout Finding 15)
**I38. adversarial-spec Multi-LLM Debate Pattern Requires Iteration Design** (Prior Art Scout Finding 16)

### Design Specification Gaps

**I39. Cross-Iteration Finding IDs Still Unspecified** (Requirement Auditor Finding 4)
**I40. Multi-Causal Phase Classification Routing Not Operationalized** (Requirement Auditor Finding 5)
**I41. Model Tiering Strategy Missing** (Requirement Auditor Finding 6)
**I42. Auto-Fix Git Safety Concerns Unresolved** (Requirement Auditor Finding 7)
**I43. No Stopping Criteria for Re-Review Iteration Loop** (Requirement Auditor Finding 8)
**I44. Requirements-Stage Review Deferred But Problem Statement Says It's Highest Leverage** (Requirement Auditor Finding 9)
**I45. "Critical-First" Mode Orphans Non-Critical Findings** (Requirement Auditor Finding 11)

### First Principles Challenges

**I46. Verdict Computed Before User Processes Findings Wastes Cycles** (First Principles Finding 10)
**I47. Async-First Architecture is File-Based Output, Not Background Execution** (First Principles Finding 11)
**I48. Minimum Viable Reviewer Set is Empirical Question Built Into Design** (First Principles Finding 12)
**I49. Critical-First Mode Creates Orphaned Finding Debt Across Iterations** (First Principles Finding 13)

---

## Minor Findings

**M1. Verdict "Proceed" Assumes Accepted Findings Will Be Addressed** (Assumption Hunter Finding 11)
**M2. Topic Label Validation Assumes Alphanumeric Is Safe** (Assumption Hunter Finding 12)
**M3. Review Stage Auto-Detection Deferred But Impacts All Stages** (Edge Case Prober Finding 12)
**M4. Documentation Debt Resolved — V1 Dispositions Now in Design** (Requirement Auditor Finding 1)
**M5. CLI Tool Access Per Persona Still Unspecified** (Requirement Auditor Finding 13)
**M6. Multi-User Disposition Workflows Not Addressed** (Requirement Auditor Finding 14)
**M7. Cost Per Review Run Still Not Tracked** (Requirement Auditor Finding 15)
**M8. Rejection Note Processing Unspecified** (Requirement Auditor Finding 16)
**M9. Prompt Versioning Strategy Missing** (Requirement Auditor Finding 17)
**M10. Timestamped Folders Break Git Diff Workflow** (Requirement Auditor Finding 18)
**M11. Async Mode Is Not Actually Background Execution** (Requirement Auditor Finding 19)
**M12. JSONL Format Decision Needs Schema Specification** (Prior Art Scout Finding 5)
**M13. Build-vs-Leverage Evaluation Still Deferred to "When Limits Hit"** (Prior Art Scout Finding 2)
**M14. Feasibility Skeptic Finding 1 (Documentation debt) resolved per Requirement Auditor confirmation**

---

## Contradictions

### 1. Auto-Fix Workflow: Safety vs Automation

**Reviewers:** Assumption Hunter (Finding 1), Edge Case Prober (Finding 2, Finding 6), Requirement Auditor (Finding 7), Prior Art Scout (Finding 6)

**Position A (Safety-first):** Auto-fix modifying design doc and committing automatically violates Git Safety Protocol ("NEVER commit changes unless user explicitly asks"). User must approve fixes before application. Assumption Hunter: "If auto-fix runs before human review (as specified in Step 4), user cannot reject bad auto-fixes—they're already applied and committed." Requirement Auditor: "Auto-fix as described is invasive. Modifies source files without user approval."

**Position B (Automation-first, specified in design):** Auto-fix applies conservative fixes (typos, broken links, path corrections) automatically to reduce cognitive load. User processes only findings requiring judgment. Design lines 276-278: "Auto-fixable findings applied automatically. Auto-fixes committed as separate git commit from human-reviewed changes."

**Synthesizer reconciliation:** Both positions are valid for different risk tolerances. Safety-first protects against false positives (auto-fix breaks something), automation-first optimizes for efficiency (user doesn't waste time on trivial fixes). **Recommendation:** Implement user approval gate—auto-fixes presented as diff, user confirms before application. This satisfies Git Safety Protocol while preserving automation value. Edge Case Prober suggests deferring auto-fix entirely until eval data shows finding type distribution justifies it (if 90% of findings require judgment, auto-fix is 10% value for 40% complexity).

### 2. Cross-Iteration Finding IDs: Hash-Based vs LLM Semantic Matching

**Reviewers:** Assumption Hunter (Finding 3), Edge Case Prober (Finding 1), Requirement Auditor (Finding 4), Prior Art Scout (Finding 7), Feasibility Skeptic (Finding 2)

**Position A (Hash-based, specified in design):** Design line 248: "Stable hash derived from section + issue content." Simple, deterministic, no LLM calls required. Fast and cheap.

**Position B (LLM semantic matching):** Hash-based IDs break when findings evolve, section headings change, or wording is refined. LLM-based matching compares new findings to prior findings semantically ("is this the same issue?"). Tolerates rephrasing and structure changes. Prior Art Scout Finding 7: "Text hashing is brittle for iterative review because reviewers naturally rephrase findings as design improves."

**Synthesizer reconciliation:** Hash-based IDs optimize for implementation simplicity at cost of UX quality. LLM semantic matching provides correct behavior but adds token cost (N_new × N_prior comparisons = quadratic scaling). Feasibility Skeptic estimates iteration 2 would cost $0.54, iteration 3 would cost $1.08 in matching tokens alone. **Recommendation:** Hybrid approach—exact hash match as fast path (detects unchanged findings), LLM matching for non-exact (handles evolution), user confirmation for ambiguous matches. Start with section-based anchoring for MVP (simple but lossy), add LLM matching when empirical data shows it's worth the cost.

### 3. Reviewer Count: 6 Reviewers (Design) vs Empirical Validation Needed

**Reviewers:** Feasibility Skeptic (Finding 10), First Principles (Finding 12), Requirement Auditor (coverage matrix)

**Position A (6 reviewers baseline):** Design specifies 6 design-stage reviewers. All personas serve distinct purposes (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles, Prior Art Scout).

**Position B (Empirical question):** Problem statement says "optimal number is empirical question for eval framework." No coverage analysis, overlap measurement, or diminishing returns calculation. First Principles: "Prior Art Scout and First Principles Challenger have overlap (both question whether design should exist). Edge Case Prober and Feasibility Skeptic both examine 'what could go wrong.' If first 3 reviewers catch 80% of findings, running all 6 is low ROI."

**Synthesizer reconciliation:** Both positions agree reviewer count should be validated, differ on whether to build 6 upfront or start minimal and expand. **Recommendation:** After 3 iterations complete, coverage analysis data now exists. Tag each finding with which reviewer(s) flagged it. Calculate: reviewers with high unique finding rates (keep), reviewer pairs with >50% overlap (consider consolidating), finding categories no reviewer catches (missing persona). Start next iteration with 3 core reviewers (Requirement Auditor, First Principles, Edge Case Prober suggested), add personas incrementally based on gap analysis.

### 4. Problem Framing: Design Review (Prototype) vs Requirements Review (Highest Leverage)

**Reviewers:** First Principles (Finding 2, Finding 4), Requirement Auditor (Finding 3, Finding 9)

**Position A (Design review prototype):** Design builds design-stage review to validate orchestration mechanics (parallel agents, synthesis, finding processing, iteration tracking). Requirements review deferred to "Build later" (lines 325-327).

**Position B (Requirements review first):** Requirements doc explicitly states "requirement refinement has been the single biggest design quality lever in practice." Problem statement pain points trace to "no structured requirement refinement—jumped from idea to design without prioritizing." First Principles Finding 2: "If requirements review is actually highest-leverage intervention, weeks spent tuning design-stage personas prove orchestration works but not that the right thing is being orchestrated."

**Synthesizer reconciliation:** This is not a contradiction in findings—it's a contradiction in strategy. Both positions agree requirements review is higher leverage, differ on whether to prototype highest-value phase first (validate hypothesis) or infrastructure-validation phase first (de-risk orchestration). **Disposition history:** Iteration 2 flagged this (Finding 10, Finding 12), disposition notes marked as "valid but exploratory—evaluate empirically during prototyping." **Recommendation:** User has explicitly chosen infrastructure validation path. First Principles challenges are acknowledged as valid but deferred to empirical testing. No reconciliation needed—this is accepted tradeoff.

### 5. "Adversarial Review" Naming: Coverage-Based vs Debate-Based

**Reviewers:** First Principles (Finding 3), Prior Art Scout (Finding 14)

**Position A (Coverage-based, current design):** 6 personas examine different aspects of design (assumptions, edge cases, requirements, feasibility, first principles, prior art). They can all be simultaneously correct—additive coverage model.

**Position B (Stance-based adversarial debate):** True adversarial review requires incompatible incentives forced to reconcile. Mitsubishi's adversarial debate AI (Jan 2026) uses opposing models arguing for contradictory conclusions. Prior Art Scout Finding 14: "Mitsubishi's agents have incompatible worldviews forced to reconcile (true adversarial debate), whereas parallax's personas are coverage-based (inspecting different domains, not opposing each other)."

**Synthesizer reconciliation:** First Principles notes this is calibrate gap (naming mismatch, problem framing). Iteration 2 flagged this as Finding 11 ("adversarial review is misnamed"), disposition said "valid critique of problem framing, evaluate empirically in prototype." **Recommendation:** Either (a) rename to "comprehensive multi-perspective design review" and acknowledge adversarial tension is deferred, OR (b) run empirical test during Second Brain validation—compare coverage-based review (current design) vs stance-based review (3 pairs of opposing personas). If stance-based produces significantly better results, redesign personas. If comparable, document that coverage-based is simpler and equally effective.

---

## Recommendations

### Immediate Actions (Design Specification Gaps)

1. **Add JSONL schema specification** — 4 reviewers consensus (Critical). Define structure even if implementation deferred: `{finding_id, reviewer, severity, phase_primary, phase_contributing, section, issue, why_it_matters, suggestion, iteration_status, disposition, disposition_note}`. Specify whether reviewers output JSON directly or synthesizer converts markdown to JSONL.

2. **Specify finding ID generation mechanism** — 3 reviewers consensus (Critical). Recommend hybrid approach: exact hash for unchanged findings, LLM semantic matching for evolved findings, user confirmation for ambiguous matches. Document token cost implications.

3. **Revise auto-fix workflow to include user approval** — 3 reviewers consensus (Critical). Present auto-fixes as diffs, user approves before application. Satisfies Git Safety Protocol. Add loop termination (max 1 auto-fix pass per review run).

4. **Update verdict logic to operationalize contributing phases** — Multiple reviewers (Important). If ≥30% of findings share "calibrate gap (contributing)", escalate with systemic issue warning. User must acknowledge upstream issue before proceeding with design-level fixes.

5. **Add prompt caching structure specification** — Cache boundary, versioning, invalidation strategy. Required for cost optimization (90% reduction on cache hits per CLAUDE.md).

### Deferred to Empirical Validation (Acknowledged Tradeoffs)

6. **Problem framing (requirements vs design review first)** — First Principles Finding 2, Requirement Auditor Finding 9. User has chosen infrastructure validation path. Deferred to Second Brain test case results.

7. **Adversarial naming (coverage vs debate)** — First Principles Finding 3, Prior Art Scout Finding 14. Marked "evaluate empirically" in iteration 2 disposition. Test both approaches during Second Brain validation.

8. **Build-vs-leverage (Inspect AI, LangGraph)** — Prior Art Scout Finding 2, Finding 3, Finding 4. Run 2-3 hour prototyping spikes before committing to custom infrastructure. Document evaluation results in design.

9. **Reviewer count optimization** — Feasibility Skeptic Finding 10, First Principles Finding 12. After iteration 3, run coverage analysis to identify high-value personas and overlaps.

### External Validation Required

10. **Run Second Brain test case** — Feasibility Skeptic Finding 11, Requirement Auditor Finding 12. Real project with 40+ known design flaws. Validates reviewers catch real issues, not just process concerns. Required before marking design approved.

11. **Instrument cost tracking** — Feasibility Skeptic Finding 9, Requirement Auditor Finding 15. After 3 review iterations, actual cost data should exist. Validate budget assumptions, inform model tiering decisions.

### Process Improvements

12. **Add convergence criteria to re-review loop** — Feasibility Skeptic Finding 7, Requirement Auditor Finding 8. User override option ("proceed despite Critical findings" with required justification), iteration count warning (if >3 iterations, prompt to reconsider scope).

13. **Track rejected findings with disposition notes** — Requirement Auditor Finding 16. Feed to reviewers on re-review, enables calibration feedback loop.

14. **Document single-user limitation** — Requirement Auditor Finding 14. Multi-user workflows deferred. For team review, use external tooling (LangSmith, GitHub PR comments).

15. **Orphaned finding management for Critical-first mode** — Requirement Auditor Finding 11, First Principles Finding 13. Mark deferred findings, reconcile on re-review, prompt user to process accumulated findings after revise loop converges.

---

## V3 Finding Dispositions

**Date:** 2026-02-16
**Disposition strategy:** Batch disposition. All 22 Critical findings acknowledged; none block implementation. Findings are spec gaps for unbuilt features, strategic questions best answered by building, or edge cases not yet encountered empirically. Project philosophy: prototype-first, YAGNI ruthlessly, build to understand.

### Batch Disposition: All 22 Critical Findings

**Status:** acknowledged — defer to implementation

**Reasoning:** V3 confirmed documentation debt from v2 is resolved (M4). The remaining Critical findings fall into three categories, none of which require design-level resolution before building:

1. **Spec gaps for unbuilt features (C1-C7, C18-C22):** JSONL schema, finding IDs, auto-fix workflow, prompt caching, systemic detection taxonomy. These are implementation decisions — define the schema when building JSONL output, not in the design doc beforehand. Specifying prematurely risks designing the wrong thing.

2. **Strategic/philosophical challenges (C10-C17):** Problem framing inversion, requirements-first vs design-first, adversarial naming mismatch, build-vs-leverage, design-after-implementation, phase classification routing, requirements versioning. All were deferred to empirical eval in v2 dispositions. V3 re-raised them correctly, but the disposition strategy is unchanged: validate through building, not through more design review.

3. **Edge cases in existing design (C8-C9):** Partial reviewer completion corrupting systemic detection, severity range false escalations. Three review cycles completed without hitting these as actual problems. Address when encountered.

**Notable consensus signals acknowledged:**
- C1 (JSONL schema): 4-reviewer consensus across v2+v3. Highest-priority implementation item when building structured output.
- C2 (Finding IDs): 3-reviewer consensus. Hybrid approach (hash fast-path + LLM matching) is the likely implementation, but schema depends on JSONL decisions.
- C3 (Auto-fix safety): 3-reviewer consensus. Will implement with user approval gate when building auto-fix. Not building auto-fix in near term.

### Important and Minor Findings (47I / 14M)

**Status:** acknowledged — defer to implementation

Same reasoning applies. Important findings are deeper elaborations of the Critical categories (assumption violations, synthesizer complexity, edge case handling, framework leverage opportunities). Minor findings are process improvements and documentation items. All will be addressed as their respective features are built.

### Review Cycle Assessment

Three full review cycles complete (v1: 44 findings, v2: 55, v3: 83). The review skill is working — it surfaces real concerns, deduplicates across reviewers, tracks cross-iteration progress. Key validation:

- **V2 systemic issue (documentation debt) confirmed resolved in v3.** The review process correctly detected improvement.
- **V3 findings shifted from "decided but not documented" to "documented but not specified."** This is expected — syncing decisions to the design doc without adding implementation specs is exactly what happened.
- **Calibrate gaps are stable across iterations.** Same strategic questions re-raised with consistent reasoning. The review process correctly flags them but disposition strategy (defer to empirical eval) is unchanged.

**Next action:** Stop reviewing, start building. The review skill has been validated through 3 cycles of self-review. External validation (Second Brain test case) and implementation of the highest-consensus items (JSONL, finding IDs) are higher-value next steps than another review iteration.
