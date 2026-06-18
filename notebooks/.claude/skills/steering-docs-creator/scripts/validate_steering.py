#!/usr/bin/env python3
"""validate_steering.py — validate every doc in a steering root.

Checks all four required steering docs exist and each has its required
sections in the correct order, per knowledge/steering-schema.md.

Usage:
  python validate_steering.py --steering-root .claude/steering
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_output import REQUIRED_SECTIONS, validate_doc  # noqa: E402

DOCS = ("product", "tech", "structure", "roadmap")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--steering-root", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root: Path = args.steering_root
    if not root.is_dir():
        print(f"error: steering root not a directory: {root}", file=sys.stderr)
        return 1

    any_fail = False
    print(f"=== steering validation: {root} ===")
    for doc in DOCS:
        path = root / f"{doc}.md"
        if not path.is_file():
            print(f"  FAIL  {doc}.md missing")
            any_fail = True
            continue
        errors = validate_doc(path.read_text(encoding="utf-8"), doc)
        if errors:
            print(f"  FAIL  {doc}.md")
            for e in errors:
                print(f"          {e}")
            any_fail = True
        else:
            n = len(REQUIRED_SECTIONS[doc])
            print(f"  PASS  {doc}.md ({n} sections)")

    print("")
    print("result: " + ("FAIL" if any_fail else "PASS"))
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
