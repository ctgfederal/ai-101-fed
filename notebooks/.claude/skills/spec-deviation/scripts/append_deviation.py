#!/usr/bin/env python3
"""append_deviation.py — render and append a deviation block to a target SDD.

Reads a validated deviation JSON payload, renders
`templates/deviation-block.md.template`, and appends the resulting block to
the target SDD under a `## Deviations` section. The section is created at
end-of-file if it does not yet exist.

Refuses to append a `DEV-NNN` block that already exists in the target SDD
unless `--force` is passed (in which case the existing block is replaced).

Usage:
  python append_deviation.py --payload payload.json --sdd path/to/SDD.md
  python append_deviation.py --payload payload.json --sdd path/to/SDD.md --force
"""
import argparse
import json
import re
import sys
from pathlib import Path

# import sibling validator so payload errors raise before append
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from validate_deviation import validate  # noqa: E402

TEMPLATE_PATH = SCRIPT_DIR.parent / "templates" / "deviation-block.md.template"
DEVIATIONS_HEADING = "## Deviations"
DEV_BLOCK_RE = re.compile(
    r"^###\s+(DEV-\d+)\s*$.*?(?=^###\s+DEV-\d+\s*$|\Z)",
    re.MULTILINE | re.DOTALL,
)


def render(payload: dict, template: str) -> str:
    repl = {
        "{{DEV_ID}}": payload["deviation_id"],
        "{{DATE}}": payload["date"],
        "{{SPEC_ID}}": payload["spec_id"],
        "{{REASON_CATEGORY}}": payload["reason_category"],
        "{{ORIGINAL_DECISION}}": payload["original_decision"],
        "{{STATUS}}": payload["status"],
        "{{APPROVER}}": payload["approver"],
        "{{DESCRIPTION}}": payload["description"],
        "{{PROPOSED_CHANGE}}": payload["proposed_change"],
        "{{IMPACT}}": payload["impact"],
    }
    out = template
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


def append_block(sdd_text: str, dev_id: str, block: str, force: bool) -> str:
    """Return updated SDD text with the rendered block appended/replaced.

    Behavior:
      - If `## Deviations` section is absent, append it (with one blank line
        separating from the prior content) plus the block.
      - If `## Deviations` exists and the dev_id already appears as a
        `### DEV-NNN` heading inside it: refuse unless force=True.
      - Otherwise append the block to the end of the Deviations section.
    """
    has_section = re.search(
        r"^##\s+Deviations\s*$", sdd_text, flags=re.MULTILINE
    )
    if not has_section:
        sep = "" if sdd_text.endswith("\n\n") else ("\n" if sdd_text.endswith("\n") else "\n\n")
        return sdd_text + sep + DEVIATIONS_HEADING + "\n\n" + block.rstrip() + "\n"

    # find the deviations section
    section_match = re.search(
        r"^(##\s+Deviations\s*$)(.*?)(?=^##\s+|\Z)",
        sdd_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    section_body = section_match.group(2) if section_match else ""

    # check for existing block with this DEV ID
    existing = re.search(
        rf"^###\s+{re.escape(dev_id)}\s*$.*?(?=^###\s+DEV-\d+\s*$|^##\s+|\Z)",
        section_body,
        flags=re.MULTILINE | re.DOTALL,
    )
    if existing and not force:
        raise FileExistsError(
            f"{dev_id} already exists in target SDD; pass --force to replace"
        )

    if existing and force:
        new_body = section_body[: existing.start()] + block.rstrip() + "\n" + section_body[existing.end():]
        new_text = sdd_text[: section_match.start(2)] + new_body + sdd_text[section_match.end(2):]
        return new_text

    # append to end of Deviations section
    insert_at = section_match.end(2)
    # ensure exactly one blank line before our block
    prefix = sdd_text[: insert_at]
    suffix = sdd_text[insert_at:]
    if not prefix.endswith("\n\n"):
        if prefix.endswith("\n"):
            prefix += "\n"
        else:
            prefix += "\n\n"
    return prefix + block.rstrip() + "\n" + suffix


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--payload", required=True, type=Path)
    p.add_argument("--sdd", required=True, type=Path)
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing DEV-NNN block",
    )
    p.add_argument("--template", type=Path, default=TEMPLATE_PATH)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload_text = args.payload.read_text(encoding="utf-8")
        payload = json.loads(payload_text)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: cannot read payload: {e}", file=sys.stderr)
        return 1

    errors = validate(payload)
    if errors:
        for e in errors:
            print(f"error: payload invalid: {e}", file=sys.stderr)
        return 1

    if not args.sdd.exists():
        print(f"error: SDD not found: {args.sdd}", file=sys.stderr)
        return 1

    try:
        template = args.template.read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: cannot read template: {e}", file=sys.stderr)
        return 1

    block = render(payload, template)
    sdd_text = args.sdd.read_text(encoding="utf-8")
    try:
        new_text = append_block(sdd_text, payload["deviation_id"], block, args.force)
    except FileExistsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    args.sdd.write_text(new_text, encoding="utf-8")
    print(f"appended {payload['deviation_id']} to {args.sdd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
