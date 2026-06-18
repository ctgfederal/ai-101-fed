"""Unit tests for scripts/update_status.py."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from update_status import main as us_main, update_row


def _run(*args):
    old = sys.argv
    sys.argv = ["update_status.py", *args]
    try:
        return us_main()
    finally:
        sys.argv = old


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


def test_updates_prd(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    rc = _run(
        "--feature", "feature-search",
        "--specs-root", str(specs_root),
        "--doc", "prd",
        "--status", "approved",
    )
    assert rc == 0
    body = (specs_root / "feature-search" / "README.md").read_text()
    assert "| PRD | approved |" in body
    assert "| SDD | draft |" in body
    assert "| PLAN | draft |" in body


def test_updates_sdd_and_plan(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--doc", "sdd", "--status", "approved")
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--doc", "plan", "--status", "deprecated")
    body = (specs_root / "feature-search" / "README.md").read_text()
    assert "| SDD | approved |" in body
    assert "| PLAN | deprecated |" in body


def test_invalid_status_rejected(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    with pytest.raises(SystemExit):
        _run("--feature", "feature-search", "--specs-root", str(specs_root),
             "--doc", "prd", "--status", "wip")


def test_invalid_doc_rejected(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    with pytest.raises(SystemExit):
        _run("--feature", "feature-search", "--specs-root", str(specs_root),
             "--doc", "readme", "--status", "approved")


def test_missing_readme_errors(tmp_path, capsys):
    specs_root = tmp_path / "specs"
    specs_root.mkdir()
    rc = _run("--feature", "no-such", "--specs-root", str(specs_root),
              "--doc", "prd", "--status", "approved")
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_update_row_pure(tmp_path):
    text = (
        "## Status\n\n"
        "| Doc | Status | Last Update |\n"
        "|---|---|---|\n"
        "| PRD | draft | 2026-01-01 |\n"
        "| SDD | draft | 2026-01-01 |\n"
        "| PLAN | draft | 2026-01-01 |\n"
    )
    new = update_row(text, "prd", "approved", "2026-05-08")
    assert "| PRD | approved | 2026-05-08 |" in new
    assert "| SDD | draft | 2026-01-01 |" in new


def test_update_row_missing_raises():
    text = "## Status\n\nno table here.\n"
    with pytest.raises(ValueError):
        update_row(text, "prd", "approved", "2026-05-08")


def test_update_preserves_other_sections(tmp_path):
    specs_root = tmp_path / "specs"
    _init(specs_root)
    before = (specs_root / "feature-search" / "README.md").read_text()
    _run("--feature", "feature-search", "--specs-root", str(specs_root),
         "--doc", "prd", "--status", "approved")
    after = (specs_root / "feature-search" / "README.md").read_text()
    # Other sections preserved.
    for header in ["## Steering References", "## Decision Log Snippets",
                   "## Phase Notes", "## Learnings", "## Open Questions"]:
        assert header in after, f"header lost after update: {header}"
