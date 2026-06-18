"""Shared fixtures for spec-execution tests."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_specs_root(tmp_path):
    return tmp_path / "specs"


@pytest.fixture
def sample_plan_text() -> str:
    return """# PLAN — feature-x

## Phase 1: Foundation

- [ ] **T-001**: Set up package
- [ ] **T-002**: Add core dataclass

## Phase 2: Core

- [ ] **T-003**: Implement add()
- [ ] **T-004**: Implement query()
"""


@pytest.fixture
def init_feature(tmp_specs_root, sample_plan_text):
    """Create a feature folder with PLAN.md ready for `init`."""
    feature = "feature-x"
    fdir = tmp_specs_root / feature
    fdir.mkdir(parents=True)
    (fdir / "PLAN.md").write_text(sample_plan_text)
    return {"feature": feature, "root": tmp_specs_root, "dir": fdir}


@pytest.fixture
def sample_state() -> dict:
    return {
        "feature": "feature-x",
        "current_task": "T-002",
        "tasks": {
            "T-001": {
                "description": "Set up package",
                "status": "done",
                "history": [
                    {"step": "red",   "result": "fail", "note": "", "duration_s": 30, "timestamp": "2026-05-08T09:00:00"},
                    {"step": "green", "result": "pass", "note": "", "duration_s": 60, "timestamp": "2026-05-08T09:01:00"},
                ],
                "blockers": [],
                "depends_on": [],
            },
            "T-002": {
                "description": "Add core dataclass",
                "status": "in-progress",
                "history": [],
                "blockers": [],
                "depends_on": ["T-001"],
            },
            "T-003": {
                "description": "Implement add()",
                "status": "pending",
                "history": [],
                "blockers": [],
                "depends_on": ["T-002"],
            },
            "T-004": {
                "description": "Implement query()",
                "status": "pending",
                "history": [],
                "blockers": [],
                "depends_on": ["T-003"],
            },
        },
        "task_order": ["T-001", "T-002", "T-003", "T-004"],
        "meta": {
            "last_updated": "2026-05-08",
            "sessions": 1,
            "total_tasks": 4,
        },
    }
