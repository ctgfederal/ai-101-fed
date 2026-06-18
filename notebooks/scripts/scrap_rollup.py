"""Graduated tool: deterministic scrap-count rollup.

Manufactured from a converged agent trajectory in NB07 (adaptation).
Replaces N per-line LLM "add this up" turns with one deterministic call.
"""
import json
from collections import Counter


def rollup(labeled_lines: list[dict]) -> dict:
    """Count scrap lines per code. Same output every time, given same input."""
    counts = Counter(r["label"] for r in labeled_lines)
    return {"total": len(labeled_lines), "by_code": dict(sorted(counts.items()))}


if __name__ == "__main__":
    import sys
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    print(json.dumps(rollup(rows), indent=2))
