"""Unit tests for scripts/build_matrix.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from build_matrix import assign_status, build, main as bm_main


def test_assign_status_covered():
    assert assign_status(["C1"], ["T1"], ["a.py"], ["test.py"]) == "covered"


def test_assign_status_partial_missing_code():
    assert assign_status(["C1"], ["T1"], [], ["test.py"]) == "partial"


def test_assign_status_partial_missing_test():
    assert assign_status(["C1"], ["T1"], ["a.py"], []) == "partial"


def test_assign_status_partial_missing_sdd():
    assert assign_status([], ["T1"], ["a.py"], ["test.py"]) == "partial"


def test_assign_status_partial_only_one_layer():
    assert assign_status(["C1"], [], [], []) == "partial"


def test_assign_status_uncovered():
    assert assign_status([], [], [], []) == "uncovered"


def test_build_full(valid_ids_payload):
    out = build(valid_ids_payload, "feature-search")
    assert out["feature"] == "feature-search"
    assert len(out["rows"]) == 3
    by_req = {r["req"]: r for r in out["rows"]}

    r1 = by_req["REQ-001"]
    assert r1["comps"] == ["COMP-001", "COMP-003"]
    assert r1["tasks"] == ["T-001"]
    assert r1["code_refs"] == ["src/search.py"]
    assert r1["tests_refs"] == ["tests/test_search.py"]
    assert r1["status"] == "covered"

    r2 = by_req["REQ-002"]
    assert r2["comps"] == ["COMP-002"]
    assert r2["tasks"] == ["T-002"]
    assert r2["code_refs"] == []
    assert r2["tests_refs"] == ["tests/test_ranking.py"]
    assert r2["status"] == "partial"

    r3 = by_req["REQ-003"]
    assert r3["comps"] == []
    assert r3["tasks"] == []
    assert r3["status"] == "uncovered"


def test_build_missing_keys():
    import pytest
    with pytest.raises(ValueError):
        build({"prd_reqs": ["REQ-001"]}, "feature-x")


def test_build_no_reqs(valid_ids_payload):
    valid_ids_payload["prd_reqs"] = []
    out = build(valid_ids_payload, "feature-empty")
    assert out["rows"] == []


def _run(*a):
    old = sys.argv
    sys.argv = ["build_matrix.py", *a]
    try:
        return bm_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--ids-json", str(tmp_path / "no.json"))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json")
    rc = _run("--ids-json", str(f))
    assert rc == 1


def test_main_happy(tmp_path, valid_ids_payload, capsys):
    f = tmp_path / "ids.json"
    f.write_text(json.dumps(valid_ids_payload))
    rc = _run("--ids-json", str(f), "--feature", "feature-x")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["feature"] == "feature-x"
    assert len(data["rows"]) == 3
