#!/usr/bin/env python3
"""record_tdd_step.py — append a TDD-cycle entry to a task's history in execution-state.json.

Args:
  --feature      feature folder name under --specs-root
  --specs-root   directory containing <feature>/execution-state.json
  --task-id      T-NNN id of the task to update
  --step         one of: red, green, refactor
  --result       one of: pass, fail
  --note         optional human-readable note (string)
  --duration-s   optional integer duration in seconds

Behavior:
  Appends one record to state.tasks[task-id].history of shape:
    {"step": "<red|green|refactor>",
     "result": "<pass|fail>",
     "note": "<note or ''>",
     "duration_s": <int or null>,
     "timestamp": "YYYY-MM-DDTHH:MM:SS"}

  Updates state.meta.last_updated.

Exit codes:
  0  appended
  1  invalid args / unknown task / missing state
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path


VALID_STEPS = {"red", "green", "refactor"}
VALID_RESULTS = {"pass", "fail"}


def state_path(specs_root: Path, feature: str) -> Path:
    return specs_root / feature / "execution-state.json"


def append_record(state: dict, task_id: str, record: dict) -> str | None:
    tasks = state.get("tasks", {})
    if task_id not in tasks:
        return f"unknown task id: {task_id}"
    tasks[task_id].setdefault("history", []).append(record)
    state.setdefault("meta", {})["last_updated"] = date.today().isoformat()
    return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--feature", required=True)
    p.add_argument("--specs-root", required=True, type=Path)
    p.add_argument("--task-id", required=True)
    p.add_argument("--step", required=True, choices=sorted(VALID_STEPS))
    p.add_argument("--result", required=True, choices=sorted(VALID_RESULTS))
    p.add_argument("--note", default="")
    p.add_argument("--duration-s", type=int, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    sp = state_path(args.specs_root, args.feature)
    if not sp.exists():
        print(f"state not found: {sp}", file=sys.stderr)
        return 1
    state = json.loads(sp.read_text(encoding="utf-8"))
    record = {
        "step": args.step,
        "result": args.result,
        "note": args.note,
        "duration_s": args.duration_s,
        "timestamp": datetime.now().replace(microsecond=0).isoformat(),
    }
    err = append_record(state, args.task_id, record)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    sp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
