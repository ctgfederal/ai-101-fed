#!/usr/bin/env python3
"""validate_tasks.py — grade each parsed task against the rubric.

Input: a JSON list of task dicts produced by `parse_tasks.py` (via `--tasks`).
Optional: PRD/SDD paths so cross-references can be checked against the truth set.

Output JSON shape (matches what `write_report.py` consumes):
  {
    "plan": "<path-or-empty>",
    "tasks": [
      {
        "id":     "T-001",
        "title":  "...",
        "phase":  "Foundation",
        "status": "ok" | "warn" | "fail",
        "issues": ["..."]
      },
      ...
    ],
    "summary": {"total": N, "ok": N, "warn": N, "fail": N},
    "verdict": "PASS" | "WARN" | "FAIL"
  }

Verdict rules (also documented in knowledge/verdict-thresholds.md):
  - PASS: every task ok
  - WARN: no fails AND ≥1 warn
  - FAIL: ≥1 fail

Usage:
  python validate_tasks.py --tasks tasks.json [--prd PRD.md] [--sdd SDD.md] [--plan PLAN.md]
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional


ALLOWED_PHASES = {"Foundation", "Core", "Integration", "Polish"}
ALLOWED_TDD = {"red", "green", "refactor"}
TASK_ID_RE = re.compile(r"^T-\d{3,}$")
REQ_DEF_RE = re.compile(r"\*\*(REQ-\d+)\*\*")
COMP_DEF_RE = re.compile(r"\*\*(COMP-\d+)\*\*")

# A measurable acceptance line contains at least one observation cue.
OBSERVATION_TOKENS = [
    "passes", "pass",
    "returns", "return",
    "matches", "match",
    "exits", "exit",
    "equals", "equal",
    "produces", "produce",
    "outputs", "output",
    "raises", "raise",
    "asserts", "assert",
    "<=", ">=", "==", "<", ">", "=",
]
# Words that strongly indicate UN-measurable (vibes-based) acceptance.
VAGUE_TOKENS = {"should work", "looks good", "tbd", "works fine"}


def _extract_ids(path: Optional[Path], pattern: re.Pattern) -> set:
    if path is None or not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    return {m.group(1) for m in pattern.finditer(text)}


def _is_measurable(text: str) -> bool:
    """Return True if the acceptance string mentions at least one observation token
    AND does not look obviously vague."""
    if not text or not text.strip():
        return False
    low = text.lower()
    for v in VAGUE_TOKENS:
        if v in low:
            return False
    # whole-word check for textual tokens
    for tok in OBSERVATION_TOKENS:
        if not tok.isalpha():
            if tok in text:
                return True
            continue
        # word-boundary search for alpha tokens
        if re.search(rf"\b{re.escape(tok)}\b", low):
            return True
    return False


def validate_task(task: dict, prd_reqs: set, sdd_comps: set, prd_provided: bool, sdd_provided: bool) -> dict:
    """Return a dict {id, title, phase, status, issues}."""
    issues: List[str] = []

    # ID format
    tid = task.get("id", "")
    if not isinstance(tid, str) or not TASK_ID_RE.match(tid):
        issues.append(f"bad task ID format: {tid!r} (expected T-NNN)")

    # phase
    phase = task.get("phase", "")
    if phase not in ALLOWED_PHASES:
        issues.append(f"phase {phase!r} not in {sorted(ALLOWED_PHASES)}")

    # tdd step
    tdd = task.get("tdd_step", "")
    if not tdd:
        issues.append("missing TDD step (expected one of red/green/refactor)")
    elif tdd not in ALLOWED_TDD:
        issues.append(f"invalid TDD step: {tdd!r}")

    # acceptance
    acc = task.get("acceptance", "")
    if not acc or not str(acc).strip():
        issues.append("missing acceptance criterion")
    elif not _is_measurable(str(acc)):
        issues.append(f"acceptance not measurable: {acc!r}")

    # REQ refs (only checkable if PRD provided)
    reqs = task.get("reqs", []) or []
    if prd_provided:
        dangling_reqs = [r for r in reqs if r not in prd_reqs]
        if dangling_reqs:
            issues.append(f"reference(s) to undefined REQ ID(s): {', '.join(dangling_reqs)}")

    # COMP refs (only checkable if SDD provided)
    comps = task.get("comps", []) or []
    if sdd_provided:
        dangling_comps = [c for c in comps if c not in sdd_comps]
        if dangling_comps:
            issues.append(f"reference(s) to undefined COMP ID(s): {', '.join(dangling_comps)}")

    # Stylistic: title should not be empty / lowercase only
    title = task.get("title", "")
    style_only_issues: List[str] = []
    if title and title == title.lower():
        style_only_issues.append("title is all-lowercase (style)")

    # status
    if issues:
        status = "fail"
    elif style_only_issues:
        status = "warn"
        issues = style_only_issues
    else:
        status = "ok"

    return {
        "id": tid,
        "title": title,
        "phase": phase,
        "status": status,
        "issues": issues,
    }


def compute_verdict(rows: List[dict]) -> str:
    if any(r["status"] == "fail" for r in rows):
        return "FAIL"
    if any(r["status"] == "warn" for r in rows):
        return "WARN"
    return "PASS"


def validate_all(
    tasks: List[dict],
    plan_path: str = "",
    prd: Optional[Path] = None,
    sdd: Optional[Path] = None,
) -> dict:
    prd_reqs = _extract_ids(prd, REQ_DEF_RE) if prd else set()
    sdd_comps = _extract_ids(sdd, COMP_DEF_RE) if sdd else set()
    prd_provided = prd is not None and prd.exists()
    sdd_provided = sdd is not None and sdd.exists()

    rows = [
        validate_task(t, prd_reqs, sdd_comps, prd_provided, sdd_provided)
        for t in tasks
    ]
    summary = {
        "total": len(rows),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "warn": sum(1 for r in rows if r["status"] == "warn"),
        "fail": sum(1 for r in rows if r["status"] == "fail"),
    }
    return {
        "plan": plan_path,
        "tasks": rows,
        "summary": summary,
        "verdict": compute_verdict(rows),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--tasks", required=True, type=Path,
                   help="path to JSON list of tasks (output of parse_tasks.py)")
    p.add_argument("--prd", type=Path, default=None, help="optional PRD.md path")
    p.add_argument("--sdd", type=Path, default=None, help="optional SDD.md path")
    p.add_argument("--plan", type=Path, default=None,
                   help="optional original PLAN.md path (for the report header)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.tasks.exists():
        print(f"error: tasks file not found: {args.tasks}", file=sys.stderr)
        return 1
    try:
        tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid tasks JSON: {e}", file=sys.stderr)
        return 1
    if not isinstance(tasks, list):
        print("error: tasks JSON must be a list", file=sys.stderr)
        return 1
    payload = validate_all(
        tasks,
        plan_path=str(args.plan) if args.plan else "",
        prd=args.prd,
        sdd=args.sdd,
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
