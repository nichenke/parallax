# Parallax Eval Framework

Systematic validation for parallax skills using [Inspect AI](https://inspect.aisi.org.uk/).

## Quick Start

```bash
make setup          # Create venv, install dependencies
make test           # Verify all unit tests pass
make eval           # Run severity calibration eval (requires ANTHROPIC_API_KEY)
make view           # Open Inspect View UI
```

## Workflow

### When the design changes significantly

```bash
make review         # Run fresh parallax review on design doc (in Claude Code)
make validate       # Classify findings in browser UI (localhost:5000)
# Ground truth is now current
```

### When iterating on skill prompts

```bash
# Edit skills/parallax:requirements/SKILL.md
make eval           # Did detection rate hold?
make regression     # Compare to baseline — nothing should drop
make view           # Inspect missed findings + false positives
make baseline       # Store when satisfied
```

### When fixing design issues

```bash
# Fix docs/plans/parallax-design-v4.md based on findings
make review         # Re-run review on updated design
make eval           # Confirmed findings should no longer appear
```

## Architecture

- `evals/` — Inspect AI task definitions (Python `@task`)
- `scorers/` — Custom scoring functions (Python `@scorer`)
- `datasets/v3_review_validated/` — Validated ground truth (JSONL)
- `tools/` — Supporting scripts (validation UI, regression detection)
- `evals/baselines/` — Stored baseline runs (gitignored, local only)
- `logs/` — Eval run outputs (gitignored, local only)

## Ground Truth Schema

Findings in `datasets/*/critical_findings.jsonl` extend the parallax JSONL schema with:

- `validated: true` — finding has been reviewed
- `validation_status: "real_flaw" | "false_positive" | "ambiguous"`
- `validation_notes: string` — why this classification
- `validator_id: string` — who validated
- `validation_date: string` — when validated

Only `real_flaw` findings are used as ground truth.

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-..."   # Personal key
# Work context: AWS credentials for Bedrock (see ADR-005)
```
