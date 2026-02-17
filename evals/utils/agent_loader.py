from pathlib import Path
import frontmatter


def load_agent_content(agent_name: str, agents_root: str | None = None) -> str:
    """
    Load agent system prompt from agents/<name>.md, stripping YAML frontmatter.
    Uses python-frontmatter for robust parsing (handles '---' inside frontmatter body).
    """
    root = Path(__file__).parent.parent.parent / "agents" if agents_root is None else Path(agents_root)
    path = root / f"{agent_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent not found: {path}")

    post = frontmatter.loads(path.read_text())
    return post.content.strip()
