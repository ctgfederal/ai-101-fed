#!/usr/bin/env python3
"""write_sdd.py — render sdd.md.template; assert traceability covers all PRD REQs.

Payload keys (required):
  feature, feature_title, overview, architecture,
  components (list of {id, name, responsibility, dependencies, contract: {inputs, outputs}}),
  data_model, integrations, traceability (dict {REQ-NNN: [COMP-NNN, ...]}),
  alternatives, risks, open_questions

Usage:
  python write_sdd.py --payload p.json --out path.md --prd PRD.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_req_ids import extract as extract_req_ids

REQUIRED = ["feature", "feature_title", "overview", "architecture",
            "components", "data_model", "integrations", "traceability",
            "alternatives", "risks", "open_questions"]
COMP_ID_RE = re.compile(r"^COMP-\d+$")
REQ_ID_RE = re.compile(r"^REQ-\d+$")


def validate(p: dict, prd_req_ids: list[str]) -> None:
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if not isinstance(p["components"], list) or not p["components"]:
        raise ValueError("components must be a non-empty list")
    seen_comp = set()
    for c in p["components"]:
        for k in ("id", "name", "responsibility", "dependencies", "contract"):
            if k not in c:
                raise ValueError(f"component missing {k}: {c}")
        if not COMP_ID_RE.match(c["id"]):
            raise ValueError(f"invalid COMP id: {c['id']!r}")
        if c["id"] in seen_comp:
            raise ValueError(f"duplicate COMP id: {c['id']}")
        seen_comp.add(c["id"])
        ct = c["contract"]
        if "inputs" not in ct or "outputs" not in ct:
            raise ValueError(f"component {c['id']} contract must have inputs and outputs")

    if not isinstance(p["traceability"], dict):
        raise ValueError("traceability must be a dict {REQ: [COMP]}")
    for req, comps in p["traceability"].items():
        if not REQ_ID_RE.match(req):
            raise ValueError(f"invalid REQ in traceability: {req!r}")
        if not isinstance(comps, list) or not comps:
            raise ValueError(f"traceability[{req}] must be a non-empty list")
        for cid in comps:
            if cid not in seen_comp:
                raise ValueError(f"traceability[{req}] references unknown component: {cid}")

    # every PRD REQ must be in traceability
    missing_reqs = [r for r in prd_req_ids if r not in p["traceability"]]
    if missing_reqs:
        raise ValueError(f"traceability missing PRD requirements: {missing_reqs}")


def render_components(comps: list[dict]) -> str:
    lines = []
    for c in comps:
        lines.append(f"### {c['id']}: {c['name']}")
        lines.append(f"**Responsibility:** {c['responsibility']}")
        deps = ", ".join(c["dependencies"]) if c["dependencies"] else "_(none)_"
        lines.append(f"**Dependencies:** {deps}")
        lines.append(f"**Inputs:** {c['contract']['inputs']}")
        lines.append(f"**Outputs:** {c['contract']['outputs']}")
        lines.append("")
    return "\n".join(lines)


def render_traceability(trace: dict) -> str:
    rows = ["| Requirement | Components |", "|---|---|"]
    for req in sorted(trace.keys()):
        comps = ", ".join(trace[req])
        rows.append(f"| {req} | {comps} |")
    return "\n".join(rows)


def render(p: dict, template: str) -> str:
    repl = {
        "{{FEATURE_TITLE}}": p["feature_title"],
        "{{OVERVIEW}}": p["overview"],
        "{{ARCHITECTURE}}": p["architecture"],
        "{{COMPONENTS}}": render_components(p["components"]),
        "{{DATA_MODEL}}": p["data_model"],
        "{{INTEGRATIONS}}": p["integrations"],
        "{{TRACEABILITY_TABLE}}": render_traceability(p["traceability"]),
        "{{ALTERNATIVES}}": p["alternatives"],
        "{{RISKS}}": p["risks"],
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
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "sdd.md.template")
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
        prd_reqs = extract_req_ids(args.prd.read_text(encoding="utf-8"))

        validate(payload, prd_reqs)

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
