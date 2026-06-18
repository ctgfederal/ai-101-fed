#!/usr/bin/env python3
"""state_manager.py — init / read / update execution state at .claude/specs/<feature>/execution-state.json.

Subcommands:
  init   --feature X --specs-root ROOT    Read PLAN.md task list, create execution-state.json with one
                                          task entry per T-NNN found, all status=pending.
  read   --feature X --specs-root ROOT    Print state JSON to stdout.
  update --feature X --specs-root ROOT [--patch PATH | stdin]  Merge JSON patch into state.
                                          When updating a task status, value must be one of:
                                          pending, in-progress, done, blocked, failed.

Exit codes:
  0  success
  1  validation / missing-state / missing-PLAN error
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

VALID_STATUSES = {"pending", "in-progress", "done", "blocked", "failed"}

# Match a line like "- [ ] T-001: short description" or "- [x] T-002 [parallel]: description"
# Anchored to capture the T-NNN ID and the trailing description.
TASK_RE = re.compile(
    r"^\s*-\s*\[[\sx]\]\s*\**(T-\d+)\**\s*[:\-]\s*(.+?)\s*$",
    re.MULTILINE,
)


def state_path(specs_root: Path, feature: str) -> Path:
    return specs_root / feature / "execution-state.json"


def plan_path(specs_root: Path, feature: str) -> Path:
    return specs_root / feature / "PLAN.md"


def deep_merge(base: dict, patch: dict) -> dict:
    """Merge patch into base recursively. Lists and scalars are replaced, not concatenated."""
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def parse_plan_tasks(plan_text: str) -> list[dict]:
    """Extract T-NNN tasks from a PLAN.md body. Returns [{id, description}, ...] in document order."""
    tasks = []
    seen = set()
    for m in TASK_RE.finditer(plan_text):
        tid = m.group(1)
        desc = m.group(2).strip()
        if tid in seen:
            continue
        seen.add(tid)
        tasks.append({"id": tid, "description": desc})
    return tasks


def initial_state(feature: str, tasks: list[dict]) -> dict:
    return {
        "feature": feature,
        "current_task": None,
        "tasks": {
            t["id"]: {
                "description": t["description"],
                "status": "pending",
                "history": [],
                "blockers": [],
                "depends_on": [],
            }
            for t in tasks
        },
        "task_order": [t["id"] for t in tasks],
        "meta": {
            "last_updated": date.today().isoformat(),
            "sessions": 1,
            "total_tasks": len(tasks),
        },
    }


def cmd_init(args) -> int:
    sp = state_path(args.specs_root, args.feature)
    if sp.exists():
        print(f"state already exists: {sp}", file=sys.stderr)
        return 0  # idempotent
    pp = plan_path(args.specs_root, args.feature)
    if not pp.exists():
        print(f"PLAN.md not found: {pp}", file=sys.stderr)
        return 1
    plan_text = pp.read_text(encoding="utf-8")
    tasks = parse_plan_tasks(plan_text)
    if not tasks:
        print(f"no T-NNN tasks found in {pp}", file=sys.stderr)
        return 1
    sp.parent.mkdir(parents=True, exist_ok=True)
    state = initial_state(args.feature, tasks)
    sp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(str(sp))
    return 0


def cmd_read(args) -> int:
    sp = state_path(args.specs_root, args.feature)
    if not sp.exists():
        print(f"state not found: {sp}", file=sys.stderr)
        return 1
    print(sp.read_text(encoding="utf-8"))
    return 0


def _validate_patch(patch: dict, state: dict) -> str | None:
    """Return error message if patch is invalid, else None."""
    if not isinstance(patch, dict):
        return "patch must be a JSON object"
    tasks_patch = patch.get("tasks")
    if tasks_patch is None:
        return None
    if not isinstance(tasks_patch, dict):
        return "patch.tasks must be a dict keyed by task id"
    for tid, tval in tasks_patch.items():
        if not isinstance(tval, dict):
            return f"patch.tasks[{tid}] must be a dict"
        status = tval.get("status")
        if status is not None and status not in VALID_STATUSES:
            return f"invalid status {status!r} for {tid}; allowed: {sorted(VALID_STATUSES)}"
    return None


def cmd_update(args) -> int:
    sp = state_path(args.specs_root, args.feature)
    if not sp.exists():
        print(f"state not found: {sp} (run init first)", file=sys.stderr)
        return 1
    patch_text = args.patch.read_text(encoding="utf-8") if args.patch else sys.stdin.read()
    if not patch_text.strip():
        print("empty patch", file=sys.stderr)
        return 1
    try:
        patch = json.loads(patch_text)
    except json.JSONDecodeError as e:
        print(f"patch is not valid JSON: {e}", file=sys.stderr)
        return 1
    state = json.loads(sp.read_text(encoding="utf-8"))
    err = _validate_patch(patch, state)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    merged = deep_merge(state, patch)
    merged.setdefault("meta", {})["last_updated"] = date.today().isoformat()
    sp.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(str(sp))
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "read", "update"):
        sp = sub.add_parser(name)
        sp.add_argument("--feature", required=True)
        sp.add_argument("--specs-root", required=True, type=Path)
        if name == "update":
            sp.add_argument("--patch", type=Path, default=None,
                            help="JSON patch file (default: stdin)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.cmd == "init":
        return cmd_init(args)
    if args.cmd == "read":
        return cmd_read(args)
    if args.cmd == "update":
        return cmd_update(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
