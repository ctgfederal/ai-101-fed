"""Unit tests for scripts/parse_spec.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from parse_spec import (
    extract_reqs, extract_comps, parse, main as parse_main,
)


def test_extract_reqs_finds_all(sample_prd):
    reqs = extract_reqs(sample_prd)
    assert reqs == ["REQ-001", "REQ-002"]


def test_extract_reqs_dedup():
    text = "- **REQ-001**: x\n- **REQ-001**: y\n- **REQ-002**: z\n"
    assert extract_reqs(text) == ["REQ-001", "REQ-002"]


def test_extract_reqs_empty():
    assert extract_reqs("# heading\n\nno reqs\n") == []


def test_extract_comps_basic(sample_sdd):
    comps = extract_comps(sample_sdd)
    assert len(comps) == 2
    assert comps[0]["id"] == "COMP-001"
    assert comps[0]["name"] == "SearchService"
    assert comps[0]["expected_paths"] == ["src/search/service.py"]
    assert comps[1]["id"] == "COMP-002"
    assert comps[1]["expected_paths"] == ["src/search/ranking.py"]


def test_extract_comps_dash_separator():
    text = "### COMP-007 - WidgetService\nPath: `src/widgets.py`\n"
    comps = extract_comps(text)
    assert len(comps) == 1
    assert comps[0]["id"] == "COMP-007"
    assert comps[0]["name"] == "WidgetService"
    assert comps[0]["expected_paths"] == ["src/widgets.py"]


def test_extract_comps_multiple_paths_via_paths():
    text = (
        "### COMP-010: ApiLayer\n"
        "Paths: `src/api/handler.py`, `src/api/router.py`\n"
    )
    comps = extract_comps(text)
    assert comps[0]["expected_paths"] == ["src/api/handler.py", "src/api/router.py"]


def test_extract_comps_no_path_line():
    text = "### COMP-020: Orphan\nDescription only, no path.\n"
    comps = extract_comps(text)
    assert comps[0]["expected_paths"] == []


def test_extract_comps_stops_at_h2():
    text = (
        "### COMP-001: A\nPath: `a.py`\n## New Section\nPath: `should-not-belong.py`\n"
    )
    comps = extract_comps(text)
    assert comps[0]["expected_paths"] == ["a.py"]


def test_parse_combines(sample_prd, sample_sdd):
    payload = parse(sample_prd, sample_sdd, "PRD.md", "SDD.md")
    assert payload["prd"] == "PRD.md"
    assert payload["sdd"] == "SDD.md"
    assert payload["reqs"] == ["REQ-001", "REQ-002"]
    assert len(payload["comps"]) == 2


def _run(*args):
    old = sys.argv
    sys.argv = ["parse_spec.py", *args]
    try:
        return parse_main()
    finally:
        sys.argv = old


def test_main_missing_prd(tmp_path):
    sdd = tmp_path / "SDD.md"
    sdd.write_text("### COMP-001: X\nPath: `x.py`\n")
    rc = _run("--prd", str(tmp_path / "nope.md"), "--sdd", str(sdd))
    assert rc == 1


def test_main_missing_sdd(tmp_path):
    prd = tmp_path / "PRD.md"
    prd.write_text("- **REQ-001**: x\n")
    rc = _run("--prd", str(prd), "--sdd", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_emits_json(tmp_path, sample_prd, sample_sdd, capsys):
    prd = tmp_path / "PRD.md"
    sdd = tmp_path / "SDD.md"
    prd.write_text(sample_prd)
    sdd.write_text(sample_sdd)
    rc = _run("--prd", str(prd), "--sdd", str(sdd))
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["reqs"] == ["REQ-001", "REQ-002"]
    assert len(payload["comps"]) == 2
