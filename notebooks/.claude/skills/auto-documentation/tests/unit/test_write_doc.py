"""Unit tests for scripts/write_doc.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from write_doc import (
    REQUIRED_KEYS,
    CANONICAL_CATEGORIES,
    render,
    validate_payload,
    slugify,
    main as wd_main,
)


def test_required_keys_complete():
    """Hard-coded expectation — change requires updating the schema doc too."""
    expected = {
        "title", "category", "date", "tags", "scope", "source",
        "description_body", "why_body", "examples_body", "related_body",
    }
    assert set(REQUIRED_KEYS) == expected


def test_canonical_categories_set():
    assert CANONICAL_CATEGORIES == {
        "business-rule", "technical-pattern", "service-interface", "domain-rule"
    }


# --- slugify ---

def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_unicode():
    assert slugify("café résumé") == "cafe-resume"


def test_slugify_punctuation():
    assert slugify("admin: edit/delete (rules)") == "admin-edit-delete-rules"


def test_slugify_truncates_long():
    long = "a" * 200
    out = slugify(long)
    assert len(out) <= 60


def test_slugify_empty_raises():
    with pytest.raises(ValueError):
        slugify("")


def test_slugify_punctuation_only_raises():
    with pytest.raises(ValueError):
        slugify("!!!---???")


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


def test_validate_payload_bad_date_format(valid_payload):
    valid_payload["date"] = "May 8, 2026"
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_payload(valid_payload)


def test_validate_payload_too_few_tags(valid_payload):
    valid_payload["tags"] = ["only"]
    with pytest.raises(ValueError, match="2-8"):
        validate_payload(valid_payload)


def test_validate_payload_too_many_tags(valid_payload):
    valid_payload["tags"] = [f"t{i}" for i in range(9)]
    with pytest.raises(ValueError, match="2-8"):
        validate_payload(valid_payload)


def test_validate_payload_duplicate_tag(valid_payload):
    valid_payload["tags"] = ["dup", "dup"]
    with pytest.raises(ValueError, match="duplicate tag"):
        validate_payload(valid_payload)


def test_validate_payload_bad_tag_format(valid_payload):
    valid_payload["tags"] = ["Has Space", "ok"]
    with pytest.raises(ValueError, match="invalid tag"):
        validate_payload(valid_payload)


def test_validate_payload_short_title(valid_payload):
    valid_payload["title"] = "tiny"
    with pytest.raises(ValueError, match="title length"):
        validate_payload(valid_payload)


def test_validate_payload_long_title(valid_payload):
    valid_payload["title"] = "x" * 121
    with pytest.raises(ValueError, match="title length"):
        validate_payload(valid_payload)


def test_validate_payload_empty_scope(valid_payload):
    valid_payload["scope"] = "  "
    with pytest.raises(ValueError, match="scope"):
        validate_payload(valid_payload)


def test_validate_payload_empty_source(valid_payload):
    valid_payload["source"] = ""
    # source is also caught by REQUIRED_KEYS empty-string check or scope check.
    # The validator should raise ValueError either way.
    with pytest.raises(ValueError):
        validate_payload(valid_payload)


# --- render ---

TEMPLATE = """---
title: "{{TITLE}}"
category: {{CATEGORY}}
date: {{DATE}}
tags:{{TAGS_YAML}}
scope: "{{SCOPE}}"
source: "{{SOURCE}}"
---

# {{TITLE}}

## Description

{{DESCRIPTION_BODY}}

## Why

{{WHY_BODY}}

## Examples

{{EXAMPLES_BODY}}

## Related

{{RELATED_BODY}}
"""


def test_render_substitutes_all(valid_payload):
    out = render(valid_payload, TEMPLATE)
    assert "{{TITLE}}" not in out
    assert "{{TAGS_YAML}}" not in out
    assert valid_payload["title"] in out
    assert valid_payload["scope"] in out


def test_render_includes_all_tags(valid_payload):
    out = render(valid_payload, TEMPLATE)
    for tag in valid_payload["tags"]:
        assert tag in out


def test_render_handles_missing_related(valid_payload):
    valid_payload["related_body"] = ""
    out = render(valid_payload, TEMPLATE)
    assert "_(none)_" in out


# --- main ---

def _run_main(argv, stdin_text=None):
    old = sys.argv
    old_stdin = sys.stdin
    sys.argv = ["write_doc.py"] + argv
    if stdin_text is not None:
        import io
        sys.stdin = io.StringIO(stdin_text)
    try:
        return wd_main()
    finally:
        sys.argv = old
        sys.stdin = old_stdin


def test_main_writes_file(tmp_path, valid_payload, tmp_docs_root, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "auto-doc.md.template"

    rc = _run_main([
        "--payload", str(payload_file),
        "--docs-root", str(tmp_docs_root),
        "--template", str(template),
    ])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert Path(out).exists()
    assert Path(out).parent.name == "business-rule"


def test_main_refuses_overwrite(tmp_path, valid_payload, tmp_docs_root, caplog):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "auto-doc.md.template"

    args = [
        "--payload", str(payload_file),
        "--docs-root", str(tmp_docs_root),
        "--template", str(template),
    ]
    assert _run_main(args) == 0
    caplog.clear()
    rc = _run_main(args)
    assert rc == 1
    assert any("exists" in r.message.lower() for r in caplog.records)


def test_main_force_overwrites(tmp_path, valid_payload, tmp_docs_root, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "auto-doc.md.template"

    args = [
        "--payload", str(payload_file),
        "--docs-root", str(tmp_docs_root),
        "--template", str(template),
    ]
    assert _run_main(args) == 0
    capsys.readouterr()
    rc = _run_main(args + ["--force"])
    assert rc == 0


def test_main_stdin_payload(valid_payload, tmp_docs_root, capsys):
    template = Path(__file__).resolve().parents[2] / "templates" / "auto-doc.md.template"
    rc = _run_main(
        ["--docs-root", str(tmp_docs_root), "--template", str(template)],
        stdin_text=json.dumps(valid_payload),
    )
    assert rc == 0


def test_main_invalid_payload(tmp_path, tmp_docs_root):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text("not json", encoding="utf-8")
    template = Path(__file__).resolve().parents[2] / "templates" / "auto-doc.md.template"
    rc = _run_main([
        "--payload", str(payload_file),
        "--docs-root", str(tmp_docs_root),
        "--template", str(template),
    ])
    assert rc == 1
