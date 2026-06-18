"""Shared fixtures for spec-validation tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def good_spec() -> str:
    """A spec that should score 10/10/10."""
    return """# Product Requirements Document: Feature X

## Context References

- See `.claude/steering/product.md`.

## Product Overview

Vision text.

## User Stories

- **US-1**: As a user, I want to search.

## Functional Requirements

- **REQ-001** (story US-1, Must): WHEN a user submits a query THEN the system SHALL return results within 200ms.
- **REQ-002** (story US-1, Should): The system SHALL rank results by relevance.

## Success Metrics

p99 latency < 200ms.
"""


@pytest.fixture
def bad_spec() -> str:
    """A spec with multiple issues across all three Cs."""
    return """# Spec

## Functional Requirements

- **REQ-001** (story US-1, Maybe): the user can search.
- **REQ-001** (story US-1, Must): WHEN a query arrives THEN the system SHALL respond.
- See REQ-999 for context.

[NEEDS CLARIFICATION]
TODO: write metrics.
"""


@pytest.fixture
def valid_payload() -> dict:
    return {
        "target": ".claude/specs/feature-x/PRD.md",
        "completeness": 9,
        "consistency": 8,
        "correctness": 10,
        "overall": 9,
        "verdict": "PASS",
        "issues": [
            {"category": "consistency",
             "message": "REQ-104 referenced in PLAN T-003 but not defined in PRD"}
        ],
        "completeness_notes": "All required sections present.",
        "consistency_notes": "One dangling cross-reference found.",
        "correctness_notes": "All requirements EARS-formatted.",
    }
