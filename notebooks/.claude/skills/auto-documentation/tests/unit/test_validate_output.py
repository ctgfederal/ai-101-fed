"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import (
    parse_yaml,
    split_frontmatter,
    validate_frontmatter,
    validate_body,
    REQUIRED_FIELDS,
    REQUIRED_SECTIONS,
    main as vo_main,
)


# --- frontmatter parser ---

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


# --- validate_frontmatter ---

def _baseline():
    return {
        "title": "Admins can edit any user post",
        "category": "business-rule",
        "date": "2026-05-08",
        "tags": ["authorization", "permissions"],
        "scope": "UserPostController#update",
        "source": "discovery during /implement",
    }


def test_validate_frontmatter_happy():
    assert validate_frontmatter(_baseline()) == []


def test_validate_frontmatter_missing_required():
    d = _baseline()
    del d["scope"]
    errors = validate_frontmatter(d)
    assert any("missing required field: scope" == e for e in errors)


def test_validate_frontmatter_empty_required():
    d = _baseline()
    d["title"] = ""
    errors = validate_frontmatter(d)
    assert any("empty" in e and "title" in e for e in errors)


def test_validate_frontmatter_unknown_category():
    d = _baseline()
    d["category"] = "made-up"
    errors = validate_frontmatter(d)
    assert any("unknown category" in e for e in errors)


def test_validate_frontmatter_bad_date_format():
    d = _baseline()
    d["date"] = "May 8, 2026"
    errors = validate_frontmatter(d)
    assert any("YYYY-MM-DD" in e for e in errors)


def test_validate_frontmatter_future_date():
    d = _baseline()
    d["date"] = "2999-01-01"
    errors = validate_frontmatter(d)
    assert any("future" in e for e in errors)


def test_validate_frontmatter_too_few_tags():
    d = _baseline()
    d["tags"] = ["only-one"]
    errors = validate_frontmatter(d)
    assert any("2-8" in e for e in errors)


def test_validate_frontmatter_duplicate_tag():
    d = _baseline()
    d["tags"] = ["a", "a"]
    errors = validate_frontmatter(d)
    assert any("duplicate" in e for e in errors)


def test_validate_frontmatter_bad_tag_format():
    d = _baseline()
    d["tags"] = ["Has Space", "ok"]
    errors = validate_frontmatter(d)
    assert any("invalid tag format" in e for e in errors)


def test_validate_frontmatter_title_too_short():
    d = _baseline()
    d["title"] = "tiny"
    errors = validate_frontmatter(d)
    assert any("title length" in e for e in errors)


def test_required_fields_set():
    assert set(REQUIRED_FIELDS) == {"title", "category", "date", "tags", "scope", "source"}


# --- validate_body ---

def test_validate_body_happy():
    body = "## Description\nx\n## Why\nx\n## Examples\nx\n## Related\nx"
    assert validate_body(body) == []


def test_validate_body_missing_section():
    body = "## Description\nx\n## Why\nx\n## Examples\nx"
    errors = validate_body(body)
    assert any("Related" in e for e in errors)


def test_validate_body_out_of_order():
    body = "## Why\nx\n## Description\nx\n## Examples\nx\n## Related\nx"
    errors = validate_body(body)
    assert any("out of order" in e for e in errors)


def test_required_sections_set():
    assert REQUIRED_SECTIONS == ["Description", "Why", "Examples", "Related"]


# --- main ---

def _run_main(argv):
    old = sys.argv
    sys.argv = ["validate_output.py"] + argv
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_happy(fixture_doc_file, capsys):
    rc = _run_main(["--file", str(fixture_doc_file)])
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


def test_main_missing_section(tmp_path):
    f = tmp_path / "incomplete.md"
    f.write_text("""---
title: "Sample missing related section"
category: business-rule
date: 2026-05-08
tags:
  - a
  - b
scope: "X"
source: "y"
---

## Description
x

## Why
x

## Examples
x
""", encoding="utf-8")
    rc = _run_main(["--file", str(f)])
    assert rc == 1
