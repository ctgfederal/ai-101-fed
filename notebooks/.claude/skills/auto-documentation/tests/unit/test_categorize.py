"""Unit tests for scripts/categorize.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from categorize import (
    classify,
    score,
    CANONICAL,
    PRECEDENCE,
    main as cat_main,
)


def test_canonical_set():
    assert set(CANONICAL) == {"business-rule", "technical-pattern", "service-interface", "domain-rule"}


def test_precedence_order():
    """Service-interface beats domain-rule beats business-rule beats technical-pattern."""
    assert PRECEDENCE == ["service-interface", "domain-rule", "business-rule", "technical-pattern"]


# --- classification happy paths ---

def test_business_rule_admin():
    assert classify("admins can edit any user post but non-admins only their own") == "business-rule"


def test_business_rule_pricing():
    assert classify("Pro trial extension policy: pro trial can be extended once max 14 days") == "business-rule"


def test_technical_pattern_caching():
    assert classify("Our caching strategy: we always wrap reads in the repository pattern") == "technical-pattern"


def test_technical_pattern_error_envelope():
    assert classify("Standard error envelope for all our API errors") == "technical-pattern"


def test_service_interface_stripe():
    assert classify("Stripe webhook retry policy uses exponential backoff for 3 days") == "service-interface"


def test_service_interface_oauth():
    assert classify("Auth0 OAuth token refresh contract") == "service-interface"


def test_domain_rule_invariant():
    assert classify("An Order cannot ship before payment; Order.ship! raises if paid_at is nil") == "domain-rule"


def test_domain_rule_self_reference():
    assert classify("A User cannot reference itself as parent — invariant") == "domain-rule"


# --- edge cases ---

def test_empty_text_raises():
    with pytest.raises(ValueError):
        classify("")


def test_whitespace_only_raises():
    with pytest.raises(ValueError):
        classify("   \n  ")


def test_no_keywords_falls_through_to_pattern():
    """Text with zero keyword hits should default to technical-pattern."""
    assert classify("xyzzy something something") == "technical-pattern"


def test_score_returns_all_buckets():
    s = score("admin permissions stripe webhook")
    assert set(s.keys()) == set(CANONICAL)


def test_tie_resolved_by_precedence():
    """When scores tie, precedence chooses service-interface > domain-rule > business-rule > technical-pattern."""
    # Construct text with exactly one keyword from each of two buckets.
    # 'admin' (business-rule, 1 hit) vs 'webhook' (service-interface, 1 hit)
    result = classify("admin webhook")
    assert result == "service-interface"


# --- main entry point ---

def _run_main(argv):
    old = sys.argv
    sys.argv = ["categorize.py"] + argv
    try:
        return cat_main()
    finally:
        sys.argv = old


def test_main_prints_category(capsys):
    rc = _run_main(["--text", "admins can edit any user post"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "business-rule"


def test_main_empty_text_exits_1(capsys):
    rc = _run_main(["--text", ""])
    assert rc == 1
