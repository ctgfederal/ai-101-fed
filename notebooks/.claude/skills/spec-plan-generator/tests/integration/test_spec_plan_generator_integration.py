"""Placeholder."""
import os, pytest
pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "1", reason="set RUN_INTEGRATION_TESTS=1")
def test_placeholder(): assert True
