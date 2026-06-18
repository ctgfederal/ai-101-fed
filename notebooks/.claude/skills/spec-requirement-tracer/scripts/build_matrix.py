#!/usr/bin/env python3
"""build_matrix.py — build the per-requirement coverage matrix.

Reads the JSON output of `extract_ids.py` and produces a matrix payload:
  {
    "feature": "<feature-name>",
    "rows": [
      {
        "req": "REQ-001",
        "comps": ["COMP-001", ...],
        "tasks": ["T-001", ...],
        "code_refs": ["src/foo.py"],
        "tests_refs": ["tests/test_foo.py"],
        "status": "covered" | "partial" | "uncovered"
      },
      ...
    ]
  }

Status assignment:
  - covered:   ≥1 link at every layer (SDD comp, PLAN task, code ref, test ref)
  - partial:   ≥1 link at some layer, but not all four
  - uncovered: 0 links at every layer

Usage:
  python build_matrix.py --ids-json ids.json [--feature feature-name]
"""
import argparse
import json
import sys
from pathlib import Path


REQUIRED_KEYS = (
    "prd_reqs",
    "sdd_comps",
    "plan_tasks",
    "sdd_traceability",
    "plan_task_reqs",
    "code_refs",
    "test_refs",
)


def assign_status(comps: list, tasks: list, code: list, tests: list) -> str:
    layers = (bool(comps), bool(tasks), bool(code), bool(tests))
    if all(layers):
        return "covered"
    if any(layers):
        return "partial"
    return "uncovered"


def build(ids: dict, feature: str) -> dict:
    missing = [k for k in REQUIRED_KEYS if k not in ids]
    if missing:
        raise ValueError(f"ids JSON missing keys: {missing}")

    sdd_trace: dict[str, list[str]] = ids["sdd_traceability"]
    plan_task_reqs: dict[str, list[str]] = ids["plan_task_reqs"]
    code_refs: dict[str, list[str]] = ids["code_refs"]
    test_refs: dict[str, list[str]] = ids["test_refs"]

    # Invert plan_task_reqs to req -> [tasks]
    req_to_tasks: dict[str, set[str]] = {}
    for task_id, req_list in plan_task_reqs.items():
        for r in req_list:
            req_to_tasks.setdefault(r, set()).add(task_id)

    rows = []
    for req in ids["prd_reqs"]:
        comps = sorted(set(sdd_trace.get(req, [])))
        tasks = sorted(req_to_tasks.get(req, set()))
        code = sorted(set(code_refs.get(req, [])))
        tests = sorted(set(test_refs.get(req, [])))
        rows.append({
            "req": req,
            "comps": comps,
            "tasks": tasks,
            "code_refs": code,
            "tests_refs": tests,
            "status": assign_status(comps, tasks, code, tests),
        })

    return {"feature": feature, "rows": rows}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--ids-json", required=True, type=Path)
    p.add_argument(
        "--feature",
        default="unknown",
        help="feature name to embed in the payload",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.ids_json.exists():
        print(f"error: ids JSON not found: {args.ids_json}", file=sys.stderr)
        return 1
    try:
        ids = json.loads(args.ids_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {args.ids_json}: {e}", file=sys.stderr)
        return 1
    try:
        payload = build(ids, args.feature)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
