#!/usr/bin/env python3
"""validate_output.py — validate a deepened document.

Checks:
  - `## Deepening Summary` block exists at top
  - Every `### Research Insights` block has all 5 subsection labels:
    From Solutions Archive, Best Practices, Edge Cases, Performance, References

Usage:
  python validate_output.py --target path.md

Exit 0 = pass.
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SUBSECTIONS = ["From Solutions Archive", "Best Practices", "Edge Cases", "Performance", "References"]


def validate(text: str) -> list[str]:
    errors: list[str] = []
    if "## Deepening Summary" not in text:
        errors.append("missing '## Deepening Summary' block")

    # find each insights block and check its subsections
    insights_blocks = list(re.finditer(
        r"### Research Insights(.*?)(?=^###\s|^##\s|\Z)",
        text, flags=re.MULTILINE | re.DOTALL,
    ))
    if not insights_blocks:
        errors.append("no `### Research Insights` blocks found — was the merge run?")
    for m in insights_blocks:
        body = m.group(1)
        for sub in REQUIRED_SUBSECTIONS:
            if f"**{sub}:**" not in body:
                errors.append(f"insights block missing subsection: {sub}")
                break  # one error per block is enough
    return errors


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--target", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.target.exists():
        print(f"error: target not found: {args.target}", file=sys.stderr)
        return 1
    text = args.target.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
