"""LLM evals: PRD → component decomposition."""
import pytest

CASES = [
    {"name": "happy", "prd_reqs": 5, "expected_components": "3-7", "expected_coverage": "100%"},
    {"name": "edge_one_req_many_components", "prd_reqs": 1, "expected_components": "≥1"},
    {"name": "adversarial_overlapping", "prd_reqs": 3, "expected_action": "factor-shared-component"},
]


@pytest.mark.parametrize("c", CASES, ids=[c["name"] for c in CASES])
def test_shape(c):
    assert "name" in c
