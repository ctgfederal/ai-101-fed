"""Shared fixtures for spec-task-validator tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def good_plan() -> str:
    """A PLAN with three clean tasks across three phases."""
    return """# Implementation Plan: feature-search

## Context References

- PRD: PRD.md
- SDD: SDD.md

## Phase 1: Foundation

- [ ] T-001 Implement search index loader
  - Load fixture data on module init
  _Acceptance:_ test_loader_caches_until_mtime_changes passes
  _Requirements:_ REQ-101
  _Components:_ COMP-001
  _TDD:_ red

## Phase 2: Core

- [ ] T-002 Implement query parser
  - Parse `field:value` syntax
  _Acceptance:_ parser returns AST with one Filter node
  _Requirements:_ REQ-102
  _Components:_ COMP-002
  _TDD:_ green

## Phase 3: Integration

- [ ] T-003 Wire parser into HTTP handler
  - Mount at /search
  _Acceptance:_ handler returns 200 with results matches schema
  _Requirements:_ REQ-103
  _Components:_ COMP-003
  _TDD:_ green
"""


@pytest.fixture
def bad_plan() -> str:
    """A PLAN with three tasks: one ok, one fail (no TDD), one fail (vague acceptance)."""
    return """# Implementation Plan: feature-x

## Phase 1: Foundation

- [ ] T-001 Implement search index loader
  _Acceptance:_ loader passes test
  _Requirements:_ REQ-101
  _Components:_ COMP-001
  _TDD:_ red

## Phase 2: Core

- [ ] T-002 Implement query parser
  - No TDD step at all
  _Acceptance:_ parser returns AST
  _Requirements:_ REQ-102
  _Components:_ COMP-002

- [ ] T-003 Implement scoring algorithm
  _Acceptance:_ should work end to end
  _Requirements:_ REQ-103
  _Components:_ COMP-003
  _TDD:_ green
"""


@pytest.fixture
def good_prd() -> str:
    return """# PRD: feature-search

## Functional Requirements

- **REQ-101**: WHEN x THEN system SHALL y.
- **REQ-102**: WHEN q THEN parser SHALL return AST.
- **REQ-103**: The handler SHALL return JSON.
"""


@pytest.fixture
def good_sdd() -> str:
    return """# SDD: feature-search

## Components

- **COMP-001**: Index loader.
- **COMP-002**: Query parser.
- **COMP-003**: HTTP handler.
"""


@pytest.fixture
def parsed_good_tasks() -> list:
    """The parsed structure that good_plan should produce."""
    return [
        {
            "id": "T-001",
            "title": "Implement search index loader",
            "phase": "Foundation",
            "comps": ["COMP-001"],
            "reqs": ["REQ-101"],
            "acceptance": "test_loader_caches_until_mtime_changes passes",
            "tdd_step": "red",
        },
        {
            "id": "T-002",
            "title": "Implement query parser",
            "phase": "Core",
            "comps": ["COMP-002"],
            "reqs": ["REQ-102"],
            "acceptance": "parser returns AST with one Filter node",
            "tdd_step": "green",
        },
        {
            "id": "T-003",
            "title": "Wire parser into HTTP handler",
            "phase": "Integration",
            "comps": ["COMP-003"],
            "reqs": ["REQ-103"],
            "acceptance": "handler returns 200 with results matches schema",
            "tdd_step": "green",
        },
    ]


@pytest.fixture
def valid_payload() -> dict:
    return {
        "plan": ".claude/specs/feature-x/PLAN.md",
        "tasks": [
            {
                "id": "T-001",
                "title": "Implement search index loader",
                "phase": "Foundation",
                "status": "ok",
                "issues": [],
            },
            {
                "id": "T-002",
                "title": "Implement query parser",
                "phase": "Core",
                "status": "fail",
                "issues": ["missing TDD step", "acceptance not measurable"],
            },
        ],
        "summary": {"total": 2, "ok": 1, "warn": 0, "fail": 1},
        "verdict": "FAIL",
    }
