#!/usr/bin/env python3
"""write_report.py — render templates/3cs-report.md.template from a JSON payload.

Payload shape (matches `score_3cs.py` output):
  target, completeness, consistency, correctness, overall, verdict, issues,
  completeness_notes, consistency_notes, correctness_notes

Usage:
  python write_report.py --payload payload.json --out report.md
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "target",
    "completeness", "consistency", "correctness", "overall",
    "verdict", "issues",
    "completeness_notes", "consistency_notes", "correctness_notes",
]
ALLOWED_VERDICTS = {"PASS", "WARN", "FAIL"}


def validate(payload: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"payload missing keys: {missing}")
    for k in ("completeness", "consistency", "correctness", "overall"):
        v = payload[k]
        if not isinstance(v, int) or v < 0 or v > 10:
            raise ValueError(f"{k} must be int in [0, 10], got {v!r}")
    if payload["verdict"] not in ALLOWED_VERDICTS:
        raise ValueError(f"verdict must be one of {sorted(ALLOWED_VERDICTS)}; got {payload['verdict']!r}")
    if not isinstance(payload["issues"], list):
        raise ValueError("issues must be a list")
    for i, issue in enumerate(payload["issues"]):
        if not isinstance(issue, dict) or "category" not in issue or "message" not in issue:
            raise ValueError(f"issue[{i}] must be a dict with category and message")


def render_issues(issues: list) -> str:
    if not issues:
        return "_(no issues found)_"
    lines = []
    for issue in issues:
        cat = issue["category"]
        msg = issue["message"]
        lines.append(f"- **{cat}** — {msg}")
    return "\n".join(lines)


def render_verdict_notes(verdict: str) -> str:
    if verdict == "PASS":
        return "Mechanically clean. PASS does NOT mean approved — product judgment is still required."
    if verdict == "WARN":
        return "Multiple issues detected. Recommend another pass before approval."
    return "Fundamental gaps detected. Spec is not ready."


def render(payload: dict, template: str) -> str:
    repl = {
        "{{TARGET}}": payload["target"],
        "{{COMPLETENESS}}": str(payload["completeness"]),
        "{{CONSISTENCY}}": str(payload["consistency"]),
        "{{CORRECTNESS}}": str(payload["correctness"]),
        "{{OVERALL}}": str(payload["overall"]),
        "{{VERDICT}}": payload["verdict"],
        "{{ISSUES}}": render_issues(payload["issues"]),
        "{{COMPLETENESS_NOTES}}": payload["completeness_notes"] or "_(no notes)_",
        "{{CONSISTENCY_NOTES}}": payload["consistency_notes"] or "_(no notes)_",
        "{{CORRECTNESS_NOTES}}": payload["correctness_notes"] or "_(no notes)_",
        "{{VERDICT_NOTES}}": render_verdict_notes(payload["verdict"]),
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None,
                   help="path to payload JSON (or read stdin)")
    p.add_argument("--out", required=True, type=Path,
                   help="path to write the rendered report")
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "3cs-report.md.template")
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
