"""LLM evals: spec-readme actions on different starting states.

The deterministic scripts are the source of truth; the LLM's job is only
to choose the right script and invoke it. These cases assert the eval
shape is well-formed.
"""
import pytest

CASES = [
    {
        "name": "init_from_empty",
        "starting_state": "empty",      # README does not exist
        "action": "init",
        "expected_script": "init_readme.py",
        "expected_doc_count": 3,
    },
    {
        "name": "approve_prd",
        "starting_state": "draft",      # README exists, all draft
        "action": "update_status",
        "expected_script": "update_status.py",
        "expected_status_after": "approved",
    },
    {
        "name": "append_phase_note",
        "starting_state": "approved",   # PRD/SDD/PLAN approved, mid-implement
        "action": "append_phase_note",
        "expected_script": "append_phase_note.py",
        "expected_phase_count_min": 1,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "starting_state" in case
    assert case["starting_state"] in {"empty", "draft", "approved"}
    assert case["action"] in {"init", "update_status", "append_phase_note"}
    assert case["expected_script"].endswith(".py")
