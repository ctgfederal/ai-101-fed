#!/usr/bin/env python3
"""state_manager.py — init / read / update build state at .claude/builds/<feature>/state.json.

Subcommands:
  init   --feature X --builds-root ROOT     Create dir + minimal state if missing.
  read   --feature X --builds-root ROOT     Print state JSON to stdout.
  update --feature X --builds-root ROOT [--patch PATH | stdin]   Merge patch into state.

Exit codes:
  0  success
  1  validation / missing-state error
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


INITIAL_STATE = {
    "feature": "",
    "brainstorm_path": None,
    "current_category": None,
    "current_decision": 0,
    "decisions": {},
    "auto_applied": [],
    "locked_decisions": [],
    "open_questions": [],
    "notes": [],
    "meta": {"last_updated": "", "sessions": 0},
}


def state_path(builds_root: Path, feature: str) -> Path:
    return builds_root / feature / "state.json"


def deep_merge(base: dict, patch: dict) -> dict:
    """Merge patch into base recursively. Patch values overwrite. Lists are replaced, not concatenated."""
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def cmd_init(args) -> int:
    p = state_path(args.builds_root, args.feature)
    if p.exists():
        print(f"state already exists: {p}", file=sys.stderr)
        return 0  # idempotent
    p.parent.mkdir(parents=True, exist_ok=True)
    state = dict(INITIAL_STATE)
    state["feature"] = args.feature
    state["meta"] = {"last_updated": date.today().isoformat(), "sessions": 1}
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(str(p))
    return 0


def cmd_read(args) -> int:
    p = state_path(args.builds_root, args.feature)
    if not p.exists():
        print(f"state not found: {p}", file=sys.stderr)
        return 1
    print(p.read_text(encoding="utf-8"))
    return 0


def cmd_update(args) -> int:
    p = state_path(args.builds_root, args.feature)
    if not p.exists():
        print(f"state not found: {p} (run init first)", file=sys.stderr)
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
    if not isinstance(patch, dict):
        print("patch must be a JSON object", file=sys.stderr)
        return 1
    state = json.loads(p.read_text(encoding="utf-8"))
    merged = deep_merge(state, patch)
    merged.setdefault("meta", {})["last_updated"] = date.today().isoformat()
    p.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(str(p))
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "read", "update"):
        sp = sub.add_parser(name)
        sp.add_argument("--feature", required=True)
        sp.add_argument("--builds-root", required=True, type=Path)
        if name == "update":
            sp.add_argument("--patch", type=Path, default=None, help="JSON patch file (default: stdin)")
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
