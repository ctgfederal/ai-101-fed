#!/usr/bin/env python3
"""write_matrix.py — render templates/traceability-matrix.md.template.

Reads the JSON output of `build_matrix.py` and writes a markdown matrix to disk.

Payload shape (matches `build_matrix.py` output):
  {
    "feature": "<name>",
    "rows": [
      {"req": "REQ-001", "comps": [...], "tasks": [...],
       "code_refs": [...], "tests_refs": [...], "status": "..."},
      ...
    ]
  }

Usage:
  python write_matrix.py --payload payload.json --out TRACEABILITY.md [--force]
"""
import argparse
import json
import sys
from pathlib import Path


VALID_STATUSES = {"covered", "partial", "uncovered"}
REQUIRED_ROW_KEYS = ("req", "comps", "tasks", "code_refs", "tests_refs", "status")


def validate_payload(payload: dict) -> None:
    if "feature" not in payload:
        raise ValueError("payload missing key: feature")
    if "rows" not in payload or not isinstance(payload["rows"], list):
        raise ValueError("payload missing key: rows (must be a list)")
    if not payload["rows"]:
        raise ValueError("payload rows is empty")
    seen_reqs: set[str] = set()
    for i, row in enumerate(payload["rows"]):
        for k in REQUIRED_ROW_KEYS:
            if k not in row:
                raise ValueError(f"row[{i}] missing key: {k}")
        if row["status"] not in VALID_STATUSES:
            raise ValueError(
                f"row[{i}] invalid status: {row['status']!r}; "
                f"must be one of {sorted(VALID_STATUSES)}"
            )
        for k in ("comps", "tasks", "code_refs", "tests_refs"):
            if not isinstance(row[k], list):
                raise ValueError(f"row[{i}].{k} must be a list")
        if row["req"] in seen_reqs:
            raise ValueError(f"duplicate REQ in payload: {row['req']}")
        seen_reqs.add(row["req"])


def render_list(items: list[str]) -> str:
    return ", ".join(items) if items else "—"


def render_rows(rows: list[dict]) -> str:
    lines = []
    for r in rows:
        lines.append(
            f"| {r['req']} | {render_list(r['comps'])} | "
            f"{render_list(r['tasks'])} | {render_list(r['code_refs'])} | "
            f"{render_list(r['tests_refs'])} | `{r['status']}` |"
        )
    return "\n".join(lines)


def render_summary(rows: list[dict]) -> str:
    counts = {s: 0 for s in VALID_STATUSES}
    for r in rows:
        counts[r["status"]] += 1
    total = len(rows)
    pct = (counts["covered"] / total * 100) if total else 0
    return (
        f"| Status | Count |\n"
        f"|---|---|\n"
        f"| covered | {counts['covered']} |\n"
        f"| partial | {counts['partial']} |\n"
        f"| uncovered | {counts['uncovered']} |\n"
        f"| **Total** | **{total}** |\n"
        f"\nCoverage: **{pct:.0f}%** ({counts['covered']}/{total} fully covered)"
    )


def render_gaps(rows: list[dict]) -> str:
    gaps = [r for r in rows if r["status"] != "covered"]
    if not gaps:
        return "_(no gaps — every REQ is covered)_"
    lines = []
    for r in gaps:
        missing = []
        if not r["comps"]:
            missing.append("SDD")
        if not r["tasks"]:
            missing.append("PLAN")
        if not r["code_refs"]:
            missing.append("code")
        if not r["tests_refs"]:
            missing.append("test")
        lines.append(
            f"- **{r['req']}** (`{r['status']}`) — missing: {', '.join(missing)}"
        )
    return "\n".join(lines)


def render_totals(rows: list[dict]) -> str:
    counts = {s: 0 for s in VALID_STATUSES}
    for r in rows:
        counts[r["status"]] += 1
    total = len(rows)
    return (
        f"- Total REQs: **{total}**\n"
        f"- Covered: **{counts['covered']}**\n"
        f"- Partial: **{counts['partial']}**\n"
        f"- Uncovered: **{counts['uncovered']}**"
    )


def render(payload: dict, template: str) -> str:
    rows = payload["rows"]
    repl = {
        "{{FEATURE_TITLE}}": payload["feature"],
        "{{SUMMARY_TABLE}}": render_summary(rows),
        "{{ROWS}}": render_rows(rows),
        "{{GAPS}}": render_gaps(rows),
        "{{TOTALS}}": render_totals(rows),
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--payload", type=Path, default=None,
                   help="payload JSON path (or read stdin if omitted)")
    p.add_argument("--out", required=True, type=Path,
                   help="path to write the rendered matrix")
    p.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent
        / "templates"
        / "traceability-matrix.md.template",
    )
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = (
            args.payload.read_text(encoding="utf-8")
            if args.payload
            else sys.stdin.read()
        )
        if not text.strip():
            raise ValueError("empty payload")
        payload = json.loads(text)
        validate_payload(payload)
        if args.out.exists() and not args.force:
            print(f"error: {args.out} exists (use --force)", file=sys.stderr)
            return 1
        template = args.template.read_text(encoding="utf-8")
        rendered = render(payload, template)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(str(args.out))
        return 0
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
