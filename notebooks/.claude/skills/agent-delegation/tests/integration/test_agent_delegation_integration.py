"""Integration tests for agent-delegation. Gated by RUN_INTEGRATION_TESTS=1.

These tests would exercise real disk paths under .claude/ in a checkout.
Currently a placeholder that asserts the gate works.
"""
import os

import pytest


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to run integration tests",
)


def test_integration_placeholder():
    # Placeholder: real integration would render a prompt, store under
    # .claude/prompts/, run check_collisions on a real spec dir, etc.
    assert True
