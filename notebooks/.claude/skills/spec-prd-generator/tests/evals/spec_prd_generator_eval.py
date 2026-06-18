"""LLM evals: turning a brainstorm into EARS criteria."""
import pytest

CASES = [
    {"name": "happy_clear",
     "input": "User wants search results within 200ms.",
     "expected_pattern": "WHEN", "expected_in_output": "200ms"},
    {"name": "edge_ambiguous",
     "input": "Search should be fast and good.",
     "expected_action": "ask-clarification"},
    {"name": "adversarial_overspecified",
     "input": "Use Postgres pg_trgm with GIN index for fuzzy search.",
     "expected_action": "abstract-to-behavior",
     "expected_in_output": "fuzzy"},
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "input" in case
