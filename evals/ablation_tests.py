from pathlib import Path
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from evals.utils.dataset_loader import load_validated_findings
from evals.utils.skill_loader import load_skill_content, drop_section
from scorers.severity_scorer import severity_calibration


DATASET_PATH = Path(__file__).parent.parent / "datasets" / "v3_review_validated"


def _ablated_task(section_to_drop: str, task_name: str) -> Task:
    skill = load_skill_content("parallax:requirements")
    ablated = drop_section(skill, section_to_drop)
    return Task(
        dataset=load_validated_findings(DATASET_PATH),
        plan=[system_message(ablated), generate()],
        scorer=severity_calibration(),
        max_tokens=16000,
        metadata={"ablation": section_to_drop, "task": task_name}
    )


@task
def ablation_no_personas() -> Task:
    """Ablation: drop persona descriptions. Expect >50% detection rate drop."""
    return _ablated_task("## Personas", "ablation_no_personas")


@task
def ablation_no_verdict_logic() -> Task:
    """Ablation: drop verdict/severity logic. Expect >50% detection rate drop."""
    return _ablated_task("## Verdict Logic", "ablation_no_verdict_logic")


@task
def ablation_no_synthesis() -> Task:
    """Ablation: drop synthesis instructions. Expect >50% detection rate drop."""
    return _ablated_task("## Synthesis", "ablation_no_synthesis")
