"""Unit tests for scripts/init_steering.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_steering import DOCS, main as init_main


def _run(*args: str) -> int:
    old = sys.argv
    sys.argv = ["init_steering.py", *args]
    try:
        return init_main()
    finally:
        sys.argv = old


def test_scaffolds_all_four(tmp_steering_root: Path) -> None:
    rc = _run("--steering-root", str(tmp_steering_root))
    assert rc == 0
    for doc in DOCS:
        assert (tmp_steering_root / f"{doc}.md").is_file()


def test_only_one_kind(tmp_steering_root: Path) -> None:
    rc = _run("--steering-root", str(tmp_steering_root), "--only", "tech")
    assert rc == 0
    assert (tmp_steering_root / "tech.md").is_file()
    for other in ("product", "structure", "roadmap"):
        assert not (tmp_steering_root / f"{other}.md").exists()


def test_idempotent_no_force(tmp_steering_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc1 = _run("--steering-root", str(tmp_steering_root))
    assert rc1 == 0
    # capture content to compare
    before = (tmp_steering_root / "tech.md").read_text()
    # mutate to ensure idempotent re-run does NOT overwrite
    (tmp_steering_root / "tech.md").write_text("MUTATED\n")
    rc2 = _run("--steering-root", str(tmp_steering_root))
    assert rc2 == 0
    after = (tmp_steering_root / "tech.md").read_text()
    assert after == "MUTATED\n", "re-run without --force should not overwrite"
    # other files should still exist (and not be the mutated one)
    assert (tmp_steering_root / "product.md").read_text() != "MUTATED\n"
    _ = before  # silence unused-warning


def test_force_overwrites(tmp_steering_root: Path) -> None:
    rc1 = _run("--steering-root", str(tmp_steering_root))
    assert rc1 == 0
    (tmp_steering_root / "tech.md").write_text("MUTATED\n")
    rc2 = _run("--steering-root", str(tmp_steering_root), "--force")
    assert rc2 == 0
    after = (tmp_steering_root / "tech.md").read_text()
    assert after != "MUTATED\n", "--force should overwrite"
    assert "Tech Stack" in after


def test_creates_root_if_missing(tmp_path: Path) -> None:
    root = tmp_path / "does-not-exist-yet"
    rc = _run("--steering-root", str(root))
    assert rc == 0
    assert root.is_dir()
    for doc in DOCS:
        assert (root / f"{doc}.md").is_file()
