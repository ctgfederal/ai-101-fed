"""Shared fixtures for spec-compliance tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def sample_prd() -> str:
    return """# Product Requirements Document: Feature Search

## Functional Requirements

- **REQ-001** (story US-1, Must): WHEN a user submits a query THEN the system SHALL return matching results within 200ms.
- **REQ-002** (story US-1, Should): The system SHALL rank results by relevance.

## Success Metrics

p99 latency < 200ms.
"""


@pytest.fixture
def sample_sdd() -> str:
    return """# Solution Design Document: Feature Search

## Components

### COMP-001: SearchService

Path: `src/search/service.py`

The entry point for search queries.

### COMP-002: RankingEngine

Path: `src/search/ranking.py`

Ranks results by relevance.
"""


@pytest.fixture
def sample_repo(tmp_path) -> Path:
    """A tiny repo with one component implemented and one missing.

    - src/search/service.py — implements REQ-001 (mentions COMP-001 + REQ-001)
    - tests/test_search.py — references REQ-001
    - (no src/search/ranking.py — COMP-002 missing)
    - (no reference to REQ-002 anywhere — unreferenced)
    """
    repo = tmp_path / "repo"
    (repo / "src" / "search").mkdir(parents=True)
    (repo / "tests").mkdir()

    (repo / "src" / "search" / "service.py").write_text(
        '"""SearchService — implements REQ-001."""\n'
        "def search(q):\n"
        "    # REQ-001: return matching results within 200ms\n"
        "    return []\n"
    )
    (repo / "tests" / "test_search.py").write_text(
        '"""Tests for REQ-001."""\n'
        "def test_returns_results():\n"
        "    pass\n"
    )
    return repo


@pytest.fixture
def parsed_spec_payload() -> dict:
    return {
        "prd": "PRD.md",
        "sdd": "SDD.md",
        "reqs": ["REQ-001", "REQ-002"],
        "comps": [
            {"id": "COMP-001", "name": "SearchService",
             "expected_paths": ["src/search/service.py"]},
            {"id": "COMP-002", "name": "RankingEngine",
             "expected_paths": ["src/search/ranking.py"]},
        ],
    }


@pytest.fixture
def valid_payload() -> dict:
    return {
        "prd": "PRD.md",
        "sdd": "SDD.md",
        "repo_root": "/tmp/repo",
        "status": "partial",
        "components": {
            "COMP-001": {
                "name": "SearchService",
                "expected_paths": ["src/search/service.py"],
                "found_paths": ["src/search/service.py"],
                "missing": False,
            },
            "COMP-002": {
                "name": "RankingEngine",
                "expected_paths": ["src/search/ranking.py"],
                "found_paths": [],
                "missing": True,
            },
        },
        "requirements": {
            "REQ-001": {
                "referenced_in": ["src/search/service.py"],
                "unreferenced": False,
            },
            "REQ-002": {
                "referenced_in": [],
                "unreferenced": True,
            },
        },
        "deviations": [
            {"type": "missing-component", "id": "COMP-002",
             "detail": "RankingEngine: no file at src/search/ranking.py"},
            {"type": "unreferenced-requirement", "id": "REQ-002",
             "detail": "REQ-002 not referenced in any source or test file"},
        ],
        "summary": {
            "components_total": 2,
            "components_found": 1,
            "requirements_total": 2,
            "requirements_referenced": 1,
            "deviation_count": 2,
        },
    }
