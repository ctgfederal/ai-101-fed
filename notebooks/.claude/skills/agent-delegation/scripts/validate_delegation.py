#!/usr/bin/env python3
"""validate_delegation.py — validate a single delegation JSON payload.

Required keys:
  agent_type        non-empty string
  task              non-empty string
  focus_files       list of strings (may be empty)
  exclude_files     list of strings (may be empty)
  success_criteria  list with >=1 non-empty string item
  return_format     non-empty string

Additional checks:
  - FOCUS and EXCLUDE must not overlap (a path appearing in both is ambiguous).
  - All entries in focus_files / exclude_files / success_criteria must be strings.

Usage:
  python validate_delegation.py --payload <path-or-stdin>

Exit codes:
  0  valid
  1  invalid (errors on stderr)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

REQUIRED_KEYS = ["agent_type", "task", "focus_files", "exclude_files", "success_criteria", "return_format"]


def validate(p: dict) -> List[str]:
    errors: List[str] = []

    missing = [k for k in REQUIRED_KEYS if k not in p]
    if missing:
        errors.append(f"missing keys: {missing}")
        return errors

    if not isinstance(p["agent_type"], str) or not p["agent_type"].strip():
        errors.append("agent_type must be a non-empty string")
    if not isinstance(p["task"], str) or not p["task"].strip():
        errors.append("task must be a non-empty string")
    if not isinstance(p["return_format"], str) or not p["return_format"].strip():
        errors.append("return_format must be a non-empty string")

    if not isinstance(p["focus_files"], list):
        errors.append("focus_files must be a list")
    else:
        for i, item in enumerate(p["focus_files"]):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"focus_files[{i}] must be a non-empty string")

    if not isinstance(p["exclude_files"], list):
        errors.append("exclude_files must be a list")
    else:
        for i, item in enumerate(p["exclude_files"]):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"exclude_files[{i}] must be a non-empty string")

    if not isinstance(p["success_criteria"], list) or len(p["success_criteria"]) < 1:
        errors.append("success_criteria must be a list with at least 1 item")
    else:
        for i, item in enumerate(p["success_criteria"]):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"success_criteria[{i}] must be a non-empty string")

    if isinstance(p.get("focus_files"), list) and isinstance(p.get("exclude_files"), list):
        focus_set = {f.strip().rstrip("/") for f in p["focus_files"] if isinstance(f, str)}
        exclude_set = {f.strip().rstrip("/") for f in p["exclude_files"] if isinstance(f, str)}
        overlap = focus_set & exclude_set
        if overlap:
            errors.append(f"FOCUS and EXCLUDE overlap on: {sorted(overlap)}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None, help="path to JSON payload (omit to read stdin)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        if not text.strip():
            print("error: empty payload", file=sys.stderr)
            return 1
        payload = json.loads(text)
    except (OSError, json.JSONDecodeError) as e:
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
