#!/usr/bin/env python3
"""merge_research.py — insert `### Research Insights` blocks under each section + add deepening summary at top.

Findings JSON shape:
  {
    "summary": {
      "date": "2026-02-14",
      "sections_count": 4,
      "solutions_count": 2,
      "skills_list": ["compound-docs", "architecture-pattern-enforcer"],
      "key_findings": ["..."],
      "new_risks": ["..."]
    },
    "sections": {
      "Architecture": {
        "solutions": ["link1", "link2"],
        "best_practices": ["..."],
        "edge_cases": ["..."],
        "performance": ["..."],
        "references": ["..."]
      }
    }
  }

Usage:
  python merge_research.py --target path.md --findings-json findings.json

Refuses if any targeted section already has `### Research Insights` without --force.
Exit 0 = wrote.
"""

import argparse
import json
import re
import sys
from pathlib import Path

INSIGHTS_HEADING = "### Research Insights"
SUMMARY_HEADING = "## Deepening Summary"
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def render_list(items: list[str]) -> str:
    if not items:
        return "_(none)_"
    return "\n".join(f"- {it}" for it in items)


def render_insights(section_findings: dict) -> str:
    template = (TEMPLATES / "research-insights.md.template").read_text(encoding="utf-8")
    return (template
            .replace("{{SOLUTIONS}}", render_list(section_findings.get("solutions", [])))
            .replace("{{BEST_PRACTICES}}", render_list(section_findings.get("best_practices", [])))
            .replace("{{EDGE_CASES}}", render_list(section_findings.get("edge_cases", [])))
            .replace("{{PERFORMANCE}}", render_list(section_findings.get("performance", [])))
            .replace("{{REFERENCES}}", render_list(section_findings.get("references", []))))


def render_summary(summary: dict) -> str:
    template = (TEMPLATES / "deepening-summary.md.template").read_text(encoding="utf-8")
    return (template
            .replace("{{DATE}}", summary["date"])
            .replace("{{SECTIONS_COUNT}}", str(summary["sections_count"]))
            .replace("{{SOLUTIONS_COUNT}}", str(summary["solutions_count"]))
            .replace("{{SKILLS_LIST}}", ", ".join(summary["skills_list"]) or "_(none)_")
            .replace("{{KEY_FINDINGS}}", render_list(summary.get("key_findings", [])))
            .replace("{{NEW_RISKS}}", render_list(summary.get("new_risks", []))))


def insert_summary(text: str, summary_block: str) -> str:
    """Insert summary block after the document title (first `# `)."""
    if SUMMARY_HEADING in text:
        # already deepened — replace existing block
        pat = re.compile(rf"^{re.escape(SUMMARY_HEADING)}.*?(?=^##\s|\Z)",
                         flags=re.MULTILINE | re.DOTALL)
        return pat.sub(summary_block + "\n", text)
    m = re.search(r"^#\s+.+?\n", text, flags=re.MULTILINE)
    if not m:
        return summary_block + "\n\n" + text
    insert_at = m.end()
    return text[:insert_at] + "\n" + summary_block + "\n" + text[insert_at:]


def insert_insights(text: str, section_heading: str, insights_block: str, force: bool) -> tuple[str, bool]:
    """Insert insights block under a `### <heading>` section. Returns (new_text, did_insert).

    The section's "scope" extends from its `### <heading>` until the next ### heading
    that is NOT `Research Insights`, OR the next ## heading, OR EOF. This keeps any
    previously-inserted `### Research Insights` inside the scope so idempotency works.
    """
    start_pat = re.compile(rf"^###\s+{re.escape(section_heading)}\s*$", flags=re.MULTILINE)
    start_m = start_pat.search(text)
    if not start_m:
        return text, False

    rest = text[start_m.end():]
    end_offset = len(rest)
    for m in re.finditer(r"^(###|##)\s+(.+?)\s*$", rest, flags=re.MULTILINE):
        kind = m.group(1)
        name = m.group(2).strip()
        if kind == "##":
            end_offset = m.start()
            break
        if kind == "###" and name != "Research Insights":
            end_offset = m.start()
            break
    section_end = start_m.end() + end_offset
    scope = text[start_m.end():section_end]

    if INSIGHTS_HEADING in scope and not force:
        return text, False

    if INSIGHTS_HEADING in scope and force:
        scope_clean = re.sub(
            rf"^{re.escape(INSIGHTS_HEADING)}.*?(?=^###\s|^##\s|\Z)",
            "", scope, flags=re.MULTILINE | re.DOTALL,
        )
        new_scope = scope_clean.rstrip() + "\n\n" + insights_block.rstrip() + "\n\n"
    else:
        new_scope = scope.rstrip() + "\n\n" + insights_block.rstrip() + "\n\n"

    new_text = text[:start_m.end()] + new_scope + text[section_end:]
    return new_text, True


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--target", required=True, type=Path)
    p.add_argument("--findings-json", type=Path, default=None)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.target.exists():
        print(f"error: target not found: {args.target}", file=sys.stderr)
        return 1
    findings_text = args.findings_json.read_text(encoding="utf-8") if args.findings_json else sys.stdin.read()
    try:
        findings = json.loads(findings_text)
    except json.JSONDecodeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    text = args.target.read_text(encoding="utf-8")
    summary_block = render_summary(findings["summary"])
    text = insert_summary(text, summary_block)

    inserted = []
    refused = []
    for section, section_findings in findings.get("sections", {}).items():
        block = render_insights(section_findings)
        text, did = insert_insights(text, section, block, args.force)
        if did:
            inserted.append(section)
        else:
            # could be missing section OR existing insights without --force
            if INSIGHTS_HEADING in text and section in text:
                refused.append(section)

    args.target.write_text(text, encoding="utf-8")
    print(json.dumps({"inserted": inserted, "refused_existing": refused}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
