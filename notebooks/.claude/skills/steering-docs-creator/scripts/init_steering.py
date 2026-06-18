#!/usr/bin/env python3
"""init_steering.py — scaffold the four steering docs from templates.

Creates `<steering-root>/` if absent and writes `product.md`, `tech.md`,
`structure.md`, `roadmap.md` from `templates/<doc>.md.template`.

Idempotent: re-running on a populated tree exits 0 and changes nothing,
unless `--force` is set, in which case existing files are overwritten.

Usage:
  python init_steering.py --steering-root .claude/steering
  python init_steering.py --steering-root .claude/steering --only product
  python init_steering.py --steering-root .claude/steering --force
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DOCS = ("product", "tech", "structure", "roadmap")
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def template_path(doc: str) -> Path:
    return TEMPLATES_DIR / f"{doc}.md.template"


def target_path(steering_root: Path, doc: str) -> Path:
    return steering_root / f"{doc}.md"


def scaffold_one(steering_root: Path, doc: str, force: bool) -> tuple[bool, str]:
    """Returns (wrote, message)."""
    src = template_path(doc)
    dst = target_path(steering_root, doc)
    if not src.is_file():
        return (False, f"error: missing template {src}")
    if dst.exists() and not force:
        return (False, f"skip: {dst} exists (use --force to overwrite)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return (True, f"wrote: {dst}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--steering-root", required=True, type=Path)
    p.add_argument("--force", action="store_true",
                   help="overwrite existing steering docs")
    p.add_argument("--only", choices=DOCS, default=None,
                   help="scaffold only one doc kind")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = (args.only,) if args.only else DOCS

    any_error = False
    for doc in targets:
        ok, msg = scaffold_one(args.steering_root, doc, args.force)
        # missing-template is the only fatal case; "skip" is fine
        if not ok and msg.startswith("error:"):
            print(msg, file=sys.stderr)
            any_error = True
        else:
            print(msg)
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
