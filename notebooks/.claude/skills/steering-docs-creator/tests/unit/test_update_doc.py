"""Unit tests for scripts/update_doc.py."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_steering import main as init_main
from update_doc import main as ud_main, replace_section


def _scaffold(root: Path) -> None:
    old = sys.argv
    sys.argv = ["init_steering.py", "--steering-root", str(root)]
    try:
        rc = init_main()
        assert rc == 0
    finally:
        sys.argv = old


def _run(*args: str) -> int:
    old = sys.argv
    sys.argv = ["update_doc.py", *args]
    try:
        return ud_main()
    finally:
        sys.argv = old


def test_replaces_existing_section(tmp_steering_root: Path, valid_section_body: str) -> None:
    _scaffold(tmp_steering_root)
    rc = _run(
        "--steering-root", str(tmp_steering_root),
        "--doc", "tech",
        "--section", "Tech Stack",
        "--body", valid_section_body,
    )
    assert rc == 0
    text = (tmp_steering_root / "tech.md").read_text()
    assert "Python" in text
    # heading itself preserved
    assert "## Tech Stack" in text
    # next section not eaten
    assert "## Conventions" in text


def test_refuses_missing_section(tmp_steering_root: Path) -> None:
    _scaffold(tmp_steering_root)
    rc = _run(
        "--steering-root", str(tmp_steering_root),
        "--doc", "tech",
        "--section", "Nonexistent Section",
        "--body", "anything",
    )
    assert rc == 1


def test_force_appends_missing_section(tmp_steering_root: Path) -> None:
    _scaffold(tmp_steering_root)
    rc = _run(
        "--steering-root", str(tmp_steering_root),
        "--doc", "tech",
        "--section", "Custom Add",
        "--body", "appended body content",
        "--force",
    )
    assert rc == 0
    text = (tmp_steering_root / "tech.md").read_text()
    assert "## Custom Add" in text
    assert "appended body content" in text


def test_stdin_body(tmp_steering_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _scaffold(tmp_steering_root)
    body = "Body via stdin\nLine 2\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(body))
    rc = _run(
        "--steering-root", str(tmp_steering_root),
        "--doc", "product",
        "--section", "Mission",
        "--body", "-",
    )
    assert rc == 0
    text = (tmp_steering_root / "product.md").read_text()
    assert "Body via stdin" in text


def test_replace_section_preserves_heading() -> None:
    text = (
        "# Title\n\n"
        "## A\n\nold body of A\n\n"
        "## B\n\nbody of B\n"
    )
    new_text, found = replace_section(text, "A", "fresh body of A")
    assert found is True
    assert "## A\n" in new_text
    assert "fresh body of A" in new_text
    assert "old body of A" not in new_text
    assert "## B\n" in new_text
    assert "body of B" in new_text


def test_replace_section_at_eof() -> None:
    text = "## A\n\nold\n\n## Z\n\nlast section\n"
    new_text, found = replace_section(text, "Z", "new last")
    assert found is True
    assert "## Z" in new_text
    assert "new last" in new_text
    assert "last section" not in new_text
    # earlier section preserved
    assert "## A" in new_text
    assert "old" in new_text


def test_replace_section_not_found_returns_false() -> None:
    text = "## A\nbody\n"
    new_text, found = replace_section(text, "NotThere", "x")
    assert found is False
    assert new_text == text


def test_empty_body_rejected(tmp_steering_root: Path) -> None:
    _scaffold(tmp_steering_root)
    rc = _run(
        "--steering-root", str(tmp_steering_root),
        "--doc", "tech",
        "--section", "Tech Stack",
        "--body", "   \n",
    )
    assert rc == 1


def test_missing_doc_file(tmp_path: Path) -> None:
    rc = _run(
        "--steering-root", str(tmp_path),
        "--doc", "tech",
        "--section", "Tech Stack",
        "--body", "x",
    )
    assert rc == 1
