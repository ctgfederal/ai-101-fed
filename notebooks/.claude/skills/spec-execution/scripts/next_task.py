#!/usr/bin/env python3
"""next_task.py — return the next task to execute from the execution state.

Selection rule:
  Lowest T-NNN (by document order, then numeric ID) that:
    - has status == 'pending'
    - has every entry in `depends_on` with status == 'done'

Args:
  --feature      feature folder name under --specs-root
  --specs-root   directory containing <feature>/execution-state.json

Output:
  Prints the selected task as JSON to stdout:
    {"id": "T-003", "description": "...", "status": "pending", ...}
  Prints empty JSON object {} if no eligible tasks remain.
  Exit 0 in both cases.
  Exit 1 only on I/O / state errors.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def state_path(specs_root: Path, feature: str) -> Path:
    return specs_root / feature / "execution-state.json"


def task_sort_key(state: dict, tid: str) -> tuple:
    """Sort key: (document-order index, numeric id)."""
    order = state.get("task_order", [])
    try:
        idx = order.index(tid)
    except ValueError:
        idx = len(order)
    m = re.match(r"T-(\d+)", tid)
    n = int(m.group(1)) if m else 9_999_999
    return (idx, n)


def find_next(state: dict) -> dict:
    tasks = state.get("tasks", {})
    if not tasks:
        return {}
    eligible = []
    for tid, t in tasks.items():
        if t.get("status") != "pending":
            continue
        deps = t.get("depends_on") or []
        if all(tasks.get(d, {}).get("status") == "done" for d in deps):
            eligible.append(tid)
    if not eligible:
        return {}
    eligible.sort(key=lambda tid: task_sort_key(state, tid))
    chosen_id = eligible[0]
    chosen = dict(tasks[chosen_id])
    chosen["id"] = chosen_id
    return chosen


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--feature", required=True)
    p.add_argument("--specs-root", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    sp = state_path(args.specs_root, args.feature)
    if not sp.exists():
        print(f"state not found: {sp}", file=sys.stderr)
        return 1
    state = json.loads(sp.read_text(encoding="utf-8"))
    print(json.dumps(find_next(state)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
