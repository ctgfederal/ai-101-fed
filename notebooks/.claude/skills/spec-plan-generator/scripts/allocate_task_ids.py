#!/usr/bin/env python3
"""allocate_task_ids.py — find max T-NNN across .claude/specs/ and allocate next batch.

Usage: python allocate_task_ids.py --specs-root .claude/specs --count 10
"""
import argparse
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"\bT-(\d+)\b")


def find_max(specs_root: Path) -> int:
    if not specs_root.is_dir():
        return 0
    max_id = 0
    for plan in specs_root.rglob("PLAN.md"):
        try:
            text = plan.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in ID_RE.findall(text):
            v = int(m)
            if v > max_id:
                max_id = v
    return max_id


def allocate(start: int, count: int) -> list[str]:
    if count <= 0:
        raise ValueError(f"count must be > 0: {count}")
    width = max(3, len(str(start + count - 1)))
    return [f"T-{i:0{width}d}" for i in range(start, start + count)]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--specs-root", required=True, type=Path)
    p.add_argument("--count", required=True, type=int)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        print(f"error: count must be > 0: {args.count}", file=sys.stderr)
        return 1
    print(" ".join(allocate(find_max(args.specs_root) + 1, args.count)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
