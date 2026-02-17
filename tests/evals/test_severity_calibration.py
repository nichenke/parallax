import pytest
from pathlib import Path
from evals.utils.skill_loader import load_skill_content, drop_section
from evals.severity_calibration import severity_calibration_eval


def test_load_skill_content_returns_string(tmp_path):
    skill_dir = tmp_path / "parallax:requirements"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n\n## Personas\nAssume Hunter")

    content = load_skill_content("parallax:requirements", skills_root=str(tmp_path))
    assert "# Test Skill" in content


def test_load_skill_content_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_skill_content("nonexistent:skill", skills_root=str(tmp_path))


def test_load_skill_content_real_skills_directory():
    """skill_loader must find skills using directory names, not plugin-qualified names."""
    content = load_skill_content("requirements")  # real dir: skills/requirements/SKILL.md
    assert len(content) > 0


def test_severity_calibration_eval_instantiates():
    """The eval task must instantiate without error — catches wrong skill name at task load time."""
    task = severity_calibration_eval()
    assert task is not None


def test_drop_section_removes_target():
    content = "# Skill\n\n## Personas\nAssume Hunter\n\n## Verdict Logic\nIf critical..."
    result = drop_section(content, "## Personas")
    assert "## Personas" not in result
    assert "Assume Hunter" not in result
    assert "## Verdict Logic" in result


def test_drop_section_nonexistent_is_noop():
    content = "# Skill\n\n## Verdict Logic\nIf critical..."
    result = drop_section(content, "## Nonexistent Section")
    assert result == content


def test_drop_section_does_not_remove_prefix_matched_sections():
    """Dropping '## Personas' must not remove '## Personas Extended' (prefix match bug)."""
    content = "## Personas\ncontent\n\n## Personas Extended\nother content\n\n## Verdict Logic\nlogic"
    result = drop_section(content, "## Personas")
    assert "## Personas Extended" in result
    assert "other content" in result
    assert "## Verdict Logic" in result
    assert "## Personas\n" not in result
