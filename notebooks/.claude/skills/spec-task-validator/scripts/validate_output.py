#!/usr/bin/env python3
"""validate_output.py — validate a rendered task validation report.

Checks:
  - Required `##` sections present in order: PLAN, Summary, Tasks, Issues, Verdict
  - Summary numbers sum (ok + warn + fail == total)
  - Verdict is one of PASS / WARN / FAIL
  - Every task ID present in the Tasks table appears at most once (no dupes)
  - No unsubstituted `{{...}}` tokens

Optional: pass `--payload` to also assert that every task in the payload appears
as a row in the Tasks table.

Usage:
  python validate_output.py --file path/to/report.md [--payload payload.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Optional

REQUIRED_SECTIONS = ["PLAN", "Summary", "Tasks", "Issues", "Verdict"]
ALLOWED_VERDICTS = {"PASS", "WARN", "FAIL"}
TEMPLATE_TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# Anchor summary rows to the start of a line and require exactly TWO cells
# (Metric | Count). This avoids matching the four-cell Tasks rows.
SUMMARY_ROW_RE = re.compile(
    r"^\|\s*(Total tasks|ok|warn|fail)\s*\|\s*(\d+)\s*\|\s*$",
    re.MULTILINE,
)
TASK_ROW_RE = re.compile(r"\|\s*(T-\d+)\s*\|\s*([^|]*)\|\s*(ok|warn|fail)\s*\|\s*(\d+)\s*\|")
VERDICT_LINE_RE = re.compile(r"^\*\*(PASS|WARN|FAIL)\*\*\s*$", re.MULTILINE)


def validate(text: str, payload: Optional[dict] = None) -> List[str]:
    errors: List[str] = []

    leftover = TEMPLATE_TOKEN_RE.findall(text)
    if leftover:
        errors.append(f"unsubstituted template tokens: {leftover}")

    found = [m.group(1).strip() for m in SECTION_RE.finditer(text)]
    found_set = set(found)
    for sect in REQUIRED_SECTIONS:
        if sect not in found_set:
            errors.append(f"missing section: ## {sect}")
    indices = [found.index(s) for s in REQUIRED_SECTIONS if s in found_set]
    if indices and indices != sorted(indices):
        errors.append(f"sections out of order: {found}")

    # summary
    summary: dict = {}
    for m in SUMMARY_ROW_RE.finditer(text):
        summary[m.group(1)] = int(m.group(2))
    needed = {"Total tasks", "ok", "warn", "fail"}
    missing_summary = needed - set(summary.keys())
    if missing_summary:
        errors.append(f"summary table missing rows: {sorted(missing_summary)}")
    else:
        if summary["ok"] + summary["warn"] + summary["fail"] != summary["Total tasks"]:
            errors.append(
                f"summary inconsistent: ok+warn+fail ({summary['ok']}+{summary['warn']}+{summary['fail']}) "
                f"!= total ({summary['Total tasks']})"
            )

    # task rows
    task_rows = TASK_ROW_RE.findall(text)
    seen_ids = set()
    for tid, _phase, _status, _ic in task_rows:
        if tid in seen_ids:
            errors.append(f"duplicate task row: {tid}")
        seen_ids.add(tid)

    # verdict
    vmatch = VERDICT_LINE_RE.search(text)
    if not vmatch:
        errors.append("no verdict line found (expected **PASS|WARN|FAIL** alone on a line)")
    elif vmatch.group(1) not in ALLOWED_VERDICTS:
        errors.append(f"invalid verdict: {vmatch.group(1)}")

    # cross-check against payload if provided
    if payload is not None:
        payload_ids = [t["id"] for t in payload.get("tasks", []) if "id" in t]
        for pid in payload_ids:
            if pid not in seen_ids:
                errors.append(f"payload task {pid} not present in report Tasks table")
        s = payload.get("summary", {})
        if s and summary:
            for key, src in (("Total tasks", "total"), ("ok", "ok"), ("warn", "warn"), ("fail", "fail")):
                if key in summary and src in s and summary[key] != s[src]:
                    errors.append(
                        f"summary mismatch on {key}: report={summary[key]} vs payload={s[src]}"
                    )

    return errors


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--payload", type=Path, default=None,
                   help="optional payload JSON to cross-check against")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    payload = None
    if args.payload:
        if not args.payload.exists():
            print(f"error: payload not found: {args.payload}", file=sys.stderr)
            return 1
        try:
            payload = json.loads(args.payload.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"error: invalid payload JSON: {e}", file=sys.stderr)
            return 1
    errors = validate(text, payload)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
