#!/usr/bin/env python3
"""validate_output.py — validate written SDD.md.

Checks: required sections; every PRD REQ is in traceability; COMP IDs unique; steering links.

Usage: python validate_output.py --file SDD.md --prd PRD.md
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_req_ids import extract as extract_req_ids

REQUIRED_SECTIONS = [
    "Context References", "Overview", "Architecture", "Components",
    "Data Model", "External Integrations", "Traceability",
    "Alternatives Considered", "Risks and Mitigations", "Open Questions",
]
COMP_RE = re.compile(r"^###\s+(COMP-\d+):", re.MULTILINE)


def validate(text: str, prd_reqs: list[str]) -> list[str]:
    errors: list[str] = []
    if "[NEEDS CLARIFICATION]" in text:
        errors.append("[NEEDS CLARIFICATION] marker present")

    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    found_set = set(found)
    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"missing section: ## {sec}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    if ".claude/steering/tech.md" not in text:
        errors.append("Context References missing link to .claude/steering/tech.md")
    if ".claude/steering/structure.md" not in text:
        errors.append("Context References missing link to .claude/steering/structure.md")

    comp_ids = COMP_RE.findall(text)
    if not comp_ids:
        errors.append("no COMP-NNN headings found")
    if len(comp_ids) != len(set(comp_ids)):
        errors.append("duplicate COMP IDs found")

    # traceability table coverage
    for req in prd_reqs:
        if req not in text:
            errors.append(f"traceability missing PRD requirement: {req}")
    return errors


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--prd", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    if not args.prd.exists():
        print(f"error: PRD not found: {args.prd}", file=sys.stderr)
        return 1
    prd_reqs = extract_req_ids(args.prd.read_text(encoding="utf-8"))
    errors = validate(args.file.read_text(encoding="utf-8"), prd_reqs)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
