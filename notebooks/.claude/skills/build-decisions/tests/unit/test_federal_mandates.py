"""Unit tests for scripts/federal_mandates.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from federal_mandates import load_db, lookup, main as fm_main


def test_load_db_real():
    db = Path(__file__).resolve().parents[2] / "knowledge" / "federal-mandates.json"
    mandates = load_db(db)
    assert len(mandates) >= 10
    for m in mandates:
        assert "category" in m
        assert "name" in m
        assert "answer" in m
        assert "citation" in m


def test_load_db_malformed(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"foo": "bar"}))
    with pytest.raises(ValueError):
        load_db(bad)


def test_lookup_hit():
    mandates = [{"category": "Security", "name": "TLS", "answer": "1.2+", "citation": "X"}]
    hit = lookup(mandates, "Security", "TLS")
    assert hit == {"answer": "1.2+", "citation": "X"}


def test_lookup_case_insensitive():
    mandates = [{"category": "Security", "name": "TLS", "answer": "1.2+", "citation": "X"}]
    assert lookup(mandates, "security", "tls") is not None


def test_lookup_miss():
    mandates = [{"category": "Security", "name": "TLS", "answer": "1.2+", "citation": "X"}]
    assert lookup(mandates, "Security", "Other") is None


def _run(*args):
    old = sys.argv
    sys.argv = ["federal_mandates.py", *args]
    try:
        return fm_main()
    finally:
        sys.argv = old


def test_main_list(capsys):
    rc = _run("list")
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) >= 10


def test_main_lookup_hit(capsys):
    rc = _run("lookup", "--category", "Security", "--name", "Encryption at rest")
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "AES" in data["answer"]


def test_main_lookup_miss():
    rc = _run("lookup", "--category", "Security", "--name", "made-up-thing")
    assert rc == 1
