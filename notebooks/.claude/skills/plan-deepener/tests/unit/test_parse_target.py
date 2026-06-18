"""Unit tests for scripts/parse_target.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from parse_target import (
    split_sections, extract_technologies, extract_categories,
    extract_open_questions, main as pt_main,
)


def test_split_sections():
    md = "# Top\n## A\nbody A\n## B\nbody B\n"
    s = split_sections(md)
    assert len(s) == 2
    assert s[0]["heading"] == "A"
    assert s[1]["body"].strip() == "body B"


def test_split_sections_levels():
    md = "## Top\n### Sub\nbody\n## Other\n"
    s = split_sections(md)
    assert s[0]["level"] == 2
    assert s[1]["level"] == 3
    assert s[2]["level"] == 2


def test_extract_technologies():
    md = "We use Postgres and Redis. Some `node` code:\n```python\nx=1\n```"
    tech = extract_technologies(md)
    assert "postgres" in tech
    assert "redis" in tech
    assert "python" in tech


def test_extract_technologies_word_boundary():
    md = "We mention firstpostgres which should not match"
    assert "postgres" not in extract_technologies(md)


def test_extract_categories():
    sections = [
        {"heading": "Architecture", "level": 3, "body": ""},
        {"heading": "Open Questions", "level": 3, "body": ""},
        {"heading": "Data Model", "level": 3, "body": ""},
    ]
    cats = extract_categories(sections)
    assert "Architecture" in cats
    assert "Data Model" in cats
    assert "Open Questions" not in cats


def test_extract_open_questions():
    sections = [{"heading": "Open Questions", "level": 3,
                 "body": "- Q1?\n- Q2?\nnot a question\n"}]
    qs = extract_open_questions(sections)
    assert qs == ["Q1?", "Q2?"]


def _run(*args):
    old = sys.argv
    sys.argv = ["parse_target.py", *args]
    try:
        return pt_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "no.md"))
    assert rc == 1


def test_main_happy(tmp_path, capsys, sample_target_md):
    f = tmp_path / "x.md"
    f.write_text(sample_target_md, encoding="utf-8")
    rc = _run("--file", str(f))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "sections" in data
    assert "postgres" in data["technologies"]
