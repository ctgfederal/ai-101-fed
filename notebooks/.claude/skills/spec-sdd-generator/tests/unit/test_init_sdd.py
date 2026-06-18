"""Unit tests for scripts/init_sdd.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from init_sdd import main as ip


def _run(*a):
    old = sys.argv
    sys.argv = ["init_sdd.py", *a]
    try:
        return ip()
    finally:
        sys.argv = old


def test_creates_target(tmp_path, capsys):
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "s"))
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out.endswith("/feat-1/SDD.md")


def test_invalid_name(tmp_path):
    rc = _run("--feature", "Bad_Name", "--specs-root", str(tmp_path / "s"))
    assert rc == 1


def test_refuses_existing(tmp_path):
    fd = tmp_path / "s" / "feat-1"
    fd.mkdir(parents=True)
    (fd / "SDD.md").write_text("x")
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "s"))
    assert rc == 1


def test_force(tmp_path):
    fd = tmp_path / "s" / "feat-1"
    fd.mkdir(parents=True)
    (fd / "SDD.md").write_text("x")
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "s"), "--force")
    assert rc == 0
