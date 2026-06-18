"""Unit tests for scripts/write_report.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_report import (
    validate, render, render_components_table, render_requirements_table,
    render_deviations, render_summary, render_status_notes,
    main as write_main,
)


TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "templates" / "compliance-report.md.template"
TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


def test_validate_accepts_valid(valid_payload):
    validate(valid_payload)


def test_validate_rejects_missing_keys(valid_payload):
    del valid_payload["status"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload)


def test_validate_rejects_bad_status(valid_payload):
    valid_payload["status"] = "ok"
    with pytest.raises(ValueError, match="status must be one of"):
        validate(valid_payload)


def test_validate_rejects_components_not_dict(valid_payload):
    valid_payload["components"] = []
    with pytest.raises(ValueError, match="components must be a dict"):
        validate(valid_payload)


def test_validate_rejects_deviations_not_list(valid_payload):
    valid_payload["deviations"] = {}
    with pytest.raises(ValueError, match="deviations must be a list"):
        validate(valid_payload)


def test_render_components_table_has_rows(valid_payload):
    out = render_components_table(valid_payload["components"])
    assert "COMP-001" in out
    assert "COMP-002" in out
    assert "PRESENT" in out
    assert "MISSING" in out


def test_render_components_table_empty():
    assert "no components" in render_components_table({})


def test_render_requirements_table_has_rows(valid_payload):
    out = render_requirements_table(valid_payload["requirements"])
    assert "REQ-001" in out
    assert "REQ-002" in out
    assert "REFERENCED" in out
    assert "UNREFERENCED" in out


def test_render_requirements_table_empty():
    assert "no requirements" in render_requirements_table({})


def test_render_deviations_has_entries(valid_payload):
    out = render_deviations(valid_payload["deviations"])
    assert "missing-component" in out
    assert "unreferenced-requirement" in out
    assert "COMP-002" in out
    assert "REQ-002" in out


def test_render_deviations_empty():
    assert "no deviations" in render_deviations([])


def test_render_summary(valid_payload):
    out = render_summary(valid_payload["summary"])
    assert "1/2" in out  # components and requirements
    assert "Deviations: 2" in out


def test_render_status_notes_known():
    assert "Every component" in render_status_notes("compliant")
    assert "Some components" in render_status_notes("partial")
    assert "not aligned" in render_status_notes("non-compliant")


def test_render_replaces_all_tokens(valid_payload):
    out = render(valid_payload, TEMPLATE)
    assert "{{" not in out
    assert "}}" not in out
    assert "**partial**" in out
    assert "COMP-001" in out
    assert "REQ-001" in out


def _run(*args):
    old = sys.argv
    sys.argv = ["write_report.py", *args]
    try:
        return write_main()
    finally:
        sys.argv = old


def test_main_writes_report(tmp_path, valid_payload):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload))
    out_file = tmp_path / "REPORT.md"
    rc = _run("--payload", str(payload_file), "--out", str(out_file))
    assert rc == 0
    assert out_file.exists()
    text = out_file.read_text()
    assert "**partial**" in text


def test_main_refuses_overwrite(tmp_path, valid_payload):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload))
    out_file = tmp_path / "REPORT.md"
    out_file.write_text("existing")
    rc = _run("--payload", str(payload_file), "--out", str(out_file))
    assert rc == 1
    assert out_file.read_text() == "existing"


def test_main_force_overwrite(tmp_path, valid_payload):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload))
    out_file = tmp_path / "REPORT.md"
    out_file.write_text("existing")
    rc = _run("--payload", str(payload_file), "--out", str(out_file), "--force")
    assert rc == 0
    assert "**partial**" in out_file.read_text()


def test_main_invalid_payload(tmp_path):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("{}")
    out_file = tmp_path / "REPORT.md"
    rc = _run("--payload", str(payload_file), "--out", str(out_file))
    assert rc == 1


def test_main_empty_payload(tmp_path):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("")
    out_file = tmp_path / "REPORT.md"
    rc = _run("--payload", str(payload_file), "--out", str(out_file))
    assert rc == 1
