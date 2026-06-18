"""Unit tests for scripts/append_phase_note.py."""
import io
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from append_phase_note import insert_phase_block, main as ap_main


def _run(*args, stdin: str | None = None):
    old_argv, old_stdin = sys.argv, sys.stdin
    sys.argv = ["append_phase_note.py", *args]
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        return ap_main()
    finally:
        sys.argv = old_argv
        sys.stdin = old_stdin


def _init(specs_root, feature="feature-search"):
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "init_readme.py"),
            "--feature", feature,
            "--specs-root", str(specs_root),
        ],
        check=True,
        capture_output=True,
    )


def test_append_first_phase(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    rc = _run(
        "--feature", "feature-search",
        "--specs-root", str(specs_root),
        "--phase", "1",
        "--name", "Foundation",
        "--note", "Spec assumed cache hit; first run was a cold miss.",
    )
    assert rc == 0
    body = (specs_root / "feature-search" / "README.md").read_text()
    assert "### Phase 1: Foundation" in body
    assert "Spec assumed cache hit" in body


def test_append_in_monotonic_order(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--phase", "3", "--name", "Integration", "--note", "Note 3.")
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--phase", "1", "--name", "Foundation", "--note", "Note 1.")
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--phase", "2", "--name", "Core", "--note", "Note 2.")
    body = (specs_root / "feature-search" / "README.md").read_text()
    p1 = body.index("### Phase 1: Foundation")
    p2 = body.index("### Phase 2: Core")
    p3 = body.index("### Phase 3: Integration")
    assert p1 < p2 < p3


def test_duplicate_phase_rejected(tmp_path, capsys):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--phase", "1", "--name", "Foundation", "--note", "Note 1.")
    rc = _run("--feature", "feature-search", "--specs-root", str(specs_root),
              "--phase", "1", "--name", "Foundation Again", "--note", "Note 1b.")
    assert rc == 1
    assert "already present" in capsys.readouterr().err


def test_stdin_note(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    rc = _run(
        "--feature", "feature-search",
        "--specs-root", str(specs_root),
        "--phase", "1",
        "--name", "Foundation",
        stdin="Note from stdin pipe.",
    )
    assert rc == 0
    body = (specs_root / "feature-search" / "README.md").read_text()
    assert "Note from stdin pipe." in body


def test_non_positive_phase_rejected(tmp_path, capsys):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    rc = _run("--feature", "feature-search", "--specs-root", str(specs_root),
              "--phase", "0", "--name", "Bad", "--note", "...")
    assert rc == 1
    assert "must be positive" in capsys.readouterr().err


def test_empty_note_rejected(tmp_path, capsys):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    rc = _run(
        "--feature", "feature-search",
        "--specs-root", str(specs_root),
        "--phase", "1",
        "--name", "Foundation",
        stdin="",
    )
    assert rc == 1
    assert "empty" in capsys.readouterr().err


def test_missing_readme(tmp_path, capsys):
    specs_root = tmp_path / "specs"
    specs_root.mkdir()
    rc = _run("--feature", "no-feat", "--specs-root", str(specs_root),
              "--phase", "1", "--name", "Foundation", "--note", "x")
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_insert_phase_block_pure():
    text = (
        "## Phase Notes\n"
        "\n"
        "_(append `### Phase N: <name>` blocks via `append_phase_note.py`.)_\n"
        "\n"
        "## Learnings\n"
    )
    out = insert_phase_block(text, 1, "Foundation", "First note.", "2026-05-08")
    assert "### Phase 1: Foundation" in out
    assert "First note." in out
    # Trailing section preserved.
    assert "## Learnings" in out


def test_insert_phase_block_missing_section_raises():
    text = "## Status\n\nno phase notes here.\n"
    with pytest.raises(ValueError):
        insert_phase_block(text, 1, "Foundation", "x", "2026-05-08")
