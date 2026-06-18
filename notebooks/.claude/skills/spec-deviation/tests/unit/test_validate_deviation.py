"""Unit tests for scripts/validate_deviation.py."""
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_deviation import (
    REQUIRED_FIELDS,
    ALLOWED_REASON_CATEGORIES,
    ALLOWED_STATUSES,
    validate,
    main as vd_main,
)


def test_required_fields_includes_all_ten():
    assert len(REQUIRED_FIELDS) == 10
    for f in (
        "spec_id", "deviation_id", "reason_category", "description",
        "original_decision", "proposed_change", "impact", "status",
        "approver", "date",
    ):
        assert f in REQUIRED_FIELDS


def test_allowed_enums_count():
    assert len(ALLOWED_REASON_CATEGORIES) == 5
    assert len(ALLOWED_STATUSES) == 3


def test_validate_happy(valid_payload):
    assert validate(valid_payload) == []


def test_validate_not_a_dict():
    errors = validate("not a dict")
    assert any("must be a JSON object" in e for e in errors)


@pytest.mark.parametrize("field", [
    "spec_id", "deviation_id", "reason_category", "description",
    "original_decision", "proposed_change", "impact", "status",
    "approver", "date",
])
def test_validate_missing_each_required_field(valid_payload, field):
    del valid_payload[field]
    errors = validate(valid_payload)
    assert any(f"missing required field: {field}" == e for e in errors)


def test_validate_empty_string_field(valid_payload):
    valid_payload["description"] = "   "
    errors = validate(valid_payload)
    assert any("description" in e and "non-empty" in e for e in errors)


def test_validate_bad_dev_id(valid_payload):
    valid_payload["deviation_id"] = "DEV-1"
    errors = validate(valid_payload)
    assert any("deviation_id" in e for e in errors)


def test_validate_bad_dev_id_no_prefix(valid_payload):
    valid_payload["deviation_id"] = "001"
    errors = validate(valid_payload)
    assert any("deviation_id" in e for e in errors)


def test_validate_bad_reason_category(valid_payload):
    valid_payload["reason_category"] = "preference"
    errors = validate(valid_payload)
    assert any("reason_category" in e for e in errors)


def test_validate_bad_status(valid_payload):
    valid_payload["status"] = "draft"
    errors = validate(valid_payload)
    assert any("status" in e for e in errors)


def test_validate_bad_original_decision_format(valid_payload):
    valid_payload["original_decision"] = "req-1"
    errors = validate(valid_payload)
    assert any("original_decision" in e for e in errors)


def test_validate_accepts_REQ_COMP_D(valid_payload):
    for v in ("REQ-1", "COMP-014", "D-7"):
        valid_payload["original_decision"] = v
        assert validate(valid_payload) == [], f"failed for {v}"


def test_validate_bad_date(valid_payload):
    valid_payload["date"] = "May 8, 2026"
    errors = validate(valid_payload)
    assert any("date" in e for e in errors)


def test_validate_collects_all_errors(bad_payload):
    errors = validate(bad_payload)
    # Multiple violations should be reported, not just the first
    assert len(errors) >= 4


def _run(*args, stdin=None):
    old, oldst = sys.argv, sys.stdin
    sys.argv = ["validate_deviation.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return vd_main()
    finally:
        sys.argv = old
        sys.stdin = oldst


def test_main_happy(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--payload", str(p))
    assert rc == 0


def test_main_invalid(tmp_path, bad_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(bad_payload))
    rc = _run("--payload", str(p))
    assert rc == 1


def test_main_stdin(valid_payload):
    rc = _run(stdin=json.dumps(valid_payload))
    assert rc == 0


def test_main_empty_payload():
    rc = _run(stdin="")
    assert rc == 1


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    rc = _run("--payload", str(p))
    assert rc == 1


def test_main_missing_payload_file(tmp_path):
    rc = _run("--payload", str(tmp_path / "nope.json"))
    assert rc == 1
