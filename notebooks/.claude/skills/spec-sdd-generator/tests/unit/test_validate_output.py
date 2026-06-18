"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_output import REQUIRED_SECTIONS, validate, main as vm


def _good_doc():
    sections = "\n".join([
        "## Context References",
        "- [.claude/steering/tech.md](../../steering/tech.md)",
        "- [.claude/steering/structure.md](../../steering/structure.md)",
        "## Overview",
        "## Architecture",
        "## Components",
        "### COMP-001: X",
        "### COMP-002: Y",
        "## Data Model",
        "## External Integrations",
        "## Traceability",
        "| REQ | Components |",
        "| REQ-001 | COMP-001 |",
        "| REQ-002 | COMP-002 |",
        "## Alternatives Considered",
        "## Risks and Mitigations",
        "## Open Questions",
    ])
    return f"# SDD\n\n{sections}\n"


def test_validate_happy():
    assert validate(_good_doc(), ["REQ-001", "REQ-002"]) == []


def test_validate_missing_steering():
    text = _good_doc().replace(".claude/steering/tech.md", "x")
    errors = validate(text, ["REQ-001"])
    assert any("steering/tech.md" in e for e in errors)


def test_validate_missing_section():
    text = _good_doc().replace("## Components", "## NotComp")
    errors = validate(text, ["REQ-001"])
    assert any("Components" in e for e in errors)


def test_validate_uncovered_req():
    text = _good_doc()
    errors = validate(text, ["REQ-001", "REQ-002", "REQ-999"])
    assert any("REQ-999" in e for e in errors)


def test_validate_duplicate_comp():
    text = _good_doc().replace("### COMP-002: Y", "### COMP-001: dup")
    errors = validate(text, ["REQ-001"])
    assert any("duplicate COMP" in e for e in errors)


def _run(*a):
    old = sys.argv
    sys.argv = ["validate_output.py", *a]
    try:
        return vm()
    finally:
        sys.argv = old


def test_main_happy(tmp_path):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(_good_doc())
    prd = tmp_path / "PRD.md"
    prd.write_text("REQ-001 REQ-002")
    rc = _run("--file", str(sdd), "--prd", str(prd))
    assert rc == 0
