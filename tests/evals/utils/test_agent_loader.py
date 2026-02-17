import pytest
from pathlib import Path
from evals.utils.agent_loader import load_agent_content


def test_load_agent_strips_frontmatter(tmp_path):
    """Body text returned, YAML frontmatter removed."""
    agent_file = tmp_path / "test-agent.md"
    agent_file.write_text(
        "---\nname: test-agent\nmodel: sonnet\n---\n\nYou are the Test Agent.\n"
    )
    result = load_agent_content("test-agent", agents_root=str(tmp_path))
    assert "You are the Test Agent." in result
    assert "name: test-agent" not in result
    assert "---" not in result


def test_load_agent_frontmatter_with_dashes_in_body(tmp_path):
    """Frontmatter body containing '---' must not confuse the parser."""
    agent_file = tmp_path / "tricky.md"
    agent_file.write_text(
        "---\nname: tricky\ndescription: |\n  A description with --- dashes inside\nmodel: sonnet\n---\n\nAgent body text.\n"
    )
    result = load_agent_content("tricky", agents_root=str(tmp_path))
    assert "Agent body text." in result
    assert "name: tricky" not in result


def test_load_agent_no_frontmatter(tmp_path):
    """Files without frontmatter returned as-is."""
    agent_file = tmp_path / "plain.md"
    agent_file.write_text("Plain agent body.\n")
    result = load_agent_content("plain", agents_root=str(tmp_path))
    assert "Plain agent body." in result


def test_load_agent_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_agent_content("nonexistent", agents_root=str(tmp_path))


def test_load_real_assumption_hunter_agent():
    """Real agent file must load without error and return non-empty body."""
    content = load_agent_content("assumption-hunter")
    assert len(content) > 100
    assert "You are the Assumption Hunter" in content
    # Frontmatter fields must not appear in body
    assert "name: assumption-hunter" not in content
    assert "model: sonnet" not in content
