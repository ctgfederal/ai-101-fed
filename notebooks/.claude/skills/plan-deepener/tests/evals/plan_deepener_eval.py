"""LLM evals for research synthesis quality.

Cases exercise:
  - Happy: clear sections, multiple sources agreeing → clean dedup
  - Sparse: thin section, few sources → identifies "more research needed"
  - Contradictory: two sources disagree → preserves disagreement, doesn't pick a side
"""
import pytest

CASES = [
    {
        "name": "happy_clean_dedup",
        "section": "Use Postgres for write-heavy logs at 1k/s",
        "sources": [
            "Postgres docs: use UNLOGGED tables for high-volume non-durable inserts",
            "In-house solution archive: same recommendation, plus async commit",
        ],
        "expected_in_output": "UNLOGGED",
        "expected_dedup": True,  # one entry, two citations
    },
    {
        "name": "sparse_thin",
        "section": "Implement custom file format ABC",
        "sources": [],
        "expected_in_output": "more research",
        "expected_dedup": False,
    },
    {
        "name": "contradictory",
        "section": "Pick ORM for the data layer",
        "sources": [
            "Source A (in-house): 'Avoid heavy ORMs at this scale; use raw SQL'",
            "Source B (general docs): 'Modern ORMs match raw SQL performance'",
        ],
        "expected_in_output": "Sources disagree",
        "expected_dedup": False,
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    """Schema check; plug LLM in CI."""
    assert "name" in case
    assert "section" in case
