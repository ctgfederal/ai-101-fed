"""Unit tests for scripts/search_solutions.py.

Builds a fixture archive in tmp_path and asserts each filter returns the right files.
Hard-codes expected paths — does NOT reuse the search logic.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from search_solutions import search


def _write(p: Path, frontmatter: str, body: str = "body") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")


@pytest.fixture
def archive(tmp_path):
    """Three solution files across two categories with distinct fields."""
    root = tmp_path / "solutions"

    _write(
        root / "performance-issues" / "2026-02-14-n-plus-one.md",
        'title: "N+1 in briefs"\n'
        "category: performance-issues\n"
        "date: 2026-02-14\n"
        "tags:\n  - activerecord\n  - n+1\n"
        'module: "BriefGenerator"\n'
        'symptom: "12s render"\n'
        'root_cause: "lazy load"\n',
        body="## Symptom\n12s render with N+1 queries.\n",
    )

    _write(
        root / "build-errors" / "2026-01-20-webpack-fail.md",
        'title: "Webpack OOM"\n'
        "category: build-errors\n"
        "date: 2026-01-20\n"
        "tags: [webpack, memory]\n"
        'module: "AssetPipeline"\n'
        'symptom: "JavaScript heap out of memory"\n'
        'root_cause: "default node heap too small"\n',
        body="## Symptom\nWebpack OOM.\n",
    )

    _write(
        root / "performance-issues" / "2026-01-15-slow-search.md",
        'title: "Slow search query"\n'
        "category: performance-issues\n"
        "date: 2026-01-15\n"
        "tags:\n  - postgres\n  - index\n"
        'module: "SearchService"\n'
        'symptom: "search query exceeded statement timeout"\n'
        'root_cause: "missing trigram index"\n',
        body="## Symptom\nSlow search.\n",
    )

    return root


def _names(hits):
    return sorted(p.name for p, _ in hits)


def test_search_by_tag(archive):
    hits = search(archive, tag="n+1")
    assert _names(hits) == ["2026-02-14-n-plus-one.md"]


def test_search_by_tag_inline_list(archive):
    hits = search(archive, tag="webpack")
    assert _names(hits) == ["2026-01-20-webpack-fail.md"]


def test_search_by_tag_no_match(archive):
    assert search(archive, tag="missing-tag") == []


def test_search_by_module(archive):
    hits = search(archive, module="BriefGenerator")
    assert _names(hits) == ["2026-02-14-n-plus-one.md"]


def test_search_by_module_exact(archive):
    # partial match should NOT hit
    assert search(archive, module="Brief") == []


def test_search_by_symptom_no_match(archive):
    """A keyword that appears in neither frontmatter nor any body returns nothing."""
    hits = search(archive, symptom="totally-absent-keyword-xyz")
    assert hits == []


def test_search_by_symptom_substring(archive):
    hits = search(archive, symptom="out of memory")
    assert _names(hits) == ["2026-01-20-webpack-fail.md"]


def test_search_by_symptom_body_match(archive):
    # "N+1 queries" appears in the body Symptom section, not in frontmatter symptom
    hits = search(archive, symptom="N+1 queries")
    assert _names(hits) == ["2026-02-14-n-plus-one.md"]


def test_search_by_category(archive):
    hits = search(archive, category="performance-issues")
    assert _names(hits) == ["2026-01-15-slow-search.md", "2026-02-14-n-plus-one.md"]


def test_search_empty_root(tmp_path):
    assert search(tmp_path / "nonexistent", tag="anything") == []


def test_search_skips_files_without_frontmatter(archive):
    """A stray file without frontmatter should not blow up the search."""
    (archive / "performance-issues" / "stray.md").write_text("no frontmatter\n", encoding="utf-8")
    hits = search(archive, tag="n+1")
    assert _names(hits) == ["2026-02-14-n-plus-one.md"]
