#!/usr/bin/env python3
"""match_agents.py — rank agents by name + description match against keywords.

Usage:
  echo '{"keywords": ["react", "form"], "max_results": 5}' \
    | python match_agents.py --agents-root ~/.claude/agents

  python match_agents.py --keywords-json query.json --agents-root ~/.claude/agents

Prints a JSON list of {agent, score, reason, tools, model, file} sorted by
score descending. Score is 0.0–1.0.

Exit 0 = ran successfully (empty list is normal).
Exit 1 = bad input.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# parse_agent_frontmatter lives in the same scripts/ dir
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_agent_frontmatter import parse_agents  # noqa: E402

# Score weights — tuned so an exact-name hit always beats a description-only hit.
W_NAME_EXACT = 1.0
W_NAME_TOKEN = 0.7
W_DESC_TOKEN = 0.3
W_TOOL_TOKEN = 0.15


def _tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9+]+", s.lower()) if t}


def score_agent(keywords: list[str], agent: dict) -> tuple[float, list[str]]:
    """Return (score in 0..1, list of reason strings)."""
    name = (agent.get("name") or "").lower()
    desc = (agent.get("description") or "").lower()
    tools = [t.lower() for t in (agent.get("tools") or [])]

    name_tokens = _tokens(name)
    desc_tokens = _tokens(desc)
    tool_tokens = {t for tool in tools for t in _tokens(tool)}

    raw = 0.0
    reasons: list[str] = []
    for kw in keywords:
        kw_l = kw.lower().strip()
        if not kw_l:
            continue
        if kw_l == name:
            raw += W_NAME_EXACT
            reasons.append(f"exact name match: {kw!r}")
            continue
        if kw_l in name_tokens:
            raw += W_NAME_TOKEN
            reasons.append(f"name token match: {kw!r}")
            continue
        if kw_l in name and len(kw_l) >= 3:
            raw += W_NAME_TOKEN * 0.8
            reasons.append(f"name substring match: {kw!r}")
            continue
        if kw_l in desc_tokens:
            raw += W_DESC_TOKEN
            reasons.append(f"description token match: {kw!r}")
            continue
        if kw_l in desc and len(kw_l) >= 3:
            raw += W_DESC_TOKEN * 0.6
            reasons.append(f"description substring match: {kw!r}")
            continue
        if kw_l in tool_tokens:
            raw += W_TOOL_TOKEN
            reasons.append(f"tool match: {kw!r}")
            continue

    # Normalize: cap at sum of best possible single-keyword scores.
    if not keywords:
        return 0.0, []
    cap = max(W_NAME_EXACT, W_NAME_TOKEN) * len(keywords)
    score = min(raw / cap, 1.0) if cap > 0 else 0.0
    return score, reasons


def rank(keywords: list[str], agents: list[dict], max_results: int | None = None,
         min_score: float = 0.0) -> list[dict]:
    out: list[dict] = []
    for agent in agents:
        score, reasons = score_agent(keywords, agent)
        if score <= 0 or score < min_score:
            continue
        out.append(
            {
                "agent": agent.get("name", ""),
                "score": round(score, 4),
                "reason": "; ".join(reasons) if reasons else "",
                "tools": agent.get("tools", []),
                "model": agent.get("model", ""),
                "file": agent.get("file", ""),
            }
        )
    # Tie-breaker: smaller tool surface (more focused) wins.
    out.sort(key=lambda r: (-r["score"], len(r["tools"]), r["agent"]))
    if max_results is not None:
        out = out[:max_results]
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--keywords-json", type=Path, default=None,
                   help="Path to JSON file with {keywords, max_results, min_score}; default: stdin")
    p.add_argument("--agents-root", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    text = args.keywords_json.read_text(encoding="utf-8") if args.keywords_json else sys.stdin.read()
    if not text.strip():
        print("error: empty input", file=sys.stderr)
        return 1
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 1

    if isinstance(payload, list):
        keywords = payload
        max_results = None
        min_score = 0.0
    elif isinstance(payload, dict):
        keywords = payload.get("keywords", [])
        max_results = payload.get("max_results")
        min_score = float(payload.get("min_score", 0.0))
    else:
        print("error: payload must be a list or object", file=sys.stderr)
        return 1

    if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
        print("error: keywords must be a list of strings", file=sys.stderr)
        return 1

    if not args.agents_root.is_dir():
        print(f"error: agents root not found: {args.agents_root}", file=sys.stderr)
        return 1

    agents = parse_agents(args.agents_root)
    matches = rank(keywords, agents, max_results=max_results, min_score=min_score)
    print(json.dumps(matches, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
