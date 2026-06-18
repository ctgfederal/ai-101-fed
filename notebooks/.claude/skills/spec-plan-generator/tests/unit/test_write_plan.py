"""Unit tests for scripts/write_plan.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from write_plan import (PHASES, validate, render, render_phase,
                         render_traceability, main as wm)


def test_phases_constant():
    assert PHASES == ["Foundation", "Core", "Integration", "Polish"]


def test_validate_happy(valid_payload):
    validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_missing_field(valid_payload):
    del valid_payload["tasks"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload, ["REQ-001"], ["COMP-001"])


def test_validate_bad_task_id(valid_payload):
    valid_payload["tasks"][0]["id"] = "X-1"
    with pytest.raises(ValueError, match="invalid task id"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_duplicate_task(valid_payload):
    valid_payload["tasks"][1]["id"] = "T-001"
    with pytest.raises(ValueError, match="duplicate task id"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_bad_phase(valid_payload):
    valid_payload["tasks"][0]["phase"] = "Madness"
    with pytest.raises(ValueError, match="invalid phase"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_bad_tdd(valid_payload):
    valid_payload["tasks"][0]["tdd_step"] = "yellow"
    with pytest.raises(ValueError, match="invalid tdd_step"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_unknown_comp(valid_payload):
    valid_payload["tasks"][0]["comps"] = ["COMP-999"]
    with pytest.raises(ValueError, match="unknown COMP"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_unknown_req(valid_payload):
    valid_payload["tasks"][0]["reqs"] = ["REQ-999"]
    with pytest.raises(ValueError, match="unknown REQ"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002"])


def test_validate_uncovered_comp(valid_payload):
    with pytest.raises(ValueError, match="components not covered"):
        validate(valid_payload, ["REQ-001", "REQ-002"], ["COMP-001", "COMP-002", "COMP-003"])


def test_validate_uncovered_req(valid_payload):
    with pytest.raises(ValueError, match="requirements not covered"):
        validate(valid_payload, ["REQ-001", "REQ-002", "REQ-003"], ["COMP-001", "COMP-002"])


def test_render_phase(valid_payload):
    out = render_phase("Foundation", valid_payload["tasks"])
    assert "T-001" in out


def test_render_phase_empty(valid_payload):
    out = render_phase("Polish", valid_payload["tasks"])
    assert "no tasks" in out


def test_render_traceability(valid_payload):
    out = render_traceability(valid_payload["tasks"])
    assert "REQ-001" in out
    assert "T-001" in out


def test_render_full(valid_payload):
    template = (Path(__file__).resolve().parents[2] / "templates" / "plan.md.template").read_text(encoding="utf-8")
    out = render(valid_payload, template)
    assert "{{" not in out


def _run(*a):
    old = sys.argv
    sys.argv = ["write_plan.py", *a]
    try:
        return wm()
    finally:
        sys.argv = old


def test_main_happy(tmp_path, valid_payload, fake_prd, fake_sdd):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "PLAN.md"
    rc = _run("--payload", str(p), "--out", str(out), "--prd", str(fake_prd), "--sdd", str(fake_sdd))
    assert rc == 0
    assert out.exists()
