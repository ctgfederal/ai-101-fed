"""LLM evals: narrating a 3Cs score for a target spec.

The deterministic scorer sets the integers; the LLM's job is only to
produce a human-readable narrative under each `## C` section. These
cases assert the eval shape is well-formed.
"""
import pytest

CASES = [
    {
        "name": "happy_clear_spec",
        "scores": {"completeness": 10, "consistency": 10, "correctness": 10},
        "expected_verdict": "PASS",
        "expected_issue_count": 0,
    },
    {
        "name": "edge_warn_spec",
        "scores": {"completeness": 7, "consistency": 8, "correctness": 9},
        "expected_verdict": "WARN",
        "expected_issue_count_min": 1,
    },
    {
        "name": "adversarial_fail_spec",
        "scores": {"completeness": 3, "consistency": 4, "correctness": 6},
        "expected_verdict": "FAIL",
        "expected_issue_count_min": 1,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "scores" in case
    assert set(case["scores"]) == {"completeness", "consistency", "correctness"}
    for v in case["scores"].values():
        assert 0 <= v <= 10
    assert case["expected_verdict"] in {"PASS", "WARN", "FAIL"}
