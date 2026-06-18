#!/usr/bin/env python3
"""validate_output.py — validate a written memory file plus its index entry.

Checks:
  - File starts with `---` and has a closing `---`
  - Frontmatter contains `name`, `description`, `type` fields
  - `type` is one of feedback | project | reference | user
  - File body is non-empty
  - Sibling MEMORY.md exists and has a bullet pointing at this file's basename
  - Bullet description is non-empty

Usage:
  python validate_output.py --file path/to/feedback_my_learning.md
"""
import argparse
import re
import sys
from pathlib import Path


ALLOWED_TYPES = {"feedback", "project", "reference", "user"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("no YAML frontmatter (must start with '---' and have closing '---')")
    block = m.group(1)
    body = m.group(2)
    data: dict = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unparseable frontmatter line: {line!r}")
        k, _, v = line.partition(":")
        data[k.strip()] = v.strip().strip("'\"")
    return data, body


def validate_memory_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        errors.append(f"file does not exist: {path}")
        return errors
    text = path.read_text(encoding="utf-8")
    try:
        data, body = _parse_frontmatter(text)
    except ValueError as e:
        errors.append(str(e))
        return errors
    for required in ("name", "description", "type"):
        if not data.get(required):
            errors.append(f"frontmatter missing or empty: {required}")
    if data.get("type") and data["type"] not in ALLOWED_TYPES:
        errors.append(f"type must be one of {sorted(ALLOWED_TYPES)}; got {data['type']!r}")
    if not body.strip():
        errors.append("body is empty")
    return errors


def validate_index(path: Path) -> list[str]:
    errors: list[str] = []
    index = path.parent / "MEMORY.md"
    if not index.is_file():
        errors.append(f"MEMORY.md not found in {path.parent}")
        return errors
    index_text = index.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^- \[{re.escape(path.name)}\]\([^)]+\)\s*-\s*(.*)$",
        re.MULTILINE,
    )
    m = pattern.search(index_text)
    if not m:
        errors.append(f"MEMORY.md missing index entry for {path.name}")
    else:
        if not m.group(1).strip():
            errors.append(f"MEMORY.md entry for {path.name} has empty description")
    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_memory_file(args.file)
    errors += validate_index(args.file)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
