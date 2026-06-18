"""Unit tests for scripts/allocate_task_ids.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from allocate_task_ids import find_max, allocate, main as am


def test_find_max_empty(tmp_path):
    assert find_max(tmp_path / "no") == 0


def test_find_max_walks_specs(tmp_path):
    specs = tmp_path / "specs"
    (specs / "a").mkdir(parents=True)
    (specs / "b").mkdir(parents=True)
    (specs / "a" / "PLAN.md").write_text("T-007 T-002")
    (specs / "b" / "PLAN.md").write_text("T-099")
    assert find_max(specs) == 99


def test_allocate():
    assert allocate(1, 2) == ["T-001", "T-002"]


def test_allocate_zero():
    with pytest.raises(ValueError):
        allocate(1, 0)


def _run(*a):
    old = sys.argv
    sys.argv = ["allocate_task_ids.py", *a]
    try:
        return am()
    finally:
        sys.argv = old


def test_main_empty(tmp_path, capsys):
    rc = _run("--specs-root", str(tmp_path), "--count", "2")
    assert rc == 0
    assert capsys.readouterr().out.strip() == "T-001 T-002"


def test_main_zero(tmp_path):
    assert _run("--specs-root", str(tmp_path), "--count", "0") == 1
