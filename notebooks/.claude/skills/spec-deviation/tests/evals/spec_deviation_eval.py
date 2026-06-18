"""LLM evals: capturing a spec deviation.

The deterministic scripts validate, allocate, and render. The LLM's job is
to pick the right `reason_category` and write the description / impact
prose. These cases assert the eval shape is well-formed.
"""
import pytest

CASES = [
    {
        "name": "happy_technical_blocker_proposed",
        "scenario": "WebSocket-required REQ blocked by serverless platform",
        "expected_reason_category": "technical-blocker",
        "expected_status": "proposed",
        "expected_original_decision_prefix": "REQ-",
    },
    {
        "name": "edge_scope_clarification_approved",
        "scenario": "Spec ambiguity surfaced mid-implementation",
        "expected_reason_category": "scope-clarification",
        "expected_status": "approved",
        "expected_original_decision_prefix": "COMP-",
    },
    {
        "name": "adversarial_performance_rejected",
        "scenario": "Performance optimization rejected — original design held",
        "expected_reason_category": "performance-required",
        "expected_status": "rejected",
        "expected_original_decision_prefix": "D-",
    },
]

ALLOWED_REASON_CATEGORIES = {
    "technical-blocker",
    "scope-clarification",
    "dependency-conflict",
    "performance-required",
    "security-required",
}
ALLOWED_STATUSES = {"proposed", "approved", "rejected"}
ALLOWED_PREFIXES = {"REQ-", "COMP-", "D-"}


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "scenario" in case
    assert case["expected_reason_category"] in ALLOWED_REASON_CATEGORIES
    assert case["expected_status"] in ALLOWED_STATUSES
    assert case["expected_original_decision_prefix"] in ALLOWED_PREFIXES
