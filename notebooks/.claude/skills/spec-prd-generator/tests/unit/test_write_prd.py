"""Unit tests for scripts/write_prd.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_prd import (
    REQUIRED, ALLOWED_MOSCOW, validate, render,
    render_user_stories, render_requirements, render_moscow,
    main as wp_main,
)


def test_required_keys():
    assert "user_stories" in REQUIRED
    assert "requirements" in REQUIRED


def test_validate_happy(valid_payload):
    validate(valid_payload)


def test_validate_missing_key(valid_payload):
    del valid_payload["vision"]
    with pytest.raises(ValueError, match="missing keys"):
        validate(valid_payload)


def test_validate_empty_stories(valid_payload):
    valid_payload["user_stories"] = []
    with pytest.raises(ValueError, match="user_stories"):
        validate(valid_payload)


def test_validate_invalid_req_id(valid_payload):
    valid_payload["requirements"][0]["id"] = "X-001"
    with pytest.raises(ValueError, match="invalid REQ ID"):
        validate(valid_payload)


def test_validate_duplicate_req_id(valid_payload):
    valid_payload["requirements"][1]["id"] = "REQ-001"
    with pytest.raises(ValueError, match="duplicate REQ"):
        validate(valid_payload)


def test_validate_bad_moscow(valid_payload):
    valid_payload["requirements"][0]["moscow"] = "Maybe"
    with pytest.raises(ValueError, match="invalid MoSCoW"):
        validate(valid_payload)


def test_validate_non_ears_requirement(valid_payload):
    valid_payload["requirements"][0]["ears"] = "the user can search"
    with pytest.raises(ValueError, match="not EARS"):
        validate(valid_payload)


def test_render_user_stories(valid_payload):
    out = render_user_stories(valid_payload["user_stories"])
    assert "US-1" in out
    assert "brief author" in out


def test_render_moscow_table(valid_payload):
    out = render_moscow(valid_payload["requirements"])
    assert "REQ-001" in out
    assert "Must" in out


def test_render_full(valid_payload):
    template = Path(__file__).resolve().parents[2] / "templates" / "prd.md.template"
    out = render(valid_payload, template.read_text(encoding="utf-8"))
    assert "{{" not in out
    assert "REQ-001" in out
    assert ".claude/steering/product.md" in out


def _run(*args, stdin=None):
    import io
    old, oldst = sys.argv, sys.stdin
    sys.argv = ["write_prd.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return wp_main()
    finally:
        sys.argv = old
        sys.stdin = oldst


def test_main_writes(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "PRD.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 0
    assert out.exists()


def test_main_refuses_overwrite(tmp_path, valid_payload):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(valid_payload))
    out = tmp_path / "PRD.md"
    out.write_text("existing")
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1


def test_main_invalid_json(tmp_path):
    p = tmp_path / "p.json"
    p.write_text("not json")
    out = tmp_path / "PRD.md"
    rc = _run("--payload", str(p), "--out", str(out))
    assert rc == 1
