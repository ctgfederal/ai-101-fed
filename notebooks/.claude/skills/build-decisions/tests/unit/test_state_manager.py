"""Unit tests for scripts/state_manager.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from state_manager import deep_merge, state_path, main as sm_main


def test_deep_merge_basic():
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_deep_merge_overwrites():
    assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_deep_merge_nested():
    base = {"meta": {"sessions": 1, "last": "x"}}
    patch = {"meta": {"sessions": 2}}
    out = deep_merge(base, patch)
    assert out == {"meta": {"sessions": 2, "last": "x"}}


def test_deep_merge_replaces_lists():
    base = {"items": [1, 2]}
    patch = {"items": [3]}
    assert deep_merge(base, patch) == {"items": [3]}


def test_state_path():
    assert state_path(Path("/x"), "feat") == Path("/x/feat/state.json")


def _run(*args):
    old = sys.argv
    sys.argv = ["state_manager.py", *args]
    try:
        return sm_main()
    finally:
        sys.argv = old


def test_init_creates_state(tmp_builds_root, capsys):
    rc = _run("init", "--feature", "f1", "--builds-root", str(tmp_builds_root))
    out = capsys.readouterr().out.strip()
    assert rc == 0
    p = tmp_builds_root / "f1" / "state.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["feature"] == "f1"


def test_init_idempotent(tmp_builds_root, capsys):
    _run("init", "--feature", "f1", "--builds-root", str(tmp_builds_root))
    capsys.readouterr()
    rc = _run("init", "--feature", "f1", "--builds-root", str(tmp_builds_root))
    assert rc == 0


def test_read_missing(tmp_builds_root):
    rc = _run("read", "--feature", "nope", "--builds-root", str(tmp_builds_root))
    assert rc == 1


def test_update_merges(tmp_builds_root, tmp_path):
    _run("init", "--feature", "f1", "--builds-root", str(tmp_builds_root))
    patch_file = tmp_path / "patch.json"
    patch_file.write_text(json.dumps({"current_category": "Security", "notes": ["hi"]}))
    rc = _run("update", "--feature", "f1", "--builds-root", str(tmp_builds_root), "--patch", str(patch_file))
    assert rc == 0
    p = tmp_builds_root / "f1" / "state.json"
    data = json.loads(p.read_text())
    assert data["current_category"] == "Security"
    assert data["notes"] == ["hi"]


def test_update_invalid_json(tmp_builds_root, tmp_path):
    _run("init", "--feature", "f1", "--builds-root", str(tmp_builds_root))
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    rc = _run("update", "--feature", "f1", "--builds-root", str(tmp_builds_root), "--patch", str(bad))
    assert rc == 1


def test_update_missing_state(tmp_builds_root, tmp_path):
    bad = tmp_path / "p.json"
    bad.write_text(json.dumps({"x": 1}))
    rc = _run("update", "--feature", "missing", "--builds-root", str(tmp_builds_root), "--patch", str(bad))
    assert rc == 1
