#!/usr/bin/env python3
"""extract_ids.py — extract REQ/COMP/T IDs from PRD/SDD/PLAN, then grep code refs.

Reads:
  - PRD for REQ-NNN definitions
  - SDD for COMP-NNN definitions and REQ -> COMP traceability lines
  - PLAN for T-NNN tasks and their reqs[] lists
  - code root: greps every file matching --code-globs for REQ-NNN occurrences,
    classifying each file as "code" or "test" based on path heuristics

Output JSON shape:
  {
    "prd_reqs": ["REQ-001", ...],
    "sdd_comps": ["COMP-001", ...],
    "plan_tasks": ["T-001", ...],
    "sdd_traceability": {"REQ-001": ["COMP-001", "COMP-002"], ...},
    "plan_task_reqs": {"T-001": ["REQ-001"], ...},
    "code_refs": {"REQ-001": ["src/foo.py", ...]},
    "test_refs": {"REQ-001": ["tests/test_foo.py", ...]}
  }

Usage:
  python extract_ids.py --prd PRD.md --sdd SDD.md --plan PLAN.md \
      --code-root . [--code-globs "*.py,*.test.py,*.ts,*.tsx"]
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQ_RE = re.compile(r"\bREQ-(\d+)\b")
COMP_RE = re.compile(r"\bCOMP-(\d+)\b")
TASK_RE = re.compile(r"\bT-(\d+)\b")

# A line in SDD that maps a REQ to one or more COMPs:
#   REQ-001 -> COMP-001, COMP-002
#   REQ-001: COMP-001, COMP-002
#   | REQ-001 | COMP-001, COMP-002 |
SDD_TRACE_RE = re.compile(
    r"\bREQ-(\d+)\b[^\n]*?(?:->|:|\|)\s*((?:COMP-\d+\s*,?\s*)+)",
)

# A PLAN task block. We assume a structured format like:
#   - **T-001** ... Requirements: REQ-001, REQ-002
PLAN_TASK_REQS_RE = re.compile(
    r"\bT-(\d+)\b[^\n]*?(?:\n[^\n]*?)*?Requirements:\s*((?:REQ-\d+\s*,?\s*)+)",
    re.IGNORECASE,
)

DEFAULT_GLOBS = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.go", "*.rs", "*.java"]
TEST_PATH_HINTS = ("test_", "_test", "/tests/", "/test/", ".test.", ".spec.")


def _format_id(prefix: str, n: int, width: int) -> str:
    return f"{prefix}-{n:0{width}d}"


def extract_ids(text: str, pattern: re.Pattern, prefix: str) -> list[str]:
    nums = sorted({int(m) for m in pattern.findall(text)})
    if not nums:
        return []
    width = max(3, len(str(nums[-1])))
    return [_format_id(prefix, n, width) for n in nums]


def parse_sdd_traceability(text: str) -> dict[str, list[str]]:
    """Parse SDD lines mapping REQ -> COMP."""
    out: dict[str, set[str]] = {}
    for m in SDD_TRACE_RE.finditer(text):
        req_num = int(m.group(1))
        req_id = f"REQ-{req_num:03d}"
        comps_blob = m.group(2)
        comp_nums = sorted({int(x) for x in COMP_RE.findall(comps_blob)})
        if not comp_nums:
            continue
        out.setdefault(req_id, set()).update(
            f"COMP-{n:03d}" for n in comp_nums
        )
    return {k: sorted(v) for k, v in out.items()}


def parse_plan_task_reqs(text: str) -> dict[str, list[str]]:
    """Parse a PLAN; map task ID to list of REQ IDs."""
    out: dict[str, set[str]] = {}
    for m in PLAN_TASK_REQS_RE.finditer(text):
        task_num = int(m.group(1))
        task_id = f"T-{task_num:03d}"
        reqs_blob = m.group(2)
        req_nums = sorted({int(x) for x in REQ_RE.findall(reqs_blob)})
        if not req_nums:
            continue
        out.setdefault(task_id, set()).update(
            f"REQ-{n:03d}" for n in req_nums
        )
    return {k: sorted(v) for k, v in out.items()}


def is_test_file(path: Path) -> bool:
    """Classify by file basename and immediate parent directories only.

    We deliberately ignore the full absolute path because temp directories
    (e.g., pytest's `pytest-58/test_xxx0/`) can contain `test_` substrings
    that have nothing to do with the file under test.
    """
    name = path.name.lower()
    if name.startswith("test_") or name.endswith("_test.py") or name.endswith("_test.go"):
        return True
    if ".test." in name or ".spec." in name:
        return True
    # Check immediate parent directory names
    for parent in path.parents:
        pname = parent.name.lower()
        if pname in {"test", "tests", "__tests__", "spec", "specs"}:
            return True
        # Stop walking once we exit a likely project boundary
        if parent.name in ("", "/"):
            break
    return False


def grep_code_refs(
    code_root: Path,
    globs: list[str],
    reqs: list[str],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Grep all matching files for REQ IDs.

    Returns (code_refs, test_refs): each is REQ_ID -> sorted list of relative paths.
    """
    code_refs: dict[str, set[str]] = {r: set() for r in reqs}
    test_refs: dict[str, set[str]] = {r: set() for r in reqs}

    if not code_root.is_dir() or not reqs:
        return ({k: sorted(v) for k, v in code_refs.items()},
                {k: sorted(v) for k, v in test_refs.items()})

    seen: set[Path] = set()
    for pat in globs:
        for fp in code_root.rglob(pat):
            if fp in seen or not fp.is_file():
                continue
            seen.add(fp)
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
            found = set(REQ_RE.findall(text))
            if not found:
                continue
            rel = fp.relative_to(code_root).as_posix()
            test_file = is_test_file(fp)
            for num_str in found:
                req_id = f"REQ-{int(num_str):03d}"
                if req_id not in code_refs:
                    # not in PRD; skip
                    continue
                if test_file:
                    test_refs[req_id].add(rel)
                else:
                    code_refs[req_id].add(rel)

    return ({k: sorted(v) for k, v in code_refs.items()},
            {k: sorted(v) for k, v in test_refs.items()})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--prd", required=True, type=Path)
    p.add_argument("--sdd", required=True, type=Path)
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--code-root", required=True, type=Path)
    p.add_argument(
        "--code-globs",
        default=",".join(DEFAULT_GLOBS),
        help="comma-separated glob patterns to search under --code-root",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    for label, path in (("PRD", args.prd), ("SDD", args.sdd), ("PLAN", args.plan)):
        if not path.exists():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 1
    if not args.code_root.exists():
        print(f"error: code root not found: {args.code_root}", file=sys.stderr)
        return 1

    prd_text = args.prd.read_text(encoding="utf-8")
    sdd_text = args.sdd.read_text(encoding="utf-8")
    plan_text = args.plan.read_text(encoding="utf-8")

    prd_reqs = extract_ids(prd_text, REQ_RE, "REQ")
    sdd_comps = extract_ids(sdd_text, COMP_RE, "COMP")
    plan_tasks = extract_ids(plan_text, TASK_RE, "T")
    sdd_trace = parse_sdd_traceability(sdd_text)
    plan_task_reqs = parse_plan_task_reqs(plan_text)

    globs = [g.strip() for g in args.code_globs.split(",") if g.strip()]
    code_refs, test_refs = grep_code_refs(args.code_root, globs, prd_reqs)

    out = {
        "prd_reqs": prd_reqs,
        "sdd_comps": sdd_comps,
        "plan_tasks": plan_tasks,
        "sdd_traceability": sdd_trace,
        "plan_task_reqs": plan_task_reqs,
        "code_refs": code_refs,
        "test_refs": test_refs,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
