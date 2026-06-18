#!/usr/bin/env python3
"""validate_output.py — validate a rendered compliance report.

Checks:
  - Required `##` sections present in order
  - Status value is one of: compliant, partial, non-compliant
  - No unsubstituted `{{...}}` template tokens
  - Components and Requirements tables present (when expected)

Optionally, with `--spec-json`, also verifies that every COMP-ID and every
REQ-ID from the parsed-spec JSON appears somewhere in the rendered report.

Usage:
  python validate_output.py --file COMPLIANCE.md
  python validate_output.py --file COMPLIANCE.md --spec-json parsed.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Spec", "Repository", "Status", "Components",
    "Requirements", "Deviations", "Summary",
]
ALLOWED_STATUSES = {"compliant", "partial", "non-compliant"}
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
STATUS_LINE_RE = re.compile(r"^\*\*(compliant|partial|non-compliant)\*\*\s*$", re.MULTILINE)


def validate(text: str, spec: dict | None = None) -> list[str]:
    errors: list[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    found_set = set(found)
    for sect in REQUIRED_SECTIONS:
        if sect not in found_set:
            errors.append(f"missing section: ## {sect}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    smatch = STATUS_LINE_RE.search(text)
    if not smatch:
        errors.append(
            "no status line found (expected **compliant|partial|non-compliant** alone on a line)"
        )
    elif smatch.group(1) not in ALLOWED_STATUSES:
        errors.append(f"invalid status: {smatch.group(1)}")

    if spec is not None:
        for cid in {c["id"] for c in spec.get("comps", [])}:
            if cid not in text:
                errors.append(f"component {cid} from SDD missing from report")
        for rid in spec.get("reqs", []):
            if rid not in text:
                errors.append(f"requirement {rid} from PRD missing from report")

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--spec-json", type=Path, default=None,
                   help="optional parsed-spec JSON for required-coverage check")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    spec = None
    if args.spec_json is not None:
        if not args.spec_json.exists():
            print(f"error: spec JSON not found: {args.spec_json}", file=sys.stderr)
            return 1
        try:
            spec = json.loads(args.spec_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"error: invalid spec JSON: {e}", file=sys.stderr)
            return 1
    errors = validate(text, spec)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
