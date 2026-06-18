#!/usr/bin/env python3
"""allocate_req_ids.py — find max REQ-NNN across .claude/specs and allocate next batch.

Usage:
  python allocate_req_ids.py --specs-root .claude/specs --count 8

Exit 0 = printed batch. 1 = invalid count.
"""
import argparse
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"\bREQ-(\d+)\b")


def find_max(specs_root: Path) -> int:
    if not specs_root.is_dir():
        return 0
    max_id = 0
    for prd in specs_root.rglob("PRD.md"):
        try:
            text = prd.read_text(encoding="utf-8")
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
    return [f"REQ-{i:0{width}d}" for i in range(start, start + count)]


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
    start = find_max(args.specs_root) + 1
    print(" ".join(allocate(start, args.count)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
