"""Unit tests for scripts/allocate_ids.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from allocate_ids import find_max, allocate, main as ai_main


def test_find_max_empty():
    assert find_max("") == 0


def test_find_max_no_ids():
    assert find_max("# Decisions Log\n\nNo ids here.") == 0


def test_find_max_single():
    assert find_max("ref D-007 here") == 7


def test_find_max_multiple():
    assert find_max("D-001 ... D-099 ... D-042") == 99


def test_find_max_padding_irrelevant():
    assert find_max("D-001 D-1000") == 1000


def test_allocate_starts_at_one():
    assert allocate("", 3) == ["D-001", "D-002", "D-003"]


def test_allocate_continues():
    assert allocate("D-100", 2) == ["D-101", "D-102"]


def test_allocate_zero_count():
    with pytest.raises(ValueError):
        allocate("", 0)


def test_allocate_negative():
    with pytest.raises(ValueError):
        allocate("", -1)


def test_allocate_widens_to_4_digits():
    out = allocate("D-998", 5)
    # 999 still fits in 3 digits; 1000+ needs 4
    assert out[0] == "D-0999"
    assert out[1] == "D-1000"


def _run(*args):
    old = sys.argv
    sys.argv = ["allocate_ids.py", *args]
    try:
        return ai_main()
    finally:
        sys.argv = old


def test_main_missing_log(tmp_path, capsys):
    rc = _run("--log", str(tmp_path / "no.md"), "--count", "3")
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "D-001 D-002 D-003"


def test_main_with_existing(tmp_path, capsys):
    log = tmp_path / "log.md"
    log.write_text("D-040 D-041 D-005")
    rc = _run("--log", str(log), "--count", "2")
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "D-042 D-043"


def test_main_zero_count(tmp_path):
    rc = _run("--log", str(tmp_path / "x.md"), "--count", "0")
    assert rc == 1
