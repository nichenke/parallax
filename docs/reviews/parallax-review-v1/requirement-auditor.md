# Requirement Auditor Review

## Coverage Matrix

| Requirement | Addressed? | Design Section | Notes |
|---|---|---|---|
| Multi-phase process support (brainstorm → plan) | Partial | Skill Interface, Pipeline Integration | Design covers **only** design stage; requirements & plan stages deferred |
| Adversarial review with multiple subagents | Yes | Reviewer Personas | 6 personas for design stage, 9 total planned |
| Parallel execution of reviewers | Yes | Step 2: Dispatch | "4-6 depending on stage" dispatched in parallel |
| Automatic consolidation & deduplication | Yes | Synthesis | Synthesizer consolidates, deduplicates, surfaces contradictions |
| Severity normalization across reviewers | Partial | Synthesis | Severity **reported as ranges** when disagreement exists, not normalized |
| Finding classification by pipeline phase | Yes | Finding Phase Classification | survey/calibrate/design/plan classification with escalation logic |
| Requirement refinement (MoSCoW, anti-goals) | Not in scope | Prototype Scope | Deferred — this design is for `parallax:review` not `parallax:calibrate` |
| Design-plan consistency checking | Partial | Reviewer Personas | "Requirement Auditor" at plan stage checks this, not implemented yet |
| Iteration tracking via git | Yes | Output Artifacts | "Iteration history tracked by git (each re-review is a new commit, diffs show what changed)" |
| Auto-fix trivial findings | No | — | Problem statement requires auto-fix, design doesn't address it |
| Escalate non-trivial findings to human | Yes | Verdict Logic, UX Flow | Human processes findings one-by-one |
| Track findings across iterations | Partial | Summary Format | Dispositions tracked in summary.md, but no cross-iteration tracking mechanism |
| ADR-style finding documentation | Implicit | Output Artifacts | Individual reviewer files persist, but no explicit ADR structure |
| Human checkpoints at phase boundaries | Yes | Pipeline Integration | Gates between phases with human approval |
| Never auto-proceed past checkpoint | Yes | Step 6: Wrap Up | Interactive processing required before verdict execution |
| Persona engineering with sharp prompts | Yes | Reviewer Personas | Each persona has distinct focus and adversarial question |
| Prompt caching architecture | No | — | Problem statement specifies this as architectural convention, design doesn't address |
| Outcome-focused requirement refinement | Not in scope | — | This is `parallax:calibrate`, not `parallax:review` |
| Assumptions/constraints as review checklist | Partial | Reviewer Personas | Assumption Hunter covers this, but no explicit checklist mechanism |
| Document chain as RFC | Partial | Pipeline Integration | Pipeline produces chain, but no RFC consolidation described |
| Self-consuming (parallax reviews its own artifacts) | No | — | Not addressed |
| Agent team comparison (multi-model) | No | Open Questions | Flagged as eval question, not in prototype |
| Output voice (engineer-targeted, SRE-style) | Partial | Per-Reviewer Output Format | Format is structured, but no voice guidelines in reviewer prompts |
| CLI-first tooling | No | — | No tooling section, no mention of CLI tools |
| Portability sanity check script | No | — | Problem statement requires this, not in design |
| Codex portability consideration | No | — | Not addressed in design |

## Critical Findings

### Finding 1: Auto-Fix Requirement Missing
- **Severity:** Critical
- **Phase:** design
- **Section:** UX Flow, Synthesis
- **Issue:** Problem statement explicitly requires "After adversarial review, auto-fix trivial findings (typos, wrong file paths) and re-review" but the design has no auto-fix mechanism. The UX flow goes straight from synthesis to human processing.
- **Why it matters:** This is a must-have feature to reduce human review burden. Without it, humans must manually process obvious fixes like typos, defeating a core value proposition of the orchestrator.
- **Suggestion:** Add an auto-fix step between synthesis and human processing. Synthesizer should classify findings as auto-fixable vs human-decision-required. Auto-fixable findings get applied, design re-reviewed, only remaining findings shown to human.

### Finding 2: Prompt Caching Architecture Not Addressed
- **Severity:** Critical
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement says "Prompt structure for caching: System prompts should be structured as stable cacheable prefix (persona + methodology + output format) + variable suffix (the design being reviewed + iteration context). This is an architectural convention, not a feature — 90% input cost reduction on cache hits. Decide before building skills." The design doc has no prompt architecture section.
- **Why it matters:** This is an architectural decision that affects **how reviewer prompts are authored**. If prompts aren't structured for caching from the start, refactoring later invalidates all eval data. This is a design-time decision, not an implementation detail.
- **Suggestion:** Add a "Reviewer Prompt Architecture" section specifying: (1) stable prefix structure (persona identity, methodology, output format rules), (2) variable suffix (artifact being reviewed, requirements context, iteration number), (3) explicit note that prompt changes to prefix invalidate cache and should be tracked.

### Finding 3: Cross-Iteration Finding Tracking Incomplete
- **Severity:** Critical
- **Phase:** design
- **Section:** Synthesis, UX Flow
- **Issue:** Problem statement requires "Track which findings have been addressed across iterations." Design tracks dispositions in summary.md but doesn't specify **how** the system knows whether Finding #3 from iteration 1 was actually resolved in iteration 2. No mechanism for linking findings across review runs.
- **Why it matters:** Without this, re-reviews require humans to manually cross-reference "did we fix the thing the Assumption Hunter flagged last time?" Defeats automation value.
- **Suggestion:** Add finding persistence mechanism — stable IDs for findings (e.g., hash of section + issue text), status field (open/addressed/rejected), cross-iteration diff in summary.md showing which findings from prior review are now resolved.

## Important Findings

### Finding 4: Scope Mismatch — Requirement Refinement Expected
- **Severity:** Important
- **Phase:** calibrate
- **Section:** Entire design
- **Issue:** The problem statement title is "Design Orchestrator" and describes a full pipeline including requirement refinement (MoSCoW, anti-goals, success criteria) as a critical phase. This design only covers `parallax:review` and explicitly defers requirement refinement. The design satisfies the review skill, not the orchestrator problem statement.
- **Why it matters:** If the requirement is "orchestrator," this design is incomplete. If the requirement is "review skill," then the problem statement is over-scoped and should be split. Currently testing against wrong requirements.
- **Suggestion:** Either (1) split the problem statement into separate docs for `parallax:review` and `parallax:orchestrate`, or (2) treat this design as phase 1 of a multi-phase orchestrator design and explicitly scope what's in/out for this iteration.

### Finding 5: Severity Normalization Not Implemented
- **Severity:** Important
- **Phase:** design
- **Section:** Synthesis
- **Issue:** Problem statement requires "Severity should be normalized across reviewers." Design says synthesizer reports severity ranges ("Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic") but explicitly does NOT normalize. The synthesizer "does NOT override or adjust reviewer severity ratings."
- **Why it matters:** Without normalization, verdict logic is ambiguous. If one reviewer says Critical and another says Minor, does the verdict become "revise" (any Critical finding) or "proceed" (no consensus on severity)? Current design punts this to the human, reducing automation value.
- **Suggestion:** Either (1) implement severity normalization (consensus-based, or weighted by persona authority), or (2) update verdict logic to handle severity disagreements explicitly (e.g., "any reviewer flags Critical → revise, unless majority disagrees").

### Finding 6: No Self-Consumption Mechanism
- **Severity:** Important
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement says "Self-consuming: Parallax should use its own document chain as input to its own review tasks. The artifacts are the context that makes adversarial review effective." The design has no mechanism for feeding prior review artifacts back into the review process.
- **Why it matters:** Iteration 2 reviewers can't reference iteration 1 findings to check whether concerns were addressed. Valuable context is lost. This is especially important for the Requirement Auditor (did design address the gap we flagged?) and First Principles Challenger (did the revision actually fix the framing issue?).
- **Suggestion:** Add to skill interface: optional prior review summary as input. Reviewer prompts should reference prior findings when present. Synthesizer should explicitly note which prior findings are now resolved vs still open.

### Finding 7: CLI Tooling Requirements Missing
- **Severity:** Important
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement specifies "CLI-first" as a tooling principle and lists specific CLI tools to adopt (`gh`, `jq`, `git`, `curl`, `inspect`, etc.). The design has no tooling section and doesn't specify which tools the reviewers or synthesizer use.
- **Why it matters:** If reviewers need to check prior art (Prior Art Scout), search codebases (survey phase context), or validate assumptions (Assumption Hunter), they need tooling. Design doesn't specify whether these capabilities exist or how they're accessed.
- **Suggestion:** Add "Reviewer Capabilities" section specifying: (1) which CLI tools are available to each persona (e.g., Prior Art Scout gets `gh` for searching repos, `curl` for fetching docs), (2) whether reviewers can invoke subagents for research, (3) what the tool access boundary is (read-only vs write).

### Finding 8: Codex Portability Not Addressed
- **Severity:** Important
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement requires "Portability sanity check script: Build a simple script early that runs a parallax skill on both Claude Code and Codex CLI and diffs the output quality. Goal: catch Claude-specific assumptions before they're baked in." Design doesn't address portability or testing on Codex.
- **Why it matters:** If reviewer prompts use Claude-specific features (like extended thinking mode, artifact rendering, or MCP tools), the skill won't work on Codex. Testing this early is cheaper than refactoring later.
- **Suggestion:** Add to prototype scope: portability validation task. Run the 6 reviewer personas on the same design doc using both Claude and Codex, diff the findings. Document any Claude-specific assumptions discovered.

### Finding 9: Output Voice Guidelines Missing
- **Severity:** Important
- **Phase:** design
- **Section:** Per-Reviewer Output Format
- **Issue:** Problem statement specifies detailed output voice requirements ("direct and engineer-targeted," "lead with verdict," "no hedging language," "SRE-style framing"). The design specifies output **format** (markdown structure) but not output **voice** (how findings should be written).
- **Why it matters:** Without voice guidelines in reviewer prompts, different personas will use different tones (some hedging, some direct). Inconsistent output quality reduces trust in findings.
- **Suggestion:** Add voice guidelines to the "Per-Reviewer Output Format" section and specify that these rules are part of the stable prompt prefix. Example rules: "Use active voice. Lead with impact, then evidence. No hedging ('might', 'could', 'possibly'). Quantify blast radius where possible."

### Finding 10: Document Chain RFC Mechanism Undefined
- **Severity:** Important
- **Phase:** design
- **Section:** Missing
- **Issue:** Problem statement says "The pipeline naturally produces a chain: problem statement → requirements → design → review findings → plan. This chain consolidates into something RFC-like." The design produces individual artifacts but has no consolidation mechanism.
- **Why it matters:** If artifacts aren't consolidated, users must manually assemble context from multiple files when sharing designs for human review. Reduces portability of design decisions.
- **Suggestion:** Add to synthesis step: RFC consolidation task. After review converges, synthesizer produces a single markdown file combining: (1) original requirements, (2) design decisions, (3) review findings + dispositions, (4) final approved design. This becomes the shareable artifact.

## Minor Findings

### Finding 11: Persona Count Justification Weak
- **Severity:** Minor
- **Phase:** design
- **Section:** Reviewer Personas
- **Issue:** Design says "9 total personas, 4-6 active per stage. Optimal count is an empirical question for the eval framework — this is the starting hypothesis." No justification for **why** these specific personas or why 4-6 is the hypothesis.
- **Why it matters:** Without rationale, it's unclear whether this is over-engineered (too many personas, overlapping concerns) or under-engineered (missing key perspectives). Eval results will be hard to interpret.
- **Suggestion:** Add brief rationale for each persona (what blind spot does it cover that others miss?) and for the 4-6 count hypothesis (based on prior art research? Intuition? Cost constraints?).

### Finding 12: Gold-Plating — Blind Spot Check
- **Severity:** Minor
- **Phase:** design
- **Section:** Per-Reviewer Output Format
- **Issue:** The blind spot check ("What might I have missed given my assigned focus?") is a novel addition not mentioned in the problem statement. This is a nice-to-have that adds complexity (prompts must self-critique) without proven value.
- **Why it matters:** If blind spot checks don't produce actionable findings in practice (flagged as open question in design), they waste tokens and human attention. This is speculative feature addition.
- **Suggestion:** Either (1) move blind spot check to "Build later" (validate core personas first), or (2) keep it but add explicit eval criterion: "Do blind spot checks surface findings the persona's main review missed? If not, remove the section."

### Finding 13: Contradiction Handling Ambiguous
- **Severity:** Minor
- **Phase:** design
- **Section:** Synthesis
- **Issue:** Design says synthesizer "surfaces contradictions" when reviewers disagree and that users resolve them, but doesn't specify **how** contradictions are resolved. Is there a structured debate? Do reviewers provide rebuttals? Does the user just pick one?
- **Why it matters:** If contradictions are common (likely, given adversarial personas), the resolution process is a major UX touchpoint. Current design leaves this to ad-hoc user decision.
- **Suggestion:** Add contradiction resolution options to UX flow: (1) Accept one position and reject the other, (2) Request debate (both reviewers present arguments, user decides), (3) Mark as "both valid" (design decision depends on unstated constraint, document the tradeoff).

### Finding 14: Stage-Specific Activation Not Validated
- **Severity:** Minor
- **Phase:** design
- **Section:** Persona Activation Matrix
- **Issue:** The activation matrix shows which personas are active per stage (e.g., Assumption Hunter active in requirements & design, not plan). No justification for **why** specific personas are excluded from specific stages.
- **Why it matters:** If Assumption Hunter would catch plan-stage assumptions (e.g., "assumes this API exists"), excluding it is a gap. If not, the exclusion is correct. No rationale provided.
- **Suggestion:** Add column to activation matrix: "Why not active?" for each excluded persona-stage pair. Example: "Assumption Hunter not in plan stage — implementation assumptions caught by Code Realist instead."

### Finding 15: Review Stage Parameter Not Future-Proof
- **Severity:** Minor
- **Phase:** design
- **Section:** Skill Interface
- **Issue:** Input contract specifies `review stage` as "one of: requirements, design, plan" but only design stage is implemented in prototype. If new stages are added later (e.g., post-execution retrospective review), the enum changes.
- **Why it matters:** Minor versioning concern — clients invoking the skill will need to update when new stages are added.
- **Suggestion:** Document stage enum as extensible in skill interface section. Consider using a `stage: string` parameter with validation rather than hardcoded enum, or version the skill (parallax:review v1 = design only, v2 = all stages).

## Blind Spot Check

What might I have missed given my focus on requirement traceability?

1. **Security & privacy:** The problem statement mentions "security review" as a subagent type multiple times, but this design doesn't include a Security Reviewer persona. Is this an intentional deferral (covered by existing tools) or a gap?

2. **Cost estimation:** Problem statement mentions model tiering and cost optimization extensively. This design doesn't specify estimated token costs per review run, whether reviewers use different models, or how to measure cost vs quality tradeoffs.

3. **Eval framework integration:** Problem statement has an entire track (#5) for skill testing evals, and the design flags several open questions "for eval framework." But there's no section on **how** this skill will be tested — what constitutes a good review, how to measure false positives/negatives, etc.

4. **Pipeline state management:** Problem statement shows a flowchart with loops (spec wrong → escalate back to earlier phase). Design describes gates between phases but doesn't specify **who** manages state when escalation happens. Does the review skill exit and tell the orchestrator to restart an earlier phase? Or does it handle the loop internally?

5. **Parallel execution semantics:** Design says reviewers run "in parallel" but doesn't specify execution model. Are these parallel API calls? Subagents spawned via TeammateTool? Background jobs? Affects cost (parallel = no caching between reviewers) and implementation.
