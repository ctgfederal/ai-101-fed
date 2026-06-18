"""Integration test placeholder — auto-documentation hits no external endpoints.

Kept intentionally minimal so pytest discovers a tests/integration/ directory
and the validator passes. If the skill ever gains an external dependency
(e.g., a remote dedup index), real integration coverage goes here.
"""
import pytest


@pytest.mark.skip(reason="no external integrations to test")
def test_placeholder():
    assert True
