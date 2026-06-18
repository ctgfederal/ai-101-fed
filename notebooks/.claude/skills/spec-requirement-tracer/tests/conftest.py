"""Shared fixtures for spec-requirement-tracer tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def fake_prd(tmp_path) -> Path:
    p = tmp_path / "PRD.md"
    p.write_text(
        "# PRD\n\n"
        "## Functional Requirements\n\n"
        "- **REQ-001**: WHEN a user searches THEN the system SHALL return results.\n"
        "- **REQ-002**: The system SHALL rank results by relevance.\n"
        "- **REQ-003**: The system SHALL paginate results.\n"
    )
    return p


@pytest.fixture
def fake_sdd(tmp_path) -> Path:
    p = tmp_path / "SDD.md"
    p.write_text(
        "# SDD\n\n"
        "## Components\n\n"
        "- **COMP-001**: SearchService\n"
        "- **COMP-002**: RankingPolicy\n"
        "- **COMP-003**: Paginator\n\n"
        "## Traceability\n\n"
        "REQ-001 -> COMP-001, COMP-003\n"
        "REQ-002 -> COMP-002\n"
    )
    return p


@pytest.fixture
def fake_plan(tmp_path) -> Path:
    p = tmp_path / "PLAN.md"
    p.write_text(
        "# Plan\n\n"
        "## Phase 1: Foundation\n\n"
        "- **T-001** (red): Search migration\n"
        "  - Components: COMP-001\n"
        "  - Requirements: REQ-001\n"
        "  - Acceptance: applies cleanly\n\n"
        "- **T-002** (green): Ranking impl\n"
        "  - Components: COMP-002\n"
        "  - Requirements: REQ-002\n"
        "  - Acceptance: tests green\n"
    )
    return p


@pytest.fixture
def fake_code_root(tmp_path) -> Path:
    root = tmp_path / "code"
    (root / "src").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    # REQ-001: full coverage (src + tests)
    (root / "src" / "search.py").write_text(
        "# REQ-001 — search service\n"
        "def search(): pass\n"
    )
    (root / "tests" / "test_search.py").write_text(
        '"""REQ-001 tests."""\n'
        "def test_search(): pass\n"
    )
    # REQ-002: only test file (no source)
    (root / "tests" / "test_ranking.py").write_text(
        "# REQ-002\n"
        "def test_ranking(): pass\n"
    )
    return root


@pytest.fixture
def valid_ids_payload() -> dict:
    return {
        "prd_reqs": ["REQ-001", "REQ-002", "REQ-003"],
        "sdd_comps": ["COMP-001", "COMP-002", "COMP-003"],
        "plan_tasks": ["T-001", "T-002"],
        "sdd_traceability": {
            "REQ-001": ["COMP-001", "COMP-003"],
            "REQ-002": ["COMP-002"],
        },
        "plan_task_reqs": {
            "T-001": ["REQ-001"],
            "T-002": ["REQ-002"],
        },
        "code_refs": {
            "REQ-001": ["src/search.py"],
            "REQ-002": [],
            "REQ-003": [],
        },
        "test_refs": {
            "REQ-001": ["tests/test_search.py"],
            "REQ-002": ["tests/test_ranking.py"],
            "REQ-003": [],
        },
    }


@pytest.fixture
def valid_matrix_payload() -> dict:
    return {
        "feature": "feature-search",
        "rows": [
            {
                "req": "REQ-001",
                "comps": ["COMP-001", "COMP-003"],
                "tasks": ["T-001"],
                "code_refs": ["src/search.py"],
                "tests_refs": ["tests/test_search.py"],
                "status": "covered",
            },
            {
                "req": "REQ-002",
                "comps": ["COMP-002"],
                "tasks": ["T-002"],
                "code_refs": [],
                "tests_refs": ["tests/test_ranking.py"],
                "status": "partial",
            },
            {
                "req": "REQ-003",
                "comps": [],
                "tasks": [],
                "code_refs": [],
                "tests_refs": [],
                "status": "uncovered",
            },
        ],
    }
