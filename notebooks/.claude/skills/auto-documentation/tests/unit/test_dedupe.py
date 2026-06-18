"""Unit tests for scripts/dedupe.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from dedupe import (
    is_duplicate,
    jaccard,
    tokenize_title,
    scope_hash,
    find_similar,
    main as dedupe_main,
)


# --- tokenize_title ---

def test_tokenize_drops_stopwords():
    tokens = tokenize_title("The order of payment for the user")
    assert "the" not in tokens
    assert "of" not in tokens
    assert "for" not in tokens
    assert "order" in tokens
    assert "payment" in tokens
    assert "user" in tokens


def test_tokenize_lowercases():
    tokens = tokenize_title("Stripe Webhook Retry")
    assert tokens == {"stripe", "webhook", "retry"}


def test_tokenize_handles_punctuation():
    tokens = tokenize_title("admin/non-admin: user posts")
    assert "admin" in tokens
    assert "non" in tokens
    assert "posts" in tokens


# --- jaccard ---

def test_jaccard_identical_sets():
    assert jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_disjoint_sets():
    assert jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_partial():
    # |∩|=1, |∪|=3 → 1/3
    assert abs(jaccard({"a", "b"}, {"a", "c"}) - (1 / 3)) < 1e-9


def test_jaccard_both_empty():
    assert jaccard(set(), set()) == 0.0


# --- scope_hash ---

def test_scope_hash_same_scope_same_hash():
    assert scope_hash("UserPostController#update") == scope_hash("UserPostController#update")


def test_scope_hash_normalizes_whitespace():
    assert scope_hash("UserPost Controller#update") == scope_hash("UserPostController#update")


def test_scope_hash_strips_punctuation():
    # "Foo.Bar" and "FooBar" should hash the same after normalization
    assert scope_hash("Foo.Bar") == scope_hash("FooBar")


def test_scope_hash_empty_returns_empty():
    assert scope_hash("") == ""


# --- is_duplicate ---

def _doc(category="business-rule", title="Some title", tags=None, scope="ModuleA"):
    return {
        "category": category,
        "title": title,
        "tags": tags if tags is not None else ["a", "b"],
        "scope": scope,
    }


def test_duplicate_when_scope_matches_and_category_matches_with_tag_overlap():
    cand = _doc(scope="UserPostController#update", tags=["auth", "admin", "permissions"])
    existing = _doc(scope="UserPostController#update", tags=["auth", "permissions", "rbac"])
    # tag overlap = 2/4 = 0.5 >= 0.3, scope matches, category matches
    assert is_duplicate(cand, existing) is True


def test_not_duplicate_when_category_differs():
    cand = _doc(category="business-rule", scope="X", tags=["a"])
    existing = _doc(category="technical-pattern", scope="X", tags=["a"])
    assert is_duplicate(cand, existing) is False


def test_duplicate_when_title_similarity_high():
    cand = _doc(title="Admin edit policy for user posts", tags=["a", "b"], scope="X")
    existing = _doc(title="Admin edit policy for user posts and comments", tags=["c"], scope="Y")
    # tokens cand={admin,edit,policy,user,posts} ex={admin,edit,policy,user,posts,comments}
    # |∩|=5, |∪|=6 → ~0.83 >= 0.6
    assert is_duplicate(cand, existing) is True


def test_not_duplicate_when_only_category_matches():
    cand = _doc(title="Refund window policy", tags=["refund"], scope="OrderController")
    existing = _doc(title="User signup flow", tags=["signup"], scope="UserController")
    assert is_duplicate(cand, existing) is False


def test_duplicate_when_tag_overlap_high_and_some_title_overlap():
    cand = _doc(
        title="Stripe webhook retry behavior",
        tags=["stripe", "webhook", "retry", "idempotency"],
        scope="A",
    )
    existing = _doc(
        title="Stripe webhook retry timing window",
        tags=["stripe", "webhook", "retry", "timing"],
        scope="B",
    )
    # tag overlap = 3/5 = 0.6 >= 0.5; title sim ~ 4/6 = 0.67 >= 0.4
    assert is_duplicate(cand, existing) is True


# --- find_similar against a fixture archive ---

def test_find_similar_in_real_archive(tmp_docs_root, valid_payload):
    # write an existing doc that should match
    existing = tmp_docs_root / "business-rule" / "2026-05-01-existing.md"
    existing.write_text("""---
title: "Admins can edit any user post; non-admins only their own"
category: business-rule
date: 2026-05-01
tags:
  - authorization
  - permissions
  - admin
scope: "UserPostController#update"
source: "earlier discovery"
---

# Admins can edit any user post; non-admins only their own

## Description
x
## Why
x
## Examples
x
## Related
x
""", encoding="utf-8")
    hits = find_similar(valid_payload, tmp_docs_root)
    assert len(hits) == 1
    assert hits[0] == existing


def test_find_similar_empty_archive(tmp_docs_root, valid_payload):
    hits = find_similar(valid_payload, tmp_docs_root)
    assert hits == []


# --- main ---

def _run_main(argv):
    old = sys.argv
    sys.argv = ["dedupe.py"] + argv
    try:
        return dedupe_main()
    finally:
        sys.argv = old


def test_main_prints_json(tmp_path, tmp_docs_root, valid_payload, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(valid_payload), encoding="utf-8")
    rc = _run_main(["--payload", str(payload_file), "--docs-root", str(tmp_docs_root)])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    parsed = json.loads(out)
    assert "is_duplicate" in parsed
    assert "similar" in parsed
    assert parsed["is_duplicate"] is False  # empty archive


def test_main_invalid_payload(tmp_path, tmp_docs_root):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    rc = _run_main(["--payload", str(bad), "--docs-root", str(tmp_docs_root)])
    assert rc == 1


def test_main_payload_not_found(tmp_path, tmp_docs_root):
    rc = _run_main(["--payload", str(tmp_path / "nope.json"), "--docs-root", str(tmp_docs_root)])
    assert rc == 1
