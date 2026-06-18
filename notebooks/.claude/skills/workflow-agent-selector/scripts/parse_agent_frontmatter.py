#!/usr/bin/env python3
"""parse_agent_frontmatter.py — read every agent's YAML frontmatter and emit JSON.

Usage:
  python parse_agent_frontmatter.py --agents-root ~/.claude/agents

Prints a JSON list of {name, description, tools, model, file} to stdout.
Exit 0 always; agents that fail to parse are skipped with a warning to stderr.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return "", text
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return "", text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1 :])


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def parse_yaml_minimal(yaml_text: str) -> dict:
    """Parse the minimal subset we need: name, description, tools, model."""
    data: dict = {"name": "", "description": "", "tools": [], "model": ""}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(name|description|tools|model):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in {"|", ">", "|-", ">-", "|+", ">+"}:
            block: list[str] = []
            i += 1
            while i < len(lines):
                ln = lines[i]
                if ln.strip() == "":
                    block.append("")
                    i += 1
                    continue
                stripped = ln.lstrip()
                indent = len(ln) - len(stripped)
                if indent == 0:
                    break
                block.append(stripped)
                i += 1
            joined = " ".join(b for b in block if b)
            if key == "tools":
                data[key] = [t.strip() for t in re.split(r"[,\s]+", joined) if t.strip()]
            else:
                data[key] = joined
            continue
        if val == "" and key == "tools":
            data[key] = []
            i += 1
            while i < len(lines):
                ln = lines[i]
                if ln.startswith("  - ") or ln.startswith("- "):
                    item = ln.lstrip()[2:].strip()
                    data[key].append(_strip_quotes(item))
                    i += 1
                else:
                    break
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [x.strip().strip('"').strip("'") for x in inner.split(",")] if inner else []
            data[key] = items if key == "tools" else " ".join(items)
            i += 1
            continue
        val = _strip_quotes(val)
        if key == "tools":
            data[key] = [t.strip() for t in val.split(",") if t.strip()]
        else:
            data[key] = val
        i += 1
    return data


def parse_agents(agents_root: Path) -> list[dict]:
    out: list[dict] = []
    for md in sorted(agents_root.glob("*.md")):
        if md.name.upper() == "CLAUDE.MD":
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            print(f"warn: cannot read {md}: {e}", file=sys.stderr)
            continue
        yaml_text, _ = split_frontmatter(text)
        if not yaml_text:
            print(f"warn: no frontmatter in {md.name}", file=sys.stderr)
            continue
        meta = parse_yaml_minimal(yaml_text)
        if not meta["name"]:
            print(f"warn: no name in {md.name}", file=sys.stderr)
            continue
        meta["file"] = str(md)
        out.append(meta)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agents-root", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.agents_root.is_dir():
        print(f"error: agents root not found: {args.agents_root}", file=sys.stderr)
        return 1
    agents = parse_agents(args.agents_root)
    print(json.dumps(agents, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
