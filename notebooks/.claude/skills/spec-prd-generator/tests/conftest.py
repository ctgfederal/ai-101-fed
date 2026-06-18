"""Shared fixtures for spec-prd-generator tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def valid_payload():
    return {
        "feature": "feature-search",
        "feature_title": "Feature Search",
        "vision": "Cross-entity search across briefs, customers, and notes returns < 200ms.",
        "problem": "Users grep across three pages and lose context.",
        "value": "Reduces time-to-context from minutes to seconds.",
        "personas": "See `.claude/steering/product.md#user-personas`.",
        "user_stories": [
            {"id": "US-1", "as": "a brief author", "i_want": "to search briefs",
             "so_that": "I can re-use prior work."},
        ],
        "requirements": [
            {"id": "REQ-001", "story": "US-1", "moscow": "Must",
             "ears": "WHEN a user submits a search query THEN the system SHALL return results within 200ms p99."},
            {"id": "REQ-002", "story": "US-1", "moscow": "Should",
             "ears": "The system SHALL rank results by relevance score and recency."},
        ],
        "metrics": "p99 latency < 200ms; engagement > 60%.",
        "risks": "DB failover causes timeout; circuit-break fallback.",
        "open_questions": [],
    }
