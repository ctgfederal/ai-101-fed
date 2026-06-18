"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import REQUIRED_SECTIONS, validate, main as vo_main


def _good_doc():
    sections = "\n".join([
        "## Context References",
        "- [.claude/steering/product.md#user-personas](../../steering/product.md#user-personas)",
        "## Product Overview",
        "## Personas",
        "## User Stories",
        "## Functional Requirements",
        "- **REQ-001** (story US-1, Must): WHEN x THEN the system SHALL y.",
        "## MoSCoW Priorities",
        "## Success Metrics",
        "## Risks and Constraints",
        "## Open Questions",
    ])
    return f"# PRD\n\n{sections}\n"


def test_validate_happy():
    assert validate(_good_doc()) == []


def test_validate_marker_present():
    text = _good_doc().replace("WHEN x", "[NEEDS CLARIFICATION]")
    errors = validate(text)
    assert any("NEEDS CLARIFICATION" in e for e in errors)


def test_validate_missing_section():
    text = _good_doc().replace("## Personas", "## Other")
    errors = validate(text)
    assert any("Personas" in e for e in errors)


def test_validate_missing_steering_link():
    text = _good_doc().replace(".claude/steering/product.md", ".claude/other.md")
    errors = validate(text)
    assert any("steering" in e for e in errors)


def test_validate_no_req_lines():
    text = _good_doc().replace("- **REQ-001** (story US-1, Must): WHEN x THEN the system SHALL y.", "")
    errors = validate(text)
    assert any("no REQ" in e for e in errors)


def test_validate_non_ears_requirement():
    text = _good_doc().replace("WHEN x THEN the system SHALL y", "user can search")
    errors = validate(text)
    assert any("not EARS-formatted" in e for e in errors)


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
