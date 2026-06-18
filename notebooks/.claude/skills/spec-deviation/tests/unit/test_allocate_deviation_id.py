"""Unit tests for scripts/allocate_deviation_id.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from allocate_deviation_id import (
    find_max_dev_id,
    allocate,
    main as alloc_main,
)


def test_find_max_empty_root(tmp_path):
    assert find_max_dev_id(tmp_path) == 0


def test_find_max_no_specs_dir(tmp_path):
    assert find_max_dev_id(tmp_path / "nope") == 0


def test_find_max_single_spec(tmp_path):
    spec_dir = tmp_path / "feature-a"
    spec_dir.mkdir()
    (spec_dir / "SDD.md").write_text("### DEV-007 some block\n")
    assert find_max_dev_id(tmp_path) == 7


def test_find_max_multiple_specs(tmp_path):
    a = tmp_path / "a"
    a.mkdir()
    (a / "SDD.md").write_text("### DEV-001\n### DEV-002\n")
    b = tmp_path / "b"
    b.mkdir()
    (b / "SDD.md").write_text("### DEV-014 stuff\n")
    c = tmp_path / "c"
    c.mkdir()
    (c / "SDD.md").write_text("# nothing here\n")
    assert find_max_dev_id(tmp_path) == 14


def test_find_max_handles_3plus_digit_ids(tmp_path):
    spec = tmp_path / "feature"
    spec.mkdir()
    (spec / "SDD.md").write_text("### DEV-1234 large\n### DEV-005 small\n")
    assert find_max_dev_id(tmp_path) == 1234


def test_allocate_first_id(tmp_path):
    ids = allocate(tmp_path, 1)
    assert ids == ["DEV-001"]


def test_allocate_after_existing(tmp_path):
    spec = tmp_path / "feature"
    spec.mkdir()
    (spec / "SDD.md").write_text("### DEV-009 prior\n")
    ids = allocate(tmp_path, 1)
    assert ids == ["DEV-010"]


def test_allocate_batch(tmp_path):
    spec = tmp_path / "feature"
    spec.mkdir()
    (spec / "SDD.md").write_text("### DEV-002 prior\n")
    ids = allocate(tmp_path, 3)
    assert ids == ["DEV-003", "DEV-004", "DEV-005"]


def test_allocate_zero_count_raises(tmp_path):
    with pytest.raises(ValueError):
        allocate(tmp_path, 0)


def test_allocate_negative_count_raises(tmp_path):
    with pytest.raises(ValueError):
        allocate(tmp_path, -1)


def test_allocate_zero_padding_at_999(tmp_path):
    spec = tmp_path / "feature"
    spec.mkdir()
    (spec / "SDD.md").write_text("### DEV-999\n")
    ids = allocate(tmp_path, 1)
    # zero-pad to 3 still works at 4-digit edge
    assert ids == ["DEV-1000"]


def _run(*args):
    old = sys.argv
    sys.argv = ["allocate_deviation_id.py", *args]
    try:
        return alloc_main()
    finally:
        sys.argv = old


def test_main_emits_one_per_line(tmp_path, capsys):
    rc = _run("--specs-root", str(tmp_path), "--count", "3")
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == ["DEV-001", "DEV-002", "DEV-003"]


def test_main_count_zero_returns_error(tmp_path):
    rc = _run("--specs-root", str(tmp_path), "--count", "0")
    assert rc == 1


def test_main_default_count_is_one(tmp_path, capsys):
    rc = _run("--specs-root", str(tmp_path))
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == ["DEV-001"]
