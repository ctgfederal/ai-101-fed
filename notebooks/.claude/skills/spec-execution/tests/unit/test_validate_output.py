"""Unit tests for scripts/validate_output.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate_state, main as vo_main


def test_validate_clean(sample_state):
    assert validate_state(sample_state, None) == []


def test_validate_with_plan(sample_state, sample_plan_text):
    assert validate_state(sample_state, sample_plan_text) == []


def test_validate_missing_top_level():
    state = {"tasks": {}}
    errs = validate_state(state, None)
    assert any("feature" in e for e in errs)
    assert any("task_order" in e for e in errs)


def test_validate_missing_task_field(sample_state):
    del sample_state["tasks"]["T-001"]["history"]
    errs = validate_state(sample_state, None)
    assert any("history" in e for e in errs)


def test_validate_invalid_status(sample_state):
    sample_state["tasks"]["T-001"]["status"] = "kinda-done"
    errs = validate_state(sample_state, None)
    assert any("invalid status" in e for e in errs)


def test_validate_history_not_list(sample_state):
    sample_state["tasks"]["T-001"]["history"] = "oops"
    errs = validate_state(sample_state, None)
    assert any("history must be a list" in e for e in errs)


def test_validate_task_order_mismatch(sample_state):
    sample_state["task_order"] = ["T-001"]  # missing the others
    errs = validate_state(sample_state, None)
    assert any("task_order missing" in e for e in errs)


def test_validate_task_order_extras(sample_state):
    sample_state["task_order"].append("T-999")
    errs = validate_state(sample_state, None)
    assert any("task_order has ids not in tasks" in e for e in errs)


def test_validate_plan_extra_id(sample_state):
    plan = "- [ ] T-001: a\n- [ ] T-002: b\n- [ ] T-007: missing\n"
    errs = validate_state(sample_state, plan)
    assert any("T-007" in e for e in errs)


def test_validate_meta_missing(sample_state):
    del sample_state["meta"]
    errs = validate_state(sample_state, None)
    assert any("meta" in e for e in errs)


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_valid(tmp_specs_root, sample_state):
    fdir = tmp_specs_root / "feat"
    fdir.mkdir(parents=True)
    (fdir / "execution-state.json").write_text(json.dumps(sample_state))
    rc = _run("--file", str(fdir / "execution-state.json"))
    assert rc == 0


def test_main_missing_file(tmp_specs_root):
    rc = _run("--file", str(tmp_specs_root / "nope.json"))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json")
    rc = _run("--file", str(p))
    assert rc == 1


def test_main_with_plan(tmp_path, sample_state, sample_plan_text):
    sf = tmp_path / "state.json"
    sf.write_text(json.dumps(sample_state))
    pf = tmp_path / "PLAN.md"
    pf.write_text(sample_plan_text)
    rc = _run("--file", str(sf), "--plan", str(pf))
    assert rc == 0


def test_main_plan_missing(tmp_path, sample_state):
    sf = tmp_path / "state.json"
    sf.write_text(json.dumps(sample_state))
    rc = _run("--file", str(sf), "--plan", str(tmp_path / "ghost.md"))
    assert rc == 1
