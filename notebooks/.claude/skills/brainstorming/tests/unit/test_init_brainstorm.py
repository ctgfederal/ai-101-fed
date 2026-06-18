"""Unit tests for scripts/init_brainstorm.py."""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_brainstorm import slugify, compute_path, main as ib_main


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_unicode():
    assert slugify("Café crash") == "cafe-crash"


def test_slugify_truncates():
    assert len(slugify("a" * 100)) == 60


def test_slugify_empty():
    with pytest.raises(ValueError):
        slugify("")


def test_slugify_only_punctuation():
    with pytest.raises(ValueError):
        slugify("!!!---")


def test_compute_path():
    p = compute_path(Path("/tmp/x"), "Hello World", date(2026, 2, 14))
    assert p == Path("/tmp/x/2026-02-14-hello-world.md")


def _run(argv):
    old = sys.argv
    sys.argv = ["init_brainstorm.py"] + argv
    try:
        return ib_main()
    finally:
        sys.argv = old


def test_main_creates_root(tmp_brainstorms_root, capsys):
    rc = _run(["--topic", "Test", "--brainstorms-root", str(tmp_brainstorms_root)])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert tmp_brainstorms_root.is_dir()
    assert out.endswith("-test.md")


def test_main_refuses_overwrite(tmp_brainstorms_root, capsys):
    tmp_brainstorms_root.mkdir(parents=True, exist_ok=True)
    target = tmp_brainstorms_root / f"{date.today().isoformat()}-test.md"
    target.write_text("existing", encoding="utf-8")
    rc = _run(["--topic", "Test", "--brainstorms-root", str(tmp_brainstorms_root)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "exists" in err


def test_main_force_allows(tmp_brainstorms_root, capsys):
    tmp_brainstorms_root.mkdir(parents=True, exist_ok=True)
    target = tmp_brainstorms_root / f"{date.today().isoformat()}-test.md"
    target.write_text("existing", encoding="utf-8")
    rc = _run(["--topic", "Test", "--brainstorms-root", str(tmp_brainstorms_root), "--force"])
    assert rc == 0


def test_main_custom_date(tmp_brainstorms_root, capsys):
    rc = _run(["--topic", "X", "--brainstorms-root", str(tmp_brainstorms_root), "--date", "2026-01-01"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert "2026-01-01-x.md" in out


def test_main_bad_date(tmp_brainstorms_root, capsys):
    # Note: argparse won't reject this; main() will catch via strptime
    rc = _run(["--topic", "X", "--brainstorms-root", str(tmp_brainstorms_root), "--date", "not-a-date"])
    assert rc == 1
