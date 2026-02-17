# Ground Truth Validation UI

## Start

```bash
./start.sh
```

Open http://localhost:8000

## Workflow

1. Read the finding (title, issue, suggestion)
2. Pick a classification: `1` Real Flaw · `2` False Positive · `3` Ambiguous · `4` Duplicate
3. Add notes explaining why
4. Press `S` to save and advance

**Other shortcuts:** `←` / `→` navigate · filter buttons (All / Unvalidated / Validated)

## Output

`datasets/v3_review_validated/critical_findings.jsonl` — auto-saved after each entry. Restart anytime, it picks up where you left off.

## Troubleshooting

**Port in use:** Edit `validate_findings.py` and change `port=8000` to something free.

**Input file missing:** Check `docs/reviews/parallax-review-v1/findings-v3-all.jsonl` exists.
