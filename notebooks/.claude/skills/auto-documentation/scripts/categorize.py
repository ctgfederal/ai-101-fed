#!/usr/bin/env python3
"""
categorize.py — heuristic classifier for a free-text insight.

Emits exactly one of:
  business-rule, technical-pattern, service-interface, domain-rule

The heuristic uses keyword scoring across four buckets. Ties break by precedence:
  service-interface > domain-rule > business-rule > technical-pattern.
This precedence reflects "external contract" being the most specific signal,
falling through to the most general "how we build" bucket.

Usage:
  python categorize.py --text "admins can edit any user post"

Exit codes:
  0  printed category to stdout
  1  empty text or other validation error
"""

import argparse
import logging
import re
import sys
from typing import Dict, List

CANONICAL = ("business-rule", "technical-pattern", "service-interface", "domain-rule")

# Precedence on tie — first wins.
PRECEDENCE: List[str] = ["service-interface", "domain-rule", "business-rule", "technical-pattern"]

# Per-bucket keywords. Each match scores +1.
KEYWORDS: Dict[str, List[str]] = {
    "service-interface": [
        "stripe", "auth0", "sendgrid", "twilio", "webhook", "webhooks",
        "third-party", "third party", "external api", "rest api",
        "rate limit", "rate-limit", "rate limits", "rate-limits",
        "oauth", "api contract", "contract drift", "rpc",
        "vendor", "upstream", "endpoint", "callback url",
        "retries", "retry policy", "idempotency-key",
    ],
    "domain-rule": [
        "invariant", "invariants",
        "cannot reference itself", "cannot equal", "cannot be",
        "must be", "must equal", "must not",
        "entity ", "aggregate", " state machine", "state-machine",
        " before paid", "before payment", "ship before",
        "single currency", "same currency",
        "raises if", "raises when",
    ],
    "business-rule": [
        "admin", "admins", "non-admin", "non-admins",
        "permission", "permissions", "authoriz", "role-based",
        "policy", "policies", "rbac",
        "pricing", "discount", "discounts",
        "refund", "refunds", "trial", "trial extension",
        "user can", "user cannot", "users can", "users cannot",
        "only their own", "own posts", "own records",
        "edit any", "edit only", "view only",
        "approval", "approve", "reject",
    ],
    "technical-pattern": [
        "caching", "cache strategy", "cache invalidation",
        "retry", "retry wrapper", "circuit breaker",
        "repository pattern", "repository class",
        "error envelope", "error handling", "error format",
        "background job", "worker queue", "job queue",
        "logging convention", "log format",
        "naming convention", "code structure",
        "we always", "we never", "we structure", "we wrap",
        "convention", "patterns",
    ],
}


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def score(text: str) -> Dict[str, int]:
    """Return per-bucket integer scores."""
    if not text or not text.strip():
        raise ValueError("text is empty")
    norm = " " + re.sub(r"\s+", " ", text.lower()).strip() + " "
    scores: Dict[str, int] = {c: 0 for c in CANONICAL}
    for bucket, keywords in KEYWORDS.items():
        for kw in keywords:
            kw_l = kw.lower()
            # word-ish match; allow short phrases too
            if " " in kw_l:
                if kw_l in norm:
                    scores[bucket] += 1
            else:
                # treat as whole word
                if re.search(rf"\b{re.escape(kw_l)}\b", norm):
                    scores[bucket] += 1
    return scores


def classify(text: str) -> str:
    """Return the winning category."""
    scores = score(text)
    max_score = max(scores.values())
    if max_score == 0:
        # nothing matched — fall through to most-general bucket.
        return "technical-pattern"
    # collect winners and apply precedence on tie
    winners = [c for c in CANONICAL if scores[c] == max_score]
    if len(winners) == 1:
        return winners[0]
    for c in PRECEDENCE:
        if c in winners:
            return c
    return winners[0]  # unreachable


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--text", required=True, help="free-text insight to classify")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("categorize")
    try:
        category = classify(args.text)
    except ValueError as e:
        log.error("%s", e)
        return 1
    print(category)
    return 0


if __name__ == "__main__":
    sys.exit(main())
