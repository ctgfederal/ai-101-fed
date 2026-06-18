#!/usr/bin/env python3
"""validate_output.py — validate a written PRD.md.

Checks:
  - Required sections present in order
  - Every REQ-NNN line has an EARS pattern + MoSCoW priority
  - No [NEEDS CLARIFICATION] markers
  - Steering anchor links present in Context References

Usage:
  python validate_output.py --file path/PRD.md
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Context References", "Product Overview", "Personas", "User Stories",
    "Functional Requirements", "MoSCoW Priorities", "Success Metrics",
    "Risks and Constraints", "Open Questions",
]
ALLOWED_MOSCOW = {"Must", "Should", "Could", "Won't"}
EARS_PATTERNS = ["SHALL", "WHEN", "WHILE", "WHERE", "IF"]
REQ_LINE_RE = re.compile(r"\*\*REQ-\d+\*\*\s*\(story\s+\S+,\s+(Must|Should|Could|Won't)\):\s*(.+)")


def validate(text: str) -> list[str]:
    errors: list[str] = []
    if "[NEEDS CLARIFICATION]" in text:
        errors.append("[NEEDS CLARIFICATION] marker present — resolve first")

    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    found_set = set(found)
    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"missing section: ## {sec}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    # Steering links
    if ".claude/steering/product.md" not in text:
        errors.append("Context References missing link to .claude/steering/product.md")

    # Requirements must have EARS + MoSCoW
    req_lines_found = list(REQ_LINE_RE.finditer(text))
    if not req_lines_found:
        errors.append("no REQ-NNN lines found — body may be missing requirements")
    for m in req_lines_found:
        moscow = m.group(1)
        body = m.group(2)
        if not any(p in body for p in EARS_PATTERNS):
            errors.append(f"requirement at {m.start()} not EARS-formatted: {body[:80]}")

    return errors


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
