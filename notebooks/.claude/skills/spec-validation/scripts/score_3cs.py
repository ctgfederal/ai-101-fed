#!/usr/bin/env python3
"""score_3cs.py — score a target file against the 3Cs framework.

Reads the target file, runs the deterministic checks defined in
knowledge/3cs-rubric.md, and prints a JSON payload suitable for
write_report.py.

Output JSON shape:
  {
    "target": "<path>",
    "completeness": 0-10,
    "consistency":  0-10,
    "correctness":  0-10,
    "overall":      0-10,
    "verdict":      "PASS" | "WARN" | "FAIL",
    "issues": [{"category": "<c>", "message": "<msg>"}],
    "completeness_notes": "<brief>",
    "consistency_notes":  "<brief>",
    "correctness_notes":  "<brief>"
  }

Usage:
  python score_3cs.py --file path/to/spec.md
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


EARS_PATTERNS = ["SHALL", "WHEN", "WHILE", "WHERE", "IF"]
ALLOWED_MOSCOW = {"Must", "Should", "Could", "Won't"}

# Detect lines defining an ID, e.g.   - **REQ-001** (story US-1, Must): ...
ID_DEF_RE = re.compile(r"\*\*([A-Z]{1,4}-\d+)\*\*")
# Detect any mention of an ID (definitions plus references)
ID_REF_RE = re.compile(r"\b([A-Z]{1,4}-\d+)\b")
# Heading detector
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# A line that *looks* like a requirement (definition of a REQ id)
REQ_LINE_RE = re.compile(r"^\s*-?\s*\*\*REQ-\d+\*\*.*", re.MULTILINE)
# MoSCoW value inside parentheses: (story US-1, Maybe): ...
MOSCOW_IN_LINE_RE = re.compile(r"\(([^)]*?)\)\s*:")


@dataclass
class Issue:
    category: str
    message: str


@dataclass
class Result:
    completeness: int = 10
    consistency: int = 10
    correctness: int = 10
    issues: List[Issue] = field(default_factory=list)
    notes: dict = field(default_factory=lambda: {
        "completeness": "", "consistency": "", "correctness": ""})


def _floor(n: int) -> int:
    return max(0, min(10, n))


def score_completeness(text: str, result: Result) -> None:
    deductions = 0

    headings = [m.group(1) for m in HEADING_RE.finditer(text)]
    if len(headings) < 3:
        deductions += 2
        result.issues.append(Issue("completeness",
                                   f"only {len(headings)} top-level section(s) found; expected at least 3"))

    if "[NEEDS CLARIFICATION]" in text:
        deductions += 3
        result.issues.append(Issue("completeness",
                                   "[NEEDS CLARIFICATION] marker present"))

    if re.search(r"\b(TODO|FIXME|XXX)\b", text):
        deductions += 1
        result.issues.append(Issue("completeness",
                                   "TODO / FIXME / XXX marker present"))

    # empty section detection: a `## ` immediately followed by another `## ` (no body lines between)
    empty = 0
    section_starts = [m.start() for m in HEADING_RE.finditer(text)]
    for i, start in enumerate(section_starts):
        end = section_starts[i + 1] if i + 1 < len(section_starts) else len(text)
        body = text[start:end].split("\n", 1)
        if len(body) < 2 or not body[1].strip():
            empty += 1
    if empty:
        deductions += empty
        result.issues.append(Issue("completeness", f"{empty} empty section(s)"))

    result.completeness = _floor(10 - deductions)
    result.notes["completeness"] = (
        f"{len(headings)} top-level sections; "
        f"NEEDS CLARIFICATION: {'yes' if '[NEEDS CLARIFICATION]' in text else 'no'}; "
        f"empty sections: {empty}."
    )


def score_consistency(text: str, result: Result) -> None:
    deductions = 0

    defined: dict[str, int] = {}
    for m in ID_DEF_RE.finditer(text):
        defined[m.group(1)] = defined.get(m.group(1), 0) + 1
    duplicates = [k for k, n in defined.items() if n > 1]
    if duplicates:
        deductions += min(6, 3 * len(duplicates))
        result.issues.append(Issue("consistency",
                                   f"duplicate ID definition(s): {', '.join(duplicates)}"))

    referenced = {m.group(1) for m in ID_REF_RE.finditer(text)}
    dangling = referenced - set(defined.keys())
    if dangling:
        deductions += min(6, 2 * len(dangling))
        result.issues.append(Issue("consistency",
                                   f"reference(s) to undefined ID(s): {', '.join(sorted(dangling))}"))

    result.consistency = _floor(10 - deductions)
    result.notes["consistency"] = (
        f"defined IDs: {len(defined)}; "
        f"referenced IDs: {len(referenced)}; "
        f"dangling: {len(dangling)}; duplicates: {len(duplicates)}."
    )


def score_correctness(text: str, result: Result) -> None:
    deductions = 0

    req_lines = REQ_LINE_RE.findall(text)
    non_ears = []
    for line in req_lines:
        if not any(p in line for p in EARS_PATTERNS):
            non_ears.append(line.strip()[:80])
    if non_ears:
        deductions += min(6, 2 * len(non_ears))
        result.issues.append(Issue("correctness",
                                   f"{len(non_ears)} requirement line(s) not EARS-formatted"))

    invalid_moscow = []
    for line in req_lines:
        m = MOSCOW_IN_LINE_RE.search(line)
        if not m:
            continue
        # parenthetical might be "story US-1, Must"
        parts = [x.strip() for x in m.group(1).split(",")]
        for part in parts:
            if part in {"Must", "Should", "Could", "Won't"}:
                break
        else:
            # found a parenthetical but no allowed MoSCoW token in it
            for part in parts:
                if re.match(r"^[A-Z][a-z]+$", part) and part not in ALLOWED_MOSCOW:
                    invalid_moscow.append(part)
                    break
    if invalid_moscow:
        deductions += min(4, 2 * len(invalid_moscow))
        result.issues.append(Issue("correctness",
                                   f"invalid MoSCoW value(s): {', '.join(set(invalid_moscow))}"))

    result.correctness = _floor(10 - deductions)
    result.notes["correctness"] = (
        f"requirement lines: {len(req_lines)}; "
        f"non-EARS: {len(non_ears)}; invalid MoSCoW: {len(invalid_moscow)}."
    )


def compute_verdict(c: int, k: int, r: int) -> str:
    if c < 5 or k < 5 or r < 5:
        return "FAIL"
    if c >= 8 and k >= 8 and r >= 8:
        return "PASS"
    return "WARN"


def score(text: str, target: str) -> dict:
    result = Result()
    score_completeness(text, result)
    score_consistency(text, result)
    score_correctness(text, result)
    overall = round((result.completeness + result.consistency + result.correctness) / 3)
    overall = _floor(overall)
    verdict = compute_verdict(result.completeness, result.consistency, result.correctness)
    return {
        "target": target,
        "completeness": result.completeness,
        "consistency": result.consistency,
        "correctness": result.correctness,
        "overall": overall,
        "verdict": verdict,
        "issues": [{"category": i.category, "message": i.message} for i in result.issues],
        "completeness_notes": result.notes["completeness"],
        "consistency_notes": result.notes["consistency"],
        "correctness_notes": result.notes["correctness"],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path,
                   help="path to the target file to score")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    payload = score(text, str(args.file))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
