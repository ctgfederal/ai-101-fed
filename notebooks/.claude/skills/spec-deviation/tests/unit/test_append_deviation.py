"""Unit tests for scripts/append_deviation.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from append_deviation import (
    render,
    append_block,
    main as ap_main,
)

TEMPLATE = (
    Path(__file__).resolve().parents[2] / "templates" / "deviation-block.md.template"
).read_text(encoding="utf-8")


def test_render_substitutes_all_tokens(valid_payload):
    out = render(valid_payload, TEMPLATE)
    assert "{{" not in out
    assert valid_payload["deviation_id"] in out
    assert valid_payload["reason_category"] in out
    assert valid_payload["original_decision"] in out
    assert valid_payload["status"] in out
    assert valid_payload["description"] in out


def test_render_preserves_template_structure(valid_payload):
    out = render(valid_payload, TEMPLATE)
    assert out.startswith("### DEV-")
    assert "**Description**" in out
    assert "**Proposed Change**" in out
    assert "**Impact**" in out


def test_append_to_clean_sdd_creates_section(clean_sdd, valid_payload):
    block = render(valid_payload, TEMPLATE)
    out = append_block(clean_sdd, valid_payload["deviation_id"], block, force=False)
    assert "## Deviations" in out
    assert "### DEV-001" in out
    assert clean_sdd.strip() in out  # original content preserved


def test_append_to_existing_section_does_not_duplicate(populated_sdd, valid_payload):
    valid_payload["deviation_id"] = "DEV-002"
    block = render(valid_payload, TEMPLATE)
    out = append_block(populated_sdd, "DEV-002", block, force=False)
    assert out.count("## Deviations") == 1
    assert "### DEV-001" in out  # original block preserved
    assert "### DEV-002" in out  # new block added


def test_append_existing_id_refuses_without_force(populated_sdd, valid_payload):
    valid_payload["deviation_id"] = "DEV-001"  # collides with populated_sdd
    block = render(valid_payload, TEMPLATE)
    with pytest.raises(FileExistsError):
        append_block(populated_sdd, "DEV-001", block, force=False)


def test_append_force_overwrites_existing(populated_sdd, valid_payload):
    valid_payload["deviation_id"] = "DEV-001"
    block = render(valid_payload, TEMPLATE)
    out = append_block(populated_sdd, "DEV-001", block, force=True)
    # Only one DEV-001 block, and it should now reflect the new payload
    assert out.count("### DEV-001") == 1
    assert valid_payload["description"] in out


def _run(*args):
    old = sys.argv
    sys.argv = ["append_deviation.py", *args]
    try:
        return ap_main()
    finally:
        sys.argv = old


def test_main_happy(tmp_path, valid_payload, clean_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(clean_sdd)
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--payload", str(p), "--sdd", str(sdd))
    assert rc == 0
    body = sdd.read_text(encoding="utf-8")
    assert "### DEV-001" in body
    assert "## Deviations" in body


def test_main_invalid_payload(tmp_path, bad_payload, clean_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(clean_sdd)
    p = tmp_path / "p.json"
    p.write_text(json.dumps(bad_payload))
    rc = _run("--payload", str(p), "--sdd", str(sdd))
    assert rc == 1
    # SDD should be untouched
    assert sdd.read_text() == clean_sdd


def test_main_missing_payload(tmp_path, clean_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(clean_sdd)
    rc = _run("--payload", str(tmp_path / "nope.json"), "--sdd", str(sdd))
    assert rc == 1


def test_main_missing_sdd(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--payload", str(p), "--sdd", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_collision_without_force(tmp_path, valid_payload, populated_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(populated_sdd)
    valid_payload["deviation_id"] = "DEV-001"
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--payload", str(p), "--sdd", str(sdd))
    assert rc == 1


def test_main_collision_with_force(tmp_path, valid_payload, populated_sdd):
    sdd = tmp_path / "SDD.md"
    sdd.write_text(populated_sdd)
    valid_payload["deviation_id"] = "DEV-001"
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    rc = _run("--payload", str(p), "--sdd", str(sdd), "--force")
    assert rc == 0
    body = sdd.read_text()
    assert body.count("### DEV-001") == 1
    assert valid_payload["description"] in body
