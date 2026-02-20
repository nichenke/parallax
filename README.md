# Parallax

**Design looks different depending on where you stand.**

Adversarial multi-perspective design review for AI-assisted development. You write a design doc, Parallax throws specialized review agents at it—an assumption hunter, an edge case prober, a feasibility skeptic—and consolidates their findings into something you can act on before you've written a line of implementation code.

The name: parallax is the shift in apparent position when you observe from a different vantage point. One-angle review is parallax error. More observation points, more accurate picture. That's the whole thesis.

## What it does

Run a design doc through multiple review agents, each tuned to a different failure mode. Get back consolidated findings ranked by severity. Fix the critical ones, re-run, watch the count drop. The ambush happens here—not three weeks later in production with customers waiting.

Today this is a pipeline of Claude Code skills:

```
parallax:survey       — research and brainstorming
parallax:calibrate    — requirement refinement (MoSCoW, anti-goals)
parallax:review       — adversarial multi-agent review
parallax:orchestrate  — full pipeline: idea → execution-ready plan
parallax:eval         — skill testing and evaluation framework
```

## Current state

This is an R&D repo. Some pieces work, some don't yet, nothing is pip-installable.

**Working:** Eval framework on [Inspect AI](https://inspect.ai-safety-institute.org.uk/)—reviewer precision/recall measurement, severity calibration, confidence self-scoring. The eval loop runs, produces real metrics, and has caught real prompt regressions.

**In progress:** Review agent prompt tuning driven by eval results. Finding consolidation across agents. Orchestrator pipeline connecting skill phases end-to-end.

**Not started:** Multi-model review teams (Claude + GPT + Gemini on the same artifact), autonomous agent R&D, self-improvement loops.

Track details in [GitHub Issues](../../issues).

## Architecture

The core bet: a pipeline of independent skills, not a monolithic agent. Each namespace segment (`survey`, `calibrate`, `review`) is useful standalone. The orchestrator composes them but doesn't own them.

Evaluation uses Inspect AI with ground-truth datasets built from real design sessions. The eval framework measures whether review agents find known flaws (recall) without hallucinating findings that aren't there (precision).

Key frameworks: **Inspect AI** for evals, **LangGraph** for pipeline orchestration, **Claude Code Swarms** for multi-agent review.

## Setup

```bash
git clone git@github.com:nichenke/parallax.git
cd parallax
git config core.hooksPath hooks    # branch protection hook
make install                        # venv + dev deps + directories
```

### Running evals

```bash
make eval              # severity calibration
make reviewer-eval     # reviewer precision/recall
make ablation          # prompt ablation studies
```

## Contributing

Feature branches only—the pre-commit hook enforces this. Use worktrees for isolation:

```bash
git worktree add .worktrees/<name> -b feature/<name>
cd .worktrees/<name>
make install
```

## License

MIT
