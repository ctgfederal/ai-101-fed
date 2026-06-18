#!/usr/bin/env python3
"""validate_output.py — validate a rendered TRACEABILITY.md.

Checks:
  - Required `##` sections present in order: Feature, Summary, Coverage Matrix,
    Gaps, Totals
  - Every PRD REQ-NNN appears as a row
  - Every status field on a row is one of `covered`, `partial`, `uncovered`
  - The Totals reconcile: covered + partial + uncovered == total PRD REQs
  - No unsubstituted `{{...}}` template tokens

Usage:
  python validate_output.py --file TRACEABILITY.md --prd PRD.md
"""
import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = ["Feature", "Summary", "Coverage Matrix", "Gaps", "Totals"]
VALID_STATUSES = {"covered", "partial", "uncovered"}
REQ_RE = re.compile(r"\bREQ-(\d+)\b")
STATUS_RE = re.compile(r"`(covered|partial|uncovered)`")
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
TOTALS_LINE_RE = re.compile(
    r"-\s*(Covered|Partial|Uncovered|Total\s*REQs):\s*\*\*(\d+)\*\*",
    re.IGNORECASE,
)


def extract_prd_reqs(prd_text: str) -> list[str]:
    nums = sorted({int(m) for m in REQ_RE.findall(prd_text)})
    if not nums:
        return []
    width = max(3, len(str(nums[-1])))
    return [f"REQ-{n:0{width}d}" for n in nums]


def validate(text: str, prd_reqs: list[str]) -> list[str]:
    errors: list[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    found = [
        m.group(1).strip()
        for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)
    ]
    found_set = set(found)
    for sect in REQUIRED_SECTIONS:
        if sect not in found_set:
            errors.append(f"missing section: ## {sect}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    # Every PRD REQ must appear in the file (typically in a row)
    for req in prd_reqs:
        if req not in text:
            errors.append(f"REQ not in matrix: {req}")

    # Every status reference is a valid value
    for m in STATUS_RE.finditer(text):
        status = m.group(1)
        if status not in VALID_STATUSES:
            errors.append(f"invalid status value: {status!r}")

    # Reconcile totals
    totals_match = re.search(
        r"^##\s+Totals\s*$(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if totals_match:
        body = totals_match.group(1)
        totals: dict[str, int] = {}
        for m in TOTALS_LINE_RE.finditer(body):
            label = m.group(1).strip().lower().replace(" ", "")
            totals[label] = int(m.group(2))
        if all(k in totals for k in ("covered", "partial", "uncovered", "totalreqs")):
            sum_parts = totals["covered"] + totals["partial"] + totals["uncovered"]
            if sum_parts != totals["totalreqs"]:
                errors.append(
                    f"totals do not reconcile: covered+partial+uncovered "
                    f"({sum_parts}) != Total REQs ({totals['totalreqs']})"
                )
            if totals["totalreqs"] != len(prd_reqs):
                errors.append(
                    f"Total REQs ({totals['totalreqs']}) != PRD REQ count "
                    f"({len(prd_reqs)})"
                )
        else:
            errors.append("Totals section missing one of: Covered/Partial/Uncovered/Total REQs")
    else:
        errors.append("Totals section not found")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
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
    prd_reqs = extract_prd_reqs(args.prd.read_text(encoding="utf-8"))
    errors = validate(args.file.read_text(encoding="utf-8"), prd_reqs)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
