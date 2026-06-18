"""Unit tests for scripts/next_task.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from next_task import find_next, task_sort_key, main as nt_main


def test_picks_lowest_pending(sample_state):
    # T-002 is in-progress, so next eligible PENDING with deps met is T-003 → blocked
    # by T-002 still in-progress. So nothing should be returned.
    out = find_next(sample_state)
    assert out == {}


def test_picks_pending_when_dep_done(sample_state):
    sample_state["tasks"]["T-002"]["status"] = "done"
    out = find_next(sample_state)
    assert out["id"] == "T-003"


def test_skips_blocked(sample_state):
    sample_state["tasks"]["T-002"]["status"] = "done"
    sample_state["tasks"]["T-003"]["status"] = "blocked"
    out = find_next(sample_state)
    # T-004 depends on T-003 which is blocked → no eligible task
    assert out == {}


def test_returns_empty_when_all_done(sample_state):
    for t in sample_state["tasks"].values():
        t["status"] = "done"
    assert find_next(sample_state) == {}


def test_respects_document_order():
    state = {
        "tasks": {
            "T-005": {"status": "pending", "depends_on": [], "description": "x", "history": [], "blockers": []},
            "T-002": {"status": "pending", "depends_on": [], "description": "x", "history": [], "blockers": []},
        },
        "task_order": ["T-002", "T-005"],
    }
    out = find_next(state)
    assert out["id"] == "T-002"


def test_falls_back_to_numeric_when_order_missing():
    state = {
        "tasks": {
            "T-005": {"status": "pending", "depends_on": [], "description": "x", "history": [], "blockers": []},
            "T-002": {"status": "pending", "depends_on": [], "description": "x", "history": [], "blockers": []},
        },
        "task_order": [],
    }
    out = find_next(state)
    assert out["id"] == "T-002"


def test_task_sort_key_doc_order_wins():
    state = {"task_order": ["T-005", "T-002"]}
    assert task_sort_key(state, "T-005") < task_sort_key(state, "T-002")


def test_empty_state():
    assert find_next({}) == {}


def _run(*args):
    old = sys.argv
    sys.argv = ["next_task.py", *args]
    try:
        return nt_main()
    finally:
        sys.argv = old


def test_main_missing_state(tmp_specs_root):
    rc = _run("--feature", "x", "--specs-root", str(tmp_specs_root))
    assert rc == 1


def test_main_emits_json(tmp_specs_root, sample_state, capsys):
    fdir = tmp_specs_root / "feat"
    fdir.mkdir(parents=True)
    sample_state["tasks"]["T-002"]["status"] = "done"
    (fdir / "execution-state.json").write_text(json.dumps(sample_state))
    rc = _run("--feature", "feat", "--specs-root", str(tmp_specs_root))
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["id"] == "T-003"


def test_main_empty_when_all_done(tmp_specs_root, sample_state, capsys):
    fdir = tmp_specs_root / "feat"
    fdir.mkdir(parents=True)
    for t in sample_state["tasks"].values():
        t["status"] = "done"
    (fdir / "execution-state.json").write_text(json.dumps(sample_state))
    rc = _run("--feature", "feat", "--specs-root", str(tmp_specs_root))
    out = capsys.readouterr().out
    assert rc == 0
    assert json.loads(out) == {}
