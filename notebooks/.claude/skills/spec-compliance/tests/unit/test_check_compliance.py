"""Unit tests for scripts/check_compliance.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_compliance import (
    resolve_paths, scan_for_req_tokens, compute_status, check,
    main as check_main,
)


def test_resolve_paths_existing(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x")
    found = resolve_paths(tmp_path, ["src/a.py"])
    assert found == ["src/a.py"]


def test_resolve_paths_glob(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x")
    (tmp_path / "src" / "b.py").write_text("y")
    found = resolve_paths(tmp_path, ["src/*.py"])
    assert sorted(found) == ["src/a.py", "src/b.py"]


def test_resolve_paths_missing(tmp_path):
    (tmp_path / "src").mkdir()
    found = resolve_paths(tmp_path, ["src/missing.py"])
    assert found == []


def test_resolve_paths_empty():
    found = resolve_paths(Path("/tmp"), [])
    assert found == []


def test_resolve_paths_dedup(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x")
    found = resolve_paths(tmp_path, ["src/a.py", "src/a.py"])
    assert found == ["src/a.py"]


def test_scan_for_req_tokens_finds_refs(sample_repo):
    refs = scan_for_req_tokens(sample_repo)
    assert "REQ-001" in refs
    assert any("service.py" in p for p in refs["REQ-001"])
    assert any("test_search.py" in p for p in refs["REQ-001"])


def test_scan_for_req_tokens_skips_vendored(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "junk.js").write_text("REQ-999")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "real.py").write_text("# REQ-001")
    refs = scan_for_req_tokens(tmp_path)
    assert "REQ-001" in refs
    assert "REQ-999" not in refs


def test_compute_status_compliant():
    comps = {"C1": {"missing": False}}
    reqs = {"R1": {"unreferenced": False}}
    assert compute_status(comps, reqs) == "compliant"


def test_compute_status_partial():
    comps = {"C1": {"missing": False}, "C2": {"missing": True}}
    reqs = {"R1": {"unreferenced": False}}
    assert compute_status(comps, reqs) == "partial"


def test_compute_status_non_compliant_no_comp():
    comps = {"C1": {"missing": True}}
    reqs = {"R1": {"unreferenced": False}}
    assert compute_status(comps, reqs) == "non-compliant"


def test_compute_status_non_compliant_no_req():
    comps = {"C1": {"missing": False}}
    reqs = {"R1": {"unreferenced": True}}
    assert compute_status(comps, reqs) == "non-compliant"


def test_compute_status_empty_spec():
    assert compute_status({}, {}) == "non-compliant"


def test_check_full_pipeline(parsed_spec_payload, sample_repo):
    payload = check(parsed_spec_payload, sample_repo)
    assert payload["status"] == "partial"
    assert payload["components"]["COMP-001"]["missing"] is False
    assert payload["components"]["COMP-002"]["missing"] is True
    assert payload["requirements"]["REQ-001"]["unreferenced"] is False
    assert payload["requirements"]["REQ-002"]["unreferenced"] is True

    types = {d["type"] for d in payload["deviations"]}
    assert "missing-component" in types
    assert "unreferenced-requirement" in types

    assert payload["summary"]["components_total"] == 2
    assert payload["summary"]["components_found"] == 1
    assert payload["summary"]["requirements_total"] == 2
    assert payload["summary"]["requirements_referenced"] == 1
    assert payload["summary"]["deviation_count"] == 2


def test_check_detects_scope_creep(parsed_spec_payload, tmp_path):
    repo = tmp_path / "repo"
    (repo / "src" / "search").mkdir(parents=True)
    (repo / "src" / "search" / "service.py").write_text(
        "# REQ-001 plus an undeclared REQ-999\n"
    )
    payload = check(parsed_spec_payload, repo)
    creep = [d for d in payload["deviations"] if d["type"] == "scope-creep"]
    assert len(creep) == 1
    assert creep[0]["id"] == "REQ-999"


def _run(*args):
    old = sys.argv
    sys.argv = ["check_compliance.py", *args]
    try:
        return check_main()
    finally:
        sys.argv = old


def test_main_missing_spec_json(tmp_path):
    rc = _run("--spec-json", str(tmp_path / "nope.json"),
              "--repo-root", str(tmp_path))
    assert rc == 1


def test_main_bad_repo_root(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text('{"reqs": [], "comps": []}')
    rc = _run("--spec-json", str(spec),
              "--repo-root", str(tmp_path / "nope"))
    assert rc == 1


def test_main_invalid_spec_json(tmp_path):
    spec = tmp_path / "spec.json"
    spec.write_text("not json")
    rc = _run("--spec-json", str(spec), "--repo-root", str(tmp_path))
    assert rc == 1


def test_main_emits_json(tmp_path, parsed_spec_payload, sample_repo, capsys):
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(parsed_spec_payload))
    rc = _run("--spec-json", str(spec_file), "--repo-root", str(sample_repo))
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["status"] == "partial"
