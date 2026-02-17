import re
from pathlib import Path


def load_skill_content(skill_name: str, skills_root: str | None = None) -> str:
    """Load skill prompt from parallax skills directory."""
    root = Path(__file__).parent.parent.parent / "skills" if skills_root is None else Path(skills_root)
    skill_path = root / skill_name / "SKILL.md"
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
    # Anchor to end of header line (\n) to prevent matching prefix-named sections
    # e.g. "## Personas" must not match "## Personas Extended"
    pattern = rf"(?m)^{re.escape(section_header)}\n.*?(?=^{'#' * level} |\Z)"
    return re.sub(pattern, "", content, flags=re.DOTALL).strip()
