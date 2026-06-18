#!/usr/bin/env python3
"""extract_learnings.py — parse a spec README's Learnings sections into JSON.

Looks for the following markdown sections in the input file:
  - `## Learnings`
  - `## Phase Notes`
  - `### For /memorize` (or `### For /memorize (Global Learnings)`)

Within each section, treats every leading `- ` bullet line as one learning item.
Preserves multi-line bullets (continuation lines indented with two spaces).

Output: JSON list of objects, one per learning, each with:
  {
    "text":  "<the bullet text>",
    "phase": "<phase id if discoverable, else 'unknown'>",
    "scope": "local" | "global"
  }

Scope rules:
  - Bullets under "## Learnings" or "## Phase Notes"      → "local"
  - Bullets under "### For /memorize..."                  → "global"
  - Lines beginning with `[x]` or `[X]` are still emitted; the marker is stripped

Phase rules:
  - If the bullet line begins with `T-NNN` or `Phase N:` it is captured.
  - Otherwise the most recent `### Phase` or `## Phase` heading scope wins.
  - Otherwise "unknown".

Usage:
  python extract_learnings.py --readme /path/to/README.md
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional


GLOBAL_HEADINGS = (
    "for /memorize",
    "for memorize",
    "global learnings",
)
LOCAL_HEADINGS = (
    "learnings",
    "phase notes",
    "implementation insights",
    "what worked",
    "what didn't work",
)
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*-\s+(.*)$")
PHASE_INLINE_RE = re.compile(r"^\s*(?:\[x\]|\[ \]|\[X\])?\s*\**\s*(T-\d+|Phase\s*\d+)\b", re.IGNORECASE)
CHECKBOX_PREFIX_RE = re.compile(r"^\[(?:x|X| )\]\s*")


def _classify_heading(heading: str) -> Optional[str]:
    h = heading.strip().lower()
    for g in GLOBAL_HEADINGS:
        if g in h:
            return "global"
    for l in LOCAL_HEADINGS:
        if l in h:
            return "local"
    return None


def _detect_phase(line: str, current_phase: str) -> str:
    m = PHASE_INLINE_RE.search(line)
    if m:
        return m.group(1).strip()
    return current_phase


def _strip_checkbox(text: str) -> str:
    return CHECKBOX_PREFIX_RE.sub("", text).strip()


def extract(readme_text: str) -> List[dict]:
    """Walk README markdown and yield learning items."""
    items: List[dict] = []
    current_scope: Optional[str] = None
    current_phase = "unknown"
    in_section = False

    lines = readme_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        m = HEADING_RE.match(line)
        if m:
            level, heading = m.group(1), m.group(2)
            scope = _classify_heading(heading)
            if scope:
                current_scope = scope
                in_section = True
                current_phase = "unknown"
            else:
                if level == "##":
                    in_section = False
                    current_scope = None
                    current_phase = "unknown"
                elif level in ("###", "####") and in_section:
                    pm = re.search(r"\b(T-\d+|Phase\s*\d+)\b", heading, re.IGNORECASE)
                    if pm:
                        current_phase = pm.group(1).strip()
            i += 1
            continue

        if in_section and current_scope:
            bm = BULLET_RE.match(line)
            if bm:
                bullet_text_lines = [bm.group(1).rstrip()]
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    if not nxt.strip():
                        break
                    if HEADING_RE.match(nxt):
                        break
                    if BULLET_RE.match(nxt):
                        break
                    if nxt.startswith("    ") or nxt.startswith("\t"):
                        bullet_text_lines.append(nxt.strip())
                        j += 1
                        continue
                    break
                joined = " ".join(bullet_text_lines).strip()
                joined = _strip_checkbox(joined)
                if joined:
                    phase = _detect_phase(joined, current_phase)
                    items.append({
                        "text": joined,
                        "phase": phase,
                        "scope": current_scope,
                    })
                i = j
                continue

        i += 1

    return items


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--readme", required=True, type=Path,
                   help="path to spec README.md")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.readme.exists():
        print(f"error: file not found: {args.readme}", file=sys.stderr)
        return 1
    text = args.readme.read_text(encoding="utf-8")
    items = extract(text)
    print(json.dumps(items, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
