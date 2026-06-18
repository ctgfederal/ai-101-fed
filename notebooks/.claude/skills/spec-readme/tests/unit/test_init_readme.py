"""Unit tests for scripts/init_readme.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_readme import derive_title, main as ir_main, render


def _run(*args):
    old = sys.argv
    sys.argv = ["init_readme.py", *args]
    try:
        return ir_main()
    finally:
        sys.argv = old


def test_creates_file(tmp_path, capsys):
    rc = _run("--feature", "feature-search", "--specs-root", str(tmp_path / "specs"))
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out.endswith("/feature-search/README.md")
    assert (tmp_path / "specs" / "feature-search" / "README.md").is_file()


def test_populated_placeholders(tmp_path):
    _run("--feature", "feature-search", "--specs-root", str(tmp_path / "specs"))
    body = (tmp_path / "specs" / "feature-search" / "README.md").read_text()
    assert "{{FEATURE}}" not in body
    assert "{{FEATURE_TITLE}}" not in body
    assert "{{CREATED}}" not in body
    assert "Feature Search" in body
    assert "feature-search" in body


def test_invalid_feature_name(tmp_path, capsys):
    rc = _run("--feature", "Bad_Name", "--specs-root", str(tmp_path / "specs"))
    assert rc == 1
    err = capsys.readouterr().err
    assert "kebab-case" in err


def test_refuses_existing(tmp_path):
    rc1 = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"))
    assert rc1 == 0
    rc2 = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"))
    assert rc2 == 1


def test_force_allows(tmp_path):
    _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"))
    rc = _run("--feature", "feat-1", "--specs-root", str(tmp_path / "specs"), "--force")
    assert rc == 0


def test_derive_title():
    assert derive_title("feature-search") == "Feature Search"
    assert derive_title("user") == "User"
    assert derive_title("ai-content-pipeline") == "Ai Content Pipeline"


def test_render_replaces_all():
    template = "{{FEATURE_TITLE}} / {{FEATURE}} / {{CREATED}}"
    out = render(template, "feature-x", "Feature X", "2026-01-01")
    assert out == "Feature X / feature-x / 2026-01-01"


def test_status_section_starts_all_draft(tmp_path):
    _run("--feature", "feat-x", "--specs-root", str(tmp_path / "specs"))
    body = (tmp_path / "specs" / "feat-x" / "README.md").read_text()
    assert "| PRD | draft |" in body
    assert "| SDD | draft |" in body
    assert "| PLAN | draft |" in body


def test_custom_title_override(tmp_path):
    _run(
        "--feature", "feat-x",
        "--specs-root", str(tmp_path / "specs"),
        "--feature-title", "Custom Title Here",
    )
    body = (tmp_path / "specs" / "feat-x" / "README.md").read_text()
    assert "Custom Title Here" in body
