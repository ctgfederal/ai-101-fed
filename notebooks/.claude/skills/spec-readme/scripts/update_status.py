#!/usr/bin/env python3
"""update_status.py — toggle PRD/SDD/PLAN status in a spec README.

Replaces the Status table row for the chosen --doc with the new --status and
updates its Last Update column to today (ISO date). Aborts if README missing
or status block malformed.

Usage:
  python update_status.py --feature feature-search --specs-root .claude/specs \\
      --doc prd --status approved
"""
import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

ALLOWED_DOCS = ("prd", "sdd", "plan")
ALLOWED_STATUSES = ("draft", "approved", "deprecated")

# Match a row like: `| PRD | draft | 2026-05-08 |` (any whitespace, any of the
# 3 statuses, any value in last column).
ROW_RE_FMT = (
    r"^\|\s*({DOC})\s*\|\s*(draft|approved|deprecated)\s*\|"
    r"\s*[^|]*\s*\|\s*$"
)


def update_row(text: str, doc: str, status: str, today: str) -> str:
    pattern = re.compile(ROW_RE_FMT.format(DOC=doc.upper()), flags=re.MULTILINE)
    new_row = f"| {doc.upper()} | {status} | {today} |"
    new_text, n = pattern.subn(new_row, text, count=1)
    if n == 0:
        raise ValueError(
            f"could not find Status table row for {doc.upper()} "
            f"(expected `| {doc.upper()} | <status> | <date> |`)"
        )
    return new_text


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feature", required=True)
    p.add_argument("--specs-root", required=True, type=Path)
    p.add_argument("--doc", required=True, choices=ALLOWED_DOCS,
                   help="which doc's status to update")
    p.add_argument("--status", required=True, choices=ALLOWED_STATUSES,
                   help="new status value")
    p.add_argument("--today", default=None,
                   help="optional ISO date override (default: today)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    target = args.specs_root / args.feature / "README.md"
    if not target.exists():
        print(f"error: README not found: {target}", file=sys.stderr)
        return 1

    today = args.today or _dt.date.today().isoformat()
    text = target.read_text(encoding="utf-8")
    try:
        new_text = update_row(text, args.doc, args.status, today)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    target.write_text(new_text, encoding="utf-8")
    print(f"{target}: {args.doc.upper()} -> {args.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
