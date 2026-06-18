"""Shared fixtures for swarm-delegation tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def valid_handoff() -> dict:
    return {
        "from_agent": "orchestrator",
        "to_agent": "backend-developer",
        "task": "Implement the GET /users/:id endpoint with authentication.",
        "context_files": [
            "src/api/users/router.ts",
            "src/auth/middleware.ts",
        ],
        "success_criteria": [
            "Endpoint returns 200 with user payload for authenticated requests",
            "All new code covered by tests in tests/api/users.test.ts",
        ],
        "return_format": "Unified diff and the path of any new test files.",
        "deadline": "Phase 2 boundary",
        "output_type": "code-diff",
        "expected_input_type": "task-spec",
    }


@pytest.fixture
def invalid_handoff() -> dict:
    """Missing task; success_criteria empty; from == to."""
    return {
        "from_agent": "alpha",
        "to_agent": "alpha",
        "task": "",
        "context_files": [],
        "success_criteria": [],
        "return_format": "",
    }


@pytest.fixture
def valid_chain() -> dict:
    return {
        "chain": [
            {
                "from_agent": "orchestrator",
                "to_agent": "backend-developer",
                "task": "Implement endpoint.",
                "context_files": ["src/x.ts"],
                "success_criteria": ["200 OK"],
                "return_format": "code-diff",
                "output_type": "code-diff",
                "expected_input_type": "task-spec",
            },
            {
                "from_agent": "backend-developer",
                "to_agent": "test-implementation",
                "task": "Write tests.",
                "context_files": ["src/x.ts"],
                "success_criteria": ["coverage >= 80%"],
                "return_format": "test-list",
                "output_type": "test-list",
                "expected_input_type": "code-diff",
            },
        ]
    }


@pytest.fixture
def cyclic_chain() -> dict:
    return {
        "chain": [
            {
                "from_agent": "alpha",
                "to_agent": "beta",
                "task": "task 1",
                "context_files": [],
                "success_criteria": ["done"],
                "return_format": "x",
                "output_type": "x",
                "expected_input_type": "task-spec",
            },
            {
                "from_agent": "beta",
                "to_agent": "alpha",
                "task": "task 2",
                "context_files": [],
                "success_criteria": ["done"],
                "return_format": "x",
                "output_type": "x",
                "expected_input_type": "x",
            },
        ]
    }


@pytest.fixture
def mismatched_chain() -> dict:
    return {
        "chain": [
            {
                "from_agent": "alpha",
                "to_agent": "beta",
                "task": "produce a diff",
                "context_files": [],
                "success_criteria": ["done"],
                "return_format": "code-diff",
                "output_type": "code-diff",
                "expected_input_type": "task-spec",
            },
            {
                "from_agent": "beta",
                "to_agent": "gamma",
                "task": "consume tests",
                "context_files": [],
                "success_criteria": ["done"],
                "return_format": "report-md",
                "output_type": "report-md",
                "expected_input_type": "test-list",
            },
        ]
    }
