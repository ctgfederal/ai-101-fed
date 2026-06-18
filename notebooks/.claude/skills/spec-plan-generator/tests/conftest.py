"""Shared fixtures."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def fake_prd(tmp_path):
    p = tmp_path / "PRD.md"
    p.write_text("REQ-001 stuff REQ-002 more")
    return p


@pytest.fixture
def fake_sdd(tmp_path):
    p = tmp_path / "SDD.md"
    p.write_text("COMP-001 stuff COMP-002 more")
    return p


@pytest.fixture
def valid_payload():
    return {
        "feature": "feature-search",
        "feature_title": "Feature Search",
        "tasks": [
            {"id": "T-001", "title": "Migration", "phase": "Foundation",
             "comps": ["COMP-001"], "reqs": ["REQ-001"],
             "acceptance": "applies cleanly", "tdd_step": "red"},
            {"id": "T-002", "title": "Service impl", "phase": "Core",
             "comps": ["COMP-002"], "reqs": ["REQ-001", "REQ-002"],
             "acceptance": "tests green", "tdd_step": "green"},
        ],
        "open_questions": [],
    }
