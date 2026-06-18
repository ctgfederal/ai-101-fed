#!/usr/bin/env python3
"""check_chain.py — check a planned delegation chain for cycles and type mismatches.

Input: JSON with shape {"chain": [<handoff>, ...]}, where each handoff has at
least `from_agent`, `to_agent`, and ideally `output_type` and
`expected_input_type` for the consecutive type-match check.

Detects:
  - Cycles in the directed handoff graph (A->B->A, A->A, etc.)
  - Output / input type mismatches between consecutive steps
  - Empty or malformed chain entries

Output JSON:
  {"valid": bool, "issues": [str, ...], "pattern": "linear" | "fan-out" | "fan-in" | "mixed" | "unknown"}

Usage:
  python check_chain.py --chain-json path/to/chain.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def detect_cycle(edges: List[tuple]) -> List[str]:
    """Return list of nodes involved in any cycle (empty if none)."""
    graph: Dict[str, Set[str]] = defaultdict(set)
    nodes: Set[str] = set()
    for a, b in edges:
        graph[a].add(b)
        nodes.add(a)
        nodes.add(b)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {n: WHITE for n in nodes}
    cycle_nodes: Set[str] = set()

    def dfs(u: str, path: List[str]) -> bool:
        color[u] = GRAY
        path.append(u)
        for v in graph[u]:
            if color[v] == GRAY:
                # found a back edge — cycle
                if v in path:
                    cycle_nodes.update(path[path.index(v):])
                else:
                    cycle_nodes.add(v)
                return True
            if color[v] == WHITE:
                if dfs(v, path):
                    return True
        color[u] = BLACK
        path.pop()
        return False

    for n in list(nodes):
        if color[n] == WHITE:
            dfs(n, [])

    return sorted(cycle_nodes)


def detect_pattern(chain: List[dict]) -> str:
    """Heuristic: linear if every from->to is unique and chained; fan-out if
    one source has multiple targets; fan-in if multiple sources hit one target."""
    if not chain:
        return "unknown"
    sources = [step["from_agent"] for step in chain if "from_agent" in step]
    targets = [step["to_agent"] for step in chain if "to_agent" in step]
    src_count: Dict[str, int] = defaultdict(int)
    tgt_count: Dict[str, int] = defaultdict(int)
    for s in sources:
        src_count[s] += 1
    for t in targets:
        tgt_count[t] += 1
    has_fan_out = any(c > 1 for c in src_count.values())
    has_fan_in = any(c > 1 for c in tgt_count.values())
    if has_fan_out and has_fan_in:
        return "mixed"
    if has_fan_out:
        return "fan-out"
    if has_fan_in:
        return "fan-in"
    return "linear"


def check(chain: List[dict]) -> dict:
    issues: List[str] = []

    if not isinstance(chain, list):
        return {"valid": False, "issues": ["chain must be a list"], "pattern": "unknown"}
    if not chain:
        return {"valid": False, "issues": ["chain is empty"], "pattern": "unknown"}

    edges: List[tuple] = []
    for i, step in enumerate(chain):
        if not isinstance(step, dict):
            issues.append(f"step[{i}] is not an object")
            continue
        fa = step.get("from_agent")
        ta = step.get("to_agent")
        if not isinstance(fa, str) or not fa.strip():
            issues.append(f"step[{i}] missing from_agent")
            continue
        if not isinstance(ta, str) or not ta.strip():
            issues.append(f"step[{i}] missing to_agent")
            continue
        if fa.strip() == ta.strip():
            issues.append(f"step[{i}] self-handoff ({fa} -> {ta})")
        edges.append((fa.strip(), ta.strip()))

    # cycle detection
    cycle_nodes = detect_cycle(edges)
    if cycle_nodes:
        issues.append(f"cycle detected involving: {', '.join(cycle_nodes)}")

    # consecutive type-match check (only for sequential / linear)
    pattern = detect_pattern(chain)
    if pattern == "linear":
        for i in range(len(chain) - 1):
            cur = chain[i]
            nxt = chain[i + 1]
            cur_out = cur.get("output_type")
            nxt_in = nxt.get("expected_input_type")
            if cur_out is None or nxt_in is None:
                # missing type info — warn-style issue
                if cur_out is None:
                    issues.append(f"step[{i}] missing output_type (cannot type-check)")
                if nxt_in is None:
                    issues.append(f"step[{i + 1}] missing expected_input_type (cannot type-check)")
                continue
            if cur_out != nxt_in:
                issues.append(
                    f"type mismatch step[{i}].output_type={cur_out!r} != "
                    f"step[{i + 1}].expected_input_type={nxt_in!r}"
                )

    valid = len(issues) == 0
    return {"valid": valid, "issues": issues, "pattern": pattern}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--chain-json", required=True, type=Path, help="path to chain JSON")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.chain_json.exists():
        print(f"error: file not found: {args.chain_json}", file=sys.stderr)
        return 1
    try:
        text = args.chain_json.read_text(encoding="utf-8")
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(json.dumps({"valid": False, "issues": [f"invalid JSON: {e}"], "pattern": "unknown"}, indent=2))
        return 1

    chain = data.get("chain") if isinstance(data, dict) else data
    result = check(chain)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
