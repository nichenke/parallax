---
name: review
description: This skill should be used when the user asks to "review a design", "adversarial review", "design critique", "find design flaws", "review against requirements", "run parallax review", "parallax:review", or mentions multi-perspective design review.
version: 0.1.0
---

# Adversarial Multi-Agent Design Review

Orchestrate a multi-perspective adversarial review of design artifacts. Dispatch multiple reviewer agents in parallel, each with a distinct critical lens, then synthesize findings for interactive human processing.

## When to Use

- After completing a design document, before moving to implementation planning
- When a design needs adversarial critique from multiple perspectives
- When checking whether a design satisfies its requirements
- At any pipeline gate: requirements -> design -> plan

**Scope:** This skill covers design-stage adversarial review (phase 1 of the parallax orchestrator). Requirements-stage and plan-stage review are planned but not yet implemented.

## Review Stages

| Stage | Active Reviewers | Escalation Target |
|---|---|---|
| `design` (default) | assumption-hunter, edge-case-prober, requirement-auditor, feasibility-skeptic, first-principles, prior-art-scout | calibrate or survey |
| `requirements` | assumption-hunter, requirement-auditor, first-principles, prior-art-scout, product-strategist | user intent |
| `plan` | edge-case-prober, requirement-auditor, feasibility-skeptic, prior-art-scout, systems-architect, code-realist | design or calibrate |

For the current version, `design` stage is fully implemented. Other stages use the same flow with different active reviewers.

## Process

### Step 1: Gather Inputs

Collect from the user:
- **Design artifact path** — the markdown document to review
- **Requirements artifact path** — the requirements/PRD to review against
- **Review stage** — `requirements`, `design`, or `plan` (default: `design`)
- **Topic label** — name for the review folder (e.g., "auth-system", "parallax-review"). Validate: alphanumeric, hyphens, underscores only. Reject invalid characters. Use timestamped subfolder for collision handling.
- **Prior review summary path** (optional) — if re-reviewing, provide the previous summary for cross-iteration tracking

Verify both files exist and are readable before proceeding.

### Step 2: Create Review Folder

Create `docs/reviews/<topic>/` in the project root. If it already exists, this is a re-review — the previous review will be overwritten (git tracks history).

### Step 3: Dispatch Reviewers

Using the Task tool, dispatch all active reviewers for the chosen stage **in parallel**. Each reviewer agent receives:
- The full text of the design document
- The full text of the requirements document
- Instructions to write findings to their assigned output file

Dispatch all reviewers in a single message with multiple Task tool calls.

Each agent writes its output to `docs/reviews/<topic>/<agent-name>.md`.

As reviewers complete, report progress: "Assumption Hunter: done [1/6]"

### Step 4: Run Synthesizer

After all reviewers complete, dispatch the review-synthesizer agent. It reads all individual review files and produces `docs/reviews/<topic>/summary.md`. If a prior review summary was provided, pass it to the synthesizer for cross-iteration comparison.

### Step 5: Present Summary

Show the user:
- Verdict (proceed / revise / escalate)
- Finding counts by severity
- Finding counts by phase
- Verdict reasoning

Then ask the user to choose a processing mode:

**Critical-first** — Walk through Critical findings only. If any require upstream changes, recommend sending the source material back for rethink before processing remaining findings. After critical findings are processed, offer to continue with Important and Minor.

**All findings** — Walk through every finding one by one, in severity order (Critical -> Important -> Minor -> Contradictions).

### Step 6: Process Findings

Present each finding one at a time. For each finding, the user can:

**Accept** — Finding is valid. Mark as "accepted" in summary.md. Note any action items.

**Reject** — Finding is wrong or not applicable. Mark as "rejected" in summary.md. Include a rejection note explaining why — this becomes calibration input for the next review cycle.

After each decision, update the finding's Status field in `docs/reviews/<topic>/summary.md`.

### Step 7: Wrap Up

After all selected findings are processed:
- Update summary.md with final dispositions
- Two commits per review cycle:
  1. Review artifacts commit: all reviewer outputs + summary
  2. Auto-fix commit (if any): changes applied from auto-fixable findings
  User confirms before each commit.
- Report the outcome:
  - If `escalate`: name the upstream phase to revisit and the specific findings driving that
  - If `revise`: list accepted findings that need design changes
  - If `proceed`: confirm the design is approved with any noted improvements

## Output Structure

```
docs/reviews/<topic>/
├── summary.md              — synthesized verdict and finding dispositions
├── assumption-hunter.md    — full review
├── edge-case-prober.md     — full review
├── requirement-auditor.md  — full review
├── feasibility-skeptic.md  — full review
├── first-principles.md     — full review
└── prior-art-scout.md      — full review
```

## Reviewer Tool Access

| Agent | Tools |
|---|---|
| assumption-hunter | Read, Grep, Glob |
| edge-case-prober | Read, Grep, Glob |
| requirement-auditor | Read, Grep, Glob |
| feasibility-skeptic | Read, Grep, Glob |
| first-principles | Read, Grep, Glob |
| prior-art-scout | Read, Grep, Glob, WebSearch |

## Key Principles

- **Adversarial, not hostile** — reviewers probe for weaknesses constructively
- **Phase-aware** — findings classify which pipeline stage failed, not just what's wrong
- **Human decides** — the review informs, the user decides what to act on
- **Persistent artifacts** — everything saved to markdown, tracked by git
- **Async-first** — review always writes artifacts to disk first. Interactive finding processing is a convenience layer that reads from those artifacts. A review can be run, artifacts committed, and findings processed in a later session.
