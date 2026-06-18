"""Eval shape tests for spec-execution.

The deterministic core decides task selection and state transitions; the LLM's
job inside this skill is only to *narrate* progress, surface blockers, and
prompt the user when status changes. These cases assert that the eval shape
itself is well-formed — the script-driven contract is exercised in unit tests.
"""
import pytest


CASES = [
    {
        "name": "happy_resume_post_red",
        "scenario": "T-002 has one red→fail history entry; resume should announce 'continue green'",
        "expected_next_step": "green",
        "expected_status_after": "in-progress",
    },
    {
        "name": "edge_dependency_blocks_progress",
        "scenario": "T-003 depends on T-002 which is still in-progress; next_task returns empty",
        "expected_next_step": None,
        "expected_status_after": "pending",
    },
    {
        "name": "adversarial_three_strikes",
        "scenario": "Three red→fail entries with no green; task should be marked failed and surfaced",
        "expected_next_step": "deviation",
        "expected_status_after": "failed",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "scenario" in case
    assert "expected_status_after" in case
    assert case["expected_status_after"] in {
        "pending", "in-progress", "done", "blocked", "failed",
    }
    if case["expected_next_step"] is not None:
        assert case["expected_next_step"] in {"red", "green", "refactor", "deviation"}
