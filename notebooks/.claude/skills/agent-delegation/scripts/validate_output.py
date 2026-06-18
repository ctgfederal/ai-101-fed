#!/usr/bin/env python3
"""validate_output.py — validate a rendered delegation prompt file.

Checks:
  - All five required sections present in order: FOCUS, EXCLUDE, TASK, SUCCESS, RETURN.
  - FOCUS, EXCLUDE, and SUCCESS sections each contain at least one bullet OR
    the literal placeholder "_(none)_" (only allowed for EXCLUDE; FOCUS and
    SUCCESS must have non-empty real content).

Usage:
  python validate_output.py --file path/to/prompt.md

Exit codes:
  0  pass
  1  fail (errors on stderr)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List

REQUIRED_SECTIONS = ["FOCUS", "EXCLUDE", "TASK", "SUCCESS", "RETURN"]


def section_order(text: str) -> List[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]


def extract_section(text: str, name: str) -> str:
    """Return the body between '## name' and the next '## ' header (or EOF)."""
    pattern = rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s+|\Z)"
    m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def validate(text: str) -> List[str]:
    errors: List[str] = []
    found = section_order(text)
    found_set = set(found)

    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"missing section: ## {sec}")

    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: expected {REQUIRED_SECTIONS}, got {found}")

    # FOCUS must have bullets
    focus_body = extract_section(text, "FOCUS")
    if not focus_body or focus_body == "_(none)_":
        errors.append("FOCUS list is empty — at least one focus path required")
    elif not any(line.lstrip().startswith("- ") for line in focus_body.splitlines()):
        errors.append("FOCUS section has no bullet items")

    # SUCCESS must have bullets
    success_body = extract_section(text, "SUCCESS")
    if not success_body or success_body == "_(none)_":
        errors.append("SUCCESS list is empty — at least one success criterion required")
    elif not any(line.lstrip().startswith("- ") for line in success_body.splitlines()):
        errors.append("SUCCESS section has no bullet items")

    # EXCLUDE may be _(none)_ but not entirely missing body
    exclude_body = extract_section(text, "EXCLUDE")
    if not exclude_body:
        errors.append("EXCLUDE section is missing a body (use _(none)_ if intentional)")

    # TASK must be non-empty
    task_body = extract_section(text, "TASK")
    if not task_body:
        errors.append("TASK section is empty")

    # RETURN must be non-empty
    return_body = extract_section(text, "RETURN")
    if not return_body:
        errors.append("RETURN section is empty")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
