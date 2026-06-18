"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate, parse_table, main as vo_main


def test_parse_table_happy():
    text = """# Title

| Agent | Score | Reason |
|-------|-------|--------|
| foo   | 0.5   | match  |
"""
    headers, rows = parse_table(text)
    assert headers == ["Agent", "Score", "Reason"]
    assert rows == [["foo", "0.5", "match"]]


def test_parse_table_no_table():
    headers, rows = parse_table("just text\n")
    assert headers == []
    assert rows == []


def test_validate_happy(fixture_results_md):
    text = fixture_results_md.read_text(encoding="utf-8")
    assert validate(text) == []


def test_validate_missing_columns():
    text = """| Foo | Bar |
|-----|-----|
| 1   | 2   |
"""
    errors = validate(text)
    assert any("missing required columns" in e for e in errors)


def test_validate_score_not_number():
    text = """| Agent | Score | Reason |
|-------|-------|--------|
| foo   | high  | match  |
"""
    errors = validate(text)
    assert any("not a number" in e for e in errors)


def test_validate_score_out_of_range():
    text = """| Agent | Score | Reason |
|-------|-------|--------|
| foo   | 1.5   | match  |
"""
    errors = validate(text)
    assert any("out of range" in e for e in errors)


def test_validate_no_data_rows():
    text = """| Agent | Score | Reason |
|-------|-------|--------|
"""
    errors = validate(text)
    assert any("no data rows" in e for e in errors)


def test_validate_empty_agent_cell():
    text = """| Agent | Score | Reason |
|-------|-------|--------|
|       | 0.5   | match  |
"""
    errors = validate(text)
    assert any("empty Agent cell" in e for e in errors)


def _run_main(argv):
    sys.argv = ["validate_output.py"] + argv
    return vo_main()


def test_main_happy(fixture_results_md):
    assert _run_main(["--file", str(fixture_results_md)]) == 0


def test_main_missing_file(tmp_path):
    assert _run_main(["--file", str(tmp_path / "nope.md")]) == 1


def test_main_invalid(tmp_path):
    f = tmp_path / "bad.md"
    f.write_text("no table at all", encoding="utf-8")
    assert _run_main(["--file", str(f)]) == 1
