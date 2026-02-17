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


_DATASETS = Path(__file__).parent.parent / "datasets"
_V2_DATASET = _DATASETS / "inspect-ai-integration-requirements-v2"
_LIGHT_DATASET = _DATASETS / "inspect-ai-integration-requirements-light"


@task
def assumption_hunter_eval() -> Task:
    """Evaluate assumption-hunter against its v2 pre-fix ground truth findings."""
    return Task(
        dataset=load_validated_findings(_V2_DATASET, reviewer_filter="assumption-hunter"),
        plan=[
            system_message(load_agent_content("assumption-hunter")),
            generate(),
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
    )


@task
def constraint_finder_eval() -> Task:
    """Evaluate constraint-finder against requirements-light ground truth.

    Note: v2 dataset has 0 constraint-finder real_flaws (all were quality failures).
    requirements-light has 2 constraint-finder real_flaws.
    """
    return Task(
        dataset=load_validated_findings(_LIGHT_DATASET, reviewer_filter="constraint-finder"),
        plan=[
            system_message(load_agent_content("constraint-finder")),
            generate(),
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
    )


@task
def problem_framer_eval() -> Task:
    """Evaluate problem-framer against its v2 pre-fix ground truth findings."""
    return Task(
        dataset=load_validated_findings(_V2_DATASET, reviewer_filter="problem-framer"),
        plan=[
            system_message(load_agent_content("problem-framer")),
            generate(),
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
    )


@task
def scope_guardian_eval() -> Task:
    """Evaluate scope-guardian against its v2 pre-fix ground truth findings."""
    return Task(
        dataset=load_validated_findings(_V2_DATASET, reviewer_filter="scope-guardian"),
        plan=[
            system_message(load_agent_content("scope-guardian")),
            generate(),
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
    )


@task
def success_validator_eval() -> Task:
    """Evaluate success-validator against its v2 pre-fix ground truth findings."""
    return Task(
        dataset=load_validated_findings(_V2_DATASET, reviewer_filter="success-validator"),
        plan=[
            system_message(load_agent_content("success-validator")),
            generate(),
        ],
        scorer=severity_calibration(),
        max_tokens=16000,
    )
