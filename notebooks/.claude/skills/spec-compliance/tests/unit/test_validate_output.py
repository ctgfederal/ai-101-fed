"""Unit tests for scripts/validate_output.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate, main as vo_main


GOOD_REPORT = """# Specification Compliance Report

## Spec

- PRD: `PRD.md`
- SDD: `SDD.md`

## Repository

`/tmp/repo`

## Status

**partial**

Some gaps.

## Components

| Component | Name | Expected | Found | Status |
|---|---|---|---|---|
| COMP-001 | A | `a.py` | `a.py` | PRESENT |
| COMP-002 | B | `b.py` | _(none)_ | MISSING |

## Requirements

| Requirement | Referenced In | Status |
|---|---|---|
| REQ-001 | `a.py` | REFERENCED |
| REQ-002 | _(none)_ | UNREFERENCED |

## Deviations

- **missing-component** (COMP-002) — B: no file at b.py
- **unreferenced-requirement** (REQ-002) — REQ-002 not referenced

## Summary

- Components: 1/2 present
- Requirements: 1/2 referenced
- Deviations: 2
"""


def test_good_report_validates():
    errors = validate(GOOD_REPORT)
    assert errors == []


def test_detects_missing_section():
    text = GOOD_REPORT.replace("## Deviations\n", "## Other\n")
    errors = validate(text)
    assert any("missing section: ## Deviations" in e for e in errors)


def test_detects_invalid_status():
    text = GOOD_REPORT.replace("**partial**", "**ok**")
    errors = validate(text)
    assert any("status" in e.lower() for e in errors)


def test_detects_template_token_leftover():
    text = GOOD_REPORT + "\n{{LEFTOVER}}\n"
    errors = validate(text)
    assert any("unsubstituted" in e for e in errors)


def test_detects_no_status_line():
    text = GOOD_REPORT.replace("**partial**", "partial-but-not-bold")
    errors = validate(text)
    assert any("status line" in e.lower() for e in errors)


def test_section_order_check():
    swapped = GOOD_REPORT.replace(
        "## Deviations\n\n- **missing-component**",
        "## Summary\n\n- swapped",
    ).replace(
        "## Summary\n\n- Components",
        "## Deviations\n\n- Components"
    )
    # we just need a report where order is wrong; do a simpler version:
    text = (
        "## Repository\n\nx\n\n"
        "## Spec\n\n- PRD: `x`\n- SDD: `y`\n\n"
        "## Status\n\n**partial**\n\n"
        "## Components\n\nx\n\n"
        "## Requirements\n\nx\n\n"
        "## Deviations\n\nx\n\n"
        "## Summary\n\nx\n"
    )
    errors = validate(text)
    assert any("out of order" in e for e in errors)


def test_with_spec_json_check_passes():
    spec = {
        "comps": [{"id": "COMP-001"}, {"id": "COMP-002"}],
        "reqs": ["REQ-001", "REQ-002"],
    }
    errors = validate(GOOD_REPORT, spec)
    assert errors == []


def test_with_spec_json_missing_component():
    spec = {
        "comps": [{"id": "COMP-999"}],
        "reqs": [],
    }
    errors = validate(GOOD_REPORT, spec)
    assert any("COMP-999" in e for e in errors)


def test_with_spec_json_missing_requirement():
    spec = {
        "comps": [],
        "reqs": ["REQ-999"],
    }
    errors = validate(GOOD_REPORT, spec)
    assert any("REQ-999" in e for e in errors)


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


def test_main_valid_report(tmp_path):
    f = tmp_path / "report.md"
    f.write_text(GOOD_REPORT)
    rc = _run("--file", str(f))
    assert rc == 0


def test_main_invalid_report(tmp_path):
    f = tmp_path / "report.md"
    f.write_text("# nothing here")
    rc = _run("--file", str(f))
    assert rc == 1


def test_main_with_spec_json(tmp_path):
    f = tmp_path / "report.md"
    f.write_text(GOOD_REPORT)
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps({
        "comps": [{"id": "COMP-001"}, {"id": "COMP-002"}],
        "reqs": ["REQ-001", "REQ-002"],
    }))
    rc = _run("--file", str(f), "--spec-json", str(spec_file))
    assert rc == 0


def test_main_with_bad_spec_json(tmp_path):
    f = tmp_path / "report.md"
    f.write_text(GOOD_REPORT)
    spec_file = tmp_path / "spec.json"
    spec_file.write_text("not json")
    rc = _run("--file", str(f), "--spec-json", str(spec_file))
    assert rc == 1
