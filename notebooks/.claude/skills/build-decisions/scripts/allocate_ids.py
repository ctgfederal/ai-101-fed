#!/usr/bin/env python3
"""allocate_ids.py — find max D-NNN in decisions log and allocate the next batch.

Usage:
  python allocate_ids.py --log .claude/decisions-log.md --count 5
  → D-042 D-043 D-044 D-045 D-046

If --log doesn't exist or is empty, allocation starts at D-001.

Exit codes:
  0  printed allocation to stdout
  1  invalid arguments (count <= 0)
"""

import argparse
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"\bD-(\d+)\b")


def find_max(text: str) -> int:
    matches = ID_RE.findall(text)
    if not matches:
        return 0
    return max(int(m) for m in matches)


def allocate(text: str, count: int) -> list[str]:
    if count <= 0:
        raise ValueError(f"count must be > 0: {count}")
    start = find_max(text) + 1
    width = max(3, len(str(start + count - 1)))
    return [f"D-{i:0{width}d}" for i in range(start, start + count)]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--count", required=True, type=int)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        print(f"error: count must be > 0: {args.count}", file=sys.stderr)
        return 1
    text = args.log.read_text(encoding="utf-8") if args.log.exists() else ""
    try:
        ids = allocate(text, args.count)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(" ".join(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
