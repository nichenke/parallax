"""
Per-reviewer eval tasks for parallax:requirements agents.

Each @task function evaluates one reviewer agent against its filtered ground truth.
Agents receive the document content directly in the prompt (Sample.input).
No tools are available in the eval context — agents must output JSONL to completion text.

Dataset decisions:
- assumption-hunter, scope-guardian, problem-framer, success-validator:
  use inspect-ai-integration-requirements-v2 (pre-fix ground truth for v2 doc)
- constraint-finder:
  use inspect-ai-integration-requirements-light (v2 dataset has 0 constraint-finder
  real_flaws — all were quality failures per Session 25)
"""
from pathlib import Path
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from evals.utils.dataset_loader import load_validated_findings
from evals.utils.agent_loader import load_agent_content
from scorers.severity_scorer import severity_calibration
from scorers.llm_judge_scorer import llm_judge_match


_DATASETS = Path(__file__).parent.parent / "datasets"
_V2_DATASET = _DATASETS / "inspect-ai-integration-requirements-v2"
_LIGHT_DATASET = _DATASETS / "inspect-ai-integration-requirements-light"


def _reviewer_task(reviewer: str, dataset_path: Path) -> Task:
    """Build a reviewer eval task: load dataset filtered to reviewer, inject agent prompt."""
    return Task(
        dataset=load_validated_findings(dataset_path, reviewer_filter=reviewer),
        plan=[
            system_message(load_agent_content(reviewer)),
            generate(),
        ],
        scorer=[severity_calibration(), llm_judge_match()],
        max_tokens=16000,
    )


@task
def assumption_hunter_eval() -> Task:
    """Evaluate assumption-hunter against its v2 pre-fix ground truth findings."""
    return _reviewer_task("assumption-hunter", _V2_DATASET)


@task
def constraint_finder_eval() -> Task:
    """Evaluate constraint-finder against requirements-light ground truth.

    Note: v2 dataset has 0 constraint-finder real_flaws (all were quality failures).
    requirements-light has 2 constraint-finder real_flaws.
    """
    return _reviewer_task("constraint-finder", _LIGHT_DATASET)


@task
def problem_framer_eval() -> Task:
    """Evaluate problem-framer against its v2 pre-fix ground truth findings."""
    return _reviewer_task("problem-framer", _V2_DATASET)


@task
def scope_guardian_eval() -> Task:
    """Evaluate scope-guardian against its v2 pre-fix ground truth findings."""
    return _reviewer_task("scope-guardian", _V2_DATASET)


@task
def success_validator_eval() -> Task:
    """Evaluate success-validator against its v2 pre-fix ground truth findings."""
    return _reviewer_task("success-validator", _V2_DATASET)
