#!/usr/bin/env python3
"""
validate_frontmatter.py — validate the YAML frontmatter of a solution file
against the schema in knowledge/frontmatter-schema.md.

Usage:
  python validate_frontmatter.py --file path/to/solution.md

Exit codes:
  0  valid
  1  invalid (errors on stderr)
  2  unexpected error
"""

import argparse
import logging
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Tuple

REQUIRED_FIELDS = ["title", "category", "date", "tags", "module", "symptom", "root_cause"]
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}

# canonical category list — kept in sync with knowledge/categories.md
CANONICAL_CATEGORIES = {
    "build-errors", "test-failures", "runtime-errors",
    "performance-issues", "database-issues", "security-issues",
    "ui-bugs", "integration-issues", "logic-errors",
    "configuration-fixes", "deployment-issues", "tooling-issues",
}

TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9+\-]*[a-z0-9+]$")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def split_frontmatter(text: str) -> Tuple[str, str]:
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        raise ValueError("file must start with YAML frontmatter '---'")
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ValueError("YAML frontmatter not closed (no second '---')")
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def parse_yaml(yaml_text: str) -> dict:
    """Parse a tiny YAML subset sufficient for solution frontmatter."""
    data: dict = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in raw:
            raise ValueError(f"unparseable line: {raw!r}")
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()

        if val == "":
            # block list
            data[key] = []
            i += 1
            while i < len(lines):
                line = lines[i]
                if not line.strip() or line.lstrip().startswith("#"):
                    i += 1
                    continue
                if line.startswith("  - ") or line.startswith("- "):
                    item = line.lstrip()[2:].strip()
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        item = item[1:-1]
                    data[key].append(item)
                    i += 1
                else:
                    break
            continue

        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
            i += 1
            continue

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        data[key] = val
        i += 1
    return data


def validate(data: dict) -> List[str]:
    errors: List[str] = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing required field: {field}")
        elif data[field] in ("", [], None):
            errors.append(f"required field is empty: {field}")

    title = data.get("title", "")
    if isinstance(title, str) and title and not (8 <= len(title) <= 120):
        errors.append(f"title length out of range (8-120 chars): {len(title)}")

    cat = data.get("category", "")
    if cat and cat not in CANONICAL_CATEGORIES:
        errors.append(f"unknown category: {cat!r} (see knowledge/categories.md)")

    raw_date = data.get("date", "")
    if raw_date:
        try:
            d = datetime.strptime(str(raw_date), "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"date not YYYY-MM-DD: {raw_date!r}")
        else:
            if d > date.today():
                errors.append(f"date is in the future: {d}")

    tags = data.get("tags", [])
    if isinstance(tags, list):
        if not (2 <= len(tags) <= 8):
            errors.append(f"tags must have 2-8 items (got {len(tags)})")
        seen = set()
        for t in tags:
            if t in seen:
                errors.append(f"duplicate tag: {t!r}")
            seen.add(t)
            if not isinstance(t, str) or not TAG_PATTERN.match(t):
                errors.append(f"invalid tag format: {t!r} (lowercase, no spaces, no leading/trailing hyphen)")
    elif "tags" in data:
        errors.append("tags must be a YAML list")

    sev = data.get("severity")
    if sev is not None and sev != "" and sev not in ALLOWED_SEVERITIES:
        errors.append(f"invalid severity: {sev!r} (must be one of {sorted(ALLOWED_SEVERITIES)})")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path, help="path to a solution markdown file")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("validate-frontmatter")

    try:
        text = args.file.read_text(encoding="utf-8")
    except FileNotFoundError:
        log.error("file not found: %s", args.file)
        return 1
    except Exception as e:  # noqa: BLE001
        log.exception("read error: %s", e)
        return 2

    try:
        yaml_text, _ = split_frontmatter(text)
        data = parse_yaml(yaml_text)
    except ValueError as e:
        log.error("frontmatter parse error: %s", e)
        return 1

    errors = validate(data)
    if errors:
        for e in errors:
            log.error(e)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
