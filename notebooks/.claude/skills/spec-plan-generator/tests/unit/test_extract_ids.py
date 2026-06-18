"""Unit tests for scripts/extract_ids.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from extract_ids import extract, REQ_RE, COMP_RE, main as em


def test_extract_reqs():
    assert extract("REQ-005 REQ-001", REQ_RE, "REQ") == ["REQ-001", "REQ-005"]


def test_extract_comps():
    assert extract("COMP-002 COMP-001", COMP_RE, "COMP") == ["COMP-001", "COMP-002"]


def test_extract_empty():
    assert extract("nothing", REQ_RE, "REQ") == []


def _run(*a):
    old = sys.argv
    sys.argv = ["extract_ids.py", *a]
    try:
        return em()
    finally:
        sys.argv = old


def test_main_missing_prd(tmp_path):
    assert _run("--prd", str(tmp_path / "no.md"), "--sdd", str(tmp_path / "no2.md")) == 1


def test_main_happy(tmp_path, capsys):
    prd = tmp_path / "PRD.md"
    prd.write_text("REQ-001")
    sdd = tmp_path / "SDD.md"
    sdd.write_text("COMP-001")
    rc = _run("--prd", str(prd), "--sdd", str(sdd))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["reqs"] == ["REQ-001"]
    assert data["comps"] == ["COMP-001"]
