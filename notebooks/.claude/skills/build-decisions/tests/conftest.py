"""Shared fixtures for build-decisions tests."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_builds_root(tmp_path):
    return tmp_path / "builds"


@pytest.fixture
def tmp_log_path(tmp_path):
    return tmp_path / "decisions-log.md"


@pytest.fixture
def valid_payload():
    return {
        "feature": "feature-search",
        "feature_title": "Feature Search",
        "date": "2026-02-14",
        "status": "complete",
        "summary": "Search across briefs, customers, and notes.",
        "id_range": "D-001 to D-005",
        "auto_applied": [
            {"id": "D-001", "category": "Security", "name": "Encryption at rest",
             "answer": "AES-256.", "citation": "NIST 800-53 SC-28"},
            {"id": "D-002", "category": "Security", "name": "Encryption in transit",
             "answer": "TLS 1.2+.", "citation": "NIST 800-52r2"},
        ],
        "categories": {
            "Architecture": [
                {"id": "D-003", "title": "Pattern", "decision": "Layered service",
                 "priority": "simplicity",
                 "alternatives": ["event-driven", "CQRS"],
                 "rationale": "Read-heavy, sync.",
                 "tiers": {"federal": "blocks", "enterprise": "warns", "personal": "info"}},
            ],
            "Data Model": [
                {"id": "D-004", "title": "Storage", "decision": "Postgres",
                 "priority": "simplicity",
                 "alternatives": ["sqlite", "elasticsearch"],
                 "rationale": "Single store, JSONB for flexible search."},
            ],
            "API Design": [
                {"id": "D-005", "title": "Endpoint", "decision": "GET /search?q=...",
                 "priority": "simplicity",
                 "alternatives": ["GraphQL"],
                 "rationale": "REST keeps the API surface narrow."},
            ],
        },
        "open_questions": ["What rate limit for personal tier?"],
        "related_solutions": [],
    }
