"""
Show full G-Eval reasoning for disagreement cases (where direct=correct, geval=wrong).
"""
import asyncio
import json
from pathlib import Path
from inspect_ai.model import get_model
from scorers.reverse_judge_scorer import _geval_judge_one

JUDGE_MODEL = "anthropic/claude-haiku-4-5-20251001"
DISAGREEMENTS = ["scope-guardian-004", "assumption-hunter-001", "success-validator-001", "assumption-hunter-013"]

async def main():
    judge = get_model(JUDGE_MODEL)
    for ds_path in ["datasets/inspect-ai-integration-requirements-v2", "datasets/inspect-ai-integration-requirements-light"]:
        ds = Path(ds_path)
        doc = next(ds.glob("*.md"), None)
        if not doc:
            continue
        doc_content = doc.read_text()
        jsonl = ds / "must_find.jsonl"
        if not jsonl.exists():
            continue
        for line in jsonl.read_text().splitlines():
            if not line.strip():
                continue
            f = json.loads(line)
            if f.get("id") not in DISAGREEMENTS:
                continue
            print(f"\n{'='*70}")
            print(f"ID: {f['id']}")
            print(f"Title: {f['title']}")
            print(f"Issue: {f.get('issue', '')[:200]}")
            print(f"{'='*70}")
            is_genuine, reasoning = await _geval_judge_one(judge, f, doc_content)
            print(f"G-Eval verdict: {'GENUINE' if is_genuine else 'NOT_GENUINE'}")
            print(f"\nReasoning:\n{reasoning}")

asyncio.run(main())
