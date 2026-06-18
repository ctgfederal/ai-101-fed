#!/usr/bin/env python3
"""validate_handoff.py — validate a handoff JSON payload against the schema.

Schema (from knowledge/handoff-schema.md):
  Required:
    from_agent           : non-empty string
    to_agent             : non-empty string (must differ from from_agent)
    task                 : non-empty string
    context_files        : list of strings (may be empty)
    success_criteria     : non-empty list of strings
    return_format        : non-empty string
  Optional:
    deadline             : string (free-form)
    output_type          : string (used by check_chain.py)
    expected_input_type  : string (used by check_chain.py)

Output JSON shape:
  {"valid": bool, "errors": [str, ...]}

Usage:
  python validate_handoff.py --file path/to/handoff.json
  python validate_handoff.py --stdin < handoff.json
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, List

REQUIRED_STRING_FIELDS = ["from_agent", "to_agent", "task", "return_format"]
REQUIRED_LIST_FIELDS = ["context_files", "success_criteria"]
OPTIONAL_FIELDS = ["deadline", "output_type", "expected_input_type"]
ALL_KNOWN_FIELDS = set(REQUIRED_STRING_FIELDS + REQUIRED_LIST_FIELDS + OPTIONAL_FIELDS)


def validate(payload: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    for field in REQUIRED_STRING_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")
            continue
        v = payload[field]
        if not isinstance(v, str):
            errors.append(f"{field} must be a string, got {type(v).__name__}")
        elif not v.strip():
            errors.append(f"{field} must be non-empty")

    for field in REQUIRED_LIST_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")
            continue
        v = payload[field]
        if not isinstance(v, list):
            errors.append(f"{field} must be a list, got {type(v).__name__}")
            continue
        for i, item in enumerate(v):
            if not isinstance(item, str):
                errors.append(f"{field}[{i}] must be a string")
        if field == "success_criteria" and isinstance(v, list) and len(v) == 0:
            errors.append("success_criteria must be non-empty")

    # from_agent must differ from to_agent
    fa = payload.get("from_agent")
    ta = payload.get("to_agent")
    if isinstance(fa, str) and isinstance(ta, str) and fa.strip() and ta.strip():
        if fa.strip() == ta.strip():
            errors.append("from_agent and to_agent must differ (self-handoff is a cycle)")

    # optional fields type check
    for field in OPTIONAL_FIELDS:
        if field in payload:
            v = payload[field]
            if not isinstance(v, str):
                errors.append(f"{field} must be a string when present")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", type=Path, help="path to handoff JSON")
    g.add_argument("--stdin", action="store_true", help="read JSON from stdin")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.stdin:
            text = sys.stdin.read()
        else:
            if not args.file.exists():
                print(f"error: file not found: {args.file}", file=sys.stderr)
                return 1
            text = args.file.read_text(encoding="utf-8")
        if not text.strip():
            print(json.dumps({"valid": False, "errors": ["empty input"]}, indent=2))
            return 1
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "errors": [f"invalid JSON: {e}"]}, indent=2))
        return 1

    errors = validate(payload)
    valid = len(errors) == 0
    print(json.dumps({"valid": valid, "errors": errors}, indent=2))
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
