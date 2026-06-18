"""Integration tests — placeholder; this skill hits no external endpoints."""
import os

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to run",
)


def test_placeholder():
    """No external endpoints to test for this skill."""
    assert True
