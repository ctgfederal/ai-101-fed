"""LLM evals: narrating a compliance status for a spec/repo pair.

The deterministic checker sets the status; the LLM's job is only to
produce a human-readable narrative under each `## Deviations` entry.
These cases assert the eval shape is well-formed.
"""
import pytest

CASES = [
    {
        "name": "happy_full_compliance",
        "expected_status": "compliant",
        "expected_deviation_count": 0,
    },
    {
        "name": "edge_partial_compliance",
        "expected_status": "partial",
        "expected_deviation_count_min": 1,
    },
    {
        "name": "adversarial_non_compliant",
        "expected_status": "non-compliant",
        "expected_deviation_count_min": 1,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "expected_status" in case
    assert case["expected_status"] in {"compliant", "partial", "non-compliant"}
    if "expected_deviation_count" in case:
        assert case["expected_deviation_count"] >= 0
    if "expected_deviation_count_min" in case:
        assert case["expected_deviation_count_min"] >= 0
