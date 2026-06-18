"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import main as vo_main, validate


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


GOOD = """# Specification: Feature Search

**Feature:** `feature-search`
**Created:** 2026-05-08

## Status

| Doc | Status | Last Update |
|---|---|---|
| PRD | approved | 2026-05-08 |
| SDD | draft | 2026-05-08 |
| PLAN | draft | 2026-05-08 |

## Steering References

- Product: [`../../steering/product.md`](../../steering/product.md)

## Decision Log Snippets

_(none)_

## Phase Notes

### Phase 1: Foundation

_Recorded 2026-05-08_

First note.

## Learnings

_(none)_

## Open Questions

_(none)_
"""


def test_happy(tmp_path):
    p = tmp_path / "README.md"
    p.write_text(GOOD)
    errors = validate(GOOD)
    assert errors == [], errors


def test_main_exits_zero_on_good(tmp_path):
    p = tmp_path / "README.md"
    p.write_text(GOOD)
    rc = _run("--file", str(p))
    assert rc == 0


def test_missing_section():
    bad = GOOD.replace("## Open Questions\n\n_(none)_\n", "")
    errors = validate(bad)
    assert any("Open Questions" in e for e in errors)


def test_invalid_status():
    bad = GOOD.replace("| PRD | approved |", "| PRD | wip |")
    errors = validate(bad)
    assert any("invalid status" in e and "PRD" in e for e in errors)


def test_unsubstituted_token():
    bad = GOOD + "\n{{LEFT_OVER}}\n"
    errors = validate(bad)
    assert any("unsubstituted" in e for e in errors)


def test_missing_status_row():
    bad = GOOD.replace("| PLAN | draft | 2026-05-08 |\n", "")
    errors = validate(bad)
    assert any("missing status row: PLAN" in e for e in errors)


def test_phase_notes_out_of_order():
    bad = GOOD.replace(
        "### Phase 1: Foundation",
        "### Phase 2: Core\n\n_Recorded 2026-05-08_\n\nB.\n\n### Phase 1: Foundation",
    )
    errors = validate(bad)
    assert any("out of order" in e for e in errors)


def test_steering_link_missing():
    bad = GOOD.replace(
        "- Product: [`../../steering/product.md`](../../steering/product.md)\n",
        "- Product: see steering.\n",
    )
    errors = validate(bad)
    assert any("Steering" in e for e in errors)


def test_main_exits_one_on_bad(tmp_path):
    p = tmp_path / "README.md"
    p.write_text(GOOD.replace("| PRD | approved |", "| PRD | wip |"))
    rc = _run("--file", str(p))
    assert rc == 1
