#!/usr/bin/env python3
"""
write_solution.py — render the solution template from a JSON payload and write
the file to .claude/solutions/<category>/<slug>.md.

The payload (JSON, on stdin or in --payload <file>) must have these keys:

  {
    "title":              "string",
    "category":           "performance-issues",
    "date":               "YYYY-MM-DD",
    "tags":               ["tag1", "tag2"],
    "module":             "BriefGenerator",
    "symptom":            "one-sentence symptom",
    "root_cause":         "one-sentence cause",
    "severity":           "high",                  # optional, default ""
    "symptom_body":       "markdown",
    "investigation_body": "markdown",
    "root_cause_body":    "markdown",
    "solution_body":      "markdown",
    "verification_body":  "markdown",
    "prevention_body":    "markdown",
    "related_body":       "markdown"               # optional, default ""
  }

Usage:
  python write_solution.py --payload payload.json --solutions-root .claude/solutions
  cat payload.json | python write_solution.py --solutions-root .claude/solutions

Exit codes:
  0  wrote file (path printed to stdout)
  1  validation error (missing field, bad payload, file already exists without --force)
  2  unexpected error
"""

import argparse
import json
import logging
import re
import sys
from datetime import date, datetime
from pathlib import Path

# import sibling scripts
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_slug import slugify  # noqa: E402
from validate_frontmatter import (  # noqa: E402
    CANONICAL_CATEGORIES,
    ALLOWED_SEVERITIES,
    TAG_PATTERN,
)

REQUIRED_KEYS = [
    "title", "category", "date", "tags", "module", "symptom", "root_cause",
    "symptom_body", "investigation_body", "root_cause_body",
    "solution_body", "verification_body", "prevention_body",
]


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def load_payload(args: argparse.Namespace) -> dict:
    if args.payload:
        text = args.payload.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    if not text.strip():
        raise ValueError("empty payload")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"payload is not valid JSON: {e}") from e


def validate_payload(payload: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"missing required keys: {missing}")

    if payload["category"] not in CANONICAL_CATEGORIES:
        raise ValueError(f"unknown category: {payload['category']!r}")

    try:
        d = datetime.strptime(payload["date"], "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        raise ValueError(f"date must be YYYY-MM-DD: {payload['date']!r}") from e
    if d > date.today():
        raise ValueError(f"date is in the future: {d}")

    tags = payload["tags"]
    if not isinstance(tags, list) or not (2 <= len(tags) <= 8):
        raise ValueError("tags must be a list of 2-8 items")
    seen = set()
    for t in tags:
        if not isinstance(t, str) or not TAG_PATTERN.match(t):
            raise ValueError(f"invalid tag: {t!r}")
        if t in seen:
            raise ValueError(f"duplicate tag: {t!r}")
        seen.add(t)

    sev = payload.get("severity", "")
    if sev and sev not in ALLOWED_SEVERITIES:
        raise ValueError(f"invalid severity: {sev!r}")

    title = payload["title"]
    if not isinstance(title, str) or not (8 <= len(title) <= 120):
        raise ValueError("title length must be 8-120 chars")


def render(payload: dict, template: str) -> str:
    tags_yaml = "\n  - " + "\n  - ".join(payload["tags"])
    severity = payload.get("severity", "") or ""
    related_body = payload.get("related_body", "") or "_(none)_"
    repl = {
        "{{TITLE}}": payload["title"],
        "{{CATEGORY}}": payload["category"],
        "{{DATE}}": payload["date"],
        "{{TAGS_YAML}}": tags_yaml,
        "{{MODULE}}": payload["module"],
        "{{SYMPTOM}}": payload["symptom"],
        "{{ROOT_CAUSE}}": payload["root_cause"],
        "{{SEVERITY}}": severity if severity else '""',
        "{{SYMPTOM_BODY}}": payload["symptom_body"],
        "{{INVESTIGATION_BODY}}": payload["investigation_body"],
        "{{ROOT_CAUSE_BODY}}": payload["root_cause_body"],
        "{{SOLUTION_BODY}}": payload["solution_body"],
        "{{VERIFICATION_BODY}}": payload["verification_body"],
        "{{PREVENTION_BODY}}": payload["prevention_body"],
        "{{RELATED_BODY}}": related_body,
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None, help="JSON payload file (default: stdin)")
    p.add_argument("--solutions-root", required=True, type=Path, help="path to .claude/solutions/")
    p.add_argument("--template", type=Path, default=Path(__file__).resolve().parent.parent / "templates" / "solution.md.template")
    p.add_argument("--force", action="store_true", help="overwrite if target file exists")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("write-solution")

    try:
        payload = load_payload(args)
        validate_payload(payload)

        template = args.template.read_text(encoding="utf-8")
        slug = slugify(payload["title"])
        filename = f"{payload['date']}-{slug}.md"
        out_dir = args.solutions_root / payload["category"]
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / filename

        if target.exists() and not args.force:
            log.error("file already exists: %s (pass --force to overwrite)", target)
            return 1

        rendered = render(payload, template)
        target.write_text(rendered, encoding="utf-8")
        print(str(target))
        return 0

    except ValueError as e:
        log.error("validation error: %s", e)
        return 1
    except Exception as e:  # noqa: BLE001
        log.exception("unexpected error: %s", e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
