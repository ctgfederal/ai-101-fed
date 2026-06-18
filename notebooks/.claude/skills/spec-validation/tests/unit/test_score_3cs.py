"""Unit tests for scripts/score_3cs.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from score_3cs import (
    score, compute_verdict, score_completeness, score_consistency,
    score_correctness, Result, main as s3cs_main,
)


def test_compute_verdict_pass():
    assert compute_verdict(10, 9, 8) == "PASS"


def test_compute_verdict_warn():
    assert compute_verdict(8, 7, 9) == "WARN"


def test_compute_verdict_fail():
    assert compute_verdict(4, 9, 9) == "FAIL"


def test_compute_verdict_borderline_low_pass():
    assert compute_verdict(8, 8, 8) == "PASS"
    assert compute_verdict(7, 8, 8) == "WARN"


def test_score_good_spec(good_spec):
    payload = score(good_spec, "good.md")
    assert payload["completeness"] == 10
    assert payload["consistency"] == 10
    assert payload["correctness"] == 10
    assert payload["overall"] == 10
    assert payload["verdict"] == "PASS"
    assert payload["issues"] == []


def test_score_bad_spec(bad_spec):
    payload = score(bad_spec, "bad.md")
    assert payload["completeness"] < 10  # NEEDS CLARIFICATION + TODO + few sections
    assert payload["consistency"] < 10   # duplicate REQ-001 + dangling REQ-999
    assert payload["correctness"] < 10   # non-EARS line + invalid Maybe MoSCoW
    assert payload["verdict"] in {"WARN", "FAIL"}
    assert payload["issues"]


def test_completeness_detects_needs_clarification():
    text = "## A\n\ncontent\n\n## B\n\nmore\n\n## C\n\n[NEEDS CLARIFICATION]\n"
    r = Result()
    score_completeness(text, r)
    assert r.completeness < 10
    assert any("NEEDS CLARIFICATION" in i.message for i in r.issues)


def test_completeness_detects_todo():
    text = "## A\n\ncontent\n\n## B\n\nmore\n\n## C\n\nTODO: do this\n"
    r = Result()
    score_completeness(text, r)
    assert r.completeness < 10


def test_completeness_detects_few_sections():
    text = "## A\n\nbody\n"
    r = Result()
    score_completeness(text, r)
    assert r.completeness < 10
    assert any("section" in i.message.lower() for i in r.issues)


def test_consistency_detects_duplicate_id():
    text = "- **REQ-001**: first\n- **REQ-001**: second\n"
    r = Result()
    score_consistency(text, r)
    assert r.consistency < 10
    assert any("duplicate" in i.message.lower() for i in r.issues)


def test_consistency_detects_dangling_ref():
    text = "- **REQ-001**: defined\n- See REQ-999 for details.\n"
    r = Result()
    score_consistency(text, r)
    assert r.consistency < 10
    assert any("undefined" in i.message.lower() or "dangling" in i.message.lower()
               for i in r.issues)


def test_consistency_clean():
    text = "- **REQ-001**: defined\n- See REQ-001.\n"
    r = Result()
    score_consistency(text, r)
    assert r.consistency == 10


def test_correctness_detects_non_ears():
    text = "- **REQ-001** (story US-1, Must): the user can search\n"
    r = Result()
    score_correctness(text, r)
    assert r.correctness < 10
    assert any("EARS" in i.message for i in r.issues)


def test_correctness_detects_bad_moscow():
    text = "- **REQ-001** (story US-1, Maybe): WHEN x THEN system SHALL y\n"
    r = Result()
    score_correctness(text, r)
    assert r.correctness < 10
    assert any("MoSCoW" in i.message for i in r.issues)


def test_correctness_clean():
    text = "- **REQ-001** (story US-1, Must): WHEN x THEN system SHALL y\n"
    r = Result()
    score_correctness(text, r)
    assert r.correctness == 10


def test_score_floors_at_zero(bad_spec):
    # crank up the badness — many duplicates, many dangling refs
    text = bad_spec + "\n".join(f"- See REQ-{n}." for n in range(900, 920))
    payload = score(text, "x.md")
    assert payload["consistency"] >= 0
    assert payload["completeness"] >= 0
    assert payload["correctness"] >= 0


def _run(*args):
    old = sys.argv
    sys.argv = ["score_3cs.py", *args]
    try:
        return s3cs_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--file", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_emits_json(tmp_path, good_spec, capsys):
    f = tmp_path / "good.md"
    f.write_text(good_spec)
    rc = _run("--file", str(f))
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["verdict"] == "PASS"
    assert payload["target"] == str(f)
