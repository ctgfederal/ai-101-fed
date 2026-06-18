"""Shared pytest fixtures for workflow-agent-selector tests."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _write_agent(root: Path, name: str, description: str, tools: list[str], model: str = "sonnet") -> Path:
    f = root / f"{name}.md"
    tools_yaml = ", ".join(tools)
    f.write_text(
        f"""---
name: {name}
description: {description}
tools: {tools_yaml}
model: {model}
---

# {name}

Body text.
""",
        encoding="utf-8",
    )
    return f


@pytest.fixture
def tmp_agents_root(tmp_path: Path) -> Path:
    """A clean ~/.claude/agents tree with a small fixture set."""
    root = tmp_path / "agents"
    root.mkdir()
    _write_agent(
        root,
        "react-specialist",
        "Expert React specialist. Hooks, server components, form state, performance optimization for React applications.",
        ["vite", "jest", "typescript"],
    )
    _write_agent(
        root,
        "frontend-developer",
        "Frontend developer for general UI work using React or Vue.",
        ["vite", "npm", "jest"],
    )
    _write_agent(
        root,
        "backend-developer",
        "Senior backend engineer for APIs, services, and PostgreSQL.",
        ["Read", "Write", "Bash", "Docker", "postgresql"],
    )
    _write_agent(
        root,
        "postgres-pro",
        "PostgreSQL specialist. Query plans, indexing, replication.",
        ["psql", "pg_dump"],
    )
    _write_agent(
        root,
        "security-engineer",
        "Implements secure authentication and authorization for web applications.",
        ["Read", "Write", "Bash"],
    )
    # one with no frontmatter, to test skip behaviour
    (root / "BROKEN.md").write_text("# no frontmatter here", encoding="utf-8")
    # uppercase CLAUDE.md should be skipped
    (root / "CLAUDE.md").write_text("# index\n", encoding="utf-8")
    return root


@pytest.fixture
def valid_query() -> dict:
    return {"keywords": ["react", "form", "component"], "min_score": 0.05, "max_results": 3}


@pytest.fixture
def invalid_query_no_keywords() -> dict:
    return {"min_score": 0.5}


@pytest.fixture
def fixture_results_md(tmp_path: Path) -> Path:
    f = tmp_path / "results.md"
    f.write_text(
        """# Agent Selection Results

## Ranked Matches

| Agent | Score | Reason | Tools | Model |
|-------|-------|--------|-------|-------|
| react-specialist | 0.42 | name token match: 'react' | vite, jest | sonnet |
| frontend-developer | 0.30 | name token match: 'frontend' | vite, npm | sonnet |
""",
        encoding="utf-8",
    )
    return f
