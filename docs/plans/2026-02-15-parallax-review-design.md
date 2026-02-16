# Design: parallax:review — Adversarial Multi-Agent Design Review

**Date:** 2026-02-15
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
- **Topic label** — name for the review folder

For the prototype, we build `design` stage only. The skill accepts docs as file paths or inline context.

**Output contract:**
- Individual reviewer files (one per persona) saved to `docs/reviews/<topic>/`
- Synthesized summary with findings classified by severity AND pipeline phase
- Overall verdict: `proceed` | `revise` | `escalate`
- Interactive finding-by-finding processing with accept/reject/discuss

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
| **Requirement Auditor** | Coverage gaps, contradictions, gold-plating, anti-goal violations | "Does this actually satisfy the requirements?" |
| **Feasibility Skeptic** | Implementation complexity, hidden costs, simpler alternatives | "Is this buildable as described, and is it the simplest approach?" |
| **First Principles Challenger** | Reexamine the problem from scratch, question whether the framing is right | "Are we solving the right problem? Would we design it this way starting from zero?" |
| **Prior Art Scout** | Existing solutions, standards, libraries, build-vs-buy | "Does this already exist? Are we reinventing something we should leverage?" |

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

The blind spot check is self-error-detection — each reviewer explicitly asks "what am I not seeing?"

## Synthesis

A **Synthesizer agent** consolidates reviewer output. Its role is purely editorial — zero judgment on content or severity.

**Responsibilities:**
1. **Deduplicate** — group findings flagged by multiple reviewers into single entries, noting which reviewers flagged each (consensus signal)
2. **Classify by phase** — assign each finding to the pipeline phase that failed
3. **Surface contradictions** — when reviewers disagree, present both positions with the tension noted (user resolves)
4. **Report severity ranges** — when reviewers rate the same issue differently, report the range ("Flagged Critical by Assumption Hunter, Important by Feasibility Skeptic"), don't editorilaize
5. **Produce summary.md** — structured summary with verdict

**The synthesizer does NOT:**
- Override or adjust reviewer severity ratings
- Pick winners in contradictions
- Add its own findings

### Finding Phase Classification

| Classification | Meaning | Action |
|---|---|---|
| **Survey gap** | Missing research, wrong problem framed | Go back to research |
| **Calibrate gap** | Conflicting requirements, missing anti-goal, wrong priority | Revisit requirements |
| **Design flaw** | Assumption violated, edge case missed, wrong approach | Revise the design |
| **Plan concern** | Implementation issue (flagged for plan review stage) | Carry forward |

### Verdict Logic

- Any Critical finding → `revise` (or `escalate` if it's a survey/calibrate gap)
- Only Important/Minor → `proceed` with noted improvements
- Survey or calibrate gap at any severity → `escalate` (the design can't be fixed without fixing upstream)

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
[Tensions between reviewers that need human resolution]

## Findings by Phase
- Survey gaps: N
- Calibrate gaps: N
- Design flaws: N
- Plan concerns: N

## Finding Dispositions
[Updated as user processes findings — accept/reject/discuss outcome for each]
```

## UX Flow

### Step 1: Invoke
User triggers `parallax:review`. Skill asks for:
- Path to design doc
- Path to requirements doc
- Review stage (default: `design`)
- Topic label for the review folder

### Step 2: Dispatch
Skill confirms inputs, creates `docs/reviews/<topic>/`, dispatches reviewer agents in parallel (4-6 depending on stage). User sees status ("Running 6 reviewers in parallel...").

### Step 3: Synthesize
Synthesizer consolidates findings into `summary.md`. Individual reviewer outputs saved to their own files. All written to disk.

### Step 4: Present Summary
User sees: verdict, finding counts, critical findings listed. Then chooses processing mode:

| Mode | When to use | Behavior |
|---|---|---|
| **Critical-first** | Many findings, want fast iteration | Address Critical findings only. Send source material back for rethink. Remaining findings processed in next pass. |
| **All findings** | Fewer findings, or tuning the reviewers | Walk through every finding one by one. |

### Step 5: Process Findings
For each finding, presented one at a time:
- **Accept** — finding is valid, will address
- **Reject** — finding is wrong or not applicable (feedback for reviewer tuning)
- **Discuss** — full back-and-forth conversation about this finding before deciding

Discuss is a first-class interaction: the user can explore a finding in depth, ask questions, challenge the reviewer's reasoning, and then make an accept/reject decision. The skill maintains its position in the finding queue and resumes after the discussion resolves.

### Step 6: Wrap Up
`summary.md` updated with accept/reject dispositions for each finding.
- If `escalate`: skill tells the user which upstream phase to revisit and why, then exits
- If `revise`: user revises the design, re-runs `parallax:review` (new commit tracks the diff)
- If `proceed`: design approved, move to next pipeline phase

All artifacts committed to git.

## Pipeline Integration

Review is a gate between phases, not a phase itself:

```
survey → calibrate → [REVIEW requirements] → design → [REVIEW design] → plan → [REVIEW plan] → execute
```

The orchestrator (`parallax:orchestrate`, future) will invoke `parallax:review` at each gate. For now, the user invokes manually.

Each stage uses the same skill, same output format, same processing workflow. Only the active personas and escalation targets change.

## Prototype Scope

**Build now (design stage):**
- 6 reviewer personas (Assumption Hunter, Edge Case Prober, Requirement Auditor, Feasibility Skeptic, First Principles Challenger, Prior Art Scout)
- Synthesizer agent
- Finding classification by severity and phase
- Interactive finding processing (accept/reject/discuss)
- Markdown output to `docs/reviews/<topic>/`
- Critical-first and all-findings processing modes

**Build later (requirements and plan stages):**
- Product Strategist persona (requirements stage)
- Systems Architect persona (plan stage)
- Code Realist persona (plan stage)
- Stage-specific persona activation
- Orchestrator integration

**Validate with:**
- Second Brain Design test case (3 reviews, 40+ findings in the original session)
- Real design docs produced by the brainstorming skill

## Open Questions (for eval framework)

- Optimal number of personas per stage (starting hypothesis: 4-6)
- Whether blind spot checks produce actionable findings or noise
- Severity calibration across different personas (prompt engineering problem)
- Cost per review run and whether model tiering (Haiku for simple personas, Sonnet for deep analysis) is worth the quality tradeoff
- Whether contradictions between reviewers are a feature (surfaces real tensions) or noise (prompt inconsistency)
