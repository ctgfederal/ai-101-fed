#!/usr/bin/env python3
"""validate_output.py — validate a rendered 3Cs report.

Checks:
  - Required `##` sections present in order
  - Each of Completeness, Consistency, Correctness, Overall scores is an
    integer in [0, 10]
  - Verdict is one of PASS / WARN / FAIL
  - Every sub-score < 10 has at least one matching entry under ## Issues
  - No unsubstituted `{{...}}` template tokens

Usage:
  python validate_output.py --file path/to/report.md
"""
import argparse
import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Target", "Scores", "Completeness", "Consistency", "Correctness",
    "Issues", "Verdict",
]
ALLOWED_VERDICTS = {"PASS", "WARN", "FAIL"}
SCORE_RE = re.compile(r"Score:\s*(\d+)\s*/\s*10")
ROW_RE = re.compile(r"\|\s*(Completeness|Consistency|Correctness|\*\*Overall\*\*)\s*\|\s*\**(\d+)/10\**\s*\|")
VERDICT_LINE_RE = re.compile(r"^\*\*(PASS|WARN|FAIL)\*\*\s*$", re.MULTILINE)
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")


def validate(text: str) -> list[str]:
    errors: list[str] = []

    # template token check
    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    # section presence + order
    found = [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, flags=re.MULTILINE)]
    found_set = set(found)
    for sect in REQUIRED_SECTIONS:
        if sect not in found_set:
            errors.append(f"missing section: ## {sect}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    # extract scores from the score table
    scores: dict[str, int] = {}
    for m in ROW_RE.finditer(text):
        name = m.group(1).strip("*").strip()
        scores[name] = int(m.group(2))
    for needed in ("Completeness", "Consistency", "Correctness", "Overall"):
        if needed not in scores:
            errors.append(f"score row missing in Scores table: {needed}")
            continue
        v = scores[needed]
        if not (0 <= v <= 10):
            errors.append(f"{needed} score out of range: {v}")

    # verdict line
    vmatch = VERDICT_LINE_RE.search(text)
    if not vmatch:
        errors.append("no verdict line found (expected **PASS|WARN|FAIL** alone on a line)")
    elif vmatch.group(1) not in ALLOWED_VERDICTS:
        errors.append(f"invalid verdict: {vmatch.group(1)}")

    # any sub-score < 10 must have at least one issue listed
    issues_section_match = re.search(
        r"^##\s+Issues\s*$(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if issues_section_match:
        issues_body = issues_section_match.group(1).strip()
    else:
        issues_body = ""

    bullet_count = len(re.findall(r"^\s*-\s+", issues_body, flags=re.MULTILINE))
    needs_issues = any(scores.get(k, 10) < 10 for k in ("Completeness", "Consistency", "Correctness"))
    if needs_issues and bullet_count == 0 and "_(no issues found)_" in issues_body:
        errors.append("at least one sub-score < 10 but Issues section says '(no issues found)'")

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
