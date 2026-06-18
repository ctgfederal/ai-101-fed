"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import REQUIRED_SECTIONS, validate, extract_section, main as vo_main


def _good_doc():
    return """# Delegation: auth-agent

## FOCUS

- src/auth/
- tests/auth/

## EXCLUDE

- src/billing/

## TASK

Build authentication.

## SUCCESS

- pytest tests/auth/ exits 0
- ruff clean

## RETURN

Markdown summary.
"""


def test_required_sections_canonical():
    assert REQUIRED_SECTIONS == ["FOCUS", "EXCLUDE", "TASK", "SUCCESS", "RETURN"]


def test_validate_happy():
    assert validate(_good_doc()) == []


def test_validate_missing_section():
    text = _good_doc().replace("## EXCLUDE", "## OTHER")
    errors = validate(text)
    assert any("EXCLUDE" in e for e in errors)


def test_validate_out_of_order():
    text = _good_doc().replace("## FOCUS", "## ZZZ_FOCUS").replace("## EXCLUDE", "## FOCUS").replace("## ZZZ_FOCUS", "## EXCLUDE")
    errors = validate(text)
    assert any("out of order" in e for e in errors)


def test_validate_empty_focus():
    text = _good_doc().replace("- src/auth/\n- tests/auth/", "_(none)_")
    errors = validate(text)
    assert any("FOCUS" in e for e in errors)


def test_validate_empty_success():
    text = _good_doc().replace("- pytest tests/auth/ exits 0\n- ruff clean", "_(none)_")
    errors = validate(text)
    assert any("SUCCESS" in e for e in errors)


def test_validate_empty_task():
    text = _good_doc().replace("Build authentication.", "")
    errors = validate(text)
    assert any("TASK" in e for e in errors)


def test_validate_exclude_can_be_none():
    text = _good_doc().replace("- src/billing/", "_(none)_")
    # EXCLUDE is allowed to be _(none)_; should still validate.
    errors = validate(text)
    # Other checks should pass — EXCLUDE _(none)_ is OK
    assert not any("EXCLUDE" in e for e in errors)


def test_extract_section_returns_body():
    body = extract_section(_good_doc(), "TASK")
    assert "Build authentication" in body


def test_extract_section_missing():
    body = extract_section(_good_doc(), "NOPE")
    assert body == ""


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "no.md"))
    assert rc == 1


def test_main_happy(tmp_path):
    f = tmp_path / "p.md"
    f.write_text(_good_doc())
    rc = _run("--file", str(f))
    assert rc == 0


def test_main_bad(tmp_path):
    f = tmp_path / "p.md"
    f.write_text("# Just a title\n\n## FOCUS\n\n_(none)_\n")
    rc = _run("--file", str(f))
    assert rc == 1
