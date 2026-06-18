#!/usr/bin/env python3
"""append_decisions.py — render and append a feature's decision section to .claude/decisions-log.md.

Payload schema (JSON):
  {
    "feature": "feature-search",
    "feature_title": "Feature Search",                    # display title
    "date": "2026-02-14",
    "status": "complete",                                  # complete | in-progress
    "summary": "1-2 sentence overview",
    "id_range": "D-042 to D-049",
    "auto_applied": [
      {"id": "D-040", "category": "Security", "name": "...", "answer": "...", "citation": "..."}
    ],
    "categories": {
      "Architecture": [
        {"id": "D-042", "title": "Overall pattern",
         "decision": "Layered service",
         "priority": "simplicity",
         "alternatives": ["event-driven", "CQRS"],
         "rationale": "...",
         "tiers": {"federal": "...", "enterprise": "...", "personal": "..."}}
      ]
    },
    "open_questions": ["..."],
    "related_solutions": ["link"]
  }

Usage:
  python append_decisions.py --payload payload.json --log .claude/decisions-log.md

Refuses if a `## <feature_title> — Build Decisions (<date>)` header already exists in the log
unless --force. Exit 0 = appended.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ["feature", "feature_title", "date", "status", "summary",
                 "id_range", "auto_applied", "categories"]
ID_RE = re.compile(r"^D-\d+$")


def validate_payload(payload: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if payload["status"] not in {"complete", "in-progress"}:
        raise ValueError(f"status invalid: {payload['status']!r}")
    if not isinstance(payload["categories"], dict):
        raise ValueError("categories must be a dict")
    # every decision must have an id matching D-NNN
    for cat, decs in payload["categories"].items():
        if not isinstance(decs, list):
            raise ValueError(f"category {cat!r} value must be a list")
        for d in decs:
            for k in ("id", "title", "decision"):
                if k not in d:
                    raise ValueError(f"decision in {cat!r} missing {k}: {d}")
            if not ID_RE.match(d["id"]):
                raise ValueError(f"decision id not D-NNN: {d['id']!r}")
    for a in payload["auto_applied"]:
        if not ID_RE.match(a.get("id", "")):
            raise ValueError(f"auto-applied id not D-NNN: {a.get('id')!r}")


def render_auto_table(rows: list[dict]) -> str:
    if not rows:
        return "_(none)_"
    out = ["| ID | Category | Decision | Mandated Answer | Citation |",
           "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['id']} | {r['category']} | {r['name']} | {r['answer']} | {r['citation']} |")
    return "\n".join(out)


def render_decision(d: dict) -> str:
    lines = [f"#### {d['id']}: {d['title']}",
             f"**Decision**: {d['decision']}"]
    if "priority" in d and d["priority"]:
        lines.append(f"**Priority**: {d['priority']}")
    if "alternatives" in d and d["alternatives"]:
        alts = "; ".join(d["alternatives"])
        lines.append(f"**Alternatives**: {alts}")
    if "rationale" in d and d["rationale"]:
        lines.append(f"**Rationale**: {d['rationale']}")
    if "tiers" in d and d["tiers"]:
        t = d["tiers"]
        lines.append(f"**Tiers**: Federal: {t.get('federal','—')} | Enterprise: {t.get('enterprise','—')} | Personal: {t.get('personal','—')}")
    return "\n".join(lines)


def render_categories(cats: dict) -> str:
    parts = []
    for category, decs in cats.items():
        parts.append(f"### {category}\n")
        if not decs:
            parts.append("_(no decisions in this category for this feature)_\n")
            continue
        for d in decs:
            parts.append(render_decision(d) + "\n")
    return "\n".join(parts)


def render_payload(payload: dict, template: str) -> str:
    auto_table = render_auto_table(payload["auto_applied"])
    cats_block = render_categories(payload["categories"])
    open_qs = "\n".join(f"- {q}" for q in payload.get("open_questions", [])) or "_(none)_"
    related = "\n".join(f"- {r}" for r in payload.get("related_solutions", [])) or "_(none)_"
    user_count = sum(len(v) for v in payload["categories"].values())
    auto_count = len(payload["auto_applied"])
    repl = {
        "{{FEATURE_TITLE}}": payload["feature_title"],
        "{{DATE}}": payload["date"],
        "{{STATUS}}": payload["status"],
        "{{TOTAL}}": str(user_count + auto_count),
        "{{USER_COUNT}}": str(user_count),
        "{{AUTO_COUNT}}": str(auto_count),
        "{{ID_RANGE}}": payload["id_range"],
        "{{SUMMARY}}": payload["summary"],
        "{{AUTO_APPLIED_TABLE}}": auto_table,
        "{{CATEGORIES}}": cats_block,
        "{{OPEN_QUESTIONS}}": open_qs,
        "{{RELATED_SOLUTIONS}}": related,
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def feature_header_exists(log_text: str, feature_title: str, date_str: str) -> bool:
    return f"## {feature_title} — Build Decisions ({date_str})" in log_text


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "feature-section.md.template")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload_text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        if not payload_text.strip():
            raise ValueError("empty payload")
        payload = json.loads(payload_text)
        validate_payload(payload)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    log_text = args.log.read_text(encoding="utf-8") if args.log.exists() else ""
    if feature_header_exists(log_text, payload["feature_title"], payload["date"]) and not args.force:
        print(f"error: section already exists for {payload['feature_title']} on {payload['date']} (use --force)", file=sys.stderr)
        return 1

    template = args.template.read_text(encoding="utf-8")
    rendered = render_payload(payload, template)

    if log_text and not log_text.endswith("\n"):
        log_text += "\n"
    if not log_text:
        log_text = (
            "# Decisions Log\n\n"
            "Centralized append-only log of all design decisions across all features and phases. "
            "**ID convention**: globally-unique `D-NNN` from a single monotonic counter. "
            "Once assigned, IDs never change.\n"
        )
    new_text = log_text + "\n" + rendered + "\n"
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.log.write_text(new_text, encoding="utf-8")
    print(str(args.log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
