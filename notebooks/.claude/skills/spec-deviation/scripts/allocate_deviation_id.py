#!/usr/bin/env python3
"""allocate_deviation_id.py — allocate the next N DEV-NNN IDs.

Scans every `.claude/specs/*/SDD.md` under a specs root, finds the
largest existing DEV-NNN, and prints the next `--count` IDs (one per line)
starting from max+1. If no DEVs exist anywhere, allocation starts at DEV-001.

Usage:
  python allocate_deviation_id.py --specs-root .claude/specs --count 1
  python allocate_deviation_id.py --specs-root .claude/specs --count 5
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List

DEV_ID_RE = re.compile(r"\bDEV-(\d+)\b")


def find_max_dev_id(specs_root: Path) -> int:
    """Return the largest DEV-NNN integer found across all SDD.md files.

    Returns 0 if none found (so the first allocated ID will be DEV-001).
    """
    if not specs_root.is_dir():
        return 0
    max_id = 0
    for sdd in specs_root.glob("*/SDD.md"):
        try:
            text = sdd.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in DEV_ID_RE.finditer(text):
            n = int(m.group(1))
            if n > max_id:
                max_id = n
    return max_id


def allocate(specs_root: Path, count: int) -> List[str]:
    if count < 1:
        raise ValueError(f"count must be >= 1; got {count}")
    start = find_max_dev_id(specs_root) + 1
    return [f"DEV-{start + i:03d}" for i in range(count)]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--specs-root",
        required=True,
        type=Path,
        help="path to .claude/specs/ (containing per-feature subfolders)",
    )
    p.add_argument(
        "--count",
        type=int,
        default=1,
        help="number of IDs to allocate (default: 1)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        ids = allocate(args.specs_root, args.count)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for i in ids:
        print(i)
    return 0


if __name__ == "__main__":
    sys.exit(main())
