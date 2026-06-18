"""Unit tests for scripts/match_skills.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from match_skills import find_matches, match, parse_yaml_minimal, main as ms_main


def test_match_name():
    r = match("postgres", "postgres-pro", "Some description")
    assert "name match" in r


def test_match_description():
    r = match("postgres", "react-specialist", "Use postgres or other DBs")
    assert "description match" in r


def test_match_no_hit():
    assert match("kafka", "react-specialist", "Frontend stuff") == ""


def test_parse_yaml_inline():
    data = parse_yaml_minimal('name: foo\ndescription: a desc')
    assert data["name"] == "foo"
    assert data["description"] == "a desc"


def test_parse_yaml_block_scalar():
    data = parse_yaml_minimal('name: foo\ndescription: |\n  multi-line\n  desc\n')
    assert data["description"] == "multi-line desc"


def test_find_matches_postgres(fake_skills_root):
    out = find_matches(["postgres"], fake_skills_root)
    names = [m["skill"] for m in out]
    assert "postgres-pro" in names
    assert "compound-docs" in names
    assert "react-specialist" not in names


def test_find_matches_empty(fake_skills_root):
    out = find_matches([], fake_skills_root)
    assert out == []


def test_find_matches_no_root(tmp_path):
    out = find_matches(["x"], tmp_path / "missing")
    assert out == []


def _run(*args, stdin_text=None):
    import io
    old, old_stdin = sys.argv, sys.stdin
    sys.argv = ["match_skills.py", *args]
    if stdin_text is not None:
        sys.stdin = io.StringIO(stdin_text)
    try:
        return ms_main()
    finally:
        sys.argv = old
        sys.stdin = old_stdin


def test_main_stdin(fake_skills_root, capsys):
    rc = _run("--skills-root", str(fake_skills_root), stdin_text='["postgres"]')
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert any(m["skill"] == "postgres-pro" for m in data)


def test_main_invalid_json(fake_skills_root, capsys):
    rc = _run("--skills-root", str(fake_skills_root), stdin_text="not json")
    assert rc == 1


def test_main_keywords_not_list(fake_skills_root):
    rc = _run("--skills-root", str(fake_skills_root), stdin_text='"a string"')
    assert rc == 1


def test_main_missing_skills_root(tmp_path):
    rc = _run("--skills-root", str(tmp_path / "missing"), stdin_text='["x"]')
    assert rc == 1
