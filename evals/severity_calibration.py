from pathlib import Path
from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from evals.utils.dataset_loader import load_validated_findings
from evals.utils.skill_loader import load_skill_content
from scorers.severity_scorer import severity_calibration


DATASET_PATH = Path(__file__).parent.parent / "datasets" / "inspect-ai-integration-requirements-light"


@task
def severity_calibration_eval() -> Task:
    """
    Evaluate Critical finding detection against validated ground truth.
    Loads actual skill content at runtime — skill changes flow through automatically.
    """
    return Task(
        dataset=load_validated_findings(DATASET_PATH),
        plan=[
            system_message(load_skill_content("requirements")),
            generate()
        ],
        scorer=severity_calibration(),
        max_tokens=16000
    )
