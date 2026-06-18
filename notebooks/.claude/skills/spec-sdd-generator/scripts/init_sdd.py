#!/usr/bin/env python3
"""init_sdd.py — compute target .claude/specs/<feature>/SDD.md path.

Usage: python init_sdd.py --feature feature-search --specs-root .claude/specs
Exit 0 = printed path. 1 = error.
"""
import argparse
import re
import sys
from pathlib import Path


VALID = re.compile(r"^[a-z][a-z0-9-]+[a-z0-9]$")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feature", required=True)
    p.add_argument("--specs-root", required=True, type=Path)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not VALID.match(args.feature):
        print(f"error: feature must be kebab-case: {args.feature!r}", file=sys.stderr)
        return 1
    feature_dir = args.specs_root / args.feature
    feature_dir.mkdir(parents=True, exist_ok=True)
    target = feature_dir / "SDD.md"
    if target.exists() and not args.force:
        print(f"error: SDD exists: {target} (use --force)", file=sys.stderr)
        return 1
    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
