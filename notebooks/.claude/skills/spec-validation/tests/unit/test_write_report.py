"""Unit tests for scripts/write_report.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_report import (
    REQUIRED_KEYS, ALLOWED_VERDICTS, validate, render,
    render_issues, render_verdict_notes,
    main as wr_main,
)


def test_required_keys():
    assert "target" in REQUIRED_KEYS
    assert "verdict" in REQUIRED_KEYS
    assert "issues" in REQUIRED_KEYS


def test_validate_happy(valid_payload):
    validate(valid_payload)


def test_validate_missing_key(valid_payload):
    del valid_payload["completeness"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload)


def test_validate_bad_score_range(valid_payload):
    valid_payload["completeness"] = 11
    with pytest.raises(ValueError, match=r"\[0, 10\]"):
        validate(valid_payload)


def test_validate_negative_score(valid_payload):
    valid_payload["consistency"] = -1
    with pytest.raises(ValueError, match=r"\[0, 10\]"):
        validate(valid_payload)


def test_validate_bad_verdict(valid_payload):
    valid_payload["verdict"] = "OK"
    with pytest.raises(ValueError, match="verdict"):
        validate(valid_payload)


def test_validate_bad_issues(valid_payload):
    valid_payload["issues"] = "not a list"
    with pytest.raises(ValueError, match="issues"):
        validate(valid_payload)


def test_validate_bad_issue_shape(valid_payload):
    valid_payload["issues"] = [{"category": "consistency"}]  # missing message
    with pytest.raises(ValueError, match="issue"):
        validate(valid_payload)


def test_render_issues_empty():
    assert "no issues found" in render_issues([])


def test_render_issues_some():
    out = render_issues([{"category": "consistency", "message": "dangling REQ-999"}])
    assert "dangling REQ-999" in out
    assert "consistency" in out


def test_render_verdict_notes():
    assert "approved" in render_verdict_notes("PASS").lower()
    assert "another pass" in render_verdict_notes("WARN").lower()
    assert "not ready" in render_verdict_notes("FAIL").lower()


def test_render_full(valid_payload):
    template = (Path(__file__).resolve().parents[2] / "templates" / "3cs-report.md.template").read_text(encoding="utf-8")
    out = render(valid_payload, template)
    assert "{{" not in out
    assert "9/10" in out
    assert "PASS" in out
    assert valid_payload["target"] in out


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
    assert "9/10" in body
    assert "PASS" in body


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
    assert "9/10" in out.read_text(encoding="utf-8")


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    out = tmp_path / "report.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
