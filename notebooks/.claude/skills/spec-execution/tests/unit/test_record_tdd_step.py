"""Unit tests for scripts/record_tdd_step.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from record_tdd_step import append_record, main as rt_main


def test_append_record_adds_history(sample_state):
    record = {"step": "red", "result": "fail", "note": "n", "duration_s": 10, "timestamp": "t"}
    err = append_record(sample_state, "T-002", record)
    assert err is None
    assert sample_state["tasks"]["T-002"]["history"][-1] == record


def test_append_record_unknown_task(sample_state):
    err = append_record(sample_state, "T-999", {"step": "red"})
    assert err is not None
    assert "unknown task" in err


def test_append_record_updates_meta(sample_state):
    sample_state["meta"]["last_updated"] = "1999-01-01"
    append_record(sample_state, "T-001", {"step": "refactor", "result": "pass"})
    assert sample_state["meta"]["last_updated"] != "1999-01-01"


def _setup(tmp_specs_root, sample_state):
    fdir = tmp_specs_root / "feat"
    fdir.mkdir(parents=True)
    (fdir / "execution-state.json").write_text(json.dumps(sample_state))
    return fdir


def _run(*args):
    old = sys.argv
    sys.argv = ["record_tdd_step.py", *args]
    try:
        return rt_main()
    finally:
        sys.argv = old


def test_main_appends_step(tmp_specs_root, sample_state):
    fdir = _setup(tmp_specs_root, sample_state)
    rc = _run(
        "--feature", "feat", "--specs-root", str(tmp_specs_root),
        "--task-id", "T-002", "--step", "red", "--result", "fail",
        "--note", "boom",
    )
    assert rc == 0
    state = json.loads((fdir / "execution-state.json").read_text())
    h = state["tasks"]["T-002"]["history"]
    assert len(h) == 1
    assert h[0]["step"] == "red"
    assert h[0]["result"] == "fail"
    assert h[0]["note"] == "boom"


def test_main_unknown_task(tmp_specs_root, sample_state):
    _setup(tmp_specs_root, sample_state)
    rc = _run(
        "--feature", "feat", "--specs-root", str(tmp_specs_root),
        "--task-id", "T-999", "--step", "red", "--result", "fail",
    )
    assert rc == 1


def test_main_invalid_step(tmp_specs_root, sample_state):
    _setup(tmp_specs_root, sample_state)
    with pytest.raises(SystemExit):
        _run(
            "--feature", "feat", "--specs-root", str(tmp_specs_root),
            "--task-id", "T-002", "--step", "yellow", "--result", "pass",
        )


def test_main_invalid_result(tmp_specs_root, sample_state):
    _setup(tmp_specs_root, sample_state)
    with pytest.raises(SystemExit):
        _run(
            "--feature", "feat", "--specs-root", str(tmp_specs_root),
            "--task-id", "T-002", "--step", "red", "--result", "kinda",
        )


def test_main_missing_state(tmp_specs_root):
    rc = _run(
        "--feature", "ghost", "--specs-root", str(tmp_specs_root),
        "--task-id", "T-001", "--step", "red", "--result", "fail",
    )
    assert rc == 1


def test_main_records_duration(tmp_specs_root, sample_state):
    fdir = _setup(tmp_specs_root, sample_state)
    rc = _run(
        "--feature", "feat", "--specs-root", str(tmp_specs_root),
        "--task-id", "T-001", "--step", "refactor", "--result", "pass",
        "--duration-s", "120",
    )
    assert rc == 0
    state = json.loads((fdir / "execution-state.json").read_text())
    assert state["tasks"]["T-001"]["history"][-1]["duration_s"] == 120
