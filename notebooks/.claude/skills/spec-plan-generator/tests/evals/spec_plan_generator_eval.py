"""LLM evals: SDD → task decomposition."""
import pytest
CASES = [
    {"name": "happy", "components": 4, "requirements": 8, "expected_tasks": "8-15"},
    {"name": "edge_one_component", "components": 1, "expected_tasks": "≥3 (foundation, core, integration)"},
    {"name": "adversarial_circular_deps", "expected_action": "split-and-flatten"},
]
@pytest.mark.parametrize("c", CASES, ids=[c["name"] for c in CASES])
def test_shape(c): assert "name" in c
