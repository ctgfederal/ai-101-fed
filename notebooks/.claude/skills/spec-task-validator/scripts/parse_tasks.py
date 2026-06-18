#!/usr/bin/env python3
"""parse_tasks.py — parse a PLAN.md into a structured task list.

Each task is a `- [ ] T-NNN <Title>` bullet under a `## Phase N: <Name>` heading.
Below the bullet, indented lines provide implementation notes plus tagged lines:

    _Acceptance:_ <text>
    _Requirements:_ REQ-001, REQ-002
    _Components:_ COMP-001
    _TDD:_ red

Output JSON shape (a list):
  [
    {
      "id": "T-001",
      "title": "...",
      "phase": "Foundation",
      "comps": ["COMP-001"],
      "reqs":  ["REQ-001"],
      "acceptance": "...",
      "tdd_step": "red"
    },
    ...
  ]

Usage:
  python parse_tasks.py --plan path/to/PLAN.md
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional


PHASE_RE = re.compile(r"^##\s+Phase\s+\d+:\s*(.+?)\s*$", re.MULTILINE)
TASK_RE = re.compile(r"^-\s+\[[ xX]\]\s+(T-\d+)\s+(.+?)\s*$")
ACCEPTANCE_RE = re.compile(r"_Acceptance:_\s*(.+?)\s*$")
REQUIREMENTS_RE = re.compile(r"_Requirements:_\s*(.*?)\s*$")
COMPONENTS_RE = re.compile(r"_Components:_\s*(.*?)\s*$")
TDD_RE = re.compile(r"_TDD:_\s*(.+?)\s*$")
ID_RE = re.compile(r"\b([A-Z]{2,4}-\d+)\b")


def _split_phases(text: str) -> List[tuple]:
    """Return list of (phase_name, body) chunks."""
    headings = list(PHASE_RE.finditer(text))
    if not headings:
        return [("", text)]
    chunks = []
    for i, m in enumerate(headings):
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        chunks.append((m.group(1).strip(), text[start:end]))
    return chunks


def _parse_task_block(block: str) -> dict:
    """Given the body lines of a single task, extract its tagged fields."""
    fields = {
        "acceptance": "",
        "reqs": [],
        "comps": [],
        "tdd_step": "",
    }
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        m = ACCEPTANCE_RE.search(line)
        if m:
            fields["acceptance"] = m.group(1).strip()
            continue
        m = REQUIREMENTS_RE.search(line)
        if m:
            fields["reqs"] = ID_RE.findall(m.group(1))
            continue
        m = COMPONENTS_RE.search(line)
        if m:
            fields["comps"] = ID_RE.findall(m.group(1))
            continue
        m = TDD_RE.search(line)
        if m:
            fields["tdd_step"] = m.group(1).strip().lower()
            continue
    return fields


def parse_plan(text: str) -> List[dict]:
    """Parse a PLAN.md text into a list of task dicts."""
    tasks: List[dict] = []
    for phase_name, phase_body in _split_phases(text):
        # Walk lines; when we hit a task header, accumulate its block
        lines = phase_body.splitlines(keepends=False)
        i = 0
        while i < len(lines):
            line = lines[i]
            mt = TASK_RE.match(line.lstrip())
            if not mt:
                i += 1
                continue
            tid = mt.group(1)
            ttitle = mt.group(2).strip()
            # Collect indented child lines until next non-indented bullet or end
            block_lines: List[str] = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                # End of task-block: a top-level bullet for a new task or a top-level non-indented heading-ish line
                if TASK_RE.match(nxt.lstrip()) and not nxt.startswith(" ") and not nxt.startswith("\t"):
                    break
                if nxt.lstrip().startswith("## "):
                    break
                block_lines.append(nxt)
                j += 1
            fields = _parse_task_block("\n".join(block_lines))
            tasks.append({
                "id": tid,
                "title": ttitle,
                "phase": phase_name,
                "comps": fields["comps"],
                "reqs": fields["reqs"],
                "acceptance": fields["acceptance"],
                "tdd_step": fields["tdd_step"],
            })
            i = j
    return tasks


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--plan", required=True, type=Path,
                   help="path to PLAN.md")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.plan.exists():
        print(f"error: plan not found: {args.plan}", file=sys.stderr)
        return 1
    text = args.plan.read_text(encoding="utf-8")
    tasks = parse_plan(text)
    print(json.dumps(tasks, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
