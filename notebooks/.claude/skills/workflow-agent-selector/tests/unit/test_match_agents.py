"""Unit tests for scripts/match_agents.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from match_agents import rank, score_agent, main as ma_main


def test_score_agent_exact_name():
    agent = {"name": "react-specialist", "description": "Expert React.", "tools": ["vite"]}
    score, reasons = score_agent(["react-specialist"], agent)
    # exact name match yields max raw points; one keyword cap is 1.0
    assert score == 1.0
    assert any("exact name match" in r for r in reasons)


def test_score_agent_name_token():
    agent = {"name": "react-specialist", "description": "Expert.", "tools": []}
    score, _ = score_agent(["react"], agent)
    assert 0.6 < score <= 0.8  # 0.7 / 1.0 cap


def test_score_agent_description_token():
    agent = {"name": "frontend-developer", "description": "Builds React UIs.", "tools": []}
    score, _ = score_agent(["react"], agent)
    # description token only; less than name match
    assert 0 < score < 0.5


def test_score_agent_no_match():
    agent = {"name": "postgres-pro", "description": "DB tuning.", "tools": ["psql"]}
    score, reasons = score_agent(["react"], agent)
    assert score == 0.0
    assert reasons == []


def test_score_agent_tool_match():
    agent = {"name": "x-engineer", "description": "Generic.", "tools": ["jest"]}
    score, _ = score_agent(["jest"], agent)
    # tool weight is 0.15 / 1.0 cap = 0.15
    assert 0 < score <= 0.2


def test_rank_sorts_descending(tmp_agents_root):
    from parse_agent_frontmatter import parse_agents

    agents = parse_agents(tmp_agents_root)
    out = rank(["react"], agents)
    assert len(out) >= 2
    scores = [r["score"] for r in out]
    assert scores == sorted(scores, reverse=True)
    # react-specialist should beat frontend-developer for the keyword 'react'
    assert out[0]["agent"] == "react-specialist"


def test_rank_min_score_filter(tmp_agents_root):
    from parse_agent_frontmatter import parse_agents

    agents = parse_agents(tmp_agents_root)
    out = rank(["react"], agents, min_score=0.99)
    # nothing should have a 1.0 score for a single-token keyword
    assert out == []


def test_rank_max_results(tmp_agents_root):
    from parse_agent_frontmatter import parse_agents

    agents = parse_agents(tmp_agents_root)
    out = rank(["react", "frontend"], agents, max_results=1)
    assert len(out) == 1


def _run_main(argv, stdin_text=None, monkeypatch=None):
    old_argv = sys.argv
    sys.argv = ["match_agents.py"] + argv
    if stdin_text is not None:
        import io
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_text))
    try:
        return ma_main()
    finally:
        sys.argv = old_argv


def test_main_with_keywords_json_file(tmp_agents_root, tmp_path, capsys):
    q = tmp_path / "q.json"
    q.write_text(json.dumps({"keywords": ["react"], "max_results": 2}), encoding="utf-8")
    rc = _run_main(["--keywords-json", str(q), "--agents-root", str(tmp_agents_root)])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert len(data) <= 2
    for row in data:
        assert 0.0 <= row["score"] <= 1.0


def test_main_bad_json(tmp_agents_root, tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("not json"))
    sys.argv = ["match_agents.py", "--agents-root", str(tmp_agents_root)]
    assert ma_main() == 1


def test_main_keywords_not_list(tmp_agents_root, tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys,
        "stdin",
        __import__("io").StringIO(json.dumps({"keywords": "react"})),
    )
    sys.argv = ["match_agents.py", "--agents-root", str(tmp_agents_root)]
    assert ma_main() == 1


def test_main_list_payload(tmp_agents_root, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO(json.dumps(["postgres"])))
    sys.argv = ["match_agents.py", "--agents-root", str(tmp_agents_root)]
    assert ma_main() == 0
    data = json.loads(capsys.readouterr().out)
    assert any(r["agent"] == "postgres-pro" for r in data)
