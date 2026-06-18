"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate, REQUIRED_SECTIONS, main as vo_main


def _good_prompt() -> str:
    return """# Agent Handoff

## FROM

orchestrator

## TO

backend-developer

## TASK

Implement the endpoint.

## CONTEXT

- src/x.ts

## SUCCESS

- 200 OK

## RETURN

unified diff
"""


def _good_prompt_with_deadline() -> str:
    return _good_prompt().rstrip() + "\n\n## DEADLINE\n\nPhase 2 boundary\n"


def test_validate_happy():
    assert validate(_good_prompt()) == []


def test_validate_with_deadline():
    assert validate(_good_prompt_with_deadline()) == []


def test_validate_missing_section():
    text = _good_prompt().replace("## RETURN", "## OTHER")
    errors = validate(text)
    assert any("RETURN" in e for e in errors)


def test_validate_unsubstituted_token():
    text = _good_prompt().replace("orchestrator", "{{FROM}}")
    errors = validate(text)
    assert any("unsubstituted" in e for e in errors)


def test_validate_out_of_order():
    text = _good_prompt().replace(
        "## FROM\n\norchestrator\n\n## TO\n\nbackend-developer",
        "## TO\n\nbackend-developer\n\n## FROM\n\norchestrator",
    )
    errors = validate(text)
    assert any("out of order" in e for e in errors)


def test_validate_unknown_section():
    text = _good_prompt() + "\n\n## EXTRA\n\nthing\n"
    errors = validate(text)
    assert any("unknown section" in e for e in errors)


def test_validate_deadline_before_return():
    # DEADLINE appears before RETURN — should error
    text = """# Agent Handoff

## FROM

a

## TO

b

## TASK

t

## CONTEXT

- x

## SUCCESS

- y

## DEADLINE

soon

## RETURN

z
"""
    errors = validate(text)
    assert any("DEADLINE" in e and "before" in e for e in errors)


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
    f = tmp_path / "p.md"
    f.write_text(_good_prompt())
    rc = _run("--file", str(f))
    assert rc == 0


def test_main_invalid(tmp_path):
    f = tmp_path / "p.md"
    f.write_text("# nothing useful\n")
    rc = _run("--file", str(f))
    assert rc == 1


def test_required_sections_constant():
    assert REQUIRED_SECTIONS == ["FROM", "TO", "TASK", "CONTEXT", "SUCCESS", "RETURN"]
