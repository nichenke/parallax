# Design: parallax:review — Adversarial Multi-Agent Design Review

**Date:** 2026-02-16
**Version:** v4 (synced with requirements v1.2)
**Status:** Approved
**Approach:** Parallel Persona Agents with Synthesizer

## Overview

`parallax:review` is a skill that dispatches multiple adversarial reviewer agents in parallel, each with a distinct critical lens, to review design artifacts against requirements. A synthesizer agent consolidates findings, classifies them by pipeline phase, and presents them for interactive human processing.

The core hypothesis: multiple perspectives catch design gaps that single-perspective review misses. The core novel contribution: finding classification routes errors back to the pipeline phase that failed.

## Skill Interface

**Trigger:** `parallax:review` — invoked by the orchestrator or directly by the user.

**Input contract:**
- **Design artifact** — markdown document (the thing being reviewed)
- **Requirements artifact** — markdown document (what the design should satisfy)
- **Review stage** — one of: `requirements`, `design`, `plan` (determines active personas and escalation targets)
  - Stage guidance for standalone use: `requirements` for MoSCoW/priority docs, `design` for architecture/approach docs, `plan` for implementation/execution docs. Auto-detection deferred (YAGNI for MVP — we know the stage).
- **Topic label** — name for the review folder
  - Topic labels validated against safe character set (alphanumeric, hyphens, underscores only). Collision handling: timestamped folders for iteration separation.

For the prototype, we build `design` stage only. The skill accepts docs as file paths or inline context.

**Output contract:**
- Individual reviewer files (one per persona) saved to `docs/reviews/<topic>/`
- Synthesized summary with findings classified by severity AND pipeline phase
- Overall verdict: `proceed` | `revise` | `escalate`
- Async-first: artifacts written to disk as baseline. Interactive finding-by-finding processing (accept/reject-with-note) as convenience layer.

## Output Artifacts

```
docs/reviews/<topic>/
├── summary.md                  — synthesized verdict, finding counts, dispositions
├── assumption-hunter.md        — full review from Assumption Hunter
├── edge-case-prober.md         — full review from Edge Case Prober
├── requirement-auditor.md      — full review from Requirement Auditor
├── feasibility-skeptic.md      — full review from Feasibility Skeptic
├── first-principles.md         — full review from First Principles Challenger
├── prior-art-scout.md          — full review from Prior Art Scout
└── [stage-specific personas]   — additional reviewers per stage
```

Iteration history tracked by git (each re-review is a new commit, diffs show what changed).

## Reviewer Personas

### Design Stage (Prototype) — 6 Personas

| Persona | Focus | Adversarial Question |
|---|---|---|
| **Assumption Hunter** | Implicit assumptions, unstated dependencies, "what if X isn't true?" | "What has the designer taken for granted?" |
| **Edge Case Prober** | Boundary conditions, failure modes, scale limits, empty/null states | "What happens when things go wrong or weird?" |
| **Requirement Auditor** | Coverage gaps, contradictions, gold-plating, anti-goal violations | "Does this actually satisfy the requirements? Are the requirements themselves contradictory?" |
| **Feasibility Skeptic** | Implementation complexity, hidden costs, simpler alternatives | "Is this buildable as described, and is it the simplest approach?" |
| **First Principles Challenger** | Reexamine the problem from scratch, question whether the framing is right | "Are we solving the right problem? Would we design it this way starting from zero?" |
| **Prior Art Scout** | Existing solutions, standards, libraries, build-vs-buy | "Does this already exist? Are we reinventing something we should leverage?" |

Requirement Auditor auto-escalates requirement-level contradictions as calibrate gap (Critical severity). Requirements must be internally consistent before design review proceeds.

### Requirements Stage — 4 Personas

| Persona | Focus | Adversarial Question |
|---|---|---|
| **Assumption Hunter** | Unstated assumptions about users, environment, constraints | "What has the author taken for granted?" |
| **Requirement Auditor** | Completeness, internal consistency, testability | "Can we verify this requirement was met?" |
| **First Principles Challenger** | Problem framing, whether we're solving the right problem | "Why this problem? Why now? Why this scope?" |
| **Prior Art Scout** | Existing solutions, industry patterns, standards | "Has someone already solved this?" |
| **Product Strategist** | User value, market fit, prioritization, success metrics, scope | "Will anyone actually use this? How do we know it worked?" |

PM lens covers: Are success criteria measurable? Is scope right for timeline? What's MVP vs nice-to-have? Who's the user and what's their journey? What are we saying no to and why?

### Plan Stage — 5 Personas

| Persona | Focus | Adversarial Question |
|---|---|---|
| **Edge Case Prober** | Failure modes, error handling gaps, boundary conditions in implementation | "What breaks at the seams?" |
| **Requirement Auditor** | Spec drift, requirements lost in translation from design to plan | "Does this plan actually deliver the design?" |
| **Feasibility Skeptic** | Timeline risk, hidden complexity, dependency chains | "What's harder than it looks?" |
| **Prior Art Scout** | Libraries, frameworks, build-vs-buy for implementation choices | "Are we building what we should buy?" |
| **Systems Architect** | Integration points, data flow, API contracts, scaling, operational concerns | "How does this actually work in production?" |
| **Code Realist** | Implementation ordering, dependency risks, testing strategy, tech debt | "What's going to break, and what's harder than it looks?" |

### Persona Activation Matrix

| Persona | Requirements | Design | Plan |
|---|---|---|---|
| Assumption Hunter | x | x | |
| Edge Case Prober | | x | x |
| Requirement Auditor | x | x | x |
| Feasibility Skeptic | | x | x |
| First Principles Challenger | x | x | |
| Prior Art Scout | x | x | x |
| Product Strategist | x | | |
| Systems Architect | | | x |
| Code Realist | | | x |

9 total personas, 4-6 active per stage. Optimal count is an empirical question for the eval framework — this is the starting hypothesis.

### Per-Reviewer Output Format

```markdown
# [Persona Name] Review

## Findings

### Finding 1: [Title]
- **Severity:** Critical | Important | Minor
- **Phase:** survey | calibrate | design | plan
- **Section:** [which part of the artifact]
- **Issue:** [what's wrong]
- **Why it matters:** [impact if unaddressed]
- **Suggestion:** [how to fix or what to reconsider]

### Finding 2: ...

## Blind Spot Check
[What might I have missed given my assigned focus?]
```

### Output Voice Guidelines

Part of the stable prompt prefix. Applied consistently across all personas:
- Use active voice. Lead with impact, then evidence.
- No hedging language ("might", "could", "possibly") — state the issue directly.
- Quantify blast radius where possible ("affects N of M endpoints", "blocks all downstream phases").
- SRE-style framing: what breaks, what's the blast radius, what's the fix.
- Direct and engineer-targeted. No filler.

The blind spot check is self-error-detection — each reviewer explicitly asks "what am I not seeing?"

## Synthesis

A **Synthesizer agent** consolidates reviewer output. Its role requires judgment — deduplication, phase classification, and contradiction surfacing all involve semantic interpretation. The synthesizer exercises editorial judgment transparently, with reasoning documented.

**Responsibilities:**
1. **Deduplicate** — group findings flagged by multiple reviewers into single entries, noting which reviewers flagged each (consensus signal)
2. **Classify by phase** — assign each finding to the pipeline phase that failed
3. **Surface contradictions** — when reviewers disagree, present both positions with the tension noted (user resolves)
4. **Report severity ranges** — when reviewers rate the same issue differently, report the range ("Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic"), don't editorialize
5. **Produce summary.md** — structured summary with verdict
6. **Resolve severity for verdict logic** — when reviewers rate the same issue differently, use highest severity in range for verdict computation (conservative). Document the range in findings for user context. User can override during processing.

**The synthesizer does NOT:**
- Pick winners in contradictions
- Add its own findings
- Suppress reviewer findings or silently downgrade severity

### Finding Phase Classification

| Classification | Meaning | Action |
|---|---|---|
| **Survey gap** | Missing research, wrong problem framed | Go back to research |
| **Calibrate gap** | Conflicting requirements, missing anti-goal, wrong priority | Revisit requirements |
| **Design flaw** | Assumption violated, edge case missed, wrong approach | Revise the design |
| **Plan concern** | Implementation issue (flagged for plan review stage) | Carry forward |

Findings are classified by **primary phase** (the most actionable fix) and optional **contributing phase** (upstream cause). Example: 'Design flaw (primary) caused by calibrate gap (contributing).' This enables two actions: immediate fix and systemic upstream correction.

**Systemic issue detection:** When >30% of findings with a contributing phase share the same contributing phase, the synthesizer flags a systemic issue. The denominator is findings with `contributing_phase` set (not all findings) because systemic issues indicate upstream root causes, not immediate symptoms. MVP scope uses exact phase label matching; semantic root cause clustering is deferred to post-MVP.

### Verdict Logic

- Any Critical finding (or finding with Critical in its severity range) → `revise` (or `escalate` if it's a survey/calibrate gap)
- Only Important/Minor → `proceed` with noted improvements
- Survey or calibrate gap at any severity → `escalate` (the design can't be fixed without fixing upstream)
- Severity range rule: conservative — highest severity in range determines verdict impact. If false escalations become a problem, investigate per-agent prompt tuning first.

`revise` = fix the design and re-review. `escalate` = the problem is upstream, go back to requirements or research.

### Summary Format

```markdown
# Review Summary: [Topic]

**Date:** YYYY-MM-DD
**Design:** [path to design doc]
**Requirements:** [path to requirements doc]
**Stage:** requirements | design | plan
**Verdict:** proceed | revise | escalate

## Finding Counts
- Critical: N
- Important: N
- Minor: N
- Contradictions: N

## Verdict Reasoning
[Why this verdict. What would need to change for a different verdict.]

## Critical Findings
[Listed first, with reviewer consensus noted]

## Important Findings
[...]

## Minor Findings
[...]

## Contradictions
[Tensions between reviewers that need human resolution. Each contradiction surfaces the underlying tension explicitly and suggests tie-breaking criteria.]

## Findings by Phase
- Survey gaps: N
- Calibrate gaps: N
- Design flaws: N
- Plan concerns: N

## Finding Dispositions
[Updated as user processes findings — accept/reject/discuss outcome for each]
```

## Parallel Agent Failure Handling

Reviewer dispatch expects partial failures as normal operation (API rate limits, transient network errors, model capacity issues).

- **Timeout:** 60-120s per agent
- **Retry:** 1 retry with exponential backoff for failed agents
- **Partial results:** Proceed if minimum threshold met (4/6 agents succeed)
- **Transparency:** Mark summary as partial if <100% reviewers completed ("5/6 reviewers completed, Feasibility Skeptic timed out")
- **Selective re-run:** Allow re-running individual failed reviewers without redoing successful ones
- **Schema validation:** Validate reviewer output format before synthesis; malformed output triggers retry, then fail-fast. (Blocked on JSONL schema definition)
- **Clean up:** Remove partial/corrupted output files before re-running failed reviewers to avoid stale data contamination

## Reviewer Prompt Architecture

Reviewer prompts use a three-part structure optimized for prompt caching (90% input cost reduction on cache hits) while enabling quality iteration without cache invalidation.

**Stable prefix** (cacheable):
- Persona identity and adversarial mandate
- Methodology and review approach
- Output format rules and constraints
- Voice guidelines (see Per-Reviewer Output Format)

**Calibration rules** (not cached, versioned separately):
- False positive/negative corrections based on prior review feedback
- Edge case handling refinements
- Severity calibration adjustments
- Enables iterative prompt quality improvement without losing cache benefits

**Variable suffix** (per-review):
- File paths to design and requirements documents (reviewers use Read tool to access content, NOT inline in prompt)
- Changed sections (git diff, when available: git repo exists AND design doc has prior committed version)
- Iteration number

Two version numbers tracked: stable prefix version (rarely changes, invalidates cache) and calibration rules version (frequently changes, does not invalidate cache).

**Document access:** Reviewers read design/requirements documents via Read tool (supports multi-file designs, non-git docs). MVP scope: local files and public URLs only. Authenticated sources (Confluence, Google Docs, Notion) deferred to MCP integration.

## Cross-Iteration Finding Tracking

Findings are tracked across iterations using a two-pass post-synthesis approach: pattern extraction followed by delta detection.

- **Finding IDs:** Per-iteration IDs with format `v{iteration}-{reviewer}-{sequence}` (e.g., `v3-assumption-hunter-001`). Simple, unique per run, no cross-run stability required.
- **Clean reviews:** Reviewers do NOT receive prior review context (avoids anchoring bias, preserves perspective diversity).
- **Pattern extraction:** After synthesis, extract semantic patterns from findings (group related issues into actionable themes). Cap: 15 patterns per review. Runs in critical path after synthesis, before finding processing. Output: `docs/reviews/<topic>/patterns-v{N}.json`
- **Delta detection:** When prior review exists, compare patterns across runs using LLM-based semantic matching (handles equivalence without exact text matching). Identify resolved/persisting/new patterns. Runs in critical path after pattern extraction. Output: `docs/reviews/<topic>/delta-v{N-1}-v{N}.json`
- **Finding processing threshold:** Reviews with ≤50 findings proceed to interactive finding processing with pattern context. Reviews with >50 findings write pattern artifacts to disk but skip interactive processing (summary notes finding count, user processes async).
- **Changed section focus:** When git diff is available (git repo exists AND design doc has prior committed version), reviewers receive it to focus extra scrutiny on newly-changed sections. First-time reviews have no diff highlighting.

## Reviewer Capabilities

Each reviewer persona has access to specific tools based on their review focus. All reviewers are read-only — no write access to the repository.

Tool access boundaries are specified in the stable prompt prefix per persona. Specific tool assignments are an empirical question for the eval framework — start with baseline access and expand based on observed reviewer needs during prototyping.

## UX Flow

Review is async-first: all artifacts are written to disk as the baseline. Interactive processing is a convenience layer that reuses those same disk artifacts — not a separate mode.

### Step 1: Invoke
User triggers `parallax:review`. Skill asks for:
- Path to design doc
- Path to requirements doc
- Review stage (default: `design`)
- Topic label for the review folder

### Step 2: Dispatch
Skill confirms inputs, creates `docs/reviews/<topic>/`, dispatches reviewer agents in parallel (4-6 depending on stage). Skill streams progress as reviewers complete ('Assumption Hunter: done [1/6]', 'Edge Case Prober: done [2/6]'). Shows elapsed time.

### Step 3: Synthesize
Synthesizer consolidates findings into `summary.md`. Individual reviewer outputs saved to their own files. All written to disk.

### Step 4: Auto-Fix
Synthesizer classifies findings as auto-fixable vs human-decision-required. Auto-fixable findings (typos in markdown, missing file extensions, broken internal links) are applied to the design artifact automatically. Auto-fixes are committed as a **separate git commit** from human-reviewed changes, enabling async review of what was auto-applied. The design is then re-reviewed with remaining findings only. Define auto-fixable criteria conservatively in MVP and expand based on eval data.

### Step 5: Present Summary
User sees: verdict, finding counts, critical findings listed. Then chooses processing mode:

| Mode | When to use | Behavior |
|---|---|---|
| **Critical-first** | Many findings, want fast iteration | Address Critical findings only. Send source material back for rethink. Remaining findings processed in next pass. |
| **All findings** | Fewer findings, or tuning the reviewers | Walk through every finding one by one. |

### Step 6: Process Findings
For each finding, presented one at a time:
- **Accept** — finding is valid, will address
- **Reject with note** — finding is wrong or not applicable. Rejection note becomes calibration input to next review cycle. (Discuss mode cut from MVP — evaluate adding in v2 if eval data shows rejected findings aren't being addressed.)

### Step 7: Wrap Up
`summary.md` updated with accept/reject dispositions for each finding.
- If `escalate`: skill tells the user which upstream phase to revisit and why, then exits
- If `revise`: user revises the design, re-runs `parallax:review` (new commit tracks the diff)
- If `proceed`: design approved, move to next pipeline phase

Review artifacts committed in a single git commit per review run (user confirms before commit). Structured commit message: `parallax:review — [topic] — [verdict] ([N] findings)`. Auto-fix changes use a separate commit (see Step 4).

## Pipeline Integration

Review is a gate between phases, not a phase itself:

```
survey → calibrate → [REVIEW requirements] → design → [REVIEW design] → plan → [REVIEW plan] → execute
```

The orchestrator (`parallax:orchestrate`, future) will invoke `parallax:review` at each gate. For now, the user invokes manually.

Each stage uses the same skill, same output format, same processing workflow. Only the active personas and escalation targets change.

## Prototype Scope

This design is phase 1 of the orchestrator problem statement. Scope boundary: review skill only. Requirement refinement (parallax:calibrate) and full pipeline orchestration (parallax:orchestrate) are separate designs.

**Build now (design stage):**
- 6 reviewer personas (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout)
- Synthesizer agent
- Finding classification by severity and phase
- Interactive finding processing (accept/reject-with-note). JSONL output enables jq-based filtering by severity/persona/phase without LLM tokens.
- Markdown output to `docs/reviews/<topic>/`
- Critical-first and all-findings processing modes
- Cost logging per review run in JSONL output (pre-dispatch estimates deferred until empirical cost data available)

**Build later (requirements and plan stages):**
- Product Strategist persona (requirements stage)
- Systems Architect persona (plan stage)
- Code Realist persona (plan stage)
- Stage-specific persona activation
- Orchestrator integration

**Validate with:**
- Second Brain Design test case (3 reviews, 40+ findings in the original session)
- Real design docs produced by the brainstorming skill

**Evaluate in early eval phase:**
- Adversarial persona pairs (stance-based, not just domain-based) — test against current coverage-based personas on same artifact (Finding 26)
- Requirements-stage review — validate that adversarial review at requirements-time prevents downstream design failures (Finding 27)
- Inspect AI as implementation substrate — evaluate whether Inspect's multi-agent patterns replace custom orchestration plumbing (Finding 30)

## Open Questions (for eval framework)

- Optimal number of personas per stage (starting hypothesis: 4-6)
- Whether blind spot checks produce actionable findings or noise
- Severity calibration across different personas (prompt engineering problem)
- Cost per review run and whether model tiering (Haiku for simple personas, Sonnet for deep analysis) is worth the quality tradeoff
- Whether contradictions between reviewers are a feature (surfaces real tensions) or noise (prompt inconsistency)
