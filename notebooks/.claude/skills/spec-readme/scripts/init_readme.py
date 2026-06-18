#!/usr/bin/env python3
"""init_readme.py — create `<specs-root>/<feature>/README.md` from the template.

Renders `templates/readme.md.template` with these placeholders substituted:
  {{FEATURE}}        — the kebab-case feature name
  {{FEATURE_TITLE}}  — Title Case version of FEATURE (auto-derived if not given)
  {{CREATED}}        — today's ISO date (auto)

Usage:
  python init_readme.py --feature feature-search --specs-root .claude/specs
  python init_readme.py --feature feat-x --specs-root .claude/specs --force

Exit 0 = wrote. 1 = error (target exists w/o --force, bad feature name, missing template).
"""
import argparse
import datetime as _dt
import re
import sys
from pathlib import Path


VALID = re.compile(r"^[a-z][a-z0-9-]+[a-z0-9]$")


def derive_title(feature: str) -> str:
    """Convert kebab-case to Title Case."""
    return " ".join(word.capitalize() for word in feature.split("-"))


def render(template: str, feature: str, feature_title: str, created: str) -> str:
    return (template
            .replace("{{FEATURE_TITLE}}", feature_title)
            .replace("{{FEATURE}}", feature)
            .replace("{{CREATED}}", created))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feature", required=True,
                   help="kebab-case feature name (matches ^[a-z][a-z0-9-]+[a-z0-9]$)")
    p.add_argument("--specs-root", required=True, type=Path,
                   help="root containing per-feature spec folders (e.g. .claude/specs)")
    p.add_argument("--feature-title", default=None,
                   help="optional Title Case override (default: derived from --feature)")
    p.add_argument("--created", default=None,
                   help="optional ISO date override (default: today)")
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "readme.md.template",
                   help="path to the README template")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing README")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not VALID.match(args.feature):
        print(f"error: feature must be kebab-case: {args.feature!r}", file=sys.stderr)
        return 1
    if not args.template.exists():
        print(f"error: template not found: {args.template}", file=sys.stderr)
        return 1

    feature_title = args.feature_title or derive_title(args.feature)
    created = args.created or _dt.date.today().isoformat()

    feature_dir = args.specs_root / args.feature
    feature_dir.mkdir(parents=True, exist_ok=True)
    target = feature_dir / "README.md"
    if target.exists() and not args.force:
        print(f"error: README exists: {target} (use --force)", file=sys.stderr)
        return 1

    template = args.template.read_text(encoding="utf-8")
    rendered = render(template, args.feature, feature_title, created)
    target.write_text(rendered, encoding="utf-8")
    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
