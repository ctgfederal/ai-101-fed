"""Unit tests for scripts/write_solution.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_solution import (
    REQUIRED_KEYS,
    render,
    validate_payload,
    main as ws_main,
)


def test_required_keys_complete():
    """Hard-coded expectation — change requires updating the schema doc too."""
    expected = {
        "title", "category", "date", "tags", "module", "symptom", "root_cause",
        "symptom_body", "investigation_body", "root_cause_body",
        "solution_body", "verification_body", "prevention_body",
    }
    assert set(REQUIRED_KEYS) == expected


# --- validate_payload ---

def test_validate_payload_happy(valid_payload):
    validate_payload(valid_payload)  # no raise


def test_validate_payload_missing_key(invalid_payload):
    with pytest.raises(ValueError, match="missing required keys"):
        validate_payload(invalid_payload)


def test_validate_payload_bad_category(valid_payload):
    valid_payload["category"] = "made-up"
    with pytest.raises(ValueError, match="unknown category"):
        validate_payload(valid_payload)


def test_validate_payload_future_date(valid_payload):
    valid_payload["date"] = "2999-01-01"
    with pytest.raises(ValueError, match="future"):
        validate_payload(valid_payload)


def test_validate_payload_too_few_tags(valid_payload):
    valid_payload["tags"] = ["only"]
    with pytest.raises(ValueError, match="2-8"):
        validate_payload(valid_payload)


def test_validate_payload_bad_severity(valid_payload):
    valid_payload["severity"] = "catastrophic"
    with pytest.raises(ValueError, match="invalid severity"):
        validate_payload(valid_payload)


def test_validate_payload_severity_optional(valid_payload):
    del valid_payload["severity"]
    validate_payload(valid_payload)  # no raise


def test_validate_payload_short_title(valid_payload):
    valid_payload["title"] = "tiny"
    with pytest.raises(ValueError, match="title length"):
        validate_payload(valid_payload)


# --- render ---

TEMPLATE = """---
title: "{{TITLE}}"
category: {{CATEGORY}}
date: {{DATE}}
tags:{{TAGS_YAML}}
module: "{{MODULE}}"
symptom: "{{SYMPTOM}}"
root_cause: "{{ROOT_CAUSE}}"
severity: {{SEVERITY}}
---

# {{TITLE}}

## Symptom
{{SYMPTOM_BODY}}

## Investigation
{{INVESTIGATION_BODY}}

## Root Cause
{{ROOT_CAUSE_BODY}}

## Solution
{{SOLUTION_BODY}}

## Verification
{{VERIFICATION_BODY}}

## Prevention
{{PREVENTION_BODY}}

## Related
{{RELATED_BODY}}
"""


def test_render_substitutes_all(valid_payload):
    out = render(valid_payload, TEMPLATE)
    assert "{{TITLE}}" not in out
    assert "{{TAGS_YAML}}" not in out
    assert valid_payload["title"] in out
    assert valid_payload["solution_body"] in out


def test_render_omits_severity_when_blank(valid_payload):
    valid_payload["severity"] = ""
    out = render(valid_payload, TEMPLATE)
    # severity line should still be present but with empty quotes
    assert 'severity: ""' in out


def test_render_handles_missing_related(valid_payload):
    del valid_payload["related_body"]
    out = render(valid_payload, TEMPLATE)
    assert "_(none)_" in out


# --- main entry: end-to-end through subprocess-style ---

def _run_main(argv, stdin_text=None):
    old = sys.argv
    old_stdin = sys.stdin
    sys.argv = ["write_solution.py"] + argv
    if stdin_text is not None:
        import io
        sys.stdin = io.StringIO(stdin_text)
    try:
        return ws_main()
    finally:
        sys.argv = old
        sys.stdin = old_stdin


def test_main_writes_file(tmp_path, valid_payload, tmp_solutions_root, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "solution.md.template"

    rc = _run_main([
        "--payload", str(payload_file),
        "--solutions-root", str(tmp_solutions_root),
        "--template", str(template),
    ])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert Path(out).exists()
    assert Path(out).parent.name == "performance-issues"


def test_main_refuses_overwrite(tmp_path, valid_payload, tmp_solutions_root, caplog):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "solution.md.template"

    args = [
        "--payload", str(payload_file),
        "--solutions-root", str(tmp_solutions_root),
        "--template", str(template),
    ]
    assert _run_main(args) == 0
    caplog.clear()
    rc = _run_main(args)
    assert rc == 1
    assert any("exists" in r.message.lower() for r in caplog.records)


def test_main_force_overwrites(tmp_path, valid_payload, tmp_solutions_root, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "solution.md.template"

    args = [
        "--payload", str(payload_file),
        "--solutions-root", str(tmp_solutions_root),
        "--template", str(template),
    ]
    assert _run_main(args) == 0
    capsys.readouterr()
    rc = _run_main(args + ["--force"])
    assert rc == 0


def test_main_stdin_payload(valid_payload, tmp_solutions_root, capsys):
    template = Path(__file__).resolve().parents[2] / "templates" / "solution.md.template"
    rc = _run_main(
        ["--solutions-root", str(tmp_solutions_root), "--template", str(template)],
        stdin_text=json.dumps(valid_payload),
    )
    assert rc == 0


def test_main_invalid_payload(tmp_path, tmp_solutions_root):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("not json", encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "solution.md.template"
    rc = _run_main([
        "--payload", str(payload_file),
        "--solutions-root", str(tmp_solutions_root),
        "--template", str(template),
    ])
    assert rc == 1
