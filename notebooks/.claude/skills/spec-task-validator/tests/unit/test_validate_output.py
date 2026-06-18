"""Unit tests for scripts/validate_output.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import REQUIRED_SECTIONS, validate, main as vo_main


def _good_report() -> str:
    return """# Task Validation Report

## PLAN

`fixture/PLAN.md`

## Summary

| Metric | Count |
|---|---|
| Total tasks | 2 |
| ok | 1 |
| warn | 0 |
| fail | 1 |

## Tasks

| Task | Phase | Status | Issues |
|---|---|---|---|
| T-001 | Foundation | ok | 0 |
| T-002 | Core | fail | 2 |

## Issues

- **T-002** — missing TDD step
- **T-002** — acceptance not measurable

## Verdict

**FAIL**

≥1 task failed validation. Fix the listed issues before /implement.
"""


def test_validate_happy():
    assert validate(_good_report()) == []


def test_validate_missing_section():
    text = _good_report().replace("## Verdict", "## Other")
    errors = validate(text)
    assert any("Verdict" in e for e in errors)


def test_validate_template_token_left():
    text = _good_report().replace("**FAIL**", "{{VERDICT}}")
    errors = validate(text)
    assert any("unsubstituted" in e for e in errors)


def test_validate_inconsistent_summary():
    text = _good_report().replace("| fail | 1 |", "| fail | 99 |")
    errors = validate(text)
    assert any("inconsistent" in e for e in errors)


def test_validate_invalid_verdict():
    text = _good_report().replace("**FAIL**", "**OK**")
    errors = validate(text)
    assert any("verdict" in e.lower() for e in errors)


def test_validate_duplicate_task_row():
    text = _good_report().replace(
        "| T-002 | Core | fail | 2 |",
        "| T-002 | Core | fail | 2 |\n| T-002 | Core | fail | 2 |",
    )
    errors = validate(text)
    assert any("duplicate" in e.lower() for e in errors)


def test_validate_with_payload_cross_check(valid_payload):
    text = _good_report()
    errors = validate(text, valid_payload)
    assert errors == []


def test_validate_payload_task_not_in_report(valid_payload):
    text = _good_report().replace("| T-001 | Foundation | ok | 0 |\n", "")
    # The payload still references T-001, but it's missing from the report
    # We must also fix the summary so it's only inconsistent on the missing task,
    # not on numeric mismatch with the payload
    errors = validate(text, valid_payload)
    assert any("T-001" in e for e in errors)


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_happy(tmp_path):
    f = tmp_path / "report.md"
    f.write_text(_good_report())
    rc = _run("--file", str(f))
    assert rc == 0


def test_main_with_payload(tmp_path, valid_payload):
    f = tmp_path / "report.md"
    f.write_text(_good_report())
    p = tmp_path / "payload.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--file", str(f), "--payload", str(p))
    assert rc == 0


def test_main_payload_missing(tmp_path):
    f = tmp_path / "report.md"
    f.write_text(_good_report())
    rc = _run("--file", str(f), "--payload", str(tmp_path / "nope.json"))
    assert rc == 1
