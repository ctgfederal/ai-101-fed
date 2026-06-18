"""LLM evals for agent-delegation: payload-assembly quality.

These cases exercise the LLM step that turns a free-form delegation request
into a structured payload. Each case ships a prompt fragment plus the shape
the assembled payload should have.

Three cases per the skill-creator template: happy / edge / adversarial.
"""
import pytest

CASES = [
    {
        "name": "happy_clear_task",
        "input": "Build JWT auth in src/auth/, exclude billing.",
        "expected_keys": ["agent_type", "task", "focus_files", "exclude_files",
                           "success_criteria", "return_format"],
        "expected_in_focus": "src/auth",
        "expected_in_exclude": "billing",
    },
    {
        "name": "edge_vague_task",
        "input": "Make the auth thing better somehow.",
        "expected_action": "ask-clarification",
    },
    {
        "name": "adversarial_scope_creep_in_success",
        "input": "Build login. Success: works great, looks good, ready for review.",
        "expected_action": "rewrite-success-criteria",
        "expected_in_output": "pytest",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "input" in case
    # Each case must declare either expected_keys (happy) or expected_action (edge/adversarial)
    assert "expected_keys" in case or "expected_action" in case
