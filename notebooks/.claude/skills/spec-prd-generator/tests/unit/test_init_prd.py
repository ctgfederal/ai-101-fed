"""Unit tests for scripts/init_prd.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_prd import main as ip_main


def _run(*args):
    old = sys.argv
    sys.argv = ["init_prd.py", *args]
    try:
        return ip_main()
    finally:
        sys.argv = old


def test_creates_dir(tmp_path, capsys):
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"))
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out.endswith("/feat-1/PRD.md")
    assert (tmp_path / "specs" / "feat-1").is_dir()


def test_invalid_feature_name(tmp_path):
    rc = _run("--feature", "Feat_1", "--specs-root", str(tmp_path / "specs"))
    assert rc == 1


def test_refuses_existing(tmp_path):
    feature_dir = tmp_path / "specs" / "feat-1"
    feature_dir.mkdir(parents=True)
    (feature_dir / "PRD.md").write_text("existing")
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"))
    assert rc == 1


def test_force_allows(tmp_path):
    feature_dir = tmp_path / "specs" / "feat-1"
    feature_dir.mkdir(parents=True)
    (feature_dir / "PRD.md").write_text("existing")
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"), "--force")
    assert rc == 0
