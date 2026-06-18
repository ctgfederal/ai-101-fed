"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate, main as vo_main


def _good_sdd_with_one_block() -> str:
    return """# SDD

## Components

- **COMP-001**: a.

## Deviations

### DEV-001

- **Date**: 2026-05-08
- **Spec**: feature
- **Reason Category**: technical-blocker
- **Original Decision**: REQ-001
- **Status**: proposed
- **Approver**: Josh

**Description**

Some description text.

**Proposed Change**

A proposed change.

**Impact**

Some impact.
"""


def _good_sdd_with_two_blocks() -> str:
    return _good_sdd_with_one_block() + """

### DEV-002

- **Date**: 2026-05-09
- **Spec**: feature
- **Reason Category**: scope-clarification
- **Original Decision**: COMP-002
- **Status**: approved
- **Approver**: Reviewer

**Description**

Different description.

**Proposed Change**

Different change.

**Impact**

Different impact.
"""


def test_validate_no_deviations_section_is_ok():
    text = "# SDD\n\n## Components\n\n- **COMP-001**: a.\n"
    assert validate(text) == []


def test_validate_one_clean_block():
    assert validate(_good_sdd_with_one_block()) == []


def test_validate_two_clean_blocks():
    assert validate(_good_sdd_with_two_blocks()) == []


def test_validate_duplicate_dev_id():
    text = _good_sdd_with_one_block() + "\n" + """### DEV-001

- **Date**: 2026-05-09
- **Spec**: feature
- **Reason Category**: scope-clarification
- **Original Decision**: COMP-002
- **Status**: approved
- **Approver**: Reviewer

**Description**

Other.

**Proposed Change**

Other.

**Impact**

Other.
"""
    errors = validate(text)
    assert any("duplicate" in e.lower() for e in errors)


def test_validate_bad_status():
    text = _good_sdd_with_one_block().replace("Status**: proposed", "Status**: draft")
    errors = validate(text)
    assert any("Status" in e for e in errors)


def test_validate_bad_reason_category():
    text = _good_sdd_with_one_block().replace(
        "Reason Category**: technical-blocker",
        "Reason Category**: preference",
    )
    errors = validate(text)
    assert any("Reason Category" in e for e in errors)


def test_validate_missing_bullet():
    text = _good_sdd_with_one_block().replace(
        "- **Status**: proposed\n", ""
    )
    errors = validate(text)
    assert any("Status" in e for e in errors)


def test_validate_missing_prose_section():
    text = _good_sdd_with_one_block().replace(
        "**Impact**\n\nSome impact.\n", ""
    )
    errors = validate(text)
    assert any("Impact" in e for e in errors)


def test_validate_unsubstituted_token():
    text = _good_sdd_with_one_block().replace("proposed", "{{STATUS}}")
    errors = validate(text)
    assert any("unsubstituted" in e.lower() for e in errors)


def test_validate_empty_section_with_no_block():
    text = """# SDD

## Components

- **COMP-001**: a.

## Deviations

Some prose but no block.
"""
    errors = validate(text)
    assert any("no `### DEV-NNN`" in e or "Deviations" in e for e in errors)


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_happy(tmp_path):
    f = tmp_path / "SDD.md"
    f.write_text(_good_sdd_with_one_block())
    rc = _run("--sdd", str(f))
    assert rc == 0


def test_main_bad(tmp_path):
    f = tmp_path / "SDD.md"
    f.write_text(_good_sdd_with_one_block().replace("Status**: proposed", "Status**: draft"))
    rc = _run("--sdd", str(f))
    assert rc == 1


def test_main_missing_file(tmp_path):
    rc = _run("--sdd", str(tmp_path / "nope.md"))
    assert rc == 1
