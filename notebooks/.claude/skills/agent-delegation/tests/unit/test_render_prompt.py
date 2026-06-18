"""Unit tests for scripts/render_prompt.py."""
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from render_prompt import render, render_list, main as rp_main


TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "templates" / "delegation-prompt.md.template"


def test_render_list_empty():
    assert render_list([]) == "_(none)_"


def test_render_list_items():
    out = render_list(["a", "b", "c"])
    assert "- a" in out
    assert "- b" in out
    assert "- c" in out


def test_render_full(valid_payload):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = render(valid_payload, template)
    assert "{{" not in out
    assert "auth-agent" in out
    assert "src/auth/" in out
    assert "src/billing/" in out
    assert "pytest tests/auth/" in out


def test_render_keeps_section_order(valid_payload):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = render(valid_payload, template)
    idx_focus = out.index("## FOCUS")
    idx_exclude = out.index("## EXCLUDE")
    idx_task = out.index("## TASK")
    idx_success = out.index("## SUCCESS")
    idx_return = out.index("## RETURN")
    assert idx_focus < idx_exclude < idx_task < idx_success < idx_return


def _run(*args, stdin=None):
    old_argv, old_stdin = sys.argv, sys.stdin
    sys.argv = ["render_prompt.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return rp_main()
    finally:
        sys.argv = old_argv
        sys.stdin = old_stdin


def test_main_writes(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "## FOCUS" in text
    assert "## RETURN" in text


def test_main_refuses_overwrite(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "prompt.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
    assert out.read_text() == "existing"


def test_main_force_overwrites(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "prompt.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out), "--force")
    assert rc == 0
    assert "## FOCUS" in out.read_text()


def test_main_invalid_payload_blocks_render(tmp_path, invalid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(invalid_payload))
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
    assert not out.exists()


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
