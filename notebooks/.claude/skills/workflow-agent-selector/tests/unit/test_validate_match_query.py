"""Unit tests for scripts/validate_match_query.py."""
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_match_query import validate, main as vmq_main


def test_validate_happy():
    assert validate({"keywords": ["a", "b"], "min_score": 0.5, "max_results": 5}) == []


def test_validate_keywords_only():
    assert validate({"keywords": ["a"]}) == []


def test_validate_missing_keywords():
    errors = validate({"min_score": 0.5})
    assert any("missing required field: keywords" in e for e in errors)


def test_validate_empty_keywords_list():
    errors = validate({"keywords": []})
    assert any("1..32" in e for e in errors)


def test_validate_too_many_keywords():
    errors = validate({"keywords": ["a"] * 33})
    assert any("1..32" in e for e in errors)


def test_validate_keyword_not_string():
    errors = validate({"keywords": [1]})
    assert any("non-empty string" in e for e in errors)


def test_validate_empty_keyword_string():
    errors = validate({"keywords": [""]})
    assert any("non-empty string" in e for e in errors)


def test_validate_min_score_out_of_range():
    errors = validate({"keywords": ["a"], "min_score": 1.5})
    assert any("0.0..1.0" in e for e in errors)


def test_validate_min_score_not_number():
    errors = validate({"keywords": ["a"], "min_score": "high"})
    assert any("min_score must be a number" in e for e in errors)


def test_validate_max_results_zero():
    errors = validate({"keywords": ["a"], "max_results": 0})
    assert any("positive int" in e for e in errors)


def test_validate_max_results_bool_rejected():
    errors = validate({"keywords": ["a"], "max_results": True})
    assert any("positive int" in e for e in errors)


def test_validate_unexpected_field():
    errors = validate({"keywords": ["a"], "extra": 1})
    assert any("unexpected fields" in e for e in errors)


def test_validate_not_object():
    errors = validate(["a"])
    assert any("payload must be a JSON object" in e for e in errors)


def _run_main(argv, stdin_text=None, monkeypatch=None):
    if stdin_text is not None and monkeypatch is not None:
        monkeypatch.setattr(sys, "stdin", io.StringIO(stdin_text))
    sys.argv = ["validate_match_query.py"] + argv
    return vmq_main()


def test_main_happy_file(tmp_path):
    p = tmp_path / "q.json"
    p.write_text(json.dumps({"keywords": ["a"]}), encoding="utf-8")
    assert _run_main(["--file", str(p)]) == 0


def test_main_invalid_file(tmp_path):
    p = tmp_path / "q.json"
    p.write_text(json.dumps({"min_score": 1.0}), encoding="utf-8")
    assert _run_main(["--file", str(p)]) == 1


def test_main_stdin_invalid_json(monkeypatch):
    assert _run_main([], stdin_text="not json", monkeypatch=monkeypatch) == 1


def test_main_stdin_empty(monkeypatch):
    assert _run_main([], stdin_text="   ", monkeypatch=monkeypatch) == 1
