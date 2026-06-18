#!/usr/bin/env python3
"""validate_output.py — validate a spec-execution state file.

Checks:
  - Required top-level keys present: feature, current_task, tasks, task_order, meta
  - Every task entry has: description, status, history (list), blockers (list), depends_on (list)
  - Every status is one of: pending, in-progress, done, blocked, failed
  - Every task id referenced in PLAN.md is present in state.tasks
    (only when --plan is provided)
  - task_order matches the keys in tasks (no missing, no extras)
  - meta has last_updated and total_tasks

Args:
  --file   path to execution-state.json
  --plan   optional path to PLAN.md to cross-check task ids

Exit:
  0  valid
  1  one or more errors (printed to stderr)
"""

import argparse
import json
import re
import sys
from pathlib import Path

VALID_STATUSES = {"pending", "in-progress", "done", "blocked", "failed"}
TASK_RE = re.compile(
    r"^\s*-\s*\[[\sx]\]\s*\**(T-\d+)\**\s*[:\-]",
    re.MULTILINE,
)
REQUIRED_KEYS = ["feature", "current_task", "tasks", "task_order", "meta"]
TASK_REQUIRED = ["description", "status", "history", "blockers", "depends_on"]


def validate_state(state: dict, plan_text: str | None) -> list[str]:
    errors: list[str] = []

    for k in REQUIRED_KEYS:
        if k not in state:
            errors.append(f"missing top-level key: {k}")

    tasks = state.get("tasks", {})
    if not isinstance(tasks, dict):
        errors.append("tasks must be a dict")
        tasks = {}

    for tid, t in tasks.items():
        if not isinstance(t, dict):
            errors.append(f"tasks[{tid}] must be a dict")
            continue
        for f in TASK_REQUIRED:
            if f not in t:
                errors.append(f"tasks[{tid}] missing field: {f}")
        status = t.get("status")
        if status is not None and status not in VALID_STATUSES:
            errors.append(f"tasks[{tid}] invalid status: {status!r}")
        for list_field in ("history", "blockers", "depends_on"):
            if list_field in t and not isinstance(t[list_field], list):
                errors.append(f"tasks[{tid}].{list_field} must be a list")

    order = state.get("task_order", [])
    if isinstance(order, list):
        order_set = set(order)
        task_set = set(tasks.keys())
        missing = task_set - order_set
        extras = order_set - task_set
        if missing:
            errors.append(f"task_order missing ids present in tasks: {sorted(missing)}")
        if extras:
            errors.append(f"task_order has ids not in tasks: {sorted(extras)}")
    else:
        errors.append("task_order must be a list")

    meta = state.get("meta", {})
    if not isinstance(meta, dict):
        errors.append("meta must be a dict")
    else:
        for f in ("last_updated", "total_tasks"):
            if f not in meta:
                errors.append(f"meta missing field: {f}")

    if plan_text is not None:
        plan_ids = {m.group(1) for m in TASK_RE.finditer(plan_text)}
        missing_in_state = plan_ids - set(tasks.keys())
        if missing_in_state:
            errors.append(
                f"task ids referenced in PLAN.md but missing from state: {sorted(missing_in_state)}"
            )

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--plan", type=Path, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: state file not found: {args.file}", file=sys.stderr)
        return 1
    try:
        state = json.loads(args.file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {args.file}: {e}", file=sys.stderr)
        return 1
    plan_text = None
    if args.plan is not None:
        if not args.plan.exists():
            print(f"error: plan file not found: {args.plan}", file=sys.stderr)
            return 1
        plan_text = args.plan.read_text(encoding="utf-8")
    errors = validate_state(state, plan_text)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
