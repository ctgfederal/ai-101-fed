"""Shared pytest fixtures for auto-documentation tests."""
import sys
from datetime import date
from pathlib import Path

import pytest

# make scripts/ importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def tmp_docs_root(tmp_path):
    """A clean .claude/docs/auto/ tree with category folders."""
    root = tmp_path / "auto"
    root.mkdir()
    for cat in ("business-rule", "technical-pattern", "service-interface", "domain-rule"):
        (root / cat).mkdir()
    return root


@pytest.fixture
def valid_payload():
    """A complete, valid JSON payload for write_doc.py."""
    return {
        "title": "Admins can edit any user post; non-admins only their own",
        "category": "business-rule",
        "date": date.today().isoformat(),
        "tags": ["authorization", "permissions", "admin", "user-posts"],
        "scope": "UserPostController#update",
        "source": "discovery during /implement on USR-014",
        "description_body": "Authorization rule for edits on `UserPost`.",
        "why_body": "Mirrors business policy from the moderation runbook.",
        "examples_body": "```ruby\ncurrent_user.admin? || post.user_id == current_user.id\n```",
        "related_body": "- `business-rule/2026-04-12-admin-elevation-policy.md`",
    }


@pytest.fixture
def invalid_payload(valid_payload):
    """Same shape but with a missing required key."""
    p = dict(valid_payload)
    del p["scope"]
    return p


@pytest.fixture
def fixture_doc_file(tmp_path):
    """Write a sample auto-doc file and return its path."""
    f = tmp_path / "sample.md"
    f.write_text("""---
title: "Sample admin edit rule"
category: business-rule
date: 2026-05-08
tags:
  - authorization
  - admin
scope: "UserPostController#update"
source: "discovery"
---

# Sample admin edit rule

## Description
Some description.

## Why
Some reason.

## Examples
Some example.

## Related
None.
""", encoding="utf-8")
    return f
