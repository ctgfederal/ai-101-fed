#!/usr/bin/env python3
"""
search_solutions.py — find solution files in .claude/solutions/ by tag, module,
symptom keyword, or category.

Exactly one of --tag, --module, --symptom, --category may be given.

Usage:
  python search_solutions.py --solutions-root .claude/solutions --tag activerecord
  python search_solutions.py --solutions-root .claude/solutions --module BriefGenerator
  python search_solutions.py --solutions-root .claude/solutions --symptom "n+1"
  python search_solutions.py --solutions-root .claude/solutions --category performance-issues

Exit codes:
  0  always (empty result is normal); prints `<path>\\t<matched-line>` per hit
  1  invalid arguments
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def iter_solution_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return
    yield from root.rglob("*.md")


def split_frontmatter(text: str) -> Tuple[str, str]:
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return "", text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return "", text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def match_tag(yaml_text: str, tag: str) -> str:
    """Return the matching tags line if `tag` is in the tags list, else ''."""
    in_tags = False
    inline_match = re.search(r"^tags:\s*\[([^\]]*)\]", yaml_text, flags=re.MULTILINE)
    if inline_match:
        inner = inline_match.group(1)
        items = [x.strip().strip('"').strip("'") for x in inner.split(",")]
        if tag in items:
            return inline_match.group(0)
        return ""
    for line in yaml_text.splitlines():
        if re.match(r"^tags:\s*$", line):
            in_tags = True
            continue
        if in_tags:
            m = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if m:
                item = m.group(1).strip().strip('"').strip("'")
                if item == tag:
                    return f"tags: ...{item}..."
            elif line.strip() and not line.startswith(" "):
                in_tags = False
    return ""


def match_field(yaml_text: str, field: str, needle: str, *, exact: bool) -> str:
    """Match a top-level field. Returns the matching line or ''."""
    pat = re.compile(rf"^{re.escape(field)}:\s*(.+?)\s*$", flags=re.MULTILINE)
    m = pat.search(yaml_text)
    if not m:
        return ""
    val = m.group(1).strip().strip('"').strip("'")
    if exact:
        return m.group(0) if val == needle else ""
    if needle.lower() in val.lower():
        return m.group(0)
    return ""


def match_symptom(yaml_text: str, body: str, needle: str) -> str:
    """Symptom match: search both `symptom:` field and `## Symptom` body section."""
    line = match_field(yaml_text, "symptom", needle, exact=False)
    if line:
        return line
    sym_match = re.search(r"^##\s+Symptom\s*$(.*?)(?=^##\s|\Z)", body, flags=re.MULTILINE | re.DOTALL)
    if sym_match and needle.lower() in sym_match.group(1).lower():
        return "## Symptom (body match)"
    return ""


def search(root: Path, *, tag: str = "", module: str = "", symptom: str = "", category: str = "") -> List[Tuple[Path, str]]:
    hits: List[Tuple[Path, str]] = []
    for f in iter_solution_files(root):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        yaml_text, body = split_frontmatter(text)
        if not yaml_text:
            continue

        line = ""
        if tag:
            line = match_tag(yaml_text, tag)
        elif module:
            line = match_field(yaml_text, "module", module, exact=True)
        elif symptom:
            line = match_symptom(yaml_text, body, symptom)
        elif category:
            line = match_field(yaml_text, "category", category, exact=True)

        if line:
            hits.append((f, line))
    return hits


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--solutions-root", required=True, type=Path, help="path to .claude/solutions/")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tag")
    g.add_argument("--module")
    g.add_argument("--symptom")
    g.add_argument("--category")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    hits = search(
        args.solutions_root,
        tag=args.tag or "",
        module=args.module or "",
        symptom=args.symptom or "",
        category=args.category or "",
    )
    for path, line in hits:
        print(f"{path}\t{line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
