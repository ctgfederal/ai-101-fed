#!/usr/bin/env python3
"""validate_output.py — validate a single steering doc against its schema.

Checks:
  - File exists and is readable
  - All required headings for the doc kind are present
  - Required headings appear in the order set by knowledge/steering-schema.md

Usage:
  python validate_output.py --file .claude/steering/product.md --doc product
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Authoritative schema (mirrors knowledge/steering-schema.md).
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "product": [
        "Mission",
        "User Personas",
        "Business Constraints",
        "Success Metrics Framework",
        "Domain Glossary",
    ],
    "tech": [
        "Tech Stack",
        "Conventions",
        "Library Choices",
        "Build & CI",
        "Observability",
    ],
    "structure": [
        "Layer Model",
        "Folder Layout",
        "Naming Rules",
        "Dependency Direction",
        "Module Boundaries",
    ],
    "roadmap": [
        "Current Phase",
        "Phase Definitions",
        "Milestones",
        "Out-of-Scope",
    ],
}

H2_RE = re.compile(r"^##\s+(.+?)\s*$", flags=re.MULTILINE)


def find_h2_headings(text: str) -> list[str]:
    """Return the list of `## ` headings in document order, trimmed."""
    return [m.group(1).strip() for m in H2_RE.finditer(text)]


def validate_doc(text: str, doc: str) -> list[str]:
    """Return a list of error strings; empty list means pass."""
    if doc not in REQUIRED_SECTIONS:
        return [f"unknown doc kind: {doc!r} (allowed: {sorted(REQUIRED_SECTIONS)})"]

    errors: list[str] = []
    required = REQUIRED_SECTIONS[doc]
    found = find_h2_headings(text)
    found_set = set(found)

    # Presence
    for h in required:
        if h not in found_set:
            errors.append(f"missing section: ## {h}")

    # Order — only meaningful when all required are present
    present_indices = [found.index(h) for h in required if h in found_set]
    if len(present_indices) == len(required) and present_indices != sorted(present_indices):
        errors.append(f"sections out of order: required {required}, found {found}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--doc", required=True, choices=sorted(REQUIRED_SECTIONS.keys()))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    errors = validate_doc(text, args.doc)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"OK: {args.file} ({args.doc})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
