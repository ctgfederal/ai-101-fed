"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import find_section, main as vo_main


def test_find_section_present():
    text = (
        "# Decisions Log\n\n"
        "## Feature Search — Build Decisions (2026-02-14)\n"
        "body line one\n"
        "body line two\n"
    )
    sec = find_section(text, "Feature Search")
    assert sec is not None
    assert "body line one" in sec


def test_find_section_absent():
    text = "# Decisions Log\n\nNothing else.\n"
    assert find_section(text, "Feature Search") is None


def test_find_section_picks_correct():
    text = (
        "## Other Feature — Build Decisions (2026-01-01)\n"
        "wrong section\n"
        "## Feature Search — Build Decisions (2026-02-14)\n"
        "right section\n"
    )
    sec = find_section(text, "Feature Search")
    assert "right section" in sec
    assert "wrong section" not in sec


def _run(*args):
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_missing_log(tmp_path):
    rc = _run("--log", str(tmp_path / "no.md"), "--feature", "F")
    assert rc == 1


def test_main_missing_feature(tmp_path):
    log = tmp_path / "log.md"
    log.write_text("# Decisions Log\n")
    rc = _run("--log", str(log), "--feature", "Missing")
    assert rc == 1


def test_main_happy(tmp_path):
    log = tmp_path / "log.md"
    log.write_text(
        "## Feature Search — Build Decisions (2026-02-14)\n\n"
        "### Auto-Applied (Federal Mandates)\n"
        "| ID | Category | Decision | Mandated Answer | Citation |\n"
        "|---|---|---|---|---|\n"
        "| D-001 | Security | TLS | TLS 1.2+ | NIST 800-52r2 |\n\n"
        "### Architecture\n"
        "#### D-002: Pattern\n"
        "**Decision**: Layered.\n"
    )
    rc = _run("--log", str(log), "--feature", "Feature Search")
    assert rc == 0


def test_main_missing_auto_applied_subsection(tmp_path):
    log = tmp_path / "log.md"
    log.write_text(
        "## Feature Search — Build Decisions (2026-02-14)\n\n"
        "### Architecture\n"
        "#### D-001: Pattern\n"
        "**Decision**: Layered.\n"
    )
    rc = _run("--log", str(log), "--feature", "Feature Search")
    assert rc == 1
