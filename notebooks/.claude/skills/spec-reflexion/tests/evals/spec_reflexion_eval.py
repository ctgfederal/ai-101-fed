"""LLM evals: classifying borderline learnings and naming memory files.

The deterministic classifier handles the obvious cases. Borderline phrasing
(mixed signals, sparse context, adversarial decoys) is where the LLM's
narrative judgement matters. These cases assert the eval shape; the LLM is
expected to read the test inputs and produce outputs that match the shape.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from classify_learning import classify  # noqa: E402


CASES = [
    {
        "name": "happy_clear_global",
        "text": "Josh prefers explicit error types over Result wrappers — clearer stack traces.",
        "expected_scope": "global",
        "expected_type": "user",
    },
    {
        "name": "happy_clear_local",
        "text": "REQ-104 was renumbered after the merge; updated three downstream files in src/api/.",
        "expected_scope": "local",
        "expected_type": None,  # not promoted
    },
    {
        "name": "edge_mixed_signals",
        "text": "We learned that React 19 useOptimistic should be wrapped in a try/catch in our forms.",
        "expected_scope_options": {"local", "global"},
        "expected_type": "project",
    },
    {
        "name": "adversarial_decoy_local",
        "text": "Always use REQ-something when referencing a requirement.",
        "expected_scope_options": {"local", "global"},
        "expected_type": "feedback",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    assert "name" in case
    assert "text" in case
    assert isinstance(case["text"], str) and case["text"].strip()
    assert case.get("expected_scope") in {"local", "global", None}
    assert case.get("expected_type") in {"feedback", "project", "reference", "user", None}


def test_eval_classifier_agrees_on_clear_cases():
    for case in CASES:
        if "expected_scope" in case:
            scope, _ = classify(case["text"])
            assert scope == case["expected_scope"], (
                f"{case['name']}: expected {case['expected_scope']}, got {scope}"
            )


def test_eval_classifier_returns_known_value_on_borderline():
    for case in CASES:
        if "expected_scope_options" in case:
            scope, _ = classify(case["text"])
            assert scope in case["expected_scope_options"], (
                f"{case['name']}: got {scope!r}, "
                f"expected one of {case['expected_scope_options']}"
            )
