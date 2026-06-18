#!/usr/bin/env python3
"""
generate_slug.py — produce a YYYY-MM-DD-<kebab-slug>.md filename for a solution.

Usage:
  python generate_slug.py --title "N+1 query in brief generation"
  python generate_slug.py --title "..." --date 2026-02-14

Exit codes:
  0  printed filename to stdout
  1  invalid input
"""

import argparse
import re
import sys
import unicodedata
from datetime import date, datetime

MAX_SLUG_LEN = 60


def slugify(title: str) -> str:
    """Lowercase, ASCII-fold, replace non-alphanumeric with hyphen, collapse."""
    if not title or not title.strip():
        raise ValueError("title is empty")
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered)
    slug = slug.strip("-")
    if not slug:
        raise ValueError(f"title produced empty slug: {title!r}")
    if len(slug) > MAX_SLUG_LEN:
        slug = slug[:MAX_SLUG_LEN].rstrip("-")
    return slug


def parse_date(s: str) -> date:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"date must be YYYY-MM-DD: {s!r}") from e


def build_filename(title: str, when: date) -> str:
    return f"{when.isoformat()}-{slugify(title)}.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--title", required=True, help="problem title")
    p.add_argument("--date", default=None, help="date in YYYY-MM-DD (default: today)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        when = parse_date(args.date) if args.date else date.today()
        print(build_filename(args.title, when))
        return 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
