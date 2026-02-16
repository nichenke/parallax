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
- **Topic label** — name for the review folder (e.g., "auth-system", "parallax-review")

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

### Step 4: Run Synthesizer

After all reviewers complete, dispatch the review-synthesizer agent. It reads all individual review files and produces `docs/reviews/<topic>/summary.md`.

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

**Reject** — Finding is wrong or not applicable. Mark as "rejected" in summary.md. Ask for a brief reason (this is tuning feedback for the reviewer).

**Discuss** — User wants to explore this finding. Have a full conversation about it — answer questions, provide context, challenge or defend the finding. When the discussion reaches a conclusion, ask for accept or reject. Then resume the finding queue.

After each decision, update the finding's Status field in `docs/reviews/<topic>/summary.md`.

### Step 7: Wrap Up

After all selected findings are processed:
- Update summary.md with final dispositions
- Commit all review artifacts to git
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

## Key Principles

- **Adversarial, not hostile** — reviewers probe for weaknesses constructively
- **Phase-aware** — findings classify which pipeline stage failed, not just what's wrong
- **Human decides** — the review informs, the user decides what to act on
- **Persistent artifacts** — everything saved to markdown, tracked by git
- **Discuss is first-class** — exploring a finding is encouraged, not a delay
