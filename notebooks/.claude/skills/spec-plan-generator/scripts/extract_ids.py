#!/usr/bin/env python3
"""extract_ids.py — extract REQ-NNN from PRD and COMP-NNN from SDD.

Usage: python extract_ids.py --prd PRD.md --sdd SDD.md
Prints JSON {reqs: [...], comps: [...]}.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQ_RE = re.compile(r"\bREQ-(\d+)\b")
COMP_RE = re.compile(r"\bCOMP-(\d+)\b")


def extract(text: str, pattern: re.Pattern, prefix: str) -> list[str]:
    nums = sorted({int(m) for m in pattern.findall(text)})
    if not nums:
        return []
    width = max(3, len(str(nums[-1])))
    return [f"{prefix}-{n:0{width}d}" for n in nums]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--prd", required=True, type=Path)
    p.add_argument("--sdd", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.prd.exists():
        print(f"error: PRD not found: {args.prd}", file=sys.stderr)
        return 1
    if not args.sdd.exists():
        print(f"error: SDD not found: {args.sdd}", file=sys.stderr)
        return 1
    out = {
        "reqs": extract(args.prd.read_text(encoding="utf-8"), REQ_RE, "REQ"),
        "comps": extract(args.sdd.read_text(encoding="utf-8"), COMP_RE, "COMP"),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
