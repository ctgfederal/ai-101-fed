"""LLM evals: assembling a handoff payload from a conversation context.

The deterministic validator catches schema errors; the LLM's job is only to
extract the right values from context. These cases assert the eval shape
is well-formed.
"""
import pytest

CASES = [
    {
        "name": "happy_clear_handoff",
        "context": "orchestrator -> backend-developer for the GET /users endpoint",
        "expected_valid": True,
        "expected_pattern_hint": "linear",
    },
    {
        "name": "edge_ambiguous_handoff",
        "context": "send this to whoever can do it",
        "expected_valid": False,
        "expected_pattern_hint": "unknown",
    },
    {
        "name": "adversarial_cyclic_chain",
        "context": "a -> b -> a (the agent will figure out which way to go)",
        "expected_valid": False,
        "expected_pattern_hint": "linear-with-cycle",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "context" in case
    assert isinstance(case["expected_valid"], bool)
    assert "expected_pattern_hint" in case
