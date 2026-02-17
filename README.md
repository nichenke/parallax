# Parallax

**Design looks different depending on where you stand. Parallax makes you look from everywhere.**

An adversarial multi-perspective design review framework for Claude Code and Codex.

---

It's Thursday afternoon. Instead of pushing your design straight to implementation, you run the tool. Seven minutes later, you're staring at a report that makes your stomach drop — in the best possible way. The Assumption Hunter found three places where you assumed exactly-once delivery but your message broker guarantees at-least-once. The Edge Case Prober identified a race condition in your cache invalidation only visible under concurrent writes from two regions. The Feasibility Skeptic noted that your "simple migration" requires a table lock on a 400M-row table during a zero-downtime deploy. Six Critical findings. You would have discovered every one of them in production, three weeks from now, under pressure, with customers waiting.

You address the six findings, re-run, watch the count drop to zero. When Monday comes, you're not hoping the design holds — you know it holds. The ambush already happened, and you won.

---

## The Problem

AI coding assistants are good at building what you ask for. They're bad at telling you what's wrong with what you asked for.

The real failure mode isn't implementation bugs — it's design flaws that survive review because review happened from one angle. Your design looks solid from where you're standing. But you're only standing in one place. The assumption you don't know you're making, the edge case outside your experience, the prior art from a domain you've never touched — these don't surface from a single perspective, no matter how senior the reviewer.

One-perspective design review is parallax error. The fix is more observation points.

## Why "Parallax"

Parallax is the apparent shift in an object's position when observed from different vantage points. The difference between views is what reveals the truth.

**Parallax error** is what happens when you only look from one angle — the core problem this solves. **Baseline** is the distance between observation points; longer baseline means more accurate depth perception, and more diverse reviewers means better coverage. **Triangulation** is what parallax enables: three sightlines converge on one fix, three review agents converge on one consolidated finding.

## Components

```
parallax:survey       research and brainstorming
parallax:calibrate    requirement refinement (MoSCoW, anti-goals, success criteria)
parallax:review       adversarial multi-agent review with finding consolidation
parallax:orchestrate  full pipeline: idea → execution-ready plan
parallax:eval         skill testing and evaluation framework
```

## Project Tracks

Each track is an independent investigation area, tracked as GitHub Issues:

| Track | Description |
|-------|-------------|
| **Orchestrator Skill** | Core pipeline: brainstorm → design → review → plan → execute |
| **Eval Framework** | Skill testing with Inspect AI: unit, integration, regression, ablation |
| **Agent Teams** | Multi-agent review configurations — effectiveness vs. cost tradeoffs |
| **Landscape Analysis** | Competing tools, frameworks, state-of-the-art monitoring |
| **Autonomous R&D** | Claude-native background automation for skill development |
| **Test Cases** | Black-box validation against real design sessions with ground truth |

## Status

Requirements complete. Early design and eval framework implementation underway. The `parallax:requirements` skill is validated and working. Eval integration with [Inspect AI](https://inspect.ai-safety-institute.org.uk/) is in progress.

## License

MIT
