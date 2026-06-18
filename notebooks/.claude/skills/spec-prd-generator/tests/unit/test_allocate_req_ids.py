"""Unit tests for scripts/allocate_req_ids.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from allocate_req_ids import find_max, allocate, main as ar_main


def test_find_max_empty_root(tmp_path):
    assert find_max(tmp_path / "no") == 0


def test_find_max_no_prds(tmp_path):
    (tmp_path / "specs").mkdir()
    assert find_max(tmp_path / "specs") == 0


def test_find_max_multiple_prds(tmp_path):
    specs = tmp_path / "specs"
    (specs / "a").mkdir(parents=True)
    (specs / "b").mkdir(parents=True)
    (specs / "a" / "PRD.md").write_text("REQ-005 stuff REQ-007")
    (specs / "b" / "PRD.md").write_text("REQ-099")
    assert find_max(specs) == 99


def test_allocate():
    assert allocate(1, 3) == ["REQ-001", "REQ-002", "REQ-003"]


def test_allocate_widens():
    assert allocate(998, 3)[0] == "REQ-0998"


def test_allocate_zero_count():
    with pytest.raises(ValueError):
        allocate(1, 0)


def _run(*args):
    old = sys.argv
    sys.argv = ["allocate_req_ids.py", *args]
    try:
        return ar_main()
    finally:
        sys.argv = old


def test_main_empty_root(tmp_path, capsys):
    rc = _run("--specs-root", str(tmp_path / "no"), "--count", "3")
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "REQ-001 REQ-002 REQ-003"


def test_main_zero_count(tmp_path):
    rc = _run("--specs-root", str(tmp_path), "--count", "0")
    assert rc == 1
