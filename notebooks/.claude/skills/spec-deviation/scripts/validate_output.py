#!/usr/bin/env python3
"""validate_output.py — validate an SDD's appended Deviations section.

Checks:
  - Every `### DEV-NNN` block under `## Deviations` has all required fields
    (Date, Spec, Reason Category, Original Decision, Status, Approver,
     Description, Proposed Change, Impact).
  - Every status value is allowed: proposed | approved | rejected.
  - Every reason_category value is allowed (5 enums).
  - Every DEV-NNN ID is unique across the file.
  - No unsubstituted `{{...}}` template tokens.

Usage:
  python validate_output.py --sdd path/to/SDD.md
"""
import argparse
import re
import sys
from pathlib import Path
from typing import List

ALLOWED_STATUSES = {"proposed", "approved", "rejected"}
ALLOWED_REASON_CATEGORIES = {
    "technical-blocker",
    "scope-clarification",
    "dependency-conflict",
    "performance-required",
    "security-required",
}

REQUIRED_BULLETS = [
    "Date",
    "Spec",
    "Reason Category",
    "Original Decision",
    "Status",
    "Approver",
]
REQUIRED_PROSE_HEADINGS = ["Description", "Proposed Change", "Impact"]

TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
DEV_HEADING_RE = re.compile(r"^###\s+(DEV-\d+)\s*$", re.MULTILINE)
BULLET_RE = re.compile(
    r"^\s*-\s+\*\*([^*]+?)\*\*\s*:\s*(.+?)\s*$", re.MULTILINE
)


def split_dev_blocks(text: str) -> List[tuple]:
    """Return list of (dev_id, block_body_text) under ## Deviations.

    A block's body is the text between its `### DEV-NNN` heading and the
    next `### DEV-NNN` heading (or the next `##` heading, whichever comes
    first), so trailing content outside the Deviations section is excluded.
    """
    section_match = re.search(
        r"^##\s+Deviations\s*$(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        return []
    section = section_match.group(1)
    headings = list(DEV_HEADING_RE.finditer(section))
    blocks: List[tuple] = []
    for i, h in enumerate(headings):
        start = h.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(section)
        blocks.append((h.group(1), section[start:end]))
    return blocks


def validate(text: str) -> List[str]:
    errors: List[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    blocks = split_dev_blocks(text)
    if not blocks:
        # No Deviations section / no blocks is allowed (could be brand-new SDD)
        # but if the section exists with nothing under it we want to flag.
        section_match = re.search(
            r"^##\s+Deviations\s*$(.*?)(?=^##\s+|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        if section_match and section_match.group(1).strip():
            errors.append(
                "## Deviations section has content but no `### DEV-NNN` block"
            )
        return errors

    seen_ids: dict = {}
    for dev_id, body in blocks:
        seen_ids[dev_id] = seen_ids.get(dev_id, 0) + 1

        # collect bullet labels in this block
        labels = {m.group(1).strip(): m.group(2).strip() for m in BULLET_RE.finditer(body)}
        for required in REQUIRED_BULLETS:
            if required not in labels:
                errors.append(f"{dev_id}: missing bullet '{required}'")
                continue
            if not labels[required]:
                errors.append(f"{dev_id}: bullet '{required}' is empty")

        # check enums
        if "Status" in labels:
            if labels["Status"] not in ALLOWED_STATUSES:
                errors.append(
                    f"{dev_id}: Status must be one of "
                    f"{sorted(ALLOWED_STATUSES)}; got {labels['Status']!r}"
                )
        if "Reason Category" in labels:
            if labels["Reason Category"] not in ALLOWED_REASON_CATEGORIES:
                errors.append(
                    f"{dev_id}: Reason Category must be one of "
                    f"{sorted(ALLOWED_REASON_CATEGORIES)}; "
                    f"got {labels['Reason Category']!r}"
                )

        # prose subheadings
        for heading in REQUIRED_PROSE_HEADINGS:
            pattern = rf"\*\*{re.escape(heading)}\*\*"
            if not re.search(pattern, body):
                errors.append(f"{dev_id}: missing **{heading}** prose section")

    duplicates = [k for k, n in seen_ids.items() if n > 1]
    if duplicates:
        errors.append(f"duplicate DEV-NNN IDs: {sorted(duplicates)}")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--sdd", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.sdd.exists():
        print(f"error: file not found: {args.sdd}", file=sys.stderr)
        return 1
    text = args.sdd.read_text(encoding="utf-8")
    errors = validate(text)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
