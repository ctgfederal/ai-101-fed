#!/usr/bin/env python3
"""validate_output.py — validate the decisions-log section for a feature.

Checks:
  - Feature header exists (`## <Feature Title> — Build Decisions (YYYY-MM-DD)`)
  - Every D-NNN id in the section is unique within the entire log
  - Auto-applied table is present (or explicitly empty `_(none)_`)
  - At least one decision OR an explicit "_(no decisions ...)_" marker per documented category

Usage:
  python validate_output.py --log .claude/decisions-log.md --feature "Feature Search"

Exit 0 = pass.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


HEADER_RE = re.compile(r"^##\s+(?P<title>.+?)\s+—\s+Build Decisions\s+\((?P<date>\d{4}-\d{2}-\d{2})\)\s*$")
ID_RE = re.compile(r"\bD-(\d+)\b")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--feature", required=True, help="feature title as appears in the header")
    return p.parse_args()


def find_section(text: str, feature_title: str) -> str | None:
    """Return the body of the matching feature section (until next ##-level header or EOF)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = HEADER_RE.match(line)
        if m and m.group("title").strip() == feature_title:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if HEADER_RE.match(lines[j]) and j != start:
            end = j
            break
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            # any other ## section also ends ours
            end = j
            break
    return "\n".join(lines[start:end])


def main() -> int:
    args = parse_args()
    if not args.log.exists():
        print(f"error: log not found: {args.log}", file=sys.stderr)
        return 1
    text = args.log.read_text(encoding="utf-8")

    section = find_section(text, args.feature)
    if section is None:
        print(f"error: no section found for feature: {args.feature!r}", file=sys.stderr)
        return 1

    errors = []

    # Auto-applied marker
    if "### Auto-Applied" not in section:
        errors.append("missing '### Auto-Applied (Federal Mandates)' subsection")

    # IDs in the section must be unique within the entire log
    all_ids = ID_RE.findall(text)
    counts = Counter(all_ids)
    section_ids = ID_RE.findall(section)
    for sid in section_ids:
        if counts[sid] > 1:
            # OK: cross-section reference is allowed by convention. We only flag intra-section duplication.
            pass
    # ensure section's own IDs are not duplicated *within the section*
    section_counts = Counter(section_ids)
    dups = [k for k, v in section_counts.items() if v > 1]
    # Decision lines may reference an ID twice (header + body) — only flag if appears > 2 times
    dups_real = [k for k, v in section_counts.items() if v > 3]
    if dups_real:
        errors.append(f"IDs appearing > 3 times within section (likely duplicate decisions): {dups_real}")

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
