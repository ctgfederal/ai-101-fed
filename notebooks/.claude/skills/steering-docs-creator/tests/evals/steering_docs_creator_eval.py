"""LLM evals: filling steering sections from sparse context.

These cases exercise the LLM portion of the workflow — taking sparse user
input and producing structured section bodies that the validator accepts.
"""
from __future__ import annotations

import pytest

CASES = [
    {
        "name": "happy_clear_persona",
        "input": (
            "We sell HR software to mid-market companies. Buyers are CHROs; "
            "users are line managers."
        ),
        "doc": "product",
        "section": "User Personas",
        "expected_terms": ["CHRO", "manager"],
    },
    {
        "name": "happy_clear_tech_stack",
        "input": "Python 3.12 backend, Postgres 16, Next.js 14 frontend.",
        "doc": "tech",
        "section": "Tech Stack",
        "expected_terms": ["Python", "Postgres", "Next.js"],
    },
    {
        "name": "edge_sparse_phase",
        "input": "We just started.",
        "doc": "roadmap",
        "section": "Current Phase",
        "expected_action": "ask-clarification",
    },
    {
        "name": "adversarial_overspecified",
        "input": (
            "Stack: Rust 1.78 with tokio 1.36, sqlx 0.7, axum 0.7, plus "
            "pgvector 0.7 and so on for 40 more libs. Just record the stack."
        ),
        "doc": "tech",
        "section": "Tech Stack",
        "expected_action": "summarize-not-dump",
        "expected_terms": ["Rust"],
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case: dict) -> None:
    """Shape check — confirms the eval cases are well-formed.

    Real LLM evaluation requires running these through a model and grading
    the output; the harness only confirms the case definitions exist.
    """
    assert "name" in case
    assert "input" in case
    assert "doc" in case
    assert case["doc"] in ("product", "tech", "structure", "roadmap")
    assert "section" in case
