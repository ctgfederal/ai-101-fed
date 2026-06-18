#!/usr/bin/env python3
"""validate_match_query.py — validate a match-query JSON payload.

Schema:
  {
    "keywords": ["str", ...],     # required, 1..32 strings
    "min_score": 0.0..1.0,         # optional, default 0.0
    "max_results": int >= 1        # optional, default unlimited
  }

Usage:
  python validate_match_query.py --file query.json
  cat query.json | python validate_match_query.py

Exit 0 = valid, 1 = invalid (errors on stderr).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    if "keywords" not in payload:
        errors.append("missing required field: keywords")
    else:
        kw = payload["keywords"]
        if not isinstance(kw, list):
            errors.append("keywords must be a list")
        else:
            if not (1 <= len(kw) <= 32):
                errors.append(f"keywords must have 1..32 items, got {len(kw)}")
            for i, k in enumerate(kw):
                if not isinstance(k, str) or not k.strip():
                    errors.append(f"keywords[{i}] must be a non-empty string")

    if "min_score" in payload:
        ms = payload["min_score"]
        if not isinstance(ms, (int, float)):
            errors.append("min_score must be a number")
        elif not (0.0 <= float(ms) <= 1.0):
            errors.append(f"min_score must be in 0.0..1.0, got {ms}")

    if "max_results" in payload:
        mr = payload["max_results"]
        if not isinstance(mr, int) or isinstance(mr, bool) or mr < 1:
            errors.append(f"max_results must be a positive int, got {mr!r}")

    extras = set(payload.keys()) - {"keywords", "min_score", "max_results"}
    if extras:
        errors.append(f"unexpected fields: {sorted(extras)}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", type=Path, default=None, help="JSON file (default: stdin)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    if not text.strip():
        print("error: empty input", file=sys.stderr)
        return 1
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
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
