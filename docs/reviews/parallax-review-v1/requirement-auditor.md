# Requirement Auditor Review

## Changes from Prior Review
This is a re-review of the parallax:review design after Task 8 (prompt iteration). The prior review produced 41 findings (8C/22I/11M). This review examines:
1. Which prior findings were resolved by the design updates
2. Whether new gaps emerged from the changes
3. Whether any prior findings remain unaddressed

**Key changes between iterations:**
- Reviewer agent prompts refined based on smoke test feedback
- Synthesizer role reframed as judgment-exercising (not "purely editorial")
- Review skill updated for async-first workflow, reject-with-note, topic validation
- Finding dispositions and UX friction log from smoke test committed

## Coverage Matrix

| Requirement | Addressed? | Design Section | Notes |
|---|---|---|---|
| **Orchestration Requirements** |
| Multi-phase pipeline (survey → calibrate → design → review → plan → execute) | Partial | Prototype Scope | Design builds review skill only. Full orchestrator deferred. Phase 1 of multi-phase plan. |
| Human checkpoints at phase boundaries | Yes | UX Flow Step 6 | Proceed/revise/escalate verdict requires human approval before next phase. |
| Parallel subagent reviews | Yes | Step 2: Dispatch | 6 reviewers dispatched in parallel. |
| Automatic finding consolidation and deduplication | Yes | Synthesis | Synthesizer consolidates, deduplicates, classifies findings. |
| Severity normalization across reviewers | No | **MISSING** | Reviewers assign severity independently. When they disagree, design reports range but no normalization. Verdict uses highest severity (conservative). Finding 8 accepted this, no mechanism change. |
| **Requirement Refinement Requirements** |
| MoSCoW prioritization | No | Out of scope | Deferred to parallax:calibrate (not yet designed). |
| Anti-goals explicitly defined | No | Out of scope | Deferred to parallax:calibrate. |
| Success criteria | No | Out of scope | Deferred to parallax:calibrate. |
| Assumption/constraint documentation | Partial | Reviewer Personas | Assumption Hunter checks design assumptions. Requirements-level assumptions not in scope (calibrate phase). |
| Outcome-focused requirement definition | No | Out of scope | Deferred to parallax:calibrate. |
| **Iteration Loop Requirements** |
| Auto-fix trivial findings | No | **MISSING** | Finding 4 (Critical) from prior review flagged this. Accepted as required, but design not yet updated. |
| Track findings across iterations | Partial | **INCOMPLETE** | Finding 5 (Critical) from prior review. Disposition: stable finding IDs + prior summary fed to reviewers. Design doc not yet updated with mechanism. |
| Escalate non-trivial findings to human | Yes | Verdict Logic | Revise/escalate verdicts require human processing of findings. |
| ADR-style finding documentation | Yes | Output Artifacts | Findings include Issue/Why it matters/Suggestion. Dispositions tracked in summary. |
| Archive plans when restarting cycles | No | Out of scope | Plan-phase concern, not design-phase. |
| **Finding Classification Requirements** |
| Classify by pipeline phase (survey/calibrate/design/plan) | Yes | Finding Phase Classification | Four-phase classification with escalation to upstream phases. |
| Route findings to failed phase | Yes | Verdict Logic | Escalate verdict for survey/calibrate gaps routes to upstream phase. |
| Distinguish bug/style from spec problems | Yes | Finding Phase Classification | Design flaws vs calibrate gaps vs survey gaps. |
| Self-error-detecting (implementation errors reveal spec problems) | Yes | Verdict Logic | Escalation mechanism treats upstream failures as success signal, not failure. |
| **Subagent Architecture Requirements** |
| Parallel review execution | Yes | Step 2: Dispatch | 4-6 reviewers in parallel depending on stage. |
| Sharp, specific persona prompts | Partial | Reviewer Personas | Table defines focus areas. Prompts refined in Task 8 but design doc not updated to include prompt architecture section. Finding 3 flagged this. |
| Non-overlapping blind spots | Yes | Reviewer Personas, Persona Activation Matrix | 9 personas across 3 stages, each with distinct focus. |
| Persona engineering (Instruction Sharpener/Position Mapper) | No | **MISSING** | Requirements doc mentions this as approach during authoring. Design doesn't specify prompt engineering methodology. |
| Prompt structure for caching (stable prefix + variable suffix) | No | **MISSING** | Finding 3 (Critical) from prior review. Accepted as required. Design not yet updated. |
| **Output Requirements** |
| Direct, engineer-targeted voice | Partial | Per-Reviewer Output Format | Format specified (markdown structure). Voice rules mentioned in Task 8 but not in design doc. Finding 23 flagged this. |
| Lead with verdict, not analysis | Yes | Summary Format | Verdict precedes finding details. |
| SRE-style framing (blast radius, rollback, confidence) | Partial | Per-Reviewer Output Format | "Why it matters" captures impact. Blast radius quantification not enforced. Voice rules in prompts but not documented. |
| No hedging language | Partial | Voice rules in prompts | Task 8 added to agent prompts. Not documented in design. |
| **Tooling Requirements** |
| CLI-first | No | **MISSING** | Finding 21 flagged this. No tooling section in design. Which CLI tools available to reviewers unspecified. |
| Portability sanity check (Claude + Codex) | No | **DEFERRED** | Finding 22 flagged. Disposition: defer to eval phase. |
| Prompt caching for cost reduction | No | **MISSING** | Finding 3. Architectural decision required, not implemented. |
| **Document Chain Requirements** |
| Self-consuming (prior review artifacts as input) | Partial | **INCOMPLETE** | Finding 5 (cross-iteration tracking) and Finding 20 (self-consumption mechanism). Disposition accepted, design not updated. |
| RFC-like consolidation of pipeline artifacts | No | **MISSING** | Finding 24. Disposition: defer, JSONL rendering may naturally produce this. |
| **Human Checkpoint Requirements** |
| After requirement refinement | No | Out of scope | Requirements stage not yet designed. |
| After design review converges | Yes | Step 6: Wrap Up | Proceed/revise/escalate requires human decision. |
| After plan review converges | No | Out of scope | Plan stage prototype not yet built. |
| Never auto-proceed past checkpoint | Yes | Verdict Logic | All verdicts require human processing of findings. |
| **Cost/Budget Requirements** |
| $2000/month budget awareness | Partial | Open Questions | Cost acknowledged as eval question. Finding 11 flagged missing cost visibility. |
| Batch API for non-interactive runs | No | **MISSING** | Not addressed in design. |
| Prompt caching (90% input cost reduction) | No | **MISSING** | Finding 3. Architectural decision, not implemented. |
| Model tiering (Haiku/Sonnet/Opus) | Partial | Prototype uses Sonnet | Default Sonnet specified. Finding 40 suggests testing Haiku for mechanical personas. Not designed. |

## Findings

### Finding 1: Accepted Critical Findings Not Yet Reflected in Design Doc
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Entire design doc (multiple sections need updates)
- **Issue:** Prior review produced 8 Critical findings, all accepted by user with disposition notes. Task 8 (prompt iteration) updated agent prompts and skill code, but the design doc at `docs/plans/2026-02-15-parallax-review-design.md` was not updated to reflect these decisions. Specifically: Finding 3 (prompt caching architecture), Finding 4 (auto-fix mechanism), Finding 5 (cross-iteration tracking), Finding 6 (discuss mode cut from MVP), Finding 7 (phase classification by primary+contributing), Finding 8 (severity range handling). The design doc still describes "discuss" mode (cut), doesn't specify auto-fix step (added), doesn't include prompt architecture section (required).
- **Why it matters:** The design doc is the authoritative specification for implementation. If it doesn't reflect accepted design decisions, it's out of date and future implementers (or eval framework) will build the wrong thing. This is documentation debt that invalidates the design-as-spec. Git commits show code/prompts were updated, but design doc wasn't. Coverage matrix shows 6 requirements flagged as "MISSING" or "INCOMPLETE" where dispositions say "accepted" but design doesn't reflect them.
- **Suggestion:** Update design doc to reflect all accepted Critical findings. Add sections: (1) "Prompt Architecture" (Finding 3 - caching structure), (2) "Auto-Fix Step" in synthesis section (Finding 4), (3) "Cross-Iteration Tracking Mechanism" (Finding 5), (4) Remove or mark "discuss" mode as future/deferred (Finding 6), (5) Update "Finding Phase Classification" to specify primary+contributing phases (Finding 7), (6) Update "Verdict Logic" to clarify severity range handling (Finding 8). Treat design doc as living spec, not snapshot.
- **Iteration status:** New finding (meta-finding about documentation debt from accepted prior findings)

### Finding 2: Auto-Fix Requirement Still Not Designed
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Synthesis, UX Flow (missing auto-fix step)
- **Issue:** Prior review Finding 4 flagged "Auto-fix requirement completely missing" (Critical severity). User accepted with disposition note: "Auto-fix step between synthesis and human processing. Git history must show auto-fixes as separate commit from human-reviewed changes, enabling async review of what was auto-applied." Design doc still shows synthesis → human processing flow with no auto-fix step. No specification for: (1) how findings are classified as auto-fixable, (2) what criteria define "auto-fixable", (3) which agent performs auto-fixes, (4) how fixes are validated before applying, (5) commit strategy for auto-fixes vs human-reviewed changes.
- **Why it matters:** This was explicitly required by problem statement ("After adversarial review, auto-fix trivial findings and re-review") and flagged Critical in prior review. User accepted it as required. Without this, humans must manually process obvious fixes (typos, broken links, path corrections), defeating automation value. The disposition note specifies a key architectural decision (separate commits for async review) that's not in the design. Coverage matrix marks this as "MISSING" — requirement exists, design doesn't address it.
- **Suggestion:** Add "Auto-Fix" section to design specifying: (1) Classification criteria (conservative MVP: typos in markdown, missing file extensions, broken internal links, path corrections based on repo structure), (2) Auto-fix agent responsibilities (apply fixes, write updated design to disk, commit separately with message "auto-fix: [summary]"), (3) Validation (re-run subset of reviewers on auto-fixed sections to verify fix didn't break anything), (4) UX flow update: synthesis → auto-fix → commit auto-fixes → human processing of remaining findings → commit human-reviewed changes. Two distinct commits per cycle enables async review transparency.
- **Iteration status:** Still an issue (was Finding 4 in prior review, accepted but not yet implemented in design)

### Finding 3: Cross-Iteration Finding Tracking Mechanism Still Incomplete
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Synthesis, UX Flow, Output Artifacts
- **Issue:** Prior review Finding 5 flagged "Cross-iteration finding tracking incomplete" (Critical severity). User accepted with disposition: "Stable finding IDs, status tracking across iterations, prior summary fed to reviewers on re-review." Finding 17 also flagged re-review producing identical findings due to no iteration context. Design doc still has no mechanism for: (1) generating stable finding IDs (hash of section + issue? manual tagging?), (2) storing finding status across iterations (open/addressed/rejected), (3) feeding prior summary to reviewers (as part of reviewer prompt context?), (4) detecting which findings from iteration N are resolved in iteration N+1.
- **Why it matters:** Requirements doc explicitly states "Track which findings have been addressed across iterations." Without this, re-reviews waste human time cross-referencing "did we fix what Assumption Hunter flagged last time?" Edge Case Prober's prior Finding 17 notes reviewers won't focus scrutiny on changed sections where bugs are likely. The disposition specifies the solution (stable IDs + prior summary as input) but design doesn't implement it. Coverage matrix marks "Track findings across iterations" as Partial/INCOMPLETE.
- **Suggestion:** Add "Finding Persistence Mechanism" section specifying: (1) Finding ID generation (hash of finding title + section reference, stable across iterations), (2) Status field in summary.md (open/addressed/rejected/partial), (3) Reviewer context update: include prior summary.md in reviewer prompts with instruction "Flag whether prior findings are resolved, still issues, or new findings", (4) Synthesizer cross-iteration diff: "Iteration 2 resolved Findings 1, 3, 5 from Iteration 1. Findings 2, 4 remain open. 8 new findings." (5) Git diff integration: highlight changed sections to reviewers so they focus scrutiny where it matters.
- **Iteration status:** Still an issue (was Finding 5 + Finding 17 in prior review, accepted but design not updated)

### Finding 4: Prompt Caching Architecture Still Not Specified
- **Severity:** Critical
- **Phase:** design (primary)
- **Section:** Missing (should be "Reviewer Prompt Architecture" section)
- **Issue:** Prior review Finding 3 flagged "Prompt caching architecture not addressed" (Critical severity). Requirements doc states "Prompt structure for caching: System prompts should be structured as stable cacheable prefix + variable suffix. This is an architectural convention, not a feature — 90% input cost reduction on cache hits. Decide before building skills." User accepted finding with disposition note acknowledging it's a design-time decision. Task 8 prompt iteration happened but design doc has no section specifying prompt architecture. Coverage matrix shows "Prompt structure for caching" and "Prompt caching for cost reduction" both marked MISSING. This is a structural decision that affects how all reviewer prompts are authored.
- **Why it matters:** This affects how reviewer prompts are written. If prompts aren't structured for caching from start, refactoring later invalidates eval data (all prior runs used different prompt structure, not comparable). Finding 19 from prior review identified the iteration tradeoff: prompt changes during prototyping invalidate cache. Disposition was "design the cache-friendly structure now, defer optimization until prompts stabilize." Without this in the design, prompt authors don't know the structure rules. Cost strategy in CLAUDE.md explicitly relies on prompt caching for 90% cost reduction — this is architectural, not optional.
- **Suggestion:** Add "Reviewer Prompt Architecture" section specifying: (1) Stable prefix structure (persona identity, focus areas, methodology, output format rules, voice guidelines), (2) Variable suffix structure (design artifact being reviewed, requirements context, prior review summary if re-review, iteration number), (3) Cache boundary (where prefix ends, suffix begins), (4) Prompt versioning (changes to prefix invalidate cache, track prompt version in output metadata), (5) Prototyping tradeoff acknowledgment (defer cache optimization until prompts stabilize post-MVP, but design structure now so it's refactor-ready). This documents the architectural constraint without prematurely optimizing.
- **Iteration status:** Still an issue (was Finding 3 in prior review, accepted but design not updated)

### Finding 5: Severity Normalization Requirement Not Addressed
- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Verdict Logic, Synthesis (severity ranges)
- **Issue:** Requirements doc states "Severity normalization across reviewers" as orchestration requirement. Prior review Finding 8 flagged "Verdict logic ambiguous with severity ranges" (Critical, later accepted). Disposition was "Conservative — use highest severity in range for verdict logic. If false escalations become a problem, investigate per-agent prompt tuning first, then severity normalization as fallback." Design still has no severity normalization mechanism. When reviewers disagree on severity (e.g., "Critical by Assumption Hunter, Important by Feasibility Skeptic"), synthesizer reports range but doesn't normalize. Verdict logic uses highest severity, but this is implicit behavior not explicitly specified in design doc. Coverage matrix marks "Severity normalization" as NO / MISSING.
- **Why it matters:** Requirements explicitly ask for normalization. Design chose not to normalize (conservative approach: use highest severity). This is a valid design decision but contradicts the stated requirement. Either (1) requirement is wrong (normalization not actually needed, conservative escalation is correct), which makes this a calibrate gap, or (2) design is incomplete (should normalize but doesn't), which is a design flaw. User's disposition suggests this is acceptable for MVP but acknowledges it might need fixing if false escalations occur. Requirement-design mismatch unresolved.
- **Suggestion:** Either (1) Update requirements to clarify normalization is optional/deferred (treat as calibrate gap — requirement was overconstrained), or (2) Add severity normalization mechanism to design (weighted consensus, majority vote, persona authority tiers). Recommend option 1: update requirements doc to say "severity normalization deferred pending empirical data on false escalation rates" and mark as future enhancement. Document the conservative approach (highest severity wins) explicitly in Verdict Logic section.
- **Iteration status:** New finding (requirement-design mismatch on severity handling)

### Finding 6: Discuss Mode Still in Design Doc Despite Being Cut
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Step 5: Process Findings, UX Flow
- **Issue:** Prior review Finding 6 flagged "Discuss mode state management underspecified" (Critical, 4 reviewers). User disposition: "Cut 'discuss' from MVP. Replace with reject-with-note — rejection note becomes calibration input to next review cycle. Evaluate adding real discussion mode in v2 if eval data shows rejected findings aren't being addressed." Design doc still describes discuss mode as "first-class interaction" where "user can explore a finding in depth, ask questions, challenge the reviewer's reasoning" and "skill maintains its position in the finding queue and resumes after discussion resolves." This contradicts the implementation decision. Step 5 lists three options: Accept / Reject / Discuss. Should be Accept / Reject (with note).
- **Why it matters:** Design doc is the spec. If it says discuss mode exists, implementers will build it or be confused why code doesn't match spec. This is documentation debt from the disposition decision. Causes implementation confusion and wastes effort. Reject-with-note pattern was implemented in Task 8 skill updates but design wasn't updated to reflect this.
- **Suggestion:** Update Step 5: Process Findings to remove discuss mode. Replace with: "For each finding, presented one at a time: (1) Accept — finding is valid, will address; (2) Reject (with note) — finding is wrong or not applicable, note becomes feedback for reviewer tuning and calibration input to next review cycle." Add note: "Full discussion mode deferred to v2 pending eval data on whether reject-with-note addresses finding quality concerns." Update UX flow description to remove discuss mode references.
- **Iteration status:** Still an issue (was Finding 6 in prior review, cut per disposition but design doc not updated)

### Finding 7: Primary + Contributing Phase Classification Not in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Finding Phase Classification
- **Issue:** Prior review Finding 7 flagged "Phase classification errors could route to wrong pipeline stage" (Critical, 2 reviewers). User disposition accepted both suggestions: "(1) Reviewers suggest phase in their findings, synthesizer reconciles disagreements with reasoning. User can override. (2) Classify by primary + contributing phases — 'design flaw (primary) caused by calibrate gap (contributing).' Systemic issue detection when >30% share root cause. Track classification accuracy in eval framework." Design doc still shows single-phase classification (survey gap, calibrate gap, design flaw, plan concern) with no mention of primary+contributing dual classification or systemic issue detection threshold.
- **Why it matters:** Phase classification is the core novel contribution per CLAUDE.md — "finding classification routes errors back to the pipeline phase that failed." If design doesn't implement the accepted classification refinement (primary+contributing phases), it's less effective at routing multi-causal findings. First Principles Challenger noted real findings are often multi-causal ("missing requirement enabled bad assumption which led to infeasible design"). Single-phase classification forces false choice. Disposition accepted dual classification as solution, but design not updated.
- **Suggestion:** Update "Finding Phase Classification" section to specify: (1) Each finding has primary phase (where to route) and optional contributing phase (systemic pattern to track), (2) Format: "Phase: design (primary), calibrate (contributing)", (3) Synthesizer analyzes aggregate: if >30% of findings share contributing phase, flag systemic issue ("5 design flaws traced to missing requirement pattern — escalate to calibrate for requirement refinement"), (4) Reviewers suggest phase in findings, synthesizer reconciles disagreements with reasoning, (5) User can override classification during processing. Update verdict logic: escalation triggered by primary phase, systemic issues flagged separately.
- **Iteration status:** Still an issue (was Finding 7 in prior review, accepted but design not updated)

### Finding 8: CLI Tooling for Reviewers Still Unspecified
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Missing (should be "Reviewer Capabilities" or "Tooling" section)
- **Issue:** Requirements doc emphasizes "CLI-first" as tooling principle and lists specific tools (`gh`, `jq`, `git`, `curl`, `inspect`). States "Reviewers should have access to CLI tools when needed." Prior review Finding 21 flagged "CLI tooling requirements missing" (Important severity, accepted). Disposition: "Valid — specify reviewer tool access in Task 8 prompt iteration. Per-persona tool boundaries belong in stable prompt prefix." Design doc has no tooling section. Coverage matrix marks "CLI-first" as NO / MISSING.
- **Why it matters:** Some reviewer personas need tools to perform their function effectively. Prior Art Scout searches for existing solutions (needs `gh` to search repos, `curl` to fetch docs). Assumption Hunter validates assumptions against codebase (needs `grep` or code search). Edge Case Prober checks boundary conditions (might need to query APIs or inspect configs). If reviewers can't access tools, their findings are limited to what's in the design doc text, missing real-world validation. Requirements doc explicitly lists CLI tools as available, design doesn't specify which reviewers get which tools.
- **Suggestion:** Add "Reviewer Capabilities" section specifying tool access per persona: (1) All reviewers: Read tool for design/requirements artifacts, git for checking repo structure, (2) Prior Art Scout: `gh` for GitHub repo/issue search, `curl` for fetching external docs, web search for standards/libraries, (3) Assumption Hunter: `grep` or code search for codebase validation, `jq` for config inspection, (4) Edge Case Prober: `curl` for API boundary testing (if applicable), (5) Tool access boundary: read-only, no write operations, no credential access. Document that tool capabilities are part of stable prompt prefix (Finding 3 caching architecture).
- **Iteration status:** Still an issue (was Finding 21 in prior review, accepted but design not updated)

### Finding 9: Voice Guidelines Not Documented in Design
- **Severity:** Important
- **Phase:** design (primary)
- **Section:** Per-Reviewer Output Format
- **Issue:** Requirements doc specifies detailed output voice requirements ("direct and engineer-targeted," "lead with verdict," "no hedging language," "SRE-style framing: blast radius, rollback path, confidence"). Prior review Finding 23 flagged "Output voice guidelines missing" (Important severity, accepted). Disposition: "Part of Task 8 prompt iteration. Voice guidelines go in stable prompt prefix per Finding 3 caching architecture." Task 8 added voice rules to agent prompts (confirmed by reviewing agent prompt context in this task). Design doc still only specifies output format (markdown structure), not voice rules. Coverage matrix marks voice requirements as Partial — prompts have it, design doc doesn't.
- **Why it matters:** Design doc is the authoritative spec. If voice guidelines are only in prompts but not documented in design, future prompt updates might drop them. Consistency across 6-9 personas requires documented standard. Requirements doc emphasizes voice as critical ("audience is senior+ engineers making go/no-go decisions"). Design should specify this as requirement for all reviewer output, not just embed it in individual prompts. Voice rules are part of prompt caching prefix (per Finding 3 disposition), so they're architecturally important to document.
- **Suggestion:** Add "Voice Guidelines" subsection to "Per-Reviewer Output Format" specifying: (1) Active voice — lead with impact, then evidence, (2) No hedging ("might", "could", "possibly") — state findings directly, (3) Quantify blast radius where possible (users affected, systems impacted, timeline risk), (4) SRE-style framing for severity: what's the failure mode, what's the blast radius, what's the mitigation, (5) Engineer-targeted audience — assume reader makes go/no-go decisions at checkpoints. Note: these rules are part of stable prompt prefix per prompt caching architecture.
- **Iteration status:** Still an issue (was Finding 23 in prior review, accepted and implemented in prompts, design doc not updated)

### Finding 10: Requirement for "Should This Exist?" Lens Not in Design
- **Severity:** Important
- **Phase:** calibrate (primary), design (contributing)
- **Section:** Reviewer Personas (Requirement Auditor specifically)
- **Issue:** Prior review Finding 25 accepted user disposition requesting addition of "The Algorithm" engineering workflow lens (delete before optimize — never optimize a requirement that shouldn't exist). Disposition: "Reviewers should ask 'should this requirement exist at all?' before checking if design satisfies it." This applies to Requirement Auditor persona specifically but also to design review generally (evaluating whether design features should exist before critiquing how they're implemented). Task 8 prompt updates included this for Requirement Auditor (confirmed by context in this task: "Before evaluating any element, ask: 'Should this exist at all?'"). Design doc doesn't mention this lens.
- **Why it matters:** This is a high-value review lens that prevents gold-plating and catches YAGNI violations. User explicitly requested it as design principle. It's in the prompt now (Task 8) but not documented in the design as part of reviewer methodology. Without design doc reference, unclear whether other personas should also use this lens (Edge Case Prober before evaluating edge cases? Feasibility Skeptic before evaluating implementation complexity?). Design doc should clarify scope of this principle.
- **Suggestion:** Update Requirement Auditor persona description to include: "Before checking coverage or contradictions, first evaluates whether each requirement should exist at all. Flags requirements that add complexity without clear value as calibrate gaps." Add note in general review methodology (if design has one, or create one): "All reviewers apply 'delete before optimize' lens — never optimize or critique something that should be deleted entirely." This makes the principle explicit and portable across personas.
- **Iteration status:** New finding (disposition added new lens, implemented in prompts, design doc not updated)

### Finding 11: Blind Spot Check Value Still Empirically Unvalidated
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Per-Reviewer Output Format (Blind Spot Check)
- **Issue:** Prior review Finding 34 flagged "Blind spot checks may produce noise" (Minor severity, 4 reviewers flagged it). Design says "blind spot check is self-error-detection" but acknowledges it's "empirical question for eval framework." No specification for: (1) whether blind spot checks are surfaced to user in summary, (2) whether synthesizer uses them, (3) what format they take (findings vs freeform), (4) removal criteria if they're noise. Coverage matrix doesn't include blind spot checks as explicit requirement, but they're in the output format.
- **Why it matters:** If blind spot checks are pure overhead (token cost, no value), they should be removed. If valuable, they should be first-class in summary. Prior review consensus (4 reviewers) was "untestable, might be noise." Design hasn't resolved this or specified how to test it. Without removal criteria, feature persists indefinitely even if it's low-value. Feasibility Skeptic suggested A/B testing (reviewers with/without blind spot prompts), Edge Case Prober suggested <10% novel findings → remove. Design doesn't specify testing approach.
- **Suggestion:** Add explicit testing plan for blind spot checks in prototype scope or eval phase: (1) First 5 review runs include blind spot checks, (2) Synthesizer tracks whether blind spot content produces novel findings (not duplicates of main findings), (3) If <10% of blind spot checks contain actionable novel findings, remove from output format, (4) If >10% actionable, make blind spot checks first-class in summary (separate section: "Reviewer Self-Identified Gaps"). Specify that this is an empirical validation target, not a committed feature.
- **Iteration status:** Previously flagged, now resolved — Specify removal criteria and validation plan.

### Finding 12: "Delete Before Optimize" Lens Scope Ambiguity
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Reviewer Personas, Methodology
- **Issue:** Finding 10 above notes the "should this exist at all?" lens was added to Requirement Auditor per Finding 25 disposition. Design doesn't clarify whether this lens applies to other personas. Should Edge Case Prober ask "should we handle this edge case at all?" before evaluating how it's handled? Should Feasibility Skeptic ask "should we build this feature?" before evaluating implementation complexity? Or is this lens exclusive to Requirement Auditor (evaluating requirements, not design elements)?
- **Why it matters:** Scope ambiguity creates inconsistent review quality. If the lens is valuable, all personas should use it. If it's only for requirements review, design-stage personas shouldn't apply it (risks conflating "design doesn't address requirement" with "requirement shouldn't exist"). The latter is a calibrate gap, not a design flaw. Clear scope prevents phase classification errors.
- **Suggestion:** Clarify in design whether "delete before optimize" is: (1) Universal reviewer lens (all personas ask this about their domain), or (2) Requirement Auditor specific (only applies when auditing requirements coverage). Recommend option 1 (universal) with phase-aware scoping: Requirement Auditor flags "requirement shouldn't exist" as calibrate gap. Feasibility Skeptic flags "feature shouldn't exist given constraints" as design flaw (if requirement says must-have) or calibrate gap (if requirement is negotiable).
- **Iteration status:** New finding (scope clarification needed for newly added lens)

### Finding 13: Synthesizer Role Still Called "Purely Editorial" in Design
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Synthesis
- **Issue:** Prior review Finding 13 flagged "Synthesizer role contradicts 'purely editorial' constraint" (Important severity, 3 reviewers). Disposition: "Reframe synthesizer as judgment-exercising role (not 'purely editorial'). Smoke test confirmed: escalated Finding 8 severity. Honest role definition is prerequisite for good prompt engineering. Part of Task 8." Task 8 updated synthesizer prompt (removed "purely editorial" framing, reframed as requiring judgment). Design doc still says "Its role is purely editorial — zero judgment on content or severity" in Synthesis section.
- **Why it matters:** Design doc contradicts implementation and prior disposition. Synthesizer exercises judgment on deduplication (are two findings the same issue?), phase classification (is this a design flaw or calibrate gap?), and finding aggregation (does this pattern indicate systemic issue?). Prior review extensively documented why "purely editorial" is dishonest. Disposition accepted this, prompts updated, but design not updated. Documentation debt creates confusion.
- **Suggestion:** Update Synthesis section to remove "purely editorial" and "zero judgment" language. Replace with honest role description: "Synthesizer exercises judgment on finding consolidation, phase classification, and pattern detection. It does not override individual reviewer severity ratings or add its own findings, but does reconcile disagreements and surface emergent patterns that individual reviewers cannot see." Acknowledge that deduplication and phase classification are judgment calls requiring semantic interpretation, not mechanical aggregation.
- **Iteration status:** Still an issue (was Finding 13 in prior review, disposition accepted and prompts updated, design doc not updated)

### Finding 14: JSONL Output Format Mentioned in Dispositions But Not in Design
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Output Artifacts, Summary Format
- **Issue:** Multiple prior review finding dispositions reference JSONL as canonical output format. Finding 14 disposition: "JSONL format enables this naturally — jq filters by severity/persona/phase without LLM tokens." Finding 24 disposition: "JSONL + markdown rendering may naturally produce this — consolidated view becomes render target." MEMORY.md notes "JSONL as canonical output format — decided but not yet implemented. Current markdown works for MVP." Design doc specifies only markdown output format. No mention of JSONL.
- **Why it matters:** If JSONL is the intended canonical format, design should specify it (even if deferred to post-MVP). Current design commits to markdown as output format with no migration path to structured data. Dispositions suggest JSONL is a design decision, not just an implementation detail. Multiple features depend on it (jq-based filtering, bulk operations, finding persistence with stable IDs). If it's deferred, design should say so explicitly. If it's planned, output format section should specify both current state (markdown) and target state (JSONL + markdown rendering). Requirements doc emphasizes CLI-first tooling, which naturally works better with JSONL (jq for filtering/processing) than markdown (requires parsing or LLM for structured extraction). Finding persistence mechanism (Finding 3 above, stable IDs) is easier with JSONL (native ID field) than markdown (ID embedded in heading or metadata block).
- **Suggestion:** Add JSONL to output format section as post-MVP enhancement: "Current prototype uses markdown for human readability. Post-MVP, structured JSONL output with markdown rendering layer enables: (1) stable finding IDs (JSON id field), (2) CLI-based filtering/processing (jq by severity/persona/phase), (3) bulk finding operations, (4) cross-iteration diff without LLM parsing. Markdown remains primary interface, JSONL becomes underlying data format." This documents the decision trajectory without committing to immediate implementation.
- **Iteration status:** New finding (design doesn't reflect JSONL intent mentioned in multiple dispositions)

### Finding 15: Model Tiering Strategy Mentioned in Requirements But Not Designed
- **Severity:** Minor
- **Phase:** design (primary)
- **Section:** Missing (should be in cost/architecture section)
- **Issue:** Requirements doc and CLAUDE.md specify model tiering as cost strategy: "Model tiering: Haiku for simple evals, Sonnet for review agents, Opus sparingly for adversarial deep analysis." Problem statement suggests "Model routing: Configurable model parameter per pipeline phase from start. Default Sonnet everywhere, tune empirically via evals." Prior review Finding 40 suggests testing Haiku for mechanical reviewers (Requirement Auditor, Edge Case Prober). Design doc specifies Sonnet for all reviewers but has no model tiering architecture or configuration mechanism. Coverage matrix marks "Model tiering" as Partial — mentioned in cost strategy, not designed.
- **Why it matters:** Cost optimization via model tiering could reduce per-review cost 30-40% if Haiku works for mechanical personas (per Finding 40). Without design-level specification, this becomes implementation detail rather than architectural decision. If model per persona is configurable from start, eval framework can test model variants empirically. If hardcoded to Sonnet, refactoring later requires code changes. Requirements suggest this should be "from start" not "tune later."
- **Suggestion:** Add "Model Configuration" subsection to design specifying: (1) Default model per stage (Sonnet for design-stage review), (2) Model parameter per persona (allows empirical testing of Haiku for mechanical reviewers), (3) Configuration via skill parameter or persona definition file (not hardcoded), (4) Eval framework tests model variants (Haiku vs Sonnet for same persona on same artifact, compare finding coverage/quality). Acknowledge default is Sonnet everywhere for prototype, tiering is empirical question post-MVP.
- **Iteration status:** New finding (requirement exists, design doesn't specify architecture for it)

## Blind Spot Check

**What might I have missed given my focus on requirements?**

My lens is requirement coverage and traceability. I checked whether design addresses stated requirements and flagged gaps, contradictions, gold-plating, anti-goal violations. What I might miss:

1. **Implementation feasibility:** I flagged that certain features are missing from the design (auto-fix, cross-iteration tracking, prompt caching architecture), but I didn't evaluate whether they're feasible to build or too complex for MVP. Feasibility Skeptic would catch implementation complexity I miss.

2. **Edge cases in requirement interpretation:** I treated requirements doc as authoritative, but some requirements might be over-constrained or wrong. First Principles Challenger would question whether the requirements themselves are right. I flagged requirement-design mismatches but deferred judgment on which should change.

3. **User experience quality beyond requirement compliance:** Design could satisfy all requirements but still have poor UX (confusing workflow, decision fatigue, unclear error messages). I focused on "does it meet the requirement" not "is it good." Edge Case Prober and Assumption Hunter catch UX gaps I miss.

4. **Prior art and simpler alternatives:** I checked build-vs-leverage requirements (CLI-first, portability) but didn't deeply evaluate whether existing tools (Inspect AI, LangSmith) already solve what's being designed. Prior Art Scout would catch "you're rebuilding something that exists" better than I do.

5. **Cross-finding patterns indicating systemic issues:** I identified 15 individual findings but didn't analyze whether they cluster around common root cause (e.g., "most findings are documentation debt from accepted dispositions not reflected in design"). Synthesizer role would catch this aggregate pattern.

**Key pattern I noticed:** 10 of 15 findings (67%) are documentation debt — accepted prior review findings or disposition decisions not yet reflected in the design doc. This suggests design doc is out of sync with implementation state. Root cause: Task 8 updated agent prompts and skill code based on dispositions, but design doc wasn't treated as living spec requiring parallel updates. This is a process issue, not a design flaw — the decisions are good, the documentation is stale.

**What this review doesn't cover:**
- Whether the design actually works (prototype testing)
- Whether the personas produce valuable findings (empirical validation)
- Cost/performance tradeoffs (model tiering, prompt size, API limits)
- Security implications of CLI tool access or subagent dispatch
- Comparison to alternative architectures (Inspect AI as substrate, LangSmith for finding processing)

These are valid evaluation concerns but outside my requirement-coverage mandate.
