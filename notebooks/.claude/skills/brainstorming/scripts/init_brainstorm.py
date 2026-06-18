#!/usr/bin/env python3
"""init_brainstorm.py — create the brainstorms/ root and compute the target file path.

Usage:
  python init_brainstorm.py --topic "AI code review" --brainstorms-root .claude/brainstorms

Exit codes:
  0  printed full target path; ready for write_brainstorm.py
  1  validation error (target exists w/o --force, empty topic)
"""

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

MAX_SLUG = 60


def slugify(s: str) -> str:
    if not s or not s.strip():
        raise ValueError("topic is empty")
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    if not slug:
        raise ValueError(f"topic produced empty slug: {s!r}")
    return slug[:MAX_SLUG].rstrip("-")


def compute_path(brainstorms_root: Path, topic: str, when: date) -> Path:
    return brainstorms_root / f"{when.isoformat()}-{slugify(topic)}.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--topic", required=True)
    p.add_argument("--brainstorms-root", required=True, type=Path)
    p.add_argument("--date", default=None)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        when = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
        args.brainstorms_root.mkdir(parents=True, exist_ok=True)
        target = compute_path(args.brainstorms_root, args.topic, when)
        if target.exists() and not args.force:
            print(f"error: target exists: {target} (use --force)", file=sys.stderr)
            return 1
        print(str(target))
        return 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
