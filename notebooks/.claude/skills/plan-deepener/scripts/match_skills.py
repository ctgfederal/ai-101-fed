#!/usr/bin/env python3
"""match_skills.py — find skills whose name or description matches keywords.

Usage:
  echo '["postgres", "search", "indexing"]' | python match_skills.py --skills-root ~/.claude/skills

Prints JSON list of {skill, why} to stdout.
Exit 0.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def split_frontmatter(text: str):
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return "", text
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return "", text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def parse_yaml_minimal(yaml_text: str) -> dict:
    """Parse `name:` and `description:` only; tolerate block scalars and quoted strings."""
    data = {"name": "", "description": ""}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(name|description):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in {"|", ">", "|-", ">-", "|+", ">+"}:
            block = []
            i += 1
            while i < len(lines):
                ln = lines[i]
                if ln.strip() == "" or (ln.startswith("  ") or ln.startswith("\t")):
                    block.append(ln.lstrip())
                    i += 1
                    continue
                if not ln.strip():
                    i += 1
                    continue
                break
            data[key] = " ".join(b.strip() for b in block if b.strip())
            continue
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        data[key] = val
        i += 1
    return data


def match(keyword: str, name: str, desc: str) -> str:
    """Return match reason or empty string."""
    kw = keyword.lower()
    if kw in name.lower():
        return f"name match: {keyword!r} in {name!r}"
    if kw in desc.lower():
        # be specific: which keyword
        return f"description match: {keyword!r}"
    return ""


def find_matches(keywords: list[str], skills_root: Path) -> list[dict]:
    out = []
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
        yaml_text, _ = split_frontmatter(text)
        meta = parse_yaml_minimal(yaml_text)
        if not meta["name"]:
            continue
        reasons = []
        for kw in keywords:
            r = match(kw, meta["name"], meta["description"])
            if r:
                reasons.append(r)
        if reasons:
            out.append({"skill": meta["name"], "why": reasons})
    return out


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--keywords-json", type=Path, default=None, help="JSON list (default: stdin)")
    p.add_argument("--skills-root", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    text = args.keywords_json.read_text(encoding="utf-8") if args.keywords_json else sys.stdin.read()
    if not text.strip():
        print("error: empty keywords input", file=sys.stderr)
        return 1
    try:
        keywords = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not isinstance(keywords, list):
        print("error: keywords must be a JSON list of strings", file=sys.stderr)
        return 1
    if not args.skills_root.is_dir():
        print(f"error: skills root not found: {args.skills_root}", file=sys.stderr)
        return 1
    matches = find_matches(keywords, args.skills_root)
    print(json.dumps(matches, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
