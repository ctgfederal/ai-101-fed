#!/usr/bin/env python3
"""write_report.py — render templates/compliance-report.md.template from a JSON payload.

Payload shape (matches `check_compliance.py` output):
  prd, sdd, repo_root, status, components, requirements, deviations, summary

Usage:
  python write_report.py --payload payload.json --out COMPLIANCE.md
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "prd", "sdd", "repo_root", "status",
    "components", "requirements", "deviations", "summary",
]
ALLOWED_STATUSES = {"compliant", "partial", "non-compliant"}


def validate(payload: dict) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"payload missing keys: {missing}")
    if payload["status"] not in ALLOWED_STATUSES:
        raise ValueError(
            f"status must be one of {sorted(ALLOWED_STATUSES)}; got {payload['status']!r}"
        )
    if not isinstance(payload["components"], dict):
        raise ValueError("components must be a dict")
    if not isinstance(payload["requirements"], dict):
        raise ValueError("requirements must be a dict")
    if not isinstance(payload["deviations"], list):
        raise ValueError("deviations must be a list")


def render_components_table(components: dict) -> str:
    if not components:
        return "_(no components defined in SDD)_"
    lines = [
        "| Component | Name | Expected | Found | Status |",
        "|---|---|---|---|---|",
    ]
    for cid in sorted(components.keys()):
        info = components[cid]
        expected = ", ".join(f"`{p}`" for p in info["expected_paths"]) or "_(none)_"
        found = ", ".join(f"`{p}`" for p in info["found_paths"]) or "_(none)_"
        status = "MISSING" if info["missing"] else "PRESENT"
        lines.append(
            f"| {cid} | {info['name']} | {expected} | {found} | {status} |"
        )
    return "\n".join(lines)


def render_requirements_table(requirements: dict) -> str:
    if not requirements:
        return "_(no requirements defined in PRD)_"
    lines = [
        "| Requirement | Referenced In | Status |",
        "|---|---|---|",
    ]
    for rid in sorted(requirements.keys()):
        info = requirements[rid]
        refs = ", ".join(f"`{p}`" for p in info["referenced_in"]) or "_(none)_"
        status = "UNREFERENCED" if info["unreferenced"] else "REFERENCED"
        lines.append(f"| {rid} | {refs} | {status} |")
    return "\n".join(lines)


def render_deviations(deviations: list) -> str:
    if not deviations:
        return "_(no deviations found)_"
    lines = []
    for d in deviations:
        lines.append(f"- **{d['type']}** ({d['id']}) — {d['detail']}")
    return "\n".join(lines)


def render_summary(summary: dict) -> str:
    return (
        f"- Components: {summary['components_found']}/{summary['components_total']} present\n"
        f"- Requirements: {summary['requirements_referenced']}/{summary['requirements_total']} referenced\n"
        f"- Deviations: {summary['deviation_count']}"
    )


def render_status_notes(status: str) -> str:
    if status == "compliant":
        return ("Every component has at least one file at its expected path and every "
                "requirement is referenced in source or tests. This does NOT mean tests "
                "pass or product approval — only that the code matches the spec's surface.")
    if status == "partial":
        return ("Some components or requirements have no evidence in the repo. "
                "See `## Deviations` for the gaps. Resolve each before declaring done.")
    return ("No component is implemented or no requirement is referenced. "
            "The spec and the code are not aligned. Stop and reconcile.")


def render(payload: dict, template: str) -> str:
    repl = {
        "{{PRD}}": payload["prd"],
        "{{SDD}}": payload["sdd"],
        "{{REPO}}": payload["repo_root"],
        "{{STATUS}}": payload["status"],
        "{{STATUS_NOTES}}": render_status_notes(payload["status"]),
        "{{COMPONENTS_TABLE}}": render_components_table(payload["components"]),
        "{{REQUIREMENTS_TABLE}}": render_requirements_table(payload["requirements"]),
        "{{DEVIATIONS}}": render_deviations(payload["deviations"]),
        "{{SUMMARY}}": render_summary(payload["summary"]),
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--payload", type=Path, default=None,
                   help="path to payload JSON (or read stdin)")
    p.add_argument("--out", required=True, type=Path,
                   help="path to write the rendered report")
    p.add_argument("--template", type=Path,
                   default=Path(__file__).resolve().parent.parent / "templates" / "compliance-report.md.template")
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
