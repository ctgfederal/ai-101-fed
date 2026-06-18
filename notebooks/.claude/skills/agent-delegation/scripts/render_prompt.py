#!/usr/bin/env python3
"""render_prompt.py — render a delegation prompt from a JSON payload.

Reads templates/delegation-prompt.md.template and substitutes:
  {{AGENT_TYPE}}    -> payload.agent_type
  {{TASK}}          -> payload.task
  {{FOCUS_LIST}}    -> bullet list of payload.focus_files (or "_(none)_")
  {{EXCLUDE_LIST}}  -> bullet list of payload.exclude_files (or "_(none)_")
  {{SUCCESS_LIST}}  -> bullet list of payload.success_criteria
  {{RETURN_FORMAT}} -> payload.return_format

Validates payload first via validate_delegation.validate().

Usage:
  python render_prompt.py --payload p.json --out path.md [--force]

Exit codes:
  0  wrote file
  1  validation or render error
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_delegation import validate  # noqa: E402


def render_list(items: list) -> str:
    if not items:
        return "_(none)_"
    return "\n".join(f"- {item}" for item in items)


def render(payload: dict, template: str) -> str:
    repl = {
        "{{AGENT_TYPE}}": payload["agent_type"],
        "{{TASK}}": payload["task"],
        "{{FOCUS_LIST}}": render_list(payload["focus_files"]),
        "{{EXCLUDE_LIST}}": render_list(payload["exclude_files"]),
        "{{SUCCESS_LIST}}": render_list(payload["success_criteria"]),
        "{{RETURN_FORMAT}}": payload["return_format"],
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None, help="path to JSON payload (omit to read stdin)")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "delegation-prompt.md.template")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        if not text.strip():
            print("error: empty payload", file=sys.stderr)
            return 1
        payload = json.loads(text)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    errors = validate(payload)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    if args.out.exists() and not args.force:
        print(f"error: {args.out} exists (use --force)", file=sys.stderr)
        return 1

    try:
        template = args.template.read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: cannot read template: {e}", file=sys.stderr)
        return 1

    rendered = render(payload, template)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
