# Parallax

**Design looks different depending on where you stand. Parallax makes you look from everywhere.**

A skill and eval framework for multi-perspective design orchestration in AI-assisted software development.

## The Problem

When building features with AI coding assistants, the workflow looks like this:

1. Brainstorm the idea
2. Write a design doc
3. Launch adversarial review agents (security, architecture, domain)
4. Consolidate findings by hand
5. Iterate the design
6. Write an implementation plan
7. Review the plan for consistency with the design
8. Execute

Today this is manual. The human invokes each skill, launches review agents, consolidates findings, and decides when to iterate vs proceed. The orchestration overhead is real: 15+ minutes per review cycle, findings missed because they fell between reviewers, inconsistencies between design docs and plans that no one caught.

## Why "Parallax"

Parallax is the apparent shift in an object's position when observed from different vantage points. The difference between views is what reveals the truth.

- **Parallax error** — the mistake you make when you only look from one angle. One-perspective design review is parallax error.
- **Baseline** — in parallax measurement, the distance between observation points. Longer baseline = more accurate depth perception. More diverse reviewers = better coverage.
- **Stellar parallax** — astronomers measure a star's distance by observing it from opposite sides of Earth's orbit. Multiple observations over time revealing truth. That's the adversarial review loop.
- **Triangulation** — parallax is the foundation of triangulation. Three sightlines, one fix. Three review agents, one consolidated finding.

## Planned Components

```
parallax:survey      — research and brainstorming phase
parallax:calibrate   — requirement refinement (MoSCoW, anti-goals, success criteria)
parallax:review      — adversarial multi-agent review with finding consolidation
parallax:orchestrate — full pipeline from idea to execution-ready plan
parallax:eval        — skill testing and evaluation framework
```

## Project Tracks

This project explores several interconnected areas. Each is tracked as a GitHub Issue for independent investigation:

| Track | Description |
|-------|-------------|
| **Orchestrator Skill** | The core pipeline: brainstorm -> design -> review -> plan -> execute |
| **Eval Framework** | Skill testing: unit/integration/smoke/perf/cost/ablation/adversarial |
| **Agent Teams** | Experimental multi-agent configurations for review effectiveness and cost |
| **Landscape Analysis** | Competing tools, frameworks, and state-of-the-art monitoring |
| **Autonomous R&D** | Claude-native background automation for skill development |
| **Test Cases** | Black-box validation using real design sessions |

## Status

Early exploration. Problem statement and landscape analysis complete. Design not yet started.

## License

MIT
