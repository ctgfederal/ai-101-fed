#!/usr/bin/env python3
"""parse_spec.py — extract REQ-IDs from a PRD and COMP-IDs + expected paths from an SDD.

A PRD requirement line looks like:
  - **REQ-001** (story US-1, Must): WHEN ...

An SDD component section looks like:
  ### COMP-001: SearchService
  Path: `src/search/service.py`
  ...

`Path:` may also appear as `Paths:` for components that span multiple files.

Output JSON shape (printed to stdout):
  {
    "prd": "<path>",
    "sdd": "<path>",
    "reqs": ["REQ-001", "REQ-002", ...],
    "comps": [
      {"id": "COMP-001", "name": "SearchService", "expected_paths": ["src/search/service.py"]},
      ...
    ]
  }

Usage:
  python parse_spec.py --prd PRD.md --sdd SDD.md
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

REQ_DEF_RE = re.compile(r"\*\*(REQ-\d+)\*\*")
COMP_HEADING_RE = re.compile(
    r"^###\s+(COMP-\d+)\s*[:\-]\s*(.+?)\s*$",
    re.MULTILINE,
)
PATH_LINE_RE = re.compile(
    r"^\s*Paths?\s*:\s*(.+?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
BACKTICK_RE = re.compile(r"`([^`]+)`")


def extract_reqs(prd_text: str) -> List[str]:
    """Return ordered, de-duplicated list of REQ-IDs defined in the PRD."""
    seen = []
    for m in REQ_DEF_RE.finditer(prd_text):
        rid = m.group(1)
        if rid not in seen:
            seen.append(rid)
    return seen


def extract_comps(sdd_text: str) -> List[dict]:
    """Return ordered list of components with their declared paths.

    Strategy: find each `### COMP-NNN: Name` heading, then capture the body
    until the next `###` or `##` heading and look for a `Path:` / `Paths:`
    line within. Paths are extracted from backticks; if no backticks, the
    whole value after the colon is treated as a single path.
    """
    comps: List[dict] = []
    matches = list(COMP_HEADING_RE.finditer(sdd_text))
    for i, m in enumerate(matches):
        cid = m.group(1)
        name = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(sdd_text)
        body = sdd_text[body_start:body_end]

        # stop body at the next `## ` heading if it comes before the next `### `
        next_h2 = re.search(r"^##\s", body, re.MULTILINE)
        if next_h2:
            body = body[:next_h2.start()]

        paths: List[str] = []
        for path_match in PATH_LINE_RE.finditer(body):
            value = path_match.group(1).strip()
            ticked = BACKTICK_RE.findall(value)
            if ticked:
                paths.extend(p.strip() for p in ticked if p.strip())
            else:
                # comma-separated bare paths
                paths.extend(p.strip() for p in value.split(",") if p.strip())

        # de-dupe while preserving order
        seen_paths: List[str] = []
        for p in paths:
            if p not in seen_paths:
                seen_paths.append(p)

        comps.append({"id": cid, "name": name, "expected_paths": seen_paths})
    return comps


def parse(prd_text: str, sdd_text: str, prd_path: str, sdd_path: str) -> dict:
    return {
        "prd": prd_path,
        "sdd": sdd_path,
        "reqs": extract_reqs(prd_text),
        "comps": extract_comps(sdd_text),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--prd", required=True, type=Path, help="path to PRD markdown")
    p.add_argument("--sdd", required=True, type=Path, help="path to SDD markdown")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.prd.exists():
        print(f"error: PRD not found: {args.prd}", file=sys.stderr)
        return 1
    if not args.sdd.exists():
        print(f"error: SDD not found: {args.sdd}", file=sys.stderr)
        return 1
    prd_text = args.prd.read_text(encoding="utf-8")
    sdd_text = args.sdd.read_text(encoding="utf-8")
    payload = parse(prd_text, sdd_text, str(args.prd), str(args.sdd))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
