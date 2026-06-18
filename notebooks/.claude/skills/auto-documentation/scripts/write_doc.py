#!/usr/bin/env python3
"""
write_doc.py — render the auto-doc template from a JSON payload and write the
file to <docs-root>/<category>/<slug>.md.

The payload (JSON, on stdin or in --payload <file>) must have these keys:

  {
    "title":             "string",
    "category":          "business-rule",
    "date":              "YYYY-MM-DD",
    "tags":              ["tag1", "tag2"],
    "scope":             "UserPostController#update",
    "source":            "discovery during /implement on USR-014",
    "description_body":  "markdown",
    "why_body":          "markdown",
    "examples_body":     "markdown",
    "related_body":      "markdown"
  }

Usage:
  python write_doc.py --payload payload.json --docs-root .claude/docs/auto
  cat payload.json | python write_doc.py --docs-root .claude/docs/auto

Exit codes:
  0  wrote file (path printed to stdout)
  1  validation error / file already exists without --force
  2  unexpected error
"""

import argparse
import json
import logging
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

CANONICAL_CATEGORIES = {"business-rule", "technical-pattern", "service-interface", "domain-rule"}
TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9+\-]*[a-z0-9+]$")
MAX_SLUG_LEN = 60

REQUIRED_KEYS = [
    "title", "category", "date", "tags", "scope", "source",
    "description_body", "why_body", "examples_body", "related_body",
]


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def slugify(title: str) -> str:
    if not title or not title.strip():
        raise ValueError("title is empty")
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    lowered = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    if not slug:
        raise ValueError(f"title produced empty slug: {title!r}")
    if len(slug) > MAX_SLUG_LEN:
        slug = slug[:MAX_SLUG_LEN].rstrip("-")
    return slug


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

    title = payload["title"]
    if not isinstance(title, str) or not (8 <= len(title) <= 120):
        raise ValueError("title length must be 8-120 chars")

    scope = payload["scope"]
    if not isinstance(scope, str) or not scope.strip():
        raise ValueError("scope must be non-empty")

    source = payload["source"]
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be non-empty")


def render(payload: dict, template: str) -> str:
    tags_yaml = "\n  - " + "\n  - ".join(payload["tags"])
    related_body = payload.get("related_body", "") or "_(none)_"
    repl = {
        "{{TITLE}}": payload["title"],
        "{{CATEGORY}}": payload["category"],
        "{{DATE}}": payload["date"],
        "{{TAGS_YAML}}": tags_yaml,
        "{{SCOPE}}": payload["scope"],
        "{{SOURCE}}": payload["source"],
        "{{DESCRIPTION_BODY}}": payload["description_body"],
        "{{WHY_BODY}}": payload["why_body"],
        "{{EXAMPLES_BODY}}": payload["examples_body"],
        "{{RELATED_BODY}}": related_body,
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None, help="JSON payload file (default: stdin)")
    p.add_argument("--docs-root", required=True, type=Path, help="path to .claude/docs/auto/")
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "auto-doc.md.template")
    p.add_argument("--force", action="store_true", help="overwrite if target file exists")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("write-doc")

    try:
        payload = load_payload(args)
        validate_payload(payload)

        template = args.template.read_text(encoding="utf-8")
        slug = slugify(payload["title"])
        filename = f"{payload['date']}-{slug}.md"
        out_dir = args.docs_root / payload["category"]
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
