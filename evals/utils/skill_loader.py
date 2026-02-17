import re
from pathlib import Path


def load_skill_content(skill_name: str, skills_root: str | None = None) -> str:
    """Load skill prompt from parallax skills directory."""
    if skills_root is None:
        skills_root = Path(__file__).parent.parent.parent / "skills"
    else:
        skills_root = Path(skills_root)

    skill_path = skills_root / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")
    return skill_path.read_text()


def drop_section(content: str, section_header: str) -> str:
    """
    Remove a markdown section (header + content until next same-level header).
    Used for ablation tests.
    """
    # Determine heading level from header
    level = len(section_header) - len(section_header.lstrip("#"))
    pattern = rf"(?m)^{re.escape(section_header)}.*?(?=^{'#' * level} |\Z)"
    return re.sub(pattern, "", content, flags=re.DOTALL).strip()
