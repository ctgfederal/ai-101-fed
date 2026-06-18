#!/usr/bin/env python3
"""validate_output.py — validate a rendered handoff prompt.

Checks:
  - All six required `##` sections present and in order: FROM, TO, TASK,
    CONTEXT, SUCCESS, RETURN
  - Optional `## DEADLINE` section, if present, comes after `## RETURN`
  - No unsubstituted `{{TOKEN}}` placeholders

Usage:
  python validate_output.py --file path/to/prompt.md
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List

REQUIRED_SECTIONS = ["FROM", "TO", "TASK", "CONTEXT", "SUCCESS", "RETURN"]
OPTIONAL_SECTIONS = ["DEADLINE"]
ALL_SECTIONS = REQUIRED_SECTIONS + OPTIONAL_SECTIONS

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")


def validate(text: str) -> List[str]:
    errors: List[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    found = [m.group(1).strip() for m in HEADING_RE.finditer(text)]

    # required sections present
    for sect in REQUIRED_SECTIONS:
        if sect not in found:
            errors.append(f"missing required section: ## {sect}")

    # required sections in order (allowing optional DEADLINE at the end)
    required_indices = [(s, found.index(s)) for s in REQUIRED_SECTIONS if s in found]
    if [i for _, i in required_indices] != sorted(i for _, i in required_indices):
        errors.append(f"required sections out of order: {[s for s, _ in required_indices]}")

    # optional DEADLINE — if present, must come AFTER all required sections
    for opt in OPTIONAL_SECTIONS:
        if opt in found:
            opt_idx = found.index(opt)
            for req in REQUIRED_SECTIONS:
                if req in found and found.index(req) > opt_idx:
                    errors.append(f"optional section {opt} appears before required {req}")
                    break

    # unknown ## sections (warn-style — surface as error to keep output strict)
    for f in found:
        if f not in ALL_SECTIONS:
            errors.append(f"unknown section: ## {f}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
