"""Unit tests for scripts/validate_output.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_steering import main as init_main
from validate_output import REQUIRED_SECTIONS, main as vo_main, validate_doc


def _scaffold(root: Path) -> None:
    old = sys.argv
    sys.argv = ["init_steering.py", "--steering-root", str(root)]
    try:
        rc = init_main()
        assert rc == 0
    finally:
        sys.argv = old


def _run(*args: str) -> int:
    old = sys.argv
    sys.argv = ["validate_output.py", *args]
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_happy_path_each_doc(tmp_steering_root: Path) -> None:
    _scaffold(tmp_steering_root)
    for doc in REQUIRED_SECTIONS:
        rc = _run(
            "--file", str(tmp_steering_root / f"{doc}.md"),
            "--doc", doc,
        )
        assert rc == 0, f"{doc} should validate"


def test_missing_section(tmp_steering_root: Path) -> None:
    _scaffold(tmp_steering_root)
    target = tmp_steering_root / "tech.md"
    text = target.read_text().replace("## Observability", "## NotObservability")
    target.write_text(text)
    rc = _run("--file", str(target), "--doc", "tech")
    assert rc == 1


def test_unknown_doc_kind() -> None:
    # argparse will reject this with exit code 2 from SystemExit
    with pytest.raises(SystemExit):
        _run("--file", "irrelevant", "--doc", "bogus")


def test_validate_doc_returns_errors() -> None:
    text = "# title\n\n## Mission\nbody\n"  # missing other sections
    errors = validate_doc(text, "product")
    assert errors
    assert any("User Personas" in e for e in errors)


def test_validate_doc_detects_out_of_order() -> None:
    # Reverse two sections
    text = (
        "## User Personas\nbody\n\n"
        "## Mission\nbody\n\n"
        "## Business Constraints\nbody\n\n"
        "## Success Metrics Framework\nbody\n\n"
        "## Domain Glossary\nbody\n"
    )
    errors = validate_doc(text, "product")
    assert any("out of order" in e for e in errors)


def test_validate_doc_unknown_kind_returns_error() -> None:
    errors = validate_doc("any", "wrong")
    assert errors
    assert "unknown doc kind" in errors[0]


def test_missing_file(tmp_path: Path) -> None:
    rc = _run("--file", str(tmp_path / "nope.md"), "--doc", "product")
    assert rc == 1
