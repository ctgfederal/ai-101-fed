"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_output import REQUIRED_SECTIONS, validate, main as vm


def _good():
    sections = "\n".join([
        "## Context References", "x",
        "## Phase 1: Foundation", "T-001 covers COMP-001 REQ-001",
        "## Phase 2: Core", "T-002 covers COMP-002 REQ-002",
        "## Phase 3: Integration", "x",
        "## Phase 4: Polish", "x",
        "## Traceability", "REQ-001 REQ-002",
        "## Open Questions", "_(none)_",
    ])
    return f"# PLAN\n\n{sections}\n"


def test_validate_happy():
    assert validate(_good(), ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"]) == []


def test_validate_missing_section():
    text = _good().replace("## Phase 2: Core", "## Phase 2: NotCore")
    errors = validate(text, ["REQ-001"], ["COMP-001"])
    assert any("Phase 2: Core" in e for e in errors)


def test_validate_uncovered_req():
    errors = validate(_good(), ["REQ-001", "REQ-002", "REQ-999"], ["COMP-001", "COMP-002"])
    assert any("REQ-999" in e for e in errors)


def test_validate_unreferenced_comp():
    errors = validate(_good(), ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002", "COMP-999"])
    assert any("COMP-999" in e for e in errors)


def _run(*a):
    old = sys.argv
    sys.argv = ["validate_output.py", *a]
    try:
        return vm()
    finally:
        sys.argv = old


def test_main_happy(tmp_path):
    plan = tmp_path / "PLAN.md"
    plan.write_text(_good())
    prd = tmp_path / "PRD.md"
    prd.write_text("REQ-001 REQ-002")
    sdd = tmp_path / "SDD.md"
    sdd.write_text("COMP-001 COMP-002")
    rc = _run("--file", str(plan), "--prd", str(prd), "--sdd", str(sdd))
    assert rc == 0
