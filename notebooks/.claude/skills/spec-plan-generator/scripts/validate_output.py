#!/usr/bin/env python3
"""validate_output.py — validate written PLAN.md.

Checks: required sections in order, unique T-NNN IDs, every PRD REQ in traceability,
every SDD COMP referenced.

Usage: python validate_output.py --file PLAN.md --prd PRD.md --sdd SDD.md
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_ids import extract, REQ_RE, COMP_RE

REQUIRED_SECTIONS = [
    "Context References", "Phase 1: Foundation", "Phase 2: Core",
    "Phase 3: Integration", "Phase 4: Polish", "Traceability", "Open Questions",
]
TASK_RE = re.compile(r"\bT-\d+\b")


def validate(text: str, prd_reqs: list[str], sdd_comps: list[str]) -> list[str]:
    errors: list[str] = []
    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    found_set = set(found)
    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"missing section: ## {sec}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    # task ID uniqueness within file
    task_ids = TASK_RE.findall(text)
    if not task_ids:
        errors.append("no T-NNN tasks found")
    # tasks appear at least 2× (header + traceability), so flag only > 4×
    from collections import Counter
    counts = Counter(task_ids)
    dup = [k for k, v in counts.items() if v > 4]
    if dup:
        errors.append(f"task IDs duplicated within file: {dup}")

    # coverage
    for req in prd_reqs:
        if req not in text:
            errors.append(f"REQ not covered: {req}")
    for comp in sdd_comps:
        if comp not in text:
            errors.append(f"COMP not referenced: {comp}")

    return errors


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--prd", required=True, type=Path)
    p.add_argument("--sdd", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    if not args.prd.exists() or not args.sdd.exists():
        print("error: PRD or SDD missing", file=sys.stderr)
        return 1
    prd_reqs = extract(args.prd.read_text(encoding="utf-8"), REQ_RE, "REQ")
    sdd_comps = extract(args.sdd.read_text(encoding="utf-8"), COMP_RE, "COMP")
    errors = validate(args.file.read_text(encoding="utf-8"), prd_reqs, sdd_comps)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
