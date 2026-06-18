"""Shared pytest fixtures for agent-delegation tests."""
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def valid_payload():
    """A complete, valid delegation payload."""
    return {
        "agent_type": "auth-agent",
        "task": "Implement JWT authentication in src/auth/.",
        "focus_files": ["src/auth/", "tests/auth/"],
        "exclude_files": ["src/billing/", "docs/"],
        "success_criteria": [
            "pytest tests/auth/ exits 0",
            "ruff check src/auth/ exits 0",
        ],
        "return_format": "Markdown summary of files created and tests added.",
    }


@pytest.fixture
def invalid_payload(valid_payload):
    """Payload missing a required key."""
    p = dict(valid_payload)
    del p["task"]
    return p


@pytest.fixture
def colliding_payloads():
    """Two payloads whose FOCUS sets overlap on src/shared/."""
    return [
        {
            "agent_type": "alpha",
            "task": "do alpha",
            "focus_files": ["src/auth/", "src/shared/"],
            "exclude_files": [],
            "success_criteria": ["alpha works"],
            "return_format": "summary",
        },
        {
            "agent_type": "beta",
            "task": "do beta",
            "focus_files": ["src/billing/", "src/shared/"],
            "exclude_files": [],
            "success_criteria": ["beta works"],
            "return_format": "summary",
        },
    ]


@pytest.fixture
def safe_payloads():
    """Two payloads with disjoint FOCUS sets."""
    return [
        {
            "agent_type": "auth",
            "task": "build auth",
            "focus_files": ["src/auth/", "tests/auth/"],
            "exclude_files": ["src/billing/"],
            "success_criteria": ["pytest tests/auth/ exits 0"],
            "return_format": "summary",
        },
        {
            "agent_type": "billing",
            "task": "build billing",
            "focus_files": ["src/billing/", "tests/billing/"],
            "exclude_files": ["src/auth/"],
            "success_criteria": ["pytest tests/billing/ exits 0"],
            "return_format": "summary",
        },
    ]
