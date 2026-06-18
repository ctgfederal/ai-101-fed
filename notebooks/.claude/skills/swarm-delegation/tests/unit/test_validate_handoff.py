"""Unit tests for scripts/validate_handoff.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_handoff import validate, main as vh_main


def test_validate_happy(valid_handoff):
    assert validate(valid_handoff) == []


def test_validate_missing_from(valid_handoff):
    del valid_handoff["from_agent"]
    errors = validate(valid_handoff)
    assert any("from_agent" in e for e in errors)


def test_validate_missing_to(valid_handoff):
    del valid_handoff["to_agent"]
    errors = validate(valid_handoff)
    assert any("to_agent" in e for e in errors)


def test_validate_missing_task(valid_handoff):
    del valid_handoff["task"]
    errors = validate(valid_handoff)
    assert any("task" in e for e in errors)


def test_validate_empty_task(valid_handoff):
    valid_handoff["task"] = "   "
    errors = validate(valid_handoff)
    assert any("task" in e and "non-empty" in e for e in errors)


def test_validate_empty_success_criteria(valid_handoff):
    valid_handoff["success_criteria"] = []
    errors = validate(valid_handoff)
    assert any("success_criteria" in e for e in errors)


def test_validate_non_list_success(valid_handoff):
    valid_handoff["success_criteria"] = "not a list"
    errors = validate(valid_handoff)
    assert any("success_criteria" in e and "list" in e for e in errors)


def test_validate_non_list_context(valid_handoff):
    valid_handoff["context_files"] = "not a list"
    errors = validate(valid_handoff)
    assert any("context_files" in e and "list" in e for e in errors)


def test_validate_self_handoff(valid_handoff):
    valid_handoff["to_agent"] = valid_handoff["from_agent"]
    errors = validate(valid_handoff)
    assert any("differ" in e or "cycle" in e for e in errors)


def test_validate_empty_return_format(valid_handoff):
    valid_handoff["return_format"] = ""
    errors = validate(valid_handoff)
    assert any("return_format" in e for e in errors)


def test_validate_optional_deadline_string(valid_handoff):
    # deadline as int should fail
    valid_handoff["deadline"] = 12
    errors = validate(valid_handoff)
    assert any("deadline" in e for e in errors)


def test_validate_payload_not_dict():
    errors = validate(["not", "a", "dict"])
    assert any("object" in e for e in errors)


def test_validate_invalid(invalid_handoff):
    errors = validate(invalid_handoff)
    # task empty, success_criteria empty, return_format empty, self-handoff
    assert len(errors) >= 3


def test_validate_context_item_not_string(valid_handoff):
    valid_handoff["context_files"] = ["ok.ts", 42]
    errors = validate(valid_handoff)
    assert any("context_files[1]" in e for e in errors)


def _run(*args, stdin=None):
    import io
    old, oldst = sys.argv, sys.stdin
    sys.argv = ["validate_handoff.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return vh_main()
    finally:
        sys.argv = old
        sys.stdin = oldst


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "nope.json"))
    assert rc == 1


def test_main_happy(tmp_path, valid_handoff):
    f = tmp_path / "h.json"
    f.write_text(json.dumps(valid_handoff))
    rc = _run("--file", str(f))
    assert rc == 0


def test_main_invalid(tmp_path, invalid_handoff):
    f = tmp_path / "h.json"
    f.write_text(json.dumps(invalid_handoff))
    rc = _run("--file", str(f))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    f = tmp_path / "h.json"
    f.write_text("not json")
    rc = _run("--file", str(f))
    assert rc == 1


def test_main_stdin(valid_handoff):
    rc = _run("--stdin", stdin=json.dumps(valid_handoff))
    assert rc == 0
