"""Unit tests for scripts/write_report.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_report import (
    REQUIRED_KEYS, ALLOWED_VERDICTS, ALLOWED_STATUSES,
    validate, render, render_task_rows, render_issues, render_verdict_notes,
    main as wr_main,
)


def test_required_keys():
    assert "plan" in REQUIRED_KEYS
    assert "tasks" in REQUIRED_KEYS
    assert "verdict" in REQUIRED_KEYS


def test_validate_happy(valid_payload):
    validate(valid_payload)


def test_validate_missing_key(valid_payload):
    del valid_payload["verdict"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload)


def test_validate_bad_status(valid_payload):
    valid_payload["tasks"][0]["status"] = "wibble"
    with pytest.raises(ValueError, match="status"):
        validate(valid_payload)


def test_validate_bad_verdict(valid_payload):
    valid_payload["verdict"] = "OK"
    with pytest.raises(ValueError, match="verdict"):
        validate(valid_payload)


def test_validate_inconsistent_summary(valid_payload):
    valid_payload["summary"]["fail"] = 99
    with pytest.raises(ValueError, match="inconsistent"):
        validate(valid_payload)


def test_validate_tasks_not_list(valid_payload):
    valid_payload["tasks"] = "nope"
    with pytest.raises(ValueError, match="tasks"):
        validate(valid_payload)


def test_validate_task_missing_field(valid_payload):
    del valid_payload["tasks"][0]["status"]
    with pytest.raises(ValueError, match="missing key"):
        validate(valid_payload)


def test_render_task_rows_empty():
    assert "no tasks" in render_task_rows([])


def test_render_task_rows_some(valid_payload):
    out = render_task_rows(valid_payload["tasks"])
    assert "T-001" in out
    assert "T-002" in out
    assert "ok" in out
    assert "fail" in out


def test_render_issues_groups_by_task(valid_payload):
    out = render_issues(valid_payload["tasks"])
    assert "T-002" in out
    assert "missing TDD step" in out
    # T-001 has no issues so it should not appear
    assert "T-001" not in out


def test_render_issues_no_issues():
    tasks = [{"id": "T-001", "status": "ok", "issues": []}]
    out = render_issues(tasks)
    assert "no issues" in out.lower()


def test_render_verdict_notes():
    assert "approved" in render_verdict_notes("PASS").lower()
    assert "addressing" in render_verdict_notes("WARN").lower()
    assert "fix" in render_verdict_notes("FAIL").lower()


def test_render_full(valid_payload):
    template_path = Path(__file__).resolve().parents[2] / "templates" / "task-validation-report.md.template"
    template = template_path.read_text(encoding="utf-8")
    out = render(valid_payload, template)
    assert "{{" not in out
    assert "T-001" in out
    assert "T-002" in out
    assert "FAIL" in out
    assert "Total tasks" in out


def _run(*args, stdin=None):
    import io
    old, oldst = sys.argv, sys.stdin
    sys.argv = ["write_report.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return wr_main()
    finally:
        sys.argv = old
        sys.stdin = oldst


def test_main_writes(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "report.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 0, "expected 0 exit"
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    assert "T-001" in body
    assert "FAIL" in body


def test_main_refuses_overwrite(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "report.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1


def test_main_force_overwrite(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "report.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out), "--force")
    assert rc == 0
    assert "T-001" in out.read_text(encoding="utf-8")


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    out = tmp_path / "report.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
