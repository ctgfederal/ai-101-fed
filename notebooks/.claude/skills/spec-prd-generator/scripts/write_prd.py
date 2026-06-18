#!/usr/bin/env python3
"""write_prd.py — render prd.md.template from JSON payload and write the file.

Payload keys (required):
  feature, feature_title, vision, problem, value, personas,
  user_stories (list of {id, as, i_want, so_that}),
  requirements (list of {id, story, moscow, ears}),
  metrics, risks, open_questions (list)

Usage:
  python write_prd.py --payload p.json --out path.md

Exit 0 = wrote.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = ["feature", "feature_title", "vision", "problem", "value", "personas",
            "user_stories", "requirements", "metrics", "risks", "open_questions"]
ALLOWED_MOSCOW = {"Must", "Should", "Could", "Won't"}
REQ_ID_RE = re.compile(r"^REQ-\d+$")
EARS_PATTERNS = ["SHALL", "WHEN", "WHILE", "WHERE", "IF"]


def validate(p: dict) -> None:
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if not isinstance(p["user_stories"], list) or not p["user_stories"]:
        raise ValueError("user_stories must be a non-empty list")
    if not isinstance(p["requirements"], list) or not p["requirements"]:
        raise ValueError("requirements must be a non-empty list")
    seen_ids = set()
    for r in p["requirements"]:
        for k in ("id", "story", "moscow", "ears"):
            if k not in r:
                raise ValueError(f"requirement missing {k}: {r}")
        if not REQ_ID_RE.match(r["id"]):
            raise ValueError(f"invalid REQ ID: {r['id']!r}")
        if r["id"] in seen_ids:
            raise ValueError(f"duplicate REQ ID: {r['id']}")
        seen_ids.add(r["id"])
        if r["moscow"] not in ALLOWED_MOSCOW:
            raise ValueError(f"invalid MoSCoW: {r['moscow']!r}")
        if not any(pat in r["ears"] for pat in EARS_PATTERNS):
            raise ValueError(f"requirement {r['id']} not EARS-formatted (must contain one of {EARS_PATTERNS})")


def render_user_stories(stories: list) -> str:
    return "\n".join(f"- **{s['id']}**: As {s['as']}, I want {s['i_want']}, so that {s['so_that']}." for s in stories)


def render_requirements(reqs: list) -> str:
    return "\n".join(f"- **{r['id']}** (story {r['story']}, {r['moscow']}): {r['ears']}" for r in reqs)


def render_moscow(reqs: list) -> str:
    by_p: dict[str, list[str]] = {p: [] for p in ALLOWED_MOSCOW}
    for r in reqs:
        by_p[r["moscow"]].append(r["id"])
    rows = ["| Priority | Requirements |", "|---|---|"]
    for p in ["Must", "Should", "Could", "Won't"]:
        ids = ", ".join(by_p[p]) if by_p[p] else "_(none)_"
        rows.append(f"| {p} | {ids} |")
    return "\n".join(rows)


def render(payload: dict, template: str) -> str:
    repl = {
        "{{FEATURE_TITLE}}": payload["feature_title"],
        "{{VISION}}": payload["vision"],
        "{{PROBLEM}}": payload["problem"],
        "{{VALUE}}": payload["value"],
        "{{PERSONAS}}": payload["personas"],
        "{{USER_STORIES}}": render_user_stories(payload["user_stories"]),
        "{{REQUIREMENTS}}": render_requirements(payload["requirements"]),
        "{{MOSCOW_TABLE}}": render_moscow(payload["requirements"]),
        "{{METRICS}}": payload["metrics"],
        "{{RISKS}}": payload["risks"],
        "{{OPEN_QUESTIONS}}": "\n".join(f"- {q}" for q in payload["open_questions"]) or "_(none)_",
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "prd.md.template")
    p.add_argument("--force", action="store_true")
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
