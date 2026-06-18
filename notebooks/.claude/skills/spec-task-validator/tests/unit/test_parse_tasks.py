"""Unit tests for scripts/parse_tasks.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from parse_tasks import parse_plan, main as pt_main


def test_parse_good_plan(good_plan):
    tasks = parse_plan(good_plan)
    assert len(tasks) == 3
    ids = [t["id"] for t in tasks]
    assert ids == ["T-001", "T-002", "T-003"]


def test_parse_extracts_titles(good_plan):
    tasks = parse_plan(good_plan)
    assert tasks[0]["title"] == "Implement search index loader"
    assert tasks[1]["title"] == "Implement query parser"


def test_parse_extracts_phases(good_plan):
    tasks = parse_plan(good_plan)
    assert tasks[0]["phase"] == "Foundation"
    assert tasks[1]["phase"] == "Core"
    assert tasks[2]["phase"] == "Integration"


def test_parse_extracts_reqs(good_plan):
    tasks = parse_plan(good_plan)
    assert tasks[0]["reqs"] == ["REQ-101"]
    assert tasks[1]["reqs"] == ["REQ-102"]


def test_parse_extracts_comps(good_plan):
    tasks = parse_plan(good_plan)
    assert tasks[0]["comps"] == ["COMP-001"]


def test_parse_extracts_tdd(good_plan):
    tasks = parse_plan(good_plan)
    assert tasks[0]["tdd_step"] == "red"
    assert tasks[1]["tdd_step"] == "green"


def test_parse_extracts_acceptance(good_plan):
    tasks = parse_plan(good_plan)
    assert "passes" in tasks[0]["acceptance"]


def test_parse_handles_missing_tdd(bad_plan):
    tasks = parse_plan(bad_plan)
    # T-002 has no TDD line
    t002 = next(t for t in tasks if t["id"] == "T-002")
    assert t002["tdd_step"] == ""


def test_parse_multiple_reqs_one_line():
    plan = """## Phase 1: Foundation

- [ ] T-001 Multi-req task
  _Acceptance:_ passes
  _Requirements:_ REQ-101, REQ-102, REQ-103
  _Components:_ COMP-001
  _TDD:_ red
"""
    tasks = parse_plan(plan)
    assert tasks[0]["reqs"] == ["REQ-101", "REQ-102", "REQ-103"]


def test_parse_no_phase_falls_back_to_empty_string():
    plan = """- [ ] T-001 Orphan task
  _Acceptance:_ passes
  _TDD:_ red
"""
    tasks = parse_plan(plan)
    assert len(tasks) == 1
    assert tasks[0]["phase"] == ""


def test_parse_completed_task_still_extracted():
    plan = """## Phase 1: Foundation

- [x] T-001 Done task
  _Acceptance:_ passes
  _Requirements:_ REQ-101
  _Components:_ COMP-001
  _TDD:_ red
"""
    tasks = parse_plan(plan)
    assert len(tasks) == 1
    assert tasks[0]["id"] == "T-001"


def test_parse_empty_plan():
    assert parse_plan("# Empty PLAN\n") == []


def _run(*args):
    old = sys.argv
    sys.argv = ["parse_tasks.py", *args]
    try:
        return pt_main()
    finally:
        sys.argv = old


def test_main_missing_file(tmp_path):
    rc = _run("--plan", str(tmp_path / "nope.md"))
    assert rc == 1


def test_main_emits_json(tmp_path, good_plan, capsys):
    f = tmp_path / "PLAN.md"
    f.write_text(good_plan)
    rc = _run("--plan", str(f))
    assert rc == 0
    out = capsys.readouterr().out
    tasks = json.loads(out)
    assert len(tasks) == 3
    assert tasks[0]["id"] == "T-001"
