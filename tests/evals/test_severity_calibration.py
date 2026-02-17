import pytest
from pathlib import Path
from evals.utils.skill_loader import load_skill_content, drop_section


def test_load_skill_content_returns_string(tmp_path):
    skill_dir = tmp_path / "parallax:requirements"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n\n## Personas\nAssume Hunter")

    content = load_skill_content("parallax:requirements", skills_root=str(tmp_path))
    assert "# Test Skill" in content


def test_load_skill_content_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_skill_content("nonexistent:skill", skills_root=str(tmp_path))


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
