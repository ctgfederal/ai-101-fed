"""LLM evals: fixture cases for traceability matrix construction."""
import pytest

CASES = [
    {
        "name": "full_coverage",
        "description": "All four layers populated for every REQ",
        "expected_status": "covered",
    },
    {
        "name": "partial_missing_test_layer",
        "description": "SDD + PLAN + code present, no test references",
        "expected_status": "partial",
    },
    {
        "name": "uncovered_req",
        "description": "REQ defined in PRD with no downstream work",
        "expected_status": "uncovered",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_case_shape(case):
    assert "name" in case
    assert "expected_status" in case
    assert case["expected_status"] in {"covered", "partial", "uncovered"}
