from pathlib import Path


def load_agent_content(agent_name: str, agents_root: str | None = None) -> str:
    """
    Load agent system prompt from agents/<name>.md, stripping YAML frontmatter.
    Frontmatter is the content between the first pair of '---' delimiters.
    """
    if agents_root is None:
        root = Path(__file__).parent.parent.parent / "agents"
    else:
        root = Path(agents_root)

    path = root / f"{agent_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Agent not found: {path}")

    content = path.read_text()

    # Strip YAML frontmatter (content between opening and closing "---")
    if content.startswith("---"):
        closing = content.index("---", 3)
        return content[closing + 3:].strip()

    return content.strip()
