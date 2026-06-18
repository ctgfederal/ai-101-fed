"""End-to-end smoke test: query -> match -> render -> validate."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from match_agents import rank
from parse_agent_frontmatter import parse_agents
from validate_match_query import validate as validate_query
from validate_output import validate as validate_report


def render_results_md(matches: list[dict], task: str, keywords: list[str], total: int) -> str:
    rows = []
    for m in matches:
        tools = ", ".join(m["tools"]) if m["tools"] else ""
        rows.append(f"| {m['agent']} | {m['score']:.2f} | {m['reason']} | {tools} | {m['model']} |")
    return f"""# Agent Selection Results

**Task**: {task}
**Keywords**: {", ".join(keywords)}
**Agents searched**: {total}
**Matches returned**: {len(matches)}

## Ranked Matches

| Agent | Score | Reason | Tools | Model |
|-------|-------|--------|-------|-------|
{chr(10).join(rows)}
"""


def test_e2e_happy(tmp_agents_root, tmp_path):
    query = {"keywords": ["react", "form"], "min_score": 0.0, "max_results": 3}

    # 1. Validate the query
    assert validate_query(query) == []

    # 2. Rank
    agents = parse_agents(tmp_agents_root)
    matches = rank(query["keywords"], agents,
                   max_results=query["max_results"],
                   min_score=query["min_score"])
    assert matches, "expected at least one match for 'react'"

    # 3. Render
    md = render_results_md(matches, "Build a RegisterForm", query["keywords"], len(agents))
    out = tmp_path / "results.md"
    out.write_text(md, encoding="utf-8")

    # 4. Validate
    assert validate_report(out.read_text(encoding="utf-8")) == []
