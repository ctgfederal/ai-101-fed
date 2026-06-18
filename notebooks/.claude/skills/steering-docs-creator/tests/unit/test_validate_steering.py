"""Unit tests for scripts/validate_steering.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_steering import main as init_main
from validate_steering import main as vs_main


def _run_init(*args: str) -> int:
    old = sys.argv
    sys.argv = ["init_steering.py", *args]
    try:
        return init_main()
    finally:
        sys.argv = old


def _run_vs(*args: str) -> int:
    old = sys.argv
    sys.argv = ["validate_steering.py", *args]
    try:
        return vs_main()
    finally:
        sys.argv = old


def test_passes_after_scaffold(tmp_steering_root: Path) -> None:
    assert _run_init("--steering-root", str(tmp_steering_root)) == 0
    assert _run_vs("--steering-root", str(tmp_steering_root)) == 0


def test_fails_when_doc_missing(tmp_steering_root: Path) -> None:
    assert _run_init("--steering-root", str(tmp_steering_root)) == 0
    (tmp_steering_root / "roadmap.md").unlink()
    assert _run_vs("--steering-root", str(tmp_steering_root)) == 1


def test_fails_when_section_missing(tmp_steering_root: Path) -> None:
    assert _run_init("--steering-root", str(tmp_steering_root)) == 0
    target = tmp_steering_root / "tech.md"
    text = target.read_text()
    text = text.replace("## Observability", "## NotObservability")
    target.write_text(text)
    assert _run_vs("--steering-root", str(tmp_steering_root)) == 1


def test_fails_on_missing_root(tmp_path: Path) -> None:
    assert _run_vs("--steering-root", str(tmp_path / "nope")) == 1
