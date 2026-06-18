"""Unit tests for scripts/render_handoff.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from render_handoff import render, render_list, main as rh_main


def _template() -> str:
    p = Path(__file__).resolve().parents[2] / "templates" / "handoff.md.template"
    return p.read_text(encoding="utf-8")


def test_render_full(valid_handoff):
    out = render(valid_handoff, _template())
    assert "{{" not in out
    assert "orchestrator" in out
    assert "backend-developer" in out
    assert "GET /users/:id" in out
    assert "## DEADLINE" in out
    assert "Phase 2" in out


def test_render_no_deadline(valid_handoff):
    del valid_handoff["deadline"]
    out = render(valid_handoff, _template())
    assert "## DEADLINE" not in out
    assert "{{" not in out


def test_render_empty_context(valid_handoff):
    valid_handoff["context_files"] = []
    out = render(valid_handoff, _template())
    assert "_(none)_" in out


def test_render_list_single():
    assert render_list(["one"]) == "- one"


def test_render_list_multiple():
    assert render_list(["a", "b"]) == "- a\n- b"


def test_render_list_empty():
    assert render_list([]) == "_(none)_"


def test_render_section_order(valid_handoff):
    out = render(valid_handoff, _template())
    sections = ["## FROM", "## TO", "## TASK", "## CONTEXT", "## SUCCESS", "## RETURN"]
    indices = [out.index(s) for s in sections]
    assert indices == sorted(indices)


def _run(*args):
    old = sys.argv
    sys.argv = ["render_handoff.py", *args]
    try:
        return rh_main()
    finally:
        sys.argv = old


def test_main_writes(tmp_path, valid_handoff):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_handoff))
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 0
    body = out.read_text(encoding="utf-8")
    assert "## FROM" in body
    assert "{{" not in body


def test_main_refuses_overwrite(tmp_path, valid_handoff):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_handoff))
    out = tmp_path / "prompt.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1


def test_main_force_overwrite(tmp_path, valid_handoff):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_handoff))
    out = tmp_path / "prompt.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out), "--force")
    assert rc == 0
    assert "existing" not in out.read_text(encoding="utf-8")


def test_main_invalid_payload(tmp_path, invalid_handoff):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(invalid_handoff))
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
    assert not out.exists()


def test_main_missing_payload(tmp_path):
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(tmp_path / "nope.json"), "--out", str(out))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    out = tmp_path / "prompt.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
