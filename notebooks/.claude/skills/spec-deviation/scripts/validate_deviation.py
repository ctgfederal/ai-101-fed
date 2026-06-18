#!/usr/bin/env python3
"""validate_deviation.py — validate a deviation JSON payload against the schema.

Required fields: spec_id, deviation_id, reason_category, description,
original_decision, proposed_change, impact, status, approver, date.

Allowed reason_category values:
  technical-blocker, scope-clarification, dependency-conflict,
  performance-required, security-required.

Allowed status values: proposed, approved, rejected.

DEV ID format: DEV-NNN (3+ digits).
Original decision format: REQ-NNN, COMP-NNN, or D-NNN.

Usage:
  python validate_deviation.py --payload path/to/payload.json
  cat payload.json | python validate_deviation.py
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

REQUIRED_FIELDS = [
    "spec_id",
    "deviation_id",
    "reason_category",
    "description",
    "original_decision",
    "proposed_change",
    "impact",
    "status",
    "approver",
    "date",
]

ALLOWED_REASON_CATEGORIES = {
    "technical-blocker",
    "scope-clarification",
    "dependency-conflict",
    "performance-required",
    "security-required",
}

ALLOWED_STATUSES = {"proposed", "approved", "rejected"}

DEV_ID_RE = re.compile(r"^DEV-\d{3,}$")
ORIGINAL_DECISION_RE = re.compile(r"^(REQ|COMP|D)-\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(payload: dict) -> List[str]:
    errors: List[str] = []

    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    # Required fields
    for f in REQUIRED_FIELDS:
        if f not in payload:
            errors.append(f"missing required field: {f}")
            continue
        v = payload[f]
        if not isinstance(v, str) or not v.strip():
            errors.append(f"field {f!r} must be a non-empty string; got {v!r}")

    # If any required field is missing, stop further per-value checks for that field
    if "deviation_id" in payload and isinstance(payload["deviation_id"], str):
        if not DEV_ID_RE.match(payload["deviation_id"]):
            errors.append(
                f"deviation_id must match ^DEV-\\d{{3,}}$; got {payload['deviation_id']!r}"
            )

    if "reason_category" in payload and isinstance(payload["reason_category"], str):
        if payload["reason_category"] not in ALLOWED_REASON_CATEGORIES:
            errors.append(
                f"reason_category must be one of {sorted(ALLOWED_REASON_CATEGORIES)}; "
                f"got {payload['reason_category']!r}"
            )

    if "status" in payload and isinstance(payload["status"], str):
        if payload["status"] not in ALLOWED_STATUSES:
            errors.append(
                f"status must be one of {sorted(ALLOWED_STATUSES)}; got {payload['status']!r}"
            )

    if "original_decision" in payload and isinstance(payload["original_decision"], str):
        if not ORIGINAL_DECISION_RE.match(payload["original_decision"]):
            errors.append(
                f"original_decision must match ^(REQ|COMP|D)-\\d+$; "
                f"got {payload['original_decision']!r}"
            )

    if "date" in payload and isinstance(payload["date"], str):
        if not DATE_RE.match(payload["date"]):
            errors.append(f"date must match YYYY-MM-DD; got {payload['date']!r}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--payload",
        type=Path,
        default=None,
        help="path to deviation JSON payload (omit to read stdin)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.payload:
            text = args.payload.read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
        if not text.strip():
            print("error: empty payload", file=sys.stderr)
            return 1
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    errors = validate(payload)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
