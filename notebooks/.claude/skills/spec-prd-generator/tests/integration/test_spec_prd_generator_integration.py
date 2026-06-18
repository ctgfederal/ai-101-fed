"""Placeholder — this skill hits no external endpoints."""
import os
import pytest
pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "1", reason="set RUN_INTEGRATION_TESTS=1")
def test_placeholder(): assert True
