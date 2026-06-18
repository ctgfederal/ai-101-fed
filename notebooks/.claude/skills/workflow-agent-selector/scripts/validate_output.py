#!/usr/bin/env python3
"""validate_output.py — validate a written match-results.md report.

The report must be a markdown table with at least these columns:
  | Agent | Score | Reason |

Score must parse as a float in 0.0..1.0.

Usage:
  python validate_output.py --file match-results.md

Exit 0 = pass, 1 = fail (errors on stderr).
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["Agent", "Score", "Reason"]


def parse_table(text: str) -> tuple[list[str], list[list[str]]]:
    """Return (headers, rows) for the first markdown table found. Empty if none."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    header_idx = None
    for i, ln in enumerate(lines):
        if "|" not in ln:
            continue
        # next line must be a separator like |---|---|
        if i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            header_idx = i
            break
    if header_idx is None:
        return [], []
    headers = [c.strip() for c in lines[header_idx].strip().strip("|").split("|")]
    rows: list[list[str]] = []
    for ln in lines[header_idx + 2 :]:
        if "|" not in ln or not ln.strip():
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    return headers, rows


def validate(text: str) -> list[str]:
    errors: list[str] = []
    headers, rows = parse_table(text)
    if not headers:
        return ["no markdown table found in report"]

    missing = [c for c in REQUIRED_COLUMNS if c not in headers]
    if missing:
        errors.append(f"missing required columns: {missing} (found: {headers})")
        return errors

    score_idx = headers.index("Score")
    agent_idx = headers.index("Agent")

    if not rows:
        errors.append("table has no data rows")
        return errors

    for row_num, cells in enumerate(rows, start=1):
        if len(cells) != len(headers):
            errors.append(f"row {row_num}: cell count {len(cells)} != header count {len(headers)}")
            continue
        agent = cells[agent_idx]
        if not agent:
            errors.append(f"row {row_num}: empty Agent cell")
        raw = cells[score_idx]
        try:
            score = float(raw)
        except ValueError:
            errors.append(f"row {row_num}: Score {raw!r} is not a number")
            continue
        if not (0.0 <= score <= 1.0):
            errors.append(f"row {row_num}: Score {score} out of range 0.0..1.0")
    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.is_file():
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
