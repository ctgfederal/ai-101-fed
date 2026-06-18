#!/usr/bin/env python3
"""validate_output.py — validate a rendered spec README.md.

Checks:
  - Required `##` sections present in order: Status, Steering References,
    Decision Log Snippets, Phase Notes, Learnings, Open Questions.
  - Status table has exactly three rows: PRD, SDD, PLAN.
  - Each status is one of: draft, approved, deprecated.
  - Steering links are relative paths under ../../steering/.
  - Phase notes (if any) are in monotonic ascending order.
  - No unsubstituted `{{TOKEN}}` placeholders.

Usage:
  python validate_output.py --file path/README.md
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Status",
    "Steering References",
    "Decision Log Snippets",
    "Phase Notes",
    "Learnings",
    "Open Questions",
]
ALLOWED_STATUSES = {"draft", "approved", "deprecated"}
ALLOWED_DOCS = ("PRD", "SDD", "PLAN")
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
STATUS_ROW_RE = re.compile(
    r"^\|\s*(PRD|SDD|PLAN)\s*\|\s*([a-z]+)\s*\|\s*[^|]*\s*\|\s*$",
    re.MULTILINE,
)
PHASE_RE = re.compile(r"^###\s+Phase\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
NEXT_TOPLEVEL_RE = re.compile(r"^##\s+", re.MULTILINE)
STEERING_LINK_RE = re.compile(r"\.\./\.\./steering/[a-z0-9_./-]+\.md")


def validate(text: str) -> list[str]:
    errors: list[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    found = [m.group(1).strip() for m in SECTION_RE.finditer(text)]
    found_set = set(found)
    for sect in REQUIRED_SECTIONS:
        if sect not in found_set:
            errors.append(f"missing section: ## {sect}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    rows = STATUS_ROW_RE.findall(text)
    rows_by_doc: dict[str, str] = {}
    for doc, status in rows:
        if doc in rows_by_doc:
            errors.append(f"duplicate status row for {doc}")
        rows_by_doc[doc] = status
    for doc in ALLOWED_DOCS:
        if doc not in rows_by_doc:
            errors.append(f"missing status row: {doc}")
            continue
        if rows_by_doc[doc] not in ALLOWED_STATUSES:
            errors.append(
                f"invalid status for {doc}: {rows_by_doc[doc]!r} "
                f"(allowed: {sorted(ALLOWED_STATUSES)})"
            )

    if "## Steering References" in text:
        if not STEERING_LINK_RE.search(text):
            errors.append(
                "Steering References section missing relative links to "
                "../../steering/*.md"
            )

    pn_idx = text.find("## Phase Notes")
    if pn_idx >= 0:
        body_start = text.find("\n", pn_idx) + 1
        rest = text[body_start:]
        nxt = NEXT_TOPLEVEL_RE.search(rest)
        body = rest[: nxt.start() if nxt else len(rest)]
        phase_numbers = [int(m.group(1)) for m in PHASE_RE.finditer(body)]
        if phase_numbers != sorted(phase_numbers):
            errors.append(f"Phase Notes out of order: {phase_numbers}")
        if len(set(phase_numbers)) != len(phase_numbers):
            errors.append(f"Phase Notes contain duplicate phase numbers: {phase_numbers}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
