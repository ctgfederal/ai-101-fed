"""Unit tests for scripts/append_decisions.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from append_decisions import (
    REQUIRED_KEYS, validate_payload, render_payload,
    feature_header_exists, main as ad_main,
)


def test_required_keys():
    assert "feature_title" in REQUIRED_KEYS
    assert "id_range" in REQUIRED_KEYS


def test_validate_happy(valid_payload):
    validate_payload(valid_payload)


def test_validate_missing_key(valid_payload):
    del valid_payload["summary"]
    with pytest.raises(ValueError, match="missing keys"):
        validate_payload(valid_payload)


def test_validate_bad_status(valid_payload):
    valid_payload["status"] = "draft"
    with pytest.raises(ValueError, match="status invalid"):
        validate_payload(valid_payload)


def test_validate_bad_decision_id(valid_payload):
    valid_payload["categories"]["Architecture"][0]["id"] = "X-1"
    with pytest.raises(ValueError, match="not D-NNN"):
        validate_payload(valid_payload)


def test_validate_missing_decision_id(valid_payload):
    del valid_payload["categories"]["Architecture"][0]["id"]
    with pytest.raises(ValueError, match="missing id"):
        validate_payload(valid_payload)


def test_validate_categories_not_dict(valid_payload):
    valid_payload["categories"] = []
    with pytest.raises(ValueError, match="dict"):
        validate_payload(valid_payload)


def test_render_includes_all_decisions(valid_payload):
    template = Path(__file__).resolve().parents[2] / "templates" / "feature-section.md.template"
    out = render_payload(valid_payload, template.read_text(encoding="utf-8"))
    for ids in ["D-001", "D-002", "D-003", "D-004", "D-005"]:
        assert ids in out
    assert "Feature Search" in out
    assert "Architecture" in out
    assert "Layered service" in out


def test_render_handles_empty_optional(valid_payload):
    template = Path(__file__).resolve().parents[2] / "templates" / "feature-section.md.template"
    valid_payload["related_solutions"] = []
    out = render_payload(valid_payload, template.read_text(encoding="utf-8"))
    assert "_(none)_" in out


def test_feature_header_exists():
    text = "## Feature Search — Build Decisions (2026-02-14)\n\nbody"
    assert feature_header_exists(text, "Feature Search", "2026-02-14")
    assert not feature_header_exists(text, "Other Feature", "2026-02-14")


def _run(*args):
    old = sys.argv
    sys.argv = ["append_decisions.py", *args]
    try:
        return ad_main()
    finally:
        sys.argv = old


def test_main_appends_to_empty_log(tmp_path, valid_payload):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload))
    log = tmp_path / "log.md"
    rc = _run("--payload", str(payload_file), "--log", str(log))
    assert rc == 0
    text = log.read_text()
    assert "# Decisions Log" in text
    assert "Feature Search — Build Decisions (2026-02-14)" in text
    assert "D-003" in text


def test_main_refuses_duplicate(tmp_path, valid_payload):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload))
    log = tmp_path / "log.md"
    assert _run("--payload", str(payload_file), "--log", str(log)) == 0
    rc = _run("--payload", str(payload_file), "--log", str(log))
    assert rc == 1


def test_main_force_appends_duplicate(tmp_path, valid_payload):
    payload_file = tmp_path / "p.json"
    payload_file.write_text(json.dumps(valid_payload))
    log = tmp_path / "log.md"
    _run("--payload", str(payload_file), "--log", str(log))
    rc = _run("--payload", str(payload_file), "--log", str(log), "--force")
    assert rc == 0
