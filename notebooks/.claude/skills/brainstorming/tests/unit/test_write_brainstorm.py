"""Unit tests for scripts/write_brainstorm.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_brainstorm import REQUIRED, ALLOWED_STATUS, validate, render, main as wb_main


def test_required_keys_complete():
    assert set(REQUIRED) == {
        "topic", "date", "status", "inspiration", "projects", "audience", "use_cases",
        "outcomes", "principles", "constraints", "scope_in", "scope_out", "open_questions", "related",
    }


def test_validate_happy(valid_payload):
    validate(valid_payload)  # no raise


def test_validate_missing_key(valid_payload):
    del valid_payload["audience"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload)


def test_validate_bad_status(valid_payload):
    valid_payload["status"] = "draft"
    with pytest.raises(ValueError, match="status must be"):
        validate(valid_payload)


def test_validate_empty_field(valid_payload):
    valid_payload["scope_out"] = ""
    with pytest.raises(ValueError, match="empty"):
        validate(valid_payload)


def test_render_substitutes_all(valid_payload):
    template = "{{TOPIC}} {{DATE}} {{STATUS}} {{AUDIENCE}}"
    out = render(valid_payload, template)
    assert "{{" not in out
    assert valid_payload["topic"] in out


def _run(argv, stdin_text=None):
    old = sys.argv
    old_stdin = sys.stdin
    sys.argv = ["write_brainstorm.py"] + argv
    if stdin_text is not None:
        import io
        sys.stdin = io.StringIO(stdin_text)
    try:
        return wb_main()
    finally:
        sys.argv = old
        sys.stdin = old_stdin


def test_main_writes_file(tmp_path, valid_payload):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    out = tmp_path / "out.md"
    template = Path(__file__).resolve().parents[2] / "templates" / "brainstorm.md.template"
    rc = _run(["--payload", str(payload_file), "--out", str(out), "--template", str(template)])
    assert rc == 0
    assert out.exists()
    text = out.read_text()
    assert valid_payload["topic"] in text
    assert "## Inspiration" in text


def test_main_refuses_overwrite(tmp_path, valid_payload):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    out = tmp_path / "out.md"
    template = Path(__file__).resolve().parents[2] / "templates" / "brainstorm.md.template"
    args = ["--payload", str(payload_file), "--out", str(out), "--template", str(template)]
    assert _run(args) == 0
    rc = _run(args)
    assert rc == 1


def test_main_stdin(tmp_path, valid_payload):
    out = tmp_path / "out.md"
    template = Path(__file__).resolve().parents[2] / "templates" / "brainstorm.md.template"
    rc = _run(
        ["--out", str(out), "--template", str(template)],
        stdin_text=json.dumps(valid_payload),
    )
    assert rc == 0
    assert out.exists()


def test_main_invalid_json(tmp_path):
    payload_file = tmp_path / "bad.json"
    payload_file.write_text("not json", encoding="utf-8")
    out = tmp_path / "out.md"
    template = Path(__file__).resolve().parents[2] / "templates" / "brainstorm.md.template"
    rc = _run(["--payload", str(payload_file), "--out", str(out), "--template", str(template)])
    assert rc == 1
