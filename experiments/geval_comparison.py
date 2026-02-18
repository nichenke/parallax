"""
G-Eval vs direct judge comparison experiment (Issue #75).

Runs both judge prompt styles on labeled findings from the datasets:
- must_find.jsonl        → expected label: GENUINE
- context_dependent_findings.jsonl → expected label: NOT_GENUINE

Reports accuracy, false positive rate, false negative rate, and token cost
for each style. Outputs a side-by-side comparison table.

Usage:
    .venv-evals/bin/python experiments/geval_comparison.py
"""
import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from inspect_ai.model import get_model

from scorers.reverse_judge_scorer import _reverse_judge_one, _geval_judge_one


DATASETS = [
    "datasets/inspect-ai-integration-requirements-v2",
    "datasets/inspect-ai-integration-requirements-light",
]

JUDGE_MODEL = "anthropic/claude-haiku-4-5-20251001"


@dataclass
class LabeledFinding:
    finding: dict
    expected_genuine: bool
    doc_content: str
    dataset: str


@dataclass
class RunResult:
    style: str
    finding_id: str
    expected: bool
    predicted: bool
    reasoning: str
    elapsed_s: float = 0.0


@dataclass
class Summary:
    style: str
    total: int = 0
    correct: int = 0
    false_positives: int = 0   # predicted GENUINE, expected NOT_GENUINE
    false_negatives: int = 0   # predicted NOT_GENUINE, expected GENUINE
    total_elapsed_s: float = 0.0
    errors: list = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def fpr(self) -> float:
        not_genuine = self.total - (self.correct + self.false_negatives)
        # false positive rate = FP / (FP + TN)
        # FP = false_positives, TN = correctly predicted NOT_GENUINE
        denom = self.false_positives + (self.total - self.correct - self.false_negatives - self.false_positives)
        # simpler: among actually-not-genuine findings, how many were called genuine?
        actual_not_genuine = sum(1 for _ in range(self.total))  # filled in aggregate
        return self.false_positives / max(actual_not_genuine, 1)

    @property
    def avg_elapsed_s(self) -> float:
        return self.total_elapsed_s / self.total if self.total else 0.0


def load_corpus() -> list[LabeledFinding]:
    corpus = []
    seen_ids: set[str] = set()

    for ds_path in DATASETS:
        ds = Path(ds_path)
        doc_path = next(ds.glob("*.md"), None)
        if not doc_path:
            print(f"  WARNING: no .md file in {ds_path}, skipping")
            continue
        doc_content = doc_path.read_text()

        for jsonl_file, expected_genuine in [
            (ds / "must_find.jsonl", True),
            (ds / "context_dependent_findings.jsonl", False),
        ]:
            if not jsonl_file.exists():
                continue
            for line in jsonl_file.read_text().splitlines():
                if not line.strip():
                    continue
                finding = json.loads(line)
                fid = finding.get("id", "")
                if fid in seen_ids:
                    continue  # deduplicate across datasets
                seen_ids.add(fid)
                corpus.append(LabeledFinding(
                    finding=finding,
                    expected_genuine=expected_genuine,
                    doc_content=doc_content,
                    dataset=ds_path,
                ))

    return corpus


async def run_style(
    style: str,
    corpus: list[LabeledFinding],
    judge_model,
) -> tuple[Summary, list[RunResult]]:
    judge_fn = _geval_judge_one if style == "geval" else _reverse_judge_one
    summary = Summary(style=style)
    results = []

    async def judge_one(lf: LabeledFinding) -> RunResult:
        t0 = time.monotonic()
        is_genuine, reasoning = await judge_fn(judge_model, lf.finding, lf.doc_content)
        elapsed = time.monotonic() - t0
        return RunResult(
            style=style,
            finding_id=lf.finding.get("id", "?"),
            expected=lf.expected_genuine,
            predicted=is_genuine,
            reasoning=reasoning,
            elapsed_s=elapsed,
        )

    tasks = [judge_one(lf) for lf in corpus]
    run_results = await asyncio.gather(*tasks)

    actual_not_genuine = sum(1 for lf in corpus if not lf.expected_genuine)

    for rr in run_results:
        summary.total += 1
        summary.total_elapsed_s += rr.elapsed_s
        if rr.predicted == rr.expected:
            summary.correct += 1
        elif rr.predicted and not rr.expected:
            summary.false_positives += 1
        elif not rr.predicted and rr.expected:
            summary.false_negatives += 1
        results.append(rr)

    return summary, results


def print_results(
    corpus: list[LabeledFinding],
    direct_summary: Summary,
    geval_summary: Summary,
    direct_results: list[RunResult],
    geval_results: list[RunResult],
):
    actual_not_genuine = sum(1 for lf in corpus if not lf.expected_genuine)
    actual_genuine = sum(1 for lf in corpus if lf.expected_genuine)

    print("\n" + "=" * 70)
    print(f"G-Eval vs Direct Judge Comparison — {direct_summary.total} labeled findings")
    print(f"  Corpus: {actual_genuine} GENUINE + {actual_not_genuine} NOT_GENUINE")
    print("=" * 70)

    header = f"{'Metric':<30} {'Direct':>12} {'G-Eval':>12}"
    print(header)
    print("-" * len(header))

    def row(label, d_val, g_val):
        print(f"{label:<30} {d_val:>12} {g_val:>12}")

    row("Accuracy", f"{direct_summary.accuracy:.1%}", f"{geval_summary.accuracy:.1%}")
    row("Correct", str(direct_summary.correct), str(geval_summary.correct))
    row("False positives (FP)", str(direct_summary.false_positives), str(geval_summary.false_positives))
    row("False negatives (FN)", str(direct_summary.false_negatives), str(geval_summary.false_negatives))

    d_fpr = direct_summary.false_positives / max(actual_not_genuine, 1)
    g_fpr = geval_summary.false_positives / max(actual_not_genuine, 1)
    d_fnr = direct_summary.false_negatives / max(actual_genuine, 1)
    g_fnr = geval_summary.false_negatives / max(actual_genuine, 1)

    row("FP rate (FP/actual-NOT_GENUINE)", f"{d_fpr:.1%}", f"{g_fpr:.1%}")
    row("FN rate (FN/actual-GENUINE)", f"{d_fnr:.1%}", f"{g_fnr:.1%}")
    row("Avg latency/finding (s)", f"{direct_summary.avg_elapsed_s:.2f}s", f"{geval_summary.avg_elapsed_s:.2f}s")

    print("=" * 70)

    # Per-finding diff — show disagreements
    disagreements = [
        (dr, gr, lf)
        for dr, gr, lf in zip(direct_results, geval_results, corpus)
        if dr.predicted != gr.predicted
    ]

    if not disagreements:
        print("\nNo disagreements between styles.")
    else:
        print(f"\nDisagreements ({len(disagreements)}):")
        for dr, gr, lf in disagreements:
            label = "GENUINE" if lf.expected_genuine else "NOT_GENUINE"
            d_pred = "GENUINE" if dr.predicted else "NOT_GENUINE"
            g_pred = "GENUINE" if gr.predicted else "NOT_GENUINE"
            correct_style = "geval" if gr.predicted == lf.expected_genuine else "direct"
            print(f"\n  [{lf.finding.get('id')}]  expected={label}")
            print(f"    direct → {d_pred}   geval → {g_pred}   (correct: {correct_style})")
            print(f"    title: {lf.finding.get('title', '')[:80]}")

    # Errors in both styles
    errors = [
        (r, lf)
        for results, corpus_lf in [(direct_results, corpus), (geval_results, corpus)]
        for r, lf in zip(results, corpus_lf)
        if r.predicted != lf.expected_genuine
    ]
    if errors:
        print(f"\nAll errors (both styles):")
        seen = set()
        for r, lf in errors:
            key = (r.style, r.finding_id)
            if key in seen:
                continue
            seen.add(key)
            label = "GENUINE" if lf.expected_genuine else "NOT_GENUINE"
            pred = "GENUINE" if r.predicted else "NOT_GENUINE"
            print(f"\n  [{r.style}] [{r.finding_id}]  expected={label}  predicted={pred}")
            # Show first 3 lines of reasoning
            lines = r.reasoning.splitlines()
            for line in lines[:3]:
                print(f"    {line}")
            if len(lines) > 3:
                print(f"    ... ({len(lines)} lines total)")


async def main():
    print("Loading corpus...")
    corpus = load_corpus()
    print(f"  {len(corpus)} labeled findings loaded")

    judge_model = get_model(JUDGE_MODEL)
    print(f"  Judge: {JUDGE_MODEL}")

    print("\nRunning direct judge...")
    direct_summary, direct_results = await run_style("direct", corpus, judge_model)

    print("Running G-Eval judge...")
    geval_summary, geval_results = await run_style("geval", corpus, judge_model)

    print_results(corpus, direct_summary, geval_summary, direct_results, geval_results)


if __name__ == "__main__":
    asyncio.run(main())
