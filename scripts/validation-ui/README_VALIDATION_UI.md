# Ground Truth Validation UI

Browser-based interface for validating design review findings for the Parallax eval framework.

## Quick Start

### 1. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Validation UI

```bash
# Make sure venv is activated
source venv/bin/activate
python validate_findings.py
```

The UI will start on http://localhost:8000

### 3. Open in Browser

Navigate to http://localhost:8000 and start validating findings.

## Usage

### Validation Flow

1. **Review Finding**: Read the title, issue description, and suggestion
2. **Classify**: Select one of three options:
   - **Real Flaw** (1): A genuine issue that should be addressed
   - **False Positive** (2): Not actually a problem, reviewer was wrong
   - **Ambiguous** (3): Unclear or debatable whether this is a real issue
3. **Add Notes**: Explain your classification (required for good ground truth)
4. **Save**: Click "Save & Continue" or press `S` to save and move to next finding

### Keyboard Shortcuts

- `1` - Mark as Real Flaw
- `2` - Mark as False Positive
- `3` - Mark as Ambiguous
- `→` - Next finding
- `←` - Previous finding
- `S` - Save & Continue

### Filters

- **All**: Show all 22 Critical findings
- **Unvalidated**: Show only findings not yet validated
- **Validated**: Show only findings you've already reviewed

### Progress Tracking

The UI shows:
- Current position (e.g., "Finding 3 of 22")
- Summary stats: Real flaws, false positives, ambiguous, remaining
- Progress is auto-saved after each validation

### Jump to Specific Finding

Use the "Jump to" input to skip to a specific finding number.

## Output

Validated findings are saved to:
```
datasets/v3_review_validated/critical_findings.jsonl
```

Each line is a JSON object with original finding data plus validation metadata:

```json
{
  "id": "v3-001",
  "title": "Original finding title",
  "issue": "...",
  "suggestion": "...",
  "severity": "Critical",
  "reviewer": "edge-case-prober",
  "confidence": "high",
  "validated": true,
  "validation_status": "real_flaw",
  "validation_notes": "This is a genuine issue because...",
  "validator_id": "nic",
  "validation_date": "2026-02-16"
}
```

## Features

✓ One-by-one finding presentation
✓ Real-time progress tracking
✓ Incremental auto-save (work is never lost)
✓ Resume capability (picks up where you left off)
✓ Keyboard shortcuts for fast workflow
✓ Filter by validation status
✓ Jump to specific findings
✓ Validation summary statistics

## Input Source

Reads from:
```
/Users/nic/src/design-parallax/parallax/docs/reviews/parallax-review-v1/findings-v3-all.jsonl
```

Filters to `severity: "Critical"` only (22 findings).

## Validation Notes Guidance

Good validation notes explain **why** you classified the finding:

**Real Flaw:**
- "This is a genuine gap - the design doesn't address X scenario"
- "Correct - this assumption will break when Y happens"

**False Positive:**
- "Not actually a problem - the design already handles this via Z"
- "Reviewer misunderstood the requirement - this is explicitly out of scope"

**Ambiguous:**
- "Could be valid depending on interpretation of requirement R"
- "Edge case that might not matter in practice, unclear if worth addressing"

## Troubleshooting

**Input file not found:**
```bash
# Verify the input file exists
ls -la /Users/nic/src/design-parallax/parallax/docs/reviews/parallax-review-v1/findings-v3-all.jsonl
```

**Port 8000 already in use:**
```bash
# Edit validate_findings.py and change the port number
app.run(debug=True, port=5001)  # Use different port
```

**Lost validation progress:**
- Progress is auto-saved after each validation to the output JSONL file
- If the browser closes, just restart the UI - it will show which findings are already validated
- Use the "Unvalidated" filter to see only remaining work
