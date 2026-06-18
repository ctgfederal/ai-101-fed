"""Unit tests for scripts/validate_tasks.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_tasks import (
    validate_task, validate_all, compute_verdict,
    _is_measurable, ALLOWED_PHASES, ALLOWED_TDD,
    main as vt_main,
)


def test_compute_verdict_pass():
    rows = [{"status": "ok"}, {"status": "ok"}]
    assert compute_verdict(rows) == "PASS"


def test_compute_verdict_warn():
    rows = [{"status": "ok"}, {"status": "warn"}]
    assert compute_verdict(rows) == "WARN"


def test_compute_verdict_fail():
    rows = [{"status": "ok"}, {"status": "fail"}]
    assert compute_verdict(rows) == "FAIL"


def test_compute_verdict_fail_dominates_warn():
    rows = [{"status": "warn"}, {"status": "fail"}]
    assert compute_verdict(rows) == "FAIL"


def test_compute_verdict_empty():
    assert compute_verdict([]) == "PASS"


def test_is_measurable_passes_with_observation_verb():
    assert _is_measurable("test_x passes")
    assert _is_measurable("function returns AST")
    assert _is_measurable("latency < 200ms")
    assert _is_measurable("output matches schema")


def test_is_measurable_rejects_vague():
    assert not _is_measurable("should work")
    assert not _is_measurable("looks good in the demo")
    assert not _is_measurable("TBD")
    assert not _is_measurable("")
    assert not _is_measurable("   ")


def test_is_measurable_rejects_no_observation_verb():
    assert not _is_measurable("the user can do search")


def _ok_task(**overrides):
    base = {
        "id": "T-001",
        "title": "Do the thing",
        "phase": "Foundation",
        "comps": ["COMP-001"],
        "reqs": ["REQ-101"],
        "acceptance": "test_x passes",
        "tdd_step": "red",
    }
    base.update(overrides)
    return base


def test_validate_clean_task():
    res = validate_task(_ok_task(), {"REQ-101"}, {"COMP-001"}, True, True)
    assert res["status"] == "ok"
    assert res["issues"] == []


def test_validate_bad_id_format():
    res = validate_task(_ok_task(id="task_1"), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("ID format" in i for i in res["issues"])


def test_validate_invalid_phase():
    res = validate_task(_ok_task(phase="Wibble"), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("phase" in i.lower() for i in res["issues"])


def test_validate_missing_tdd():
    res = validate_task(_ok_task(tdd_step=""), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("TDD" in i for i in res["issues"])


def test_validate_invalid_tdd():
    res = validate_task(_ok_task(tdd_step="puce"), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("TDD" in i for i in res["issues"])


def test_validate_missing_acceptance():
    res = validate_task(_ok_task(acceptance=""), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("acceptance" in i.lower() for i in res["issues"])


def test_validate_unmeasurable_acceptance():
    res = validate_task(_ok_task(acceptance="should work"), set(), set(), False, False)
    assert res["status"] == "fail"
    assert any("measurable" in i for i in res["issues"])


def test_validate_dangling_req_only_when_prd_provided():
    # Without PRD, dangling refs are not checked
    res_nopde = validate_task(_ok_task(reqs=["REQ-999"]), set(), set(), False, False)
    assert res_nopde["status"] == "ok"
    # With PRD, it fails
    res = validate_task(_ok_task(reqs=["REQ-999"]), {"REQ-101"}, set(), True, False)
    assert res["status"] == "fail"
    assert any("REQ" in i for i in res["issues"])


def test_validate_dangling_comp_only_when_sdd_provided():
    res = validate_task(_ok_task(comps=["COMP-999"]), set(), {"COMP-001"}, False, True)
    assert res["status"] == "fail"
    assert any("COMP" in i for i in res["issues"])


def test_validate_lowercase_title_warns():
    res = validate_task(_ok_task(title="implement search index loader"),
                        set(), set(), False, False)
    assert res["status"] == "warn"
    assert any("lowercase" in i.lower() for i in res["issues"])


def test_validate_all_summary_consistent(parsed_good_tasks):
    payload = validate_all(parsed_good_tasks)
    s = payload["summary"]
    assert s["ok"] + s["warn"] + s["fail"] == s["total"]
    assert s["total"] == len(parsed_good_tasks)


def test_validate_all_pass_on_good(parsed_good_tasks):
    payload = validate_all(parsed_good_tasks)
    assert payload["verdict"] == "PASS"
    assert payload["summary"]["fail"] == 0


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_tasks.py", *args]
    try:
        return vt_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--tasks", str(tmp_path / "nope.json"))
    assert rc == 1


def test_main_emits_json(tmp_path, parsed_good_tasks, capsys):
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps(parsed_good_tasks))
    rc = _run("--tasks", str(f))
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "PASS"


def test_main_invalid_json(tmp_path):
    f = tmp_path / "tasks.json"
    f.write_text("not json")
    rc = _run("--tasks", str(f))
    assert rc == 1


def test_main_non_list_json(tmp_path):
    f = tmp_path / "tasks.json"
    f.write_text(json.dumps({"not": "a list"}))
    rc = _run("--tasks", str(f))
    assert rc == 1
