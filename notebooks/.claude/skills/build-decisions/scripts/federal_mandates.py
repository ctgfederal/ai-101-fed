#!/usr/bin/env python3
"""federal_mandates.py — auto-apply lookup table.

Subcommands:
  list                                    Print all mandates as JSON.
  lookup --category CAT --name DECISION   Find mandate; print {answer, citation} JSON, exit 0.
                                          Exit 1 (with empty stdout) if no match.

Mandates source: knowledge/federal-mandates.json
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "knowledge" / "federal-mandates.json"


def load_db(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "mandates" not in data:
        raise ValueError(f"malformed mandates DB at {path}: missing 'mandates'")
    return data["mandates"]


def lookup(mandates: list[dict], category: str, name: str) -> dict | None:
    for m in mandates:
        if m["category"].lower() == category.lower() and m["name"].lower() == name.lower():
            return {"answer": m["answer"], "citation": m["citation"]}
    return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").add_argument("--db", type=Path, default=DEFAULT_DB)
    lp = sub.add_parser("lookup")
    lp.add_argument("--category", required=True)
    lp.add_argument("--name", required=True)
    lp.add_argument("--db", type=Path, default=DEFAULT_DB)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        mandates = load_db(args.db)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.cmd == "list":
        print(json.dumps(mandates, indent=2))
        return 0
    hit = lookup(mandates, args.category, args.name)
    if hit is None:
        return 1
    print(json.dumps(hit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
