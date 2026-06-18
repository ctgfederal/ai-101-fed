"""Unit tests for scripts/parse_agent_frontmatter.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from parse_agent_frontmatter import (  # noqa: E402
    parse_agents,
    parse_yaml_minimal,
    split_frontmatter,
    main as paf_main,
)


def test_split_frontmatter_happy():
    text = "---\nname: foo\n---\nbody\n"
    yaml, body = split_frontmatter(text)
    assert "name: foo" in yaml
    assert "body" in body


def test_split_frontmatter_no_frontmatter():
    text = "no leading triple dash\n"
    yaml, body = split_frontmatter(text)
    assert yaml == ""
    assert body == text


def test_parse_yaml_minimal_inline_string():
    meta = parse_yaml_minimal('name: react-specialist\ndescription: Expert React.\nmodel: sonnet')
    assert meta["name"] == "react-specialist"
    assert meta["description"] == "Expert React."
    assert meta["model"] == "sonnet"


def test_parse_yaml_minimal_inline_tools():
    meta = parse_yaml_minimal("tools: vite, jest, typescript")
    assert meta["tools"] == ["vite", "jest", "typescript"]


def test_parse_yaml_minimal_block_list_tools():
    yaml = "tools:\n  - vite\n  - jest\n  - typescript\n"
    meta = parse_yaml_minimal(yaml)
    assert meta["tools"] == ["vite", "jest", "typescript"]


def test_parse_yaml_minimal_block_scalar_description():
    yaml = "description: |\n  line one\n  line two\n"
    meta = parse_yaml_minimal(yaml)
    assert "line one" in meta["description"]
    assert "line two" in meta["description"]


def test_parse_agents_skips_claude_md_and_no_frontmatter(tmp_agents_root):
    agents = parse_agents(tmp_agents_root)
    names = {a["name"] for a in agents}
    assert "react-specialist" in names
    assert "frontend-developer" in names
    assert "postgres-pro" in names
    # CLAUDE.md and BROKEN.md must not appear
    assert "claude" not in {n.lower() for n in names}
    for a in agents:
        assert a["name"]


def test_parse_agents_sets_file_path(tmp_agents_root):
    agents = parse_agents(tmp_agents_root)
    for a in agents:
        assert Path(a["file"]).is_file()
        assert a["file"].endswith(".md")


def test_parse_agents_returns_tools_as_list(tmp_agents_root):
    agents = parse_agents(tmp_agents_root)
    for a in agents:
        assert isinstance(a["tools"], list)


def _run_main(argv):
    old = sys.argv
    sys.argv = ["parse_agent_frontmatter.py"] + argv
    try:
        return paf_main()
    finally:
        sys.argv = old


def test_main_happy(tmp_agents_root, capsys):
    rc = _run_main(["--agents-root", str(tmp_agents_root)])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert any(a["name"] == "react-specialist" for a in data)


def test_main_missing_root(tmp_path, capsys):
    rc = _run_main(["--agents-root", str(tmp_path / "does-not-exist")])
    assert rc == 1
