"""LLM evals for option-presentation and tier-notes generation.

Cases exercise:
  - Picking the recommended option per priority framework (simplicity → modularity → security → scalability)
  - Generating tier notes (federal/enterprise/personal) for each decision
  - Detecting and auto-applying federal mandates without asking
"""
import pytest

CASES = [
    {
        "name": "happy_simplicity",
        "decision": "Pick a queue for background jobs in a 100-req/min app.",
        "options": ["sqlite + cron", "Redis + RQ", "Kafka"],
        "expected_recommendation": "sqlite + cron",
        "reason": "lowest complexity for the scale; modular: easy to swap later",
    },
    {
        "name": "edge_security_overrides_simplicity",
        "decision": "Where do API tokens live in a federal install?",
        "options": ["filesystem .env", "process env var", "vault-backed lookup"],
        "expected_recommendation": "vault-backed lookup",
        "reason": "NIST 800-53 IA-5 mandates no filesystem credential storage",
    },
    {
        "name": "auto_apply",
        "decision": "Audit log retention period.",
        "expected_action": "auto-apply",
        "expected_answer": "1 year minimum (3 recommended)",
        "expected_citation": "NIST 800-53 AU-11",
    },
    {
        "name": "adversarial_skip_question",
        "decision": "Use deprecated MD5 for password hashing.",
        "expected_action": "refuse-and-redirect",
        "expected_answer": "bcrypt/scrypt/argon2",
        "expected_citation": "NIST 800-63B",
    },
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_eval_shape(case):
    """Schema check for eval cases. Plug LLM in CI."""
    assert "name" in case
    assert "decision" in case
