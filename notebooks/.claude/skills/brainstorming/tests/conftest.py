"""Shared pytest fixtures for brainstorming tests."""
import sys
from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_brainstorms_root(tmp_path):
    root = tmp_path / "brainstorms"
    return root


@pytest.fixture
def valid_payload():
    return {
        "topic": "AI-powered code review for solo devs",
        "date": date.today().isoformat(),
        "status": "complete",
        "inspiration": "Solo devs ship without review; mistakes compound.",
        "projects": "CLI, GitHub action, IDE extension.",
        "audience": "Solo founders, indie hackers, contractors.",
        "use_cases": "- pre-push review\n- staged-diff review\n- PR comment generation",
        "outcomes": "Fewer regressions; faster ship cadence; objective second eye.",
        "principles": "Speed > completeness; suggestion > prescription; offline-first.",
        "constraints": "Must run on consumer hardware; no PII to third parties.",
        "scope_in": "Static review of staged diffs.",
        "scope_out": "Auto-fixing; full project linting; PR auto-merge.",
        "open_questions": "- pricing model?\n- which LLMs to support locally?",
        "related": "_(none yet)_",
    }
