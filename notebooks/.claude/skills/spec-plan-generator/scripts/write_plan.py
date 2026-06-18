#!/usr/bin/env python3
"""write_plan.py — render plan.md.template; assert COMP and REQ coverage.

Payload (required keys): feature, feature_title, tasks (list), open_questions (list).
Each task: id (T-NNN), title, phase, comps (list of COMP-NNN), reqs (list of REQ-NNN),
acceptance, tdd_step (red/green/refactor).

Usage: python write_plan.py --payload p.json --out path.md --prd PRD.md --sdd SDD.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_ids import extract, REQ_RE, COMP_RE

REQUIRED = ["feature", "feature_title", "tasks", "open_questions"]
PHASES = ["Foundation", "Core", "Integration", "Polish"]
TASK_ID_RE = re.compile(r"^T-\d+$")
COMP_ID_RE = re.compile(r"^COMP-\d+$")
REQ_ID_RE = re.compile(r"^REQ-\d+$")
TDD_STEPS = {"red", "green", "refactor"}


def validate(p: dict, prd_reqs: list[str], sdd_comps: list[str]) -> None:
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if not isinstance(p["tasks"], list) or not p["tasks"]:
        raise ValueError("tasks must be a non-empty list")
    seen_ids = set()
    covered_comps = set()
    covered_reqs = set()
    for t in p["tasks"]:
        for k in ("id", "title", "phase", "comps", "reqs", "acceptance", "tdd_step"):
            if k not in t:
                raise ValueError(f"task missing {k}: {t}")
        if not TASK_ID_RE.match(t["id"]):
            raise ValueError(f"invalid task id: {t['id']!r}")
        if t["id"] in seen_ids:
            raise ValueError(f"duplicate task id: {t['id']}")
        seen_ids.add(t["id"])
        if t["phase"] not in PHASES:
            raise ValueError(f"invalid phase: {t['phase']!r}")
        if t["tdd_step"] not in TDD_STEPS:
            raise ValueError(f"invalid tdd_step: {t['tdd_step']!r}")
        if not isinstance(t["comps"], list) or not t["comps"]:
            raise ValueError(f"task {t['id']} has no comps")
        for c in t["comps"]:
            if not COMP_ID_RE.match(c):
                raise ValueError(f"task {t['id']} bad COMP: {c!r}")
            if c not in sdd_comps:
                raise ValueError(f"task {t['id']} references unknown COMP: {c}")
            covered_comps.add(c)
        for r in t["reqs"]:
            if not REQ_ID_RE.match(r):
                raise ValueError(f"task {t['id']} bad REQ: {r!r}")
            if r not in prd_reqs:
                raise ValueError(f"task {t['id']} references unknown REQ: {r}")
            covered_reqs.add(r)

    missing_comps = [c for c in sdd_comps if c not in covered_comps]
    if missing_comps:
        raise ValueError(f"SDD components not covered by any task: {missing_comps}")
    missing_reqs = [r for r in prd_reqs if r not in covered_reqs]
    if missing_reqs:
        raise ValueError(f"PRD requirements not covered by any task: {missing_reqs}")


def render_phase(phase: str, tasks: list[dict]) -> str:
    phase_tasks = [t for t in tasks if t["phase"] == phase]
    if not phase_tasks:
        return "_(no tasks in this phase)_"
    lines = []
    for t in phase_tasks:
        lines.append(f"- **{t['id']}** ({t['tdd_step']}): {t['title']}")
        lines.append(f"  - Components: {', '.join(t['comps'])}")
        lines.append(f"  - Requirements: {', '.join(t['reqs'])}")
        lines.append(f"  - Acceptance: {t['acceptance']}")
    return "\n".join(lines)


def render_traceability(tasks: list[dict]) -> str:
    rows = ["| Requirement | Tasks |", "|---|---|"]
    by_req: dict[str, list[str]] = {}
    for t in tasks:
        for r in t["reqs"]:
            by_req.setdefault(r, []).append(t["id"])
    for req in sorted(by_req.keys()):
        rows.append(f"| {req} | {', '.join(by_req[req])} |")
    return "\n".join(rows)


def render(p: dict, template: str) -> str:
    repl = {
        "{{FEATURE_TITLE}}": p["feature_title"],
        "{{PHASE_FOUNDATION}}": render_phase("Foundation", p["tasks"]),
        "{{PHASE_CORE}}": render_phase("Core", p["tasks"]),
        "{{PHASE_INTEGRATION}}": render_phase("Integration", p["tasks"]),
        "{{PHASE_POLISH}}": render_phase("Polish", p["tasks"]),
        "{{TRACEABILITY_TABLE}}": render_traceability(p["tasks"]),
        "{{OPEN_QUESTIONS}}": "\n".join(f"- {q}" for q in p["open_questions"]) or "_(none)_",
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", type=Path, default=None)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--prd", required=True, type=Path)
    p.add_argument("--sdd", required=True, type=Path)
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "plan.md.template")
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        if not text.strip():
            raise ValueError("empty payload")
        payload = json.loads(text)

        if not args.prd.exists():
            raise ValueError(f"PRD not found: {args.prd}")
        if not args.sdd.exists():
            raise ValueError(f"SDD not found: {args.sdd}")
        prd_reqs = extract(args.prd.read_text(encoding="utf-8"), REQ_RE, "REQ")
        sdd_comps = extract(args.sdd.read_text(encoding="utf-8"), COMP_RE, "COMP")

        validate(payload, prd_reqs, sdd_comps)

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
