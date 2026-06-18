"""Unit tests for scripts/validate_frontmatter.py.

Tests hard-code expected error messages — they must NOT reimplement validation logic.
"""
import sys
from pathlib import Path

import pytest

# scripts on path via conftest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_frontmatter import (
    parse_yaml,
    split_frontmatter,
    validate,
    main as vfm_main,
)


# --- parsing ---

def test_split_frontmatter_happy():
    text = "---\ntitle: foo\n---\nbody\n"
    yaml_text, body = split_frontmatter(text)
    assert "title: foo" in yaml_text
    assert body.strip() == "body"


def test_split_frontmatter_no_open_delim():
    with pytest.raises(ValueError, match="frontmatter"):
        split_frontmatter("body without frontmatter")


def test_split_frontmatter_unclosed():
    with pytest.raises(ValueError, match="not closed"):
        split_frontmatter("---\ntitle: foo\nbody\n")


def test_parse_yaml_inline_list():
    data = parse_yaml("tags: [a, b, c]")
    assert data["tags"] == ["a", "b", "c"]


def test_parse_yaml_block_list():
    data = parse_yaml("tags:\n  - a\n  - b\n")
    assert data["tags"] == ["a", "b"]


def test_parse_yaml_quoted_string():
    data = parse_yaml('title: "Foo Bar"')
    assert data["title"] == "Foo Bar"


# --- schema validation ---

def _baseline():
    return {
        "title": "N+1 query in brief generation",
        "category": "performance-issues",
        "date": "2026-02-14",
        "tags": ["rails", "n+1"],
        "module": "BriefGenerator",
        "symptom": "12s render",
        "root_cause": "lazy load",
    }


def test_validate_happy():
    assert validate(_baseline()) == []


def test_validate_missing_required():
    d = _baseline()
    del d["module"]
    errors = validate(d)
    assert any("missing required field: module" == e for e in errors)


def test_validate_empty_required():
    d = _baseline()
    d["title"] = ""
    errors = validate(d)
    assert any("empty" in e and "title" in e for e in errors)


def test_validate_unknown_category():
    d = _baseline()
    d["category"] = "made-up-category"
    errors = validate(d)
    assert any("unknown category" in e for e in errors)


def test_validate_bad_date_format():
    d = _baseline()
    d["date"] = "Feb 14, 2026"
    errors = validate(d)
    assert any("date" in e and "YYYY-MM-DD" in e for e in errors)


def test_validate_future_date():
    d = _baseline()
    d["date"] = "2999-01-01"
    errors = validate(d)
    assert any("future" in e for e in errors)


def test_validate_too_few_tags():
    d = _baseline()
    d["tags"] = ["only-one"]
    errors = validate(d)
    assert any("2-8" in e for e in errors)


def test_validate_too_many_tags():
    d = _baseline()
    d["tags"] = [f"t{i}" for i in range(9)]
    errors = validate(d)
    assert any("2-8" in e for e in errors)


def test_validate_duplicate_tag():
    d = _baseline()
    d["tags"] = ["a", "a"]
    errors = validate(d)
    assert any("duplicate tag" in e for e in errors)


def test_validate_bad_tag_format():
    d = _baseline()
    d["tags"] = ["Has Space", "ok"]
    errors = validate(d)
    assert any("invalid tag format" in e for e in errors)


def test_validate_bad_severity():
    d = _baseline()
    d["severity"] = "catastrophic"
    errors = validate(d)
    assert any("invalid severity" in e for e in errors)


def test_validate_severity_optional():
    d = _baseline()
    # no severity key — must still pass
    assert validate(d) == []


def test_validate_title_too_short():
    d = _baseline()
    d["title"] = "tiny"
    errors = validate(d)
    assert any("title length" in e for e in errors)


def test_validate_title_too_long():
    d = _baseline()
    d["title"] = "x" * 121
    errors = validate(d)
    assert any("title length" in e for e in errors)


# --- main entry point ---

def test_main_happy(fixture_solution_file, capsys):
    rc = _run_main(["--file", str(fixture_solution_file)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "OK" in captured.out


def test_main_missing_file(tmp_path):
    rc = _run_main(["--file", str(tmp_path / "nope.md")])
    assert rc == 1


def test_main_bad_frontmatter(tmp_path):
    f = tmp_path / "broken.md"
    f.write_text("no frontmatter here", encoding="utf-8")
    rc = _run_main(["--file", str(f)])
    assert rc == 1


def _run_main(argv):
    """Invoke main() with sys.argv set."""
    old = sys.argv
    sys.argv = ["validate_frontmatter.py"] + argv
    try:
        return vfm_main()
    finally:
        sys.argv = old
