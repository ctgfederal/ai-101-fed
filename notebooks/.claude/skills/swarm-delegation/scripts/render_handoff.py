#!/usr/bin/env python3
"""render_handoff.py — render templates/handoff.md.template from a JSON payload.

The payload must validate against scripts/validate_handoff.py first; this
script re-validates as a defensive measure.

Usage:
  python render_handoff.py --payload handoff.json --out prompt.md
  python render_handoff.py --payload handoff.json --out prompt.md --force
"""
import argparse
import json
import sys
from pathlib import Path

# import the validator from the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_handoff import validate  # noqa: E402


def render_list(items: list) -> str:
    if not items:
        return "_(none)_"
    return "\n".join(f"- {item}" for item in items)


def render(payload: dict, template: str) -> str:
    deadline = payload.get("deadline", "").strip() if isinstance(payload.get("deadline"), str) else ""
    if deadline:
        deadline_block = f"## DEADLINE\n\n{deadline}"
    else:
        deadline_block = ""

    repl = {
        "{{FROM}}": payload["from_agent"],
        "{{TO}}": payload["to_agent"],
        "{{TASK}}": payload["task"],
        "{{CONTEXT}}": render_list(payload.get("context_files", [])),
        "{{SUCCESS}}": render_list(payload.get("success_criteria", [])),
        "{{RETURN}}": payload["return_format"],
        "{{DEADLINE_BLOCK}}": deadline_block,
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    # collapse trailing blank lines so absent deadline doesn't leave a gap
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--payload", required=True, type=Path, help="path to handoff JSON")
    p.add_argument("--out", required=True, type=Path, help="path to write rendered prompt")
    p.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates" / "handoff.md.template",
    )
    p.add_argument("--force", action="store_true", help="overwrite existing output file")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if not args.payload.exists():
            print(f"error: payload not found: {args.payload}", file=sys.stderr)
            return 1
        text = args.payload.read_text(encoding="utf-8")
        if not text.strip():
            print("error: empty payload", file=sys.stderr)
            return 1
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 1

    errors = validate(payload)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 1

    if args.out.exists() and not args.force:
        print(f"error: {args.out} exists (use --force)", file=sys.stderr)
        return 1

    template = args.template.read_text(encoding="utf-8")
    rendered = render(payload, template)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(str(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
