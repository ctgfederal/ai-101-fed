"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate, REQUIRED_SUBSECTIONS, main as vo_main


def _good_doc():
    return """# F

## Deepening Summary

**Deepened on:** 2026-02-14

## Architecture

### Service pattern
**Decision**: Layered.

### Research Insights

**From Solutions Archive:**
- a

**Best Practices:**
- b

**Edge Cases:**
- c

**Performance:**
- d

**References:**
- e
"""


def test_validate_happy():
    assert validate(_good_doc()) == []


def test_validate_no_summary():
    text = _good_doc().replace("## Deepening Summary", "## Other")
    errors = validate(text)
    assert any("Deepening Summary" in e for e in errors)


def test_validate_no_insights_block():
    text = "# F\n\n## Deepening Summary\n**Deepened on:** today\n\n## Section\nbody\n"
    errors = validate(text)
    assert any("no `### Research Insights`" in e for e in errors)


def test_validate_missing_subsection():
    text = _good_doc().replace("**References:**", "**Other:**")
    errors = validate(text)
    assert any("References" in e for e in errors)


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_target(tmp_path):
    rc = _run("--target", str(tmp_path / "no.md"))
    assert rc == 1


def test_main_happy(tmp_path):
    f = tmp_path / "x.md"
    f.write_text(_good_doc(), encoding="utf-8")
    rc = _run("--target", str(f))
    assert rc == 0
