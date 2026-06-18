#!/usr/bin/env python3
"""write_report.py — render templates/task-validation-report.md.template from a JSON payload.

Payload shape (matches validate_tasks.py output):
  plan, tasks: [{id, title, phase, status, issues}], summary: {total, ok, warn, fail}, verdict

Usage:
  python write_report.py --payload payload.json --out report.md
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = ["plan", "tasks", "summary", "verdict"]
ALLOWED_VERDICTS = {"PASS", "WARN", "FAIL"}
ALLOWED_STATUSES = {"ok", "warn", "fail"}


def validate(payload: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"payload missing keys: {missing}")
    if not isinstance(payload["tasks"], list):
        raise ValueError("tasks must be a list")
    for i, t in enumerate(payload["tasks"]):
        if not isinstance(t, dict):
            raise ValueError(f"task[{i}] must be a dict")
        for k in ("id", "phase", "status", "issues"):
            if k not in t:
                raise ValueError(f"task[{i}] missing key: {k}")
        if t["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"task[{i}] status invalid: {t['status']!r}")
        if not isinstance(t["issues"], list):
            raise ValueError(f"task[{i}] issues must be a list")
    s = payload["summary"]
    if not isinstance(s, dict):
        raise ValueError("summary must be a dict")
    for k in ("total", "ok", "warn", "fail"):
        if k not in s or not isinstance(s[k], int):
            raise ValueError(f"summary.{k} missing or not int")
    if s["ok"] + s["warn"] + s["fail"] != s["total"]:
        raise ValueError(
            f"summary inconsistent: ok+warn+fail ({s['ok']}+{s['warn']}+{s['fail']}) != total ({s['total']})"
        )
    if payload["verdict"] not in ALLOWED_VERDICTS:
        raise ValueError(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}; got {payload['verdict']!r}")


def render_task_rows(tasks: list) -> str:
    if not tasks:
        return "| _(no tasks)_ | | | |"
    lines = []
    for t in tasks:
        tid = t.get("id", "")
        phase = t.get("phase", "") or "_(none)_"
        status = t.get("status", "")
        issue_count = len(t.get("issues", []))
        lines.append(f"| {tid} | {phase} | {status} | {issue_count} |")
    return "\n".join(lines)


def render_issues(tasks: list) -> str:
    bullets = []
    for t in tasks:
        if t.get("status") == "ok":
            continue
        for issue in t.get("issues", []):
            bullets.append(f"- **{t['id']}** — {issue}")
    if not bullets:
        return "_(no issues found)_"
    return "\n".join(bullets)


def render_verdict_notes(verdict: str) -> str:
    if verdict == "PASS":
        return "All tasks ok. PASS does NOT mean approved — product judgment is still required."
    if verdict == "WARN":
        return "No fails, but ≥1 warning. Recommend addressing before /implement."
    return "≥1 task failed validation. Fix the listed issues before /implement."


def render(payload: dict, template: str) -> str:
    tasks = payload["tasks"]
    s = payload["summary"]
    repl = {
        "{{PLAN}}": payload["plan"] or "_(unspecified)_",
        "{{TOTAL}}": str(s["total"]),
        "{{OK}}": str(s["ok"]),
        "{{WARN}}": str(s["warn"]),
        "{{FAIL}}": str(s["fail"]),
        "{{TASK_ROWS}}": render_task_rows(tasks),
        "{{ISSUES}}": render_issues(tasks),
        "{{VERDICT}}": payload["verdict"],
        "{{VERDICT_NOTES}}": render_verdict_notes(payload["verdict"]),
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--payload", type=Path, default=None,
                   help="path to payload JSON (or read stdin)")
    p.add_argument("--out", required=True, type=Path,
                   help="path to write the rendered report")
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "task-validation-report.md.template")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing output file")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        if not text.strip():
            raise ValueError("empty payload")
        payload = json.loads(text)
        validate(payload)
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
