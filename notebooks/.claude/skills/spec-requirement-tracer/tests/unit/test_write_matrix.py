"""Unit tests for scripts/write_matrix.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from write_matrix import (
    validate_payload,
    render_list,
    render_rows,
    render_summary,
    render_gaps,
    render_totals,
    render,
    main as wm_main,
)


TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / "traceability-matrix.md.template"
)


def test_validate_payload_happy(valid_matrix_payload):
    validate_payload(valid_matrix_payload)


def test_validate_payload_missing_feature(valid_matrix_payload):
    del valid_matrix_payload["feature"]
    with pytest.raises(ValueError, match="feature"):
        validate_payload(valid_matrix_payload)


def test_validate_payload_missing_rows():
    with pytest.raises(ValueError, match="rows"):
        validate_payload({"feature": "x"})


def test_validate_payload_empty_rows():
    with pytest.raises(ValueError, match="empty"):
        validate_payload({"feature": "x", "rows": []})


def test_validate_payload_invalid_status(valid_matrix_payload):
    valid_matrix_payload["rows"][0]["status"] = "MAYBE"
    with pytest.raises(ValueError, match="invalid status"):
        validate_payload(valid_matrix_payload)


def test_validate_payload_missing_row_key(valid_matrix_payload):
    del valid_matrix_payload["rows"][0]["status"]
    with pytest.raises(ValueError, match="missing key"):
        validate_payload(valid_matrix_payload)


def test_validate_payload_duplicate_req(valid_matrix_payload):
    valid_matrix_payload["rows"].append(dict(valid_matrix_payload["rows"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        validate_payload(valid_matrix_payload)


def test_render_list_empty():
    assert render_list([]) == "—"


def test_render_list_items():
    assert render_list(["a", "b"]) == "a, b"


def test_render_rows(valid_matrix_payload):
    out = render_rows(valid_matrix_payload["rows"])
    assert "REQ-001" in out
    assert "covered" in out
    assert "uncovered" in out


def test_render_summary(valid_matrix_payload):
    out = render_summary(valid_matrix_payload["rows"])
    assert "covered" in out
    assert "**Total**" in out


def test_render_gaps_present(valid_matrix_payload):
    out = render_gaps(valid_matrix_payload["rows"])
    assert "REQ-002" in out
    assert "REQ-003" in out
    assert "REQ-001" not in out  # covered, not a gap


def test_render_gaps_empty():
    rows = [{
        "req": "REQ-001",
        "comps": ["COMP-001"],
        "tasks": ["T-001"],
        "code_refs": ["a.py"],
        "tests_refs": ["test_a.py"],
        "status": "covered",
    }]
    out = render_gaps(rows)
    assert "no gaps" in out


def test_render_totals(valid_matrix_payload):
    out = render_totals(valid_matrix_payload["rows"])
    assert "Total REQs: **3**" in out
    assert "Covered: **1**" in out
    assert "Partial: **1**" in out
    assert "Uncovered: **1**" in out


def test_render_full(valid_matrix_payload):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    out = render(valid_matrix_payload, template)
    assert "{{" not in out
    assert "}}" not in out
    assert "REQ-001" in out
    assert "REQ-002" in out
    assert "REQ-003" in out


def _run(*a):
    old = sys.argv
    sys.argv = ["write_matrix.py", *a]
    try:
        return wm_main()
    finally:
        sys.argv = old


def test_main_writes_file(tmp_path, valid_matrix_payload):
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(valid_matrix_payload))
    out = tmp_path / "TRACEABILITY.md"
    rc = _run("--payload", str(payload), "--out", str(out))
    assert rc == 0
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    assert "REQ-001" in body
    assert "{{" not in body


def test_main_no_overwrite(tmp_path, valid_matrix_payload):
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(valid_matrix_payload))
    out = tmp_path / "TRACEABILITY.md"
    out.write_text("existing")
    rc = _run("--payload", str(payload), "--out", str(out))
    assert rc == 1
    assert out.read_text() == "existing"


def test_main_force(tmp_path, valid_matrix_payload):
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(valid_matrix_payload))
    out = tmp_path / "TRACEABILITY.md"
    out.write_text("existing")
    rc = _run("--payload", str(payload), "--out", str(out), "--force")
    assert rc == 0
    assert "existing" not in out.read_text()


def test_main_invalid_payload(tmp_path):
    payload = tmp_path / "p.json"
    payload.write_text("{}")
    out = tmp_path / "T.md"
    rc = _run("--payload", str(payload), "--out", str(out))
    assert rc == 1


def test_main_empty_payload(tmp_path):
    payload = tmp_path / "p.json"
    payload.write_text("")
    out = tmp_path / "T.md"
    rc = _run("--payload", str(payload), "--out", str(out))
    assert rc == 1
