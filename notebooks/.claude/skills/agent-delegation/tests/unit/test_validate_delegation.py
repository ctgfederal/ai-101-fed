"""Unit tests for scripts/validate_delegation.py."""
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_delegation import REQUIRED_KEYS, validate, main as vd_main


def test_required_keys_complete():
    expected = {"agent_type", "task", "focus_files", "exclude_files", "success_criteria", "return_format"}
    assert set(REQUIRED_KEYS) == expected


def test_validate_happy(valid_payload):
    assert validate(valid_payload) == []


def test_validate_missing_key(valid_payload):
    del valid_payload["agent_type"]
    errors = validate(valid_payload)
    assert any("missing keys" in e for e in errors)


def test_validate_empty_agent_type(valid_payload):
    valid_payload["agent_type"] = ""
    errors = validate(valid_payload)
    assert any("agent_type" in e for e in errors)


def test_validate_empty_task(valid_payload):
    valid_payload["task"] = "   "
    errors = validate(valid_payload)
    assert any("task" in e for e in errors)


def test_validate_focus_not_list(valid_payload):
    valid_payload["focus_files"] = "src/auth/"
    errors = validate(valid_payload)
    assert any("focus_files" in e and "list" in e for e in errors)


def test_validate_focus_exclude_overlap(valid_payload):
    valid_payload["focus_files"] = ["src/auth/", "src/shared/"]
    valid_payload["exclude_files"] = ["src/shared/"]
    errors = validate(valid_payload)
    assert any("overlap" in e for e in errors)


def test_validate_focus_exclude_overlap_normalized(valid_payload):
    """Overlap detection normalizes trailing slashes."""
    valid_payload["focus_files"] = ["src/shared"]
    valid_payload["exclude_files"] = ["src/shared/"]
    errors = validate(valid_payload)
    assert any("overlap" in e for e in errors)


def test_validate_empty_success_criteria(valid_payload):
    valid_payload["success_criteria"] = []
    errors = validate(valid_payload)
    assert any("success_criteria" in e for e in errors)


def test_validate_success_criteria_not_list(valid_payload):
    valid_payload["success_criteria"] = "pytest passes"
    errors = validate(valid_payload)
    assert any("success_criteria" in e for e in errors)


def test_validate_focus_item_not_string(valid_payload):
    valid_payload["focus_files"] = ["src/auth/", 123]
    errors = validate(valid_payload)
    assert any("focus_files[1]" in e for e in errors)


def test_validate_empty_return_format(valid_payload):
    valid_payload["return_format"] = ""
    errors = validate(valid_payload)
    assert any("return_format" in e for e in errors)


def _run(*args, stdin=None):
    old_argv, old_stdin = sys.argv, sys.stdin
    sys.argv = ["validate_delegation.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return vd_main()
    finally:
        sys.argv = old_argv
        sys.stdin = old_stdin


def test_main_happy(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    assert _run("--payload", str(p)) == 0


def test_main_invalid_payload(tmp_path, invalid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(invalid_payload))
    assert _run("--payload", str(p)) == 1


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    assert _run("--payload", str(p)) == 1


def test_main_empty_payload():
    assert _run(stdin="") == 1


def test_main_stdin_happy(valid_payload):
    assert _run(stdin=json.dumps(valid_payload)) == 0
