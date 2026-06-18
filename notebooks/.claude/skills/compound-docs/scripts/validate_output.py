#!/usr/bin/env python3
"""
validate_output.py — validate a written solution file end-to-end.

Runs validate_frontmatter.py and checks the body has all six required sections
(Symptom, Investigation, Root Cause, Solution, Verification, Prevention) in
order.

Usage:
  python validate_output.py --file path/to/solution.md

Exit codes:
  0  pass
  1  fail (errors on stderr)
  2  unexpected error
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_frontmatter import (  # noqa: E402
    parse_yaml,
    split_frontmatter,
    validate as validate_fm,
)

REQUIRED_SECTIONS = ["Symptom", "Investigation", "Root Cause", "Solution", "Verification", "Prevention"]


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def section_order(body: str) -> List[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)]


def validate_body(body: str) -> List[str]:
    errors: List[str] = []
    found = section_order(body)
    found_set = set(found)
    for sec in REQUIRED_SECTIONS:
        if sec not in found_set:
            errors.append(f"body missing required section: ## {sec}")

    indices: List[int] = []
    for sec in REQUIRED_SECTIONS:
        if sec in found_set:
            indices.append(found.index(sec))
    if indices and indices != sorted(indices):
        errors.append(f"body sections out of order; expected order: {REQUIRED_SECTIONS}, got: {found}")
    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("validate-output")

    try:
        text = args.file.read_text(encoding="utf-8")
    except FileNotFoundError:
        log.error("file not found: %s", args.file)
        return 1
    except Exception as e:  # noqa: BLE001
        log.exception("read error: %s", e)
        return 2

    try:
        yaml_text, body = split_frontmatter(text)
        data = parse_yaml(yaml_text)
    except ValueError as e:
        log.error("frontmatter parse error: %s", e)
        return 1

    errors = validate_fm(data) + validate_body(body)
    if errors:
        for e in errors:
            log.error(e)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
