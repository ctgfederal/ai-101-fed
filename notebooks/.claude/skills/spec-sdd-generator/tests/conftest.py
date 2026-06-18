"""Shared fixtures."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def fake_prd(tmp_path):
    p = tmp_path / "PRD.md"
    p.write_text("# PRD\n- **REQ-001** stuff\n- **REQ-002** more\n", encoding="utf-8")
    return p


@pytest.fixture
def valid_payload():
    return {
        "feature": "feature-search",
        "feature_title": "Feature Search",
        "overview": "Search service.",
        "architecture": "Layered.",
        "components": [
            {"id": "COMP-001", "name": "SearchController", "responsibility": "HTTP entry",
             "dependencies": ["SearchService"], "contract": {"inputs": "GET /search", "outputs": "JSON"}},
            {"id": "COMP-002", "name": "SearchService", "responsibility": "Orchestrate",
             "dependencies": [], "contract": {"inputs": "Query", "outputs": "Results"}},
        ],
        "data_model": "tsvector + GIN",
        "integrations": "_(none)_",
        "traceability": {"REQ-001": ["COMP-001"], "REQ-002": ["COMP-002"]},
        "alternatives": "Considered Elasticsearch — rejected.",
        "risks": "DB outage — circuit-break.",
        "open_questions": [],
    }
