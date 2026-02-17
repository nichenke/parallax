# Research Report: Inspect AI Best Practices for Complex Multi-Step Evaluations

> Commissioned: Session 21 (2026-02-17). Opus 4.6 background agent.
> Context: `make eval` returning accuracy 0.000 — skill/eval mismatch diagnosed, need path forward.

## Executive Summary

The core problem — parallax skills are **orchestration workflows** (dispatch subagents, write to disk, interact with users) that cannot be used as simple eval system prompts — is documented in ground truth as finding `v1-post-review-001`. This report lays out three concrete approaches Inspect AI supports, evaluates each against the use case, and recommends the path forward.

**Bottom line recommendation:** Decompose. Test individual reviewer agents (assumption-hunter, scope-guardian, etc.) directly in Inspect AI, not the orchestration wrapper. The orchestration skill (`requirements/SKILL.md`) is a coordinator — it adds no analytical content. The reviewers are where finding quality lives, and they map cleanly to Inspect AI's native patterns.

---

## 1. How Inspect AI Handles Complex Multi-Step Agents

Inspect AI provides three tiers of agent complexity:

### Tier 1: Solver Chains (Current approach)

```python
plan=[
    system_message(load_skill_content("requirements")),
    generate()
]
```

Simplest pattern: load a system prompt, call generate once, score the output. Works for single-turn tasks. **Does not work** for orchestration skills — model sees instructions to "use the Task tool" and "dispatch 5 reviewers" but has no Task tool available, producing the 102-token failure documented in ground truth finding v1-post-review-001.

### Tier 2: Agents with Tools (Right fit for individual reviewers)

Reviewer agents have `tools: ["Read", "Grep", "Glob", "Write"]` in their frontmatter. In eval context, you can provide **mock versions** of these tools that return pre-loaded content:

```python
@tool
def mock_read():
    async def execute(path: str):
        """Read a file from the project."""
        return preloaded_content[path]
    return execute

solver=[
    system_message(reviewer_prompt),
    use_tools(mock_read()),
    generate()
]
```

**Phase 1 shortcut:** Since the skill pre-loads document content before dispatching reviewers, the reviewer agents can work with just the document in their `Sample.input`. No tools needed for Phase 1. Add mock tools in Phase 2 for richer behavior testing.

### Tier 3: Agent Bridge / inspect_swe (Full CLI agent in Docker)

Runs the actual Claude Code CLI inside a Docker sandbox, proxying API calls through Inspect. Used by `inspect_swe` to run Claude Code and Codex on SWE-Bench tasks.

**Skip for Phase 1-2.** This is for evaluating agents that *are* the product (like Claude Code solving SWE-Bench). In parallax, Claude Code is the runtime environment, not the thing being evaluated.

---

## 2. Whether Agent Bridge / inspect_swe Is the Right Tool

**No.** Comparison:

| Factor | Agent Bridge | Decomposed Reviewers |
|--------|-------------|---------------------|
| Setup complexity | Docker, sandbox config, proxy networking | Pure Python, no containers |
| Cost per run | Full orchestration: 6 reviewer calls + synthesizer | 1 reviewer call per eval sample |
| Iteration speed | Minutes per run | Seconds per run |
| Debugging | Opaque — failures inside container | Full Inspect transcript visibility |
| What it tests | "Does the orchestration workflow run?" | "Does reviewer X detect finding Y?" |
| Value added | Tests coordinator (thin routing layer) | Tests analytical agents (where quality lives) |

Agent bridge becomes relevant in **Phase 3+** when testing the full end-to-end workflow including synthesis, cross-reviewer deduplication, and verdict logic. That is deferred scope.

---

## 3. Concrete Recommendation: Decompose

### Why decompose

The orchestration skill adds: input gathering (interactive), folder creation (mechanical), parallel dispatch (coordination), summary synthesis (testable separately), user presentation (interactive).

The **analytical work** happens in individual reviewer agents. Each agent:
1. Given a document
2. Produces structured findings
3. Quality is measurable (did it find the ground truth findings?)

This maps exactly to Inspect AI's Dataset/Sample/Task/Scorer pattern:
- **Sample input**: The design document content
- **System prompt**: The reviewer agent prompt
- **Target**: Ground truth findings attributed to that reviewer
- **Scorer**: Existing `severity_calibration` scorer

### What you gain

1. **Per-reviewer quality metrics**: "Assumption-hunter detects 9/10 findings at 90% recall" — tells you *which reviewer to improve*
2. **Ablation at the right level**: Ablate sections of individual reviewer prompts, not the coordination wrapper
3. **Much cheaper**: 1 API call per reviewer per sample vs 8+
4. **Faster iteration**: Edit reviewer prompt → run eval → results in seconds
5. **Inspect AI conventions work natively**: No agent bridge, no Docker

---

## 4. Patterns and Tools You Are Missing

### 4a. Per-Reviewer Dataset Splitting

Filter ground truth to only that reviewer's findings:

```python
def load_reviewer_dataset(reviewer_name: str, dataset_path: Path) -> Dataset:
    findings = read_jsonl(dataset_path / "critical_findings.jsonl")
    reviewer_findings = [
        f for f in findings
        if f.get("reviewer") == reviewer_name
        and f.get("validation_status") == "real_flaw"
    ]
    # create Sample with reviewer-specific ground truth
```

Measures: "Does assumption-hunter find the assumption-hunter findings?" without penalizing it for not finding problem-framer findings.

### 4b. The Output Format Gap (CRITICAL — why accuracy is 0.000)

Reviewer agents output **structured markdown** (assumption-hunter.md: "Write your findings as structured markdown"). But `parse_review_output` in `output_parser.py` expects **JSONL output**. This mismatch means the eval parses zero findings from the model's markdown output.

Resolution options:
1. Add "Output your findings as JSONL" instruction to each reviewer prompt in eval context (via solver step)
2. Write a markdown parser for the structured markdown format
3. **Modify reviewer prompts to always output JSONL** (preferred — one format, testable in both contexts)

### 4c. LLM-as-Judge for Finding Quality (Phase 2)

```python
@scorer(metrics={"detection": [accuracy()], "quality": [mean(), stderr()]})
def finding_quality_scorer(grader_model: str = "anthropic/claude-sonnet-4-5"):
    async def score(state, target):
        actual = parse_review_output(state.output.completion)
        expected = state.metadata["expected_findings"]

        # Phase 1: fuzzy match for detection
        detected = match_findings(actual, expected)

        # Phase 2: LLM-as-judge for quality
        quality_scores = []
        for finding in actual:
            grade = await get_model(grader_model).generate(
                f"""Rate this design review finding on 1-5:
                Finding: {json.dumps(finding)}
                Criteria: specific+actionable, severity appropriate, suggestion helpful, "why it matters" convincing
                GRADE: [1-5]"""
            )
            quality_scores.append(parse_grade(grade.completion))

        return Score(value={
            "detection": 1.0 if len(detected)/len(expected) >= 0.9 else 0.0,
            "quality": sum(quality_scores)/len(quality_scores) if quality_scores else 0.0
        })
    return score
```

Inspect AI also supports **multi-model grading** (majority vote across Claude, GPT, Gemini).

### 4d. Epochs for Statistical Robustness

```python
eval(reviewer_eval, epochs=Epochs(5, "mode"))
```

With N=10 ground truth findings, running 5 epochs gives 50 data points for statistical confidence. Directly addresses the design doc's note that "N=15-22 is too small for reliable p-values."

### 4e. Multi-Model Comparison (Free)

```bash
inspect eval evals/reviewer_eval.py \
    --model anthropic/claude-sonnet-4-5 \
    --model openai/gpt-4o \
    --model google/gemini-2.5-pro
```

No code changes needed. Each model runs independently, results compared in Inspect View.

### 4f. Batch API (Free 50% Cost Reduction)

```bash
inspect eval evals/reviewer_eval.py --model anthropic/claude-sonnet-4-5 --batch
```

Routes through Anthropic's Batch API automatically.

---

## 5. Code Sketch: Recommended Architecture

### `evals/reviewer_eval.py`

```python
"""
Per-reviewer evaluation tasks.
Tests individual reviewer agents against their attributed ground truth findings.
"""
from pathlib import Path
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message
from inspect_ai.dataset import MemoryDataset, Sample

from evals.utils.dataset_loader import read_jsonl, count_by_severity
from scorers.severity_scorer import severity_calibration

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "inspect-ai-integration-requirements-light"
AGENTS_DIR = Path(__file__).parent.parent / "agents"

LIGHT_REVIEWERS = [
    "problem-framer",
    "scope-guardian",
    "constraint-finder",
    "assumption-hunter",
    "success-validator",
]


def load_agent_prompt(agent_name: str) -> str:
    """Load reviewer agent prompt, stripping YAML frontmatter."""
    path = AGENTS_DIR / f"{agent_name}.md"
    content = path.read_text()
    if content.startswith("---"):
        end = content.index("---", 3)
        content = content[end + 3:].strip()
    return content


def load_reviewer_dataset(reviewer_name: str) -> MemoryDataset:
    """Load ground truth filtered to a specific reviewer's findings."""
    import json

    findings = read_jsonl(DATASET_PATH / "critical_findings.jsonl")
    metadata = json.loads((DATASET_PATH / "metadata.json").read_text())

    reviewer_findings = [
        f for f in findings
        if f.get("reviewer") == reviewer_name
        and f.get("validation_status") == "real_flaw"
        and f.get("type") == "finding"
    ]

    doc_path = Path(metadata["design_doc_path"])
    if not doc_path.is_absolute():
        doc_path = Path(__file__).parent.parent / doc_path
    doc_content = doc_path.read_text()

    return MemoryDataset(samples=[Sample(
        input=doc_content,
        target=[f["id"] for f in reviewer_findings],
        metadata={
            **metadata,
            "expected_findings": reviewer_findings,
            "severity_distribution": count_by_severity(reviewer_findings),
            "reviewer": reviewer_name,
        }
    )])


def _reviewer_task(reviewer_name: str) -> Task:
    return Task(
        dataset=load_reviewer_dataset(reviewer_name),
        solver=[
            system_message(load_agent_prompt(reviewer_name)),
            generate()
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
        metadata={"reviewer": reviewer_name}
    )


@task
def eval_problem_framer() -> Task:
    return _reviewer_task("problem-framer")

@task
def eval_scope_guardian() -> Task:
    return _reviewer_task("scope-guardian")

@task
def eval_constraint_finder() -> Task:
    return _reviewer_task("constraint-finder")

@task
def eval_assumption_hunter() -> Task:
    return _reviewer_task("assumption-hunter")

@task
def eval_success_validator() -> Task:
    return _reviewer_task("success-validator")
```

---

## 6. Evaluation Layers (Full Strategy)

| Phase | What | How | Inspect Pattern |
|-------|------|-----|-----------------|
| **1** | Individual reviewer quality | Per-reviewer `@task`, doc-as-input, fuzzy-match scorer | `system_message() + generate()` |
| **1.5** | Cross-reviewer aggregate detection | Run all 5 tasks, aggregate scores | Same + result aggregation |
| **2** | Synthesis quality | Pre-compute reviewer outputs, feed to synthesizer | Same, different scorer |
| **2.5** | Finding quality (subjective) | LLM-as-judge with custom rubric | `model_graded_qa()` |
| **3** | End-to-end orchestration | Full skill in Docker | `sandbox_agent_bridge` |

Phase 3 only needed once component evals are passing and integration confidence is required.

---

## 7. Key Findings and Gotchas

### The Output Format Gap (Root Cause of accuracy: 0.000)
Reviewer agent prompts say "Write your findings as structured markdown." Scorer expects JSONL. The eval parses zero findings. **Fix: add JSONL output instruction to reviewer prompts or modify scorer to parse markdown.**

### Sample.input must be a string
`dataset_loader.py` now correctly puts `doc_content` as a string. Original design had `input={"design_doc": path}` — wrong.

### Ground truth in metadata, not target
`expected_findings` in `metadata`, finding IDs in `target` as `list[str]`. Matches Inspect AI's constraint.

### Reviewer agent tools in eval context
Reviewer frontmatter has `tools: ["Read", "Grep", "Glob"]`. In Phase 1, pre-loading content in `Sample.input` is sufficient — reviewers receive full doc text when dispatched by the skill. Mock tools only needed in Phase 2.

---

## 8. Summary of Recommendations

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| Decompose vs. end-to-end | **Decompose** | Reviewer agents are the unit of quality |
| Agent bridge / inspect_swe | **Skip Phase 1-2** | Overkill; Docker complexity for no gain |
| Testing pattern | **Per-reviewer @task** | Per-reviewer metrics; Inspect conventions |
| Tool mocking | **Phase 1: pre-load; Phase 2: mock tools** | Reviewers already receive full text |
| Output format | **Align on JSONL** | Scorer expects JSONL; one format wins |
| LLM-as-judge | **Phase 2 with model_graded_qa** | Finding quality is subjective |
| Multi-model comparison | **Free via --model flag** | No code changes |
| Statistical robustness | **Use epochs (5-10 runs)** | Addresses small N problem |

---

*Sources: Inspect AI docs (solvers, agents, tools, scorers, datasets, agent bridge, react agent, multi-agent), inspect_swe docs, Hamel Husain's Inspect AI notes, Braintrust agent eval framework.*
