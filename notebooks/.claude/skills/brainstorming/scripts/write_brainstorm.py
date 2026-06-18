#!/usr/bin/env python3
"""write_brainstorm.py — render brainstorm.md.template from a JSON payload and write the file.

Payload required keys:
  topic, date, status (in {complete, in-progress}),
  inspiration, projects, audience, use_cases, outcomes,
  principles, constraints, scope_in, scope_out, open_questions, related

Usage:
  python write_brainstorm.py --payload payload.json --out path.md

Exit 0 = wrote file (path on stdout). Exit 1 = validation error.
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED = [
    "topic", "date", "status",
    "inspiration", "projects", "audience", "use_cases",
    "outcomes", "principles", "constraints",
    "scope_in", "scope_out", "open_questions", "related",
]

ALLOWED_STATUS = {"complete", "in-progress"}


def load_payload(args) -> dict:
    text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
    if not text.strip():
        raise ValueError("empty payload")
    return json.loads(text)


def validate(payload: dict) -> None:
    missing = [k for k in REQUIRED if k not in payload]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if payload["status"] not in ALLOWED_STATUS:
        raise ValueError(f"status must be one of {ALLOWED_STATUS}: {payload['status']!r}")
    for k in REQUIRED:
        if payload[k] in ("", None):
            raise ValueError(f"required field empty: {k}")


def render(payload: dict, template: str) -> str:
    repl = {
        "{{TOPIC}}": payload["topic"],
        "{{DATE}}": payload["date"],
        "{{STATUS}}": payload["status"],
        "{{INSPIRATION}}": payload["inspiration"],
        "{{PROJECTS}}": payload["projects"],
        "{{AUDIENCE}}": payload["audience"],
        "{{USE_CASES}}": payload["use_cases"],
        "{{OUTCOMES}}": payload["outcomes"],
        "{{PRINCIPLES}}": payload["principles"],
        "{{CONSTRAINTS}}": payload["constraints"],
        "{{SCOPE_IN}}": payload["scope_in"],
        "{{SCOPE_OUT}}": payload["scope_out"],
        "{{OPEN_QUESTIONS}}": payload["open_questions"],
        "{{RELATED}}": payload["related"],
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "brainstorm.md.template")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args)
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
