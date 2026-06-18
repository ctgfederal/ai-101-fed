"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import (
    REQUIRED_FRONT, REQUIRED_SECTIONS, ALLOWED_STATUS,
    parse_yaml, split_frontmatter, validate, main as vo_main,
)


def test_split_frontmatter_happy():
    yaml_text, body = split_frontmatter("---\ntopic: x\n---\nbody\n")
    assert "topic: x" in yaml_text
    assert body.strip() == "body"


def test_split_frontmatter_no_open():
    with pytest.raises(ValueError):
        split_frontmatter("body only")


def test_parse_yaml_quoted():
    data = parse_yaml('topic: "Hello"\ndate: 2026-02-14')
    assert data["topic"] == "Hello"
    assert data["date"] == "2026-02-14"


def _good_body():
    return "\n".join(f"## {s}\nfoo\n" for s in REQUIRED_SECTIONS)


def test_validate_happy():
    data = {"topic": "x", "date": "2026-02-14", "status": "complete"}
    assert validate(data, _good_body()) == []


def test_validate_missing_front():
    data = {"topic": "x"}
    errors = validate(data, _good_body())
    assert any("date" in e for e in errors)
    assert any("status" in e for e in errors)


def test_validate_bad_status():
    data = {"topic": "x", "date": "2026-02-14", "status": "draft"}
    errors = validate(data, _good_body())
    assert any("status" in e for e in errors)


def test_validate_bad_date():
    data = {"topic": "x", "date": "Feb 14", "status": "complete"}
    errors = validate(data, _good_body())
    assert any("YYYY-MM-DD" in e for e in errors)


def test_validate_missing_section():
    body = "## Inspiration\nfoo\n## Audience\nfoo\n"
    data = {"topic": "x", "date": "2026-02-14", "status": "complete"}
    errors = validate(data, body)
    assert any("Projects" in e for e in errors)
    assert any("Scope" in e for e in errors)


def test_validate_out_of_order():
    body = "\n".join(f"## {s}\nfoo\n" for s in reversed(REQUIRED_SECTIONS))
    data = {"topic": "x", "date": "2026-02-14", "status": "complete"}
    errors = validate(data, body)
    assert any("out of order" in e for e in errors)


def _run(argv):
    old = sys.argv
    sys.argv = ["validate_output.py"] + argv
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run(["--file", str(tmp_path / "nope.md")])
    assert rc == 1


def test_main_no_frontmatter(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("body only", encoding="utf-8")
    rc = _run(["--file", str(f)])
    assert rc == 1


def test_main_happy(tmp_path):
    f = tmp_path / "x.md"
    sections = "\n".join(f"## {s}\nfoo\n" for s in REQUIRED_SECTIONS)
    f.write_text(f"---\ntopic: t\ndate: 2026-02-14\nstatus: complete\n---\n\n{sections}\n", encoding="utf-8")
    rc = _run(["--file", str(f)])
    assert rc == 0
