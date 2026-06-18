"""Unit tests for scripts/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_output import validate_body, REQUIRED_SECTIONS, main as vo_main


def test_validate_body_happy():
    body = "\n".join([f"## {s}\n\nfoo\n" for s in REQUIRED_SECTIONS])
    assert validate_body(body) == []


def test_validate_body_missing():
    body = "## Symptom\nfoo\n## Investigation\nbar\n"
    errors = validate_body(body)
    # missing Root Cause, Solution, Verification, Prevention
    assert any("Root Cause" in e for e in errors)
    assert any("Solution" in e for e in errors)
    assert any("Verification" in e for e in errors)
    assert any("Prevention" in e for e in errors)


def test_validate_body_out_of_order():
    body = "\n".join([
        "## Investigation\nfoo",
        "## Symptom\nfoo",
        "## Root Cause\nfoo",
        "## Solution\nfoo",
        "## Verification\nfoo",
        "## Prevention\nfoo",
    ])
    errors = validate_body(body)
    assert any("out of order" in e for e in errors)


def _run_main(argv):
    old = sys.argv
    sys.argv = ["validate_output.py"] + argv
    try:
        return vo_main()
    finally:
        sys.argv = old


def test_main_happy(fixture_solution_file, capsys):
    rc = _run_main(["--file", str(fixture_solution_file)])
    assert rc == 0


def test_main_missing_file(tmp_path):
    rc = _run_main(["--file", str(tmp_path / "nope.md")])
    assert rc == 1


def test_main_body_incomplete(tmp_path):
    f = tmp_path / "incomplete.md"
    f.write_text("""---
title: "Sample N+1"
category: performance-issues
date: 2026-02-14
tags:
  - rails
  - n+1
module: "Foo"
symptom: "bar"
root_cause: "baz"
---

# Sample
## Symptom
foo
""", encoding="utf-8")
    rc = _run_main(["--file", str(f)])
    assert rc == 1
