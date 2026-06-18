#!/usr/bin/env python3
"""extract_req_ids.py — list every REQ-NNN in a PRD file.

Usage: python extract_req_ids.py --prd .claude/specs/feature/PRD.md
Prints space-separated REQ-IDs (sorted by numeric value).
"""
import argparse
import re
import sys
from pathlib import Path


ID_RE = re.compile(r"\bREQ-(\d+)\b")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prd", required=True, type=Path)
    return p.parse_args()


def extract(text: str) -> list[str]:
    seen = set()
    for m in ID_RE.findall(text):
        seen.add(int(m))
    width = max(3, len(str(max(seen))) if seen else 3)
    return [f"REQ-{i:0{width}d}" for i in sorted(seen)]


def main() -> int:
    args = parse_args()
    if not args.prd.exists():
        print(f"error: PRD not found: {args.prd}", file=sys.stderr)
        return 1
    ids = extract(args.prd.read_text(encoding="utf-8"))
    print(" ".join(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
