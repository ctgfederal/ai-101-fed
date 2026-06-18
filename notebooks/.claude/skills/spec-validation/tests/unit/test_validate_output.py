"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import REQUIRED_SECTIONS, validate, main as vo_main


def _good_report() -> str:
    return """# 3Cs Validation Report

## Target

`fixture.md`

## Scores

| C | Score |
|---|---|
| Completeness | 10/10 |
| Consistency | 10/10 |
| Correctness | 10/10 |
| **Overall** | **10/10** |

## Completeness

Score: 10/10

All sections present.

## Consistency

Score: 10/10

No dangling refs.

## Correctness

Score: 10/10

All EARS.

## Issues

_(no issues found)_

## Verdict

**PASS**

Mechanically clean.
"""


def _report_with_issue() -> str:
    return _good_report().replace(
        "| Completeness | 10/10 |",
        "| Completeness | 7/10 |",
    ).replace(
        "## Issues\n\n_(no issues found)_",
        "## Issues\n\n- **completeness** — empty section\n",
    )


def test_validate_happy():
    assert validate(_good_report()) == []


def test_validate_missing_section():
    text = _good_report().replace("## Verdict", "## Other")
    errors = validate(text)
    assert any("Verdict" in e for e in errors)


def test_validate_score_out_of_range():
    text = _good_report().replace("| Completeness | 10/10 |", "| Completeness | 11/10 |")
    errors = validate(text)
    assert any("out of range" in e for e in errors)


def test_validate_template_token_left():
    text = _good_report().replace("**PASS**", "{{VERDICT}}")
    errors = validate(text)
    assert any("unsubstituted" in e for e in errors)


def test_validate_invalid_verdict():
    text = _good_report().replace("**PASS**", "**OK**")
    errors = validate(text)
    # "OK" doesn't match the verdict regex at all => "no verdict line found"
    assert any("verdict" in e.lower() for e in errors)


def test_validate_low_score_no_issues():
    text = _good_report().replace(
        "| Completeness | 10/10 |", "| Completeness | 7/10 |",
    )
    # Issues section still says "(no issues found)"
    errors = validate(text)
    assert any("Issues" in e for e in errors)


def test_validate_low_score_with_issues():
    assert validate(_report_with_issue()) == []


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
