"""Unit tests for scripts/extract_req_ids.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from extract_req_ids import extract, main as em


def test_extract_empty():
    assert extract("nothing") == []


def test_extract_single():
    assert extract("REQ-007") == ["REQ-007"]


def test_extract_dedups_and_sorts():
    out = extract("REQ-005 REQ-002 REQ-005")
    assert out == ["REQ-002", "REQ-005"]


def test_extract_preserves_padding():
    assert extract("REQ-001 REQ-1000")[0] == "REQ-0001"
    assert extract("REQ-001 REQ-1000")[1] == "REQ-1000"


def _run(*a):
    old = sys.argv
    sys.argv = ["extract_req_ids.py", *a]
    try:
        return em()
    finally:
        sys.argv = old


def test_main_missing(tmp_path):
    rc = _run("--prd", str(tmp_path / "no.md"))
    assert rc == 1


def test_main_happy(tmp_path, capsys):
    p = tmp_path / "PRD.md"
    p.write_text("REQ-005 REQ-001")
    rc = _run("--prd", str(p))
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "REQ-001 REQ-005"
