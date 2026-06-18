#!/usr/bin/env python3
"""check_collisions.py — detect FOCUS file-path overlap across multiple delegation payloads.

Two agents launched in parallel must not share any FOCUS path. This script
reads a JSON list of payloads, normalizes each FOCUS set, expands simple
`*` and `**` globs into prefix matches, and reports every pair (or N-tuple)
of agents whose FOCUS sets intersect.

Glob handling (simple, no filesystem walk):
  - Trailing `/` on a path is normalized off.
  - Trailing `/*` or `/**` are treated as "prefix" matches: any path that
    starts with the same prefix collides.
  - Bare paths collide on exact match (after normalization).

Usage:
  python check_collisions.py --payloads-json <path>

Output: JSON to stdout
  {
    "collisions": [
      {"agents": ["auth-agent", "user-agent"], "files": ["src/shared/util.py"]}
    ],
    "safe": false
  }

Exit code: 0 always (the "safe" field carries the result).
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import List, Tuple


def normalize(path: str) -> Tuple[str, bool]:
    """Return (normalized_prefix, is_prefix_match).

    A `**` or `*` suffix means "match anything starting with this prefix".
    """
    p = path.strip().rstrip("/")
    if p.endswith("/**"):
        return p[:-3].rstrip("/"), True
    if p.endswith("/*"):
        return p[:-2].rstrip("/"), True
    if p.endswith("**"):
        return p[:-2].rstrip("/"), True
    if p.endswith("*"):
        return p[:-1].rstrip("/"), True
    # bare directory (no glob) — also acts like a prefix to catch nested files
    if "." not in Path(p).name and p:
        return p, True
    return p, False


def paths_collide(a: Tuple[str, bool], b: Tuple[str, bool]) -> bool:
    a_path, a_pref = a
    b_path, b_pref = b
    if a_path == b_path:
        return True
    if a_pref and (b_path == a_path or b_path.startswith(a_path + "/")):
        return True
    if b_pref and (a_path == b_path or a_path.startswith(b_path + "/")):
        return True
    return False


def find_collisions(payloads: List[dict]) -> List[dict]:
    """Return list of {agents, files} for every colliding pair."""
    normalized = []
    for p in payloads:
        agent = p.get("agent_type", "<unknown>")
        focus = [normalize(f) for f in p.get("focus_files", []) if isinstance(f, str)]
        normalized.append((agent, focus, p.get("focus_files", [])))

    collisions: List[dict] = []
    for (i, j) in combinations(range(len(normalized)), 2):
        agent_i, focus_i, raw_i = normalized[i]
        agent_j, focus_j, raw_j = normalized[j]
        shared: List[str] = []
        for ai_idx, ai in enumerate(focus_i):
            for aj_idx, aj in enumerate(focus_j):
                if paths_collide(ai, aj):
                    # Report the more specific raw form
                    shared.append(raw_i[ai_idx])
        if shared:
            # dedupe while preserving order
            seen = set()
            unique = []
            for s in shared:
                if s not in seen:
                    seen.add(s)
                    unique.append(s)
            collisions.append({"agents": [agent_i, agent_j], "files": unique})
    return collisions


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payloads-json", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payloads = json.loads(args.payloads_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e), "safe": False}))
        return 0

    if not isinstance(payloads, list):
        print(json.dumps({"error": "payloads-json must be a JSON list", "safe": False}))
        return 0

    if len(payloads) < 2:
        # Single (or zero) payload is always safe — nothing to collide with.
        print(json.dumps({"collisions": [], "safe": True}))
        return 0

    collisions = find_collisions(payloads)
    print(json.dumps({"collisions": collisions, "safe": not collisions}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
