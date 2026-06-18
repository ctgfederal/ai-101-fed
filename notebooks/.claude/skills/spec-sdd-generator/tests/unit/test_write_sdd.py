"""Unit tests for scripts/write_sdd.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from write_sdd import (REQUIRED, validate, render, render_components,
                       render_traceability, main as wm)


def test_required_keys():
    assert "components" in REQUIRED
    assert "traceability" in REQUIRED


def test_validate_happy(valid_payload):
    validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_missing_field(valid_payload):
    del valid_payload["overview"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_no_components(valid_payload):
    valid_payload["components"] = []
    with pytest.raises(ValueError, match="non-empty list"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_invalid_comp_id(valid_payload):
    valid_payload["components"][0]["id"] = "X-1"
    with pytest.raises(ValueError, match="invalid COMP id"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_duplicate_comp_id(valid_payload):
    valid_payload["components"][1]["id"] = "COMP-001"
    with pytest.raises(ValueError, match="duplicate COMP id"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_missing_contract(valid_payload):
    del valid_payload["components"][0]["contract"]["outputs"]
    with pytest.raises(ValueError, match="contract must have"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_unknown_comp_in_traceability(valid_payload):
    valid_payload["traceability"]["REQ-001"] = ["COMP-999"]
    with pytest.raises(ValueError, match="unknown component"):
        validate(valid_payload, ["REQ-001", "REQ-002"])


def test_validate_missing_req_coverage(valid_payload):
    with pytest.raises(ValueError, match="missing PRD requirements"):
        validate(valid_payload, ["REQ-001", "REQ-002", "REQ-003"])


def test_render_components(valid_payload):
    out = render_components(valid_payload["components"])
    assert "COMP-001" in out
    assert "SearchController" in out


def test_render_traceability(valid_payload):
    out = render_traceability(valid_payload["traceability"])
    assert "REQ-001" in out
    assert "COMP-001" in out


def test_render_full(valid_payload):
    template = (Path(__file__).resolve().parents[2] / "templates" / "sdd.md.template").read_text(encoding="utf-8")
    out = render(valid_payload, template)
    assert "{{" not in out
    assert "REQ-001" in out


def _run(*a):
    old = sys.argv
    sys.argv = ["write_sdd.py", *a]
    try:
        return wm()
    finally:
        sys.argv = old


def test_main_writes(tmp_path, valid_payload, fake_prd):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "SDD.md"
    rc = _run("--payload", str(p), "--out", str(out), "--prd", str(fake_prd))
    assert rc == 0
    assert out.exists()


def test_main_missing_prd(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "SDD.md"
    rc = _run("--payload", str(p), "--out", str(out), "--prd", str(tmp_path / "no.md"))
    assert rc == 1
