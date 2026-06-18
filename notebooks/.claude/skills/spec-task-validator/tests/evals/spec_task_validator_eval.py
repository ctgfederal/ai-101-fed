"""LLM evals: narrating per-task validation results.

The deterministic validator sets the per-task statuses; the LLM's job is only to
produce a human-readable narrative under each issue. These cases assert the
eval shape is well-formed.
"""
import pytest

CASES = [
    {
        "name": "happy_clean_plan",
        "tasks": [
            {"id": "T-001", "status": "ok", "issues": []},
            {"id": "T-002", "status": "ok", "issues": []},
        ],
        "expected_verdict": "PASS",
    },
    {
        "name": "edge_warn_plan",
        "tasks": [
            {"id": "T-001", "status": "ok", "issues": []},
            {"id": "T-002", "status": "warn", "issues": ["title is all-lowercase"]},
        ],
        "expected_verdict": "WARN",
    },
    {
        "name": "adversarial_fail_plan",
        "tasks": [
            {"id": "T-001", "status": "ok", "issues": []},
            {"id": "T-002", "status": "fail", "issues": ["missing TDD step"]},
            {"id": "T-003", "status": "fail", "issues": ["acceptance not measurable"]},
        ],
        "expected_verdict": "FAIL",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "tasks" in case
    assert isinstance(case["tasks"], list)
    for t in case["tasks"]:
        assert "id" in t
        assert "status" in t
        assert t["status"] in {"ok", "warn", "fail"}
        assert "issues" in t
    assert case["expected_verdict"] in {"PASS", "WARN", "FAIL"}
