# Quick Start

## One-Command Launch

```bash
./start.sh
```

Then open http://localhost:5000

## Manual Launch

```bash
source venv/bin/activate
python validate_findings.py
```

## What You'll See

- 28 Critical findings from `findings-v3-all.jsonl`
- One-by-one validation interface
- Progress: "Finding 1 of 28 Critical findings"
- Summary stats: Real flaws, false positives, ambiguous, remaining

## Workflow

1. Read finding (title, issue, suggestion)
2. Press `1` (Real Flaw), `2` (False Positive), or `3` (Ambiguous)
3. Add notes explaining why
4. Press `S` to save and move to next

## Output

`datasets/v3_review_validated/critical_findings.jsonl`

Auto-saved after each validation. Progress is never lost.

## Resume Later

Just restart the UI - it picks up where you left off. Use the "Unvalidated" filter to see remaining work.
