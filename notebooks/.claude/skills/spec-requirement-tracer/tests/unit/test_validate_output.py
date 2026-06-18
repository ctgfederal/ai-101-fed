"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_output import extract_prd_reqs, validate, main as vo_main


GOOD_REPORT = """# Traceability Matrix: feature-search

## Feature

`feature-search`

## Summary

3 reqs

## Coverage Matrix

| REQ | SDD Components | PLAN Tasks | Code Refs | Test Refs | Status |
|---|---|---|---|---|---|
| REQ-001 | COMP-001 | T-001 | src/a.py | test_a.py | `covered` |
| REQ-002 | COMP-002 | T-002 | — | — | `partial` |
| REQ-003 | — | — | — | — | `uncovered` |

## Gaps

- **REQ-002** (`partial`) — missing: code, test
- **REQ-003** (`uncovered`) — missing: SDD, PLAN, code, test

## Totals

- Total REQs: **3**
- Covered: **1**
- Partial: **1**
- Uncovered: **1**
"""


def test_extract_prd_reqs():
    text = "REQ-001 stuff REQ-005 things"
    assert extract_prd_reqs(text) == ["REQ-001", "REQ-005"]


def test_extract_prd_reqs_empty():
    assert extract_prd_reqs("nothing") == []


def test_validate_happy():
    errors = validate(GOOD_REPORT, ["REQ-001", "REQ-002", "REQ-003"])
    assert errors == []


def test_validate_missing_section():
    text = GOOD_REPORT.replace("## Gaps\n", "")
    errors = validate(text, ["REQ-001", "REQ-002", "REQ-003"])
    assert any("Gaps" in e for e in errors)


def test_validate_missing_req():
    errors = validate(GOOD_REPORT, ["REQ-001", "REQ-002", "REQ-003", "REQ-099"])
    assert any("REQ-099" in e for e in errors)


def test_validate_template_token_left():
    text = GOOD_REPORT + "\n{{LEFTOVER}}\n"
    errors = validate(text, ["REQ-001", "REQ-002", "REQ-003"])
    assert any("template" in e.lower() for e in errors)


def test_validate_totals_mismatch():
    text = GOOD_REPORT.replace(
        "- Total REQs: **3**", "- Total REQs: **5**"
    )
    errors = validate(text, ["REQ-001", "REQ-002", "REQ-003"])
    assert any("totals" in e.lower() or "Total" in e for e in errors)


def test_validate_totals_dont_reconcile():
    text = GOOD_REPORT.replace("- Covered: **1**", "- Covered: **9**")
    errors = validate(text, ["REQ-001", "REQ-002", "REQ-003"])
    assert any("reconcile" in e for e in errors)


def _run(*a):
    old = sys.argv
    sys.argv = ["validate_output.py", *a]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "no.md"), "--prd", str(tmp_path / "no.md"))
    assert rc == 1


def test_main_happy(tmp_path):
    prd = tmp_path / "PRD.md"
    prd.write_text("REQ-001 REQ-002 REQ-003")
    f = tmp_path / "T.md"
    f.write_text(GOOD_REPORT)
    rc = _run("--file", str(f), "--prd", str(prd))
    assert rc == 0


def test_main_failing(tmp_path):
    prd = tmp_path / "PRD.md"
    prd.write_text("REQ-001 REQ-002 REQ-003 REQ-099")
    f = tmp_path / "T.md"
    f.write_text(GOOD_REPORT)
    rc = _run("--file", str(f), "--prd", str(prd))
    assert rc == 1
