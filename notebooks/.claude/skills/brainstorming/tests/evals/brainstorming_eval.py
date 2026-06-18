"""LLM evals for the clarity-assessment + question-flow steps.

The deterministic parts of brainstorming are tested via unit tests. The
LLM-driven parts are:
  1. Clarity assessment (clear / directional / exploratory)
  2. Adaptive question pruning (skip questions already answered)
  3. Stop detection (knowing when vision is clear)

These cases exercise that judgment. Replace the assert with a real LLM
call when wiring into a CI eval framework.
"""
import pytest

CASES = [
    {
        "name": "clear",
        "input": (
            "I want to build a CLI tool for solo developers that runs offline-only "
            "AI code review on staged git diffs. Audience: indie hackers and "
            "contractors. Outcome: catch bugs pre-push, save time on PR review. "
            "Principles: speed over completeness, no PII to third parties."
        ),
        "expected_classification": "clear",
        "expected_action": "skip-to-build",
    },
    {
        "name": "directional",
        "input": "I want to build something for solo devs around code review.",
        "expected_classification": "directional",
        "expected_action": "ask-3-to-5",
    },
    {
        "name": "exploratory",
        "input": "I have an idea about AI in dev tools but I'm not sure what.",
        "expected_classification": "exploratory",
        "expected_action": "full-walk",
    },
    {
        "name": "design-attempt",
        "input": "Let's brainstorm — I want to build it in Rust with sled for storage.",
        "expected_classification": "directional",
        "expected_action": "redirect-to-build",  # technical decisions don't belong here
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_clarity_classification_shape(case):
    """Schema-check on eval cases. Plug in real LLM calls in CI."""
    assert case["expected_classification"] in {"clear", "directional", "exploratory"}
    assert case["expected_action"] in {"skip-to-build", "ask-3-to-5", "full-walk", "redirect-to-build"}
