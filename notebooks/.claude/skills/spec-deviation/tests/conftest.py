"""Shared fixtures for spec-deviation tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def valid_payload() -> dict:
    """A schema-valid deviation payload."""
    return {
        "spec_id": "feature-search",
        "deviation_id": "DEV-001",
        "reason_category": "technical-blocker",
        "description": "REQ-101 specifies WebSockets but the runtime doesn't support persistent connections.",
        "original_decision": "REQ-101",
        "proposed_change": "Use SSE with polling fallback.",
        "impact": "Same latency profile; minor codebase complexity.",
        "status": "proposed",
        "approver": "Josh Schultz",
        "date": "2026-05-08",
    }


@pytest.fixture
def bad_payload() -> dict:
    """A payload with multiple schema violations."""
    return {
        "spec_id": "",
        "deviation_id": "DEV-1",  # too few digits
        "reason_category": "made-up-category",
        "description": "x",
        "original_decision": "req-1",  # bad case
        "proposed_change": "x",
        "impact": "x",
        "status": "maybe",  # invalid
        "approver": "Josh",
        "date": "yesterday",  # bad format
    }


@pytest.fixture
def clean_sdd() -> str:
    """An SDD with no Deviations section."""
    return """# Solution Design Document: Test Feature

## Context

Test.

## Components

- **COMP-001**: First component.

## Traceability

| PRD | SDD |
|---|---|
| REQ-001 | COMP-001 |
"""


@pytest.fixture
def populated_sdd() -> str:
    """An SDD that already has a Deviations section with one block."""
    return """# Solution Design Document: Test Feature

## Context

Test.

## Components

- **COMP-001**: First component.

## Deviations

### DEV-001

- **Date**: 2026-01-01
- **Spec**: test-feature
- **Reason Category**: scope-clarification
- **Original Decision**: REQ-001
- **Status**: approved
- **Approver**: Reviewer A

**Description**

The original requirement was ambiguous about caching behavior.

**Proposed Change**

Treat caching as opt-in via header.

**Impact**

No user-visible change.
"""
