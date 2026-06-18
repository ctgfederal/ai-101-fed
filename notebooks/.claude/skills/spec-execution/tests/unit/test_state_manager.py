"""Unit tests for scripts/state_manager.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from state_manager import (
    deep_merge, state_path, plan_path, parse_plan_tasks, initial_state,
    main as sm_main,
)


def test_deep_merge_basic():
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_deep_merge_overwrites():
    assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_deep_merge_nested():
    base = {"meta": {"sessions": 1, "last": "x"}}
    patch = {"meta": {"sessions": 2}}
    assert deep_merge(base, patch) == {"meta": {"sessions": 2, "last": "x"}}


def test_deep_merge_replaces_lists():
    assert deep_merge({"items": [1, 2]}, {"items": [3]}) == {"items": [3]}


def test_state_path():
    assert state_path(Path("/x"), "feat") == Path("/x/feat/execution-state.json")


def test_plan_path():
    assert plan_path(Path("/x"), "feat") == Path("/x/feat/PLAN.md")


def test_parse_plan_tasks_simple(sample_plan_text):
    tasks = parse_plan_tasks(sample_plan_text)
    assert [t["id"] for t in tasks] == ["T-001", "T-002", "T-003", "T-004"]
    assert tasks[0]["description"] == "Set up package"


def test_parse_plan_tasks_empty():
    assert parse_plan_tasks("# nothing to do here\n") == []


def test_parse_plan_tasks_dedupes():
    text = "- [ ] T-001: a\n- [x] T-001: a-again\n- [ ] T-002: b\n"
    tasks = parse_plan_tasks(text)
    assert [t["id"] for t in tasks] == ["T-001", "T-002"]


def test_parse_plan_tasks_handles_checked():
    text = "- [x] **T-001**: done already\n- [ ] **T-002**: pending\n"
    tasks = parse_plan_tasks(text)
    assert [t["id"] for t in tasks] == ["T-001", "T-002"]


def test_initial_state_shape():
    state = initial_state("feat", [{"id": "T-001", "description": "x"}])
    assert state["feature"] == "feat"
    assert state["current_task"] is None
    assert state["task_order"] == ["T-001"]
    assert state["tasks"]["T-001"]["status"] == "pending"
    assert state["meta"]["total_tasks"] == 1


def _run(*args):
    old = sys.argv
    sys.argv = ["state_manager.py", *args]
    try:
        return sm_main()
    finally:
        sys.argv = old


def test_init_creates_state(init_feature, capsys):
    rc = _run("init", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]))
    assert rc == 0
    p = init_feature["dir"] / "execution-state.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["feature"] == "feature-x"
    assert set(data["tasks"]) == {"T-001", "T-002", "T-003", "T-004"}


def test_init_idempotent(init_feature, capsys):
    _run("init", "--feature", init_feature["feature"],
         "--specs-root", str(init_feature["root"]))
    capsys.readouterr()
    rc = _run("init", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]))
    assert rc == 0


def test_init_missing_plan(tmp_specs_root):
    fdir = tmp_specs_root / "ghost"
    fdir.mkdir(parents=True)
    rc = _run("init", "--feature", "ghost", "--specs-root", str(tmp_specs_root))
    assert rc == 1


def test_init_empty_plan(tmp_specs_root):
    fdir = tmp_specs_root / "empty"
    fdir.mkdir(parents=True)
    (fdir / "PLAN.md").write_text("# nothing to see here\n")
    rc = _run("init", "--feature", "empty", "--specs-root", str(tmp_specs_root))
    assert rc == 1


def test_read_missing(tmp_specs_root):
    rc = _run("read", "--feature", "nope", "--specs-root", str(tmp_specs_root))
    assert rc == 1


def test_read_after_init(init_feature):
    _run("init", "--feature", init_feature["feature"],
         "--specs-root", str(init_feature["root"]))
    rc = _run("read", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]))
    assert rc == 0


def test_update_merges(init_feature, tmp_path):
    _run("init", "--feature", init_feature["feature"],
         "--specs-root", str(init_feature["root"]))
    patch = tmp_path / "patch.json"
    patch.write_text(json.dumps({
        "current_task": "T-002",
        "tasks": {"T-001": {"status": "done"}},
    }))
    rc = _run("update", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]),
              "--patch", str(patch))
    assert rc == 0
    state = json.loads((init_feature["dir"] / "execution-state.json").read_text())
    assert state["current_task"] == "T-002"
    assert state["tasks"]["T-001"]["status"] == "done"
    # other fields preserved
    assert state["tasks"]["T-001"]["description"] == "Set up package"


def test_update_invalid_status_rejected(init_feature, tmp_path):
    _run("init", "--feature", init_feature["feature"],
         "--specs-root", str(init_feature["root"]))
    patch = tmp_path / "p.json"
    patch.write_text(json.dumps({"tasks": {"T-001": {"status": "wat"}}}))
    rc = _run("update", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]),
              "--patch", str(patch))
    assert rc == 1


def test_update_bad_json(init_feature, tmp_path):
    _run("init", "--feature", init_feature["feature"],
         "--specs-root", str(init_feature["root"]))
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    rc = _run("update", "--feature", init_feature["feature"],
              "--specs-root", str(init_feature["root"]),
              "--patch", str(bad))
    assert rc == 1


def test_update_missing_state(tmp_specs_root, tmp_path):
    bad = tmp_path / "p.json"
    bad.write_text(json.dumps({"x": 1}))
    rc = _run("update", "--feature", "missing", "--specs-root", str(tmp_specs_root),
              "--patch", str(bad))
    assert rc == 1
