#!/usr/bin/env python3
"""validate_output.py — validate a written brainstorm file.

Checks:
  - Frontmatter: topic, date, status (in {complete, in-progress})
  - Body: 8 required sections in order
    Inspiration, Projects, Audience, Use Cases, Desired Outcomes,
    Guiding Principles, Constraints, Scope

Usage:
  python validate_output.py --file path.md

Exit 0 = pass.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List

REQUIRED_FRONT = ["topic", "date", "status"]
REQUIRED_SECTIONS = [
    "Inspiration", "Projects", "Audience", "Use Cases",
    "Desired Outcomes", "Guiding Principles", "Constraints", "Scope",
]
ALLOWED_STATUS = {"complete", "in-progress"}


def split_frontmatter(text: str):
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("no frontmatter")
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("frontmatter not closed")
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def parse_yaml(yaml_text: str) -> dict:
    data = {}
    for line in yaml_text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"bad yaml line: {line!r}")
        key, _, val = line.partition(":")
        val = val.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        data[key.strip()] = val
    return data


def validate(data: dict, body: str) -> List[str]:
    errors = []
    for f in REQUIRED_FRONT:
        if f not in data or data[f] in ("", None):
            errors.append(f"frontmatter missing or empty: {f}")
    if "status" in data and data["status"] not in ALLOWED_STATUS:
        errors.append(f"status invalid: {data['status']!r}")
    if "date" in data and data["date"]:
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            errors.append(f"date not YYYY-MM-DD: {data['date']!r}")

    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)]
    found_set = set(found)
    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"body missing section: ## {sec}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"body sections out of order: {found}")
    return errors


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.file.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    try:
        yaml_text, body = split_frontmatter(text)
        data = parse_yaml(yaml_text)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    errors = validate(data, body)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
