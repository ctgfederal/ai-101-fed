#!/usr/bin/env python3
"""append_phase_note.py — append a `### Phase N: <name>` block under `## Phase Notes`.

The note text is taken from --note or, if absent, stdin. The block is inserted
in monotonic order: scan existing `### Phase <int>: ...` headers, place the
new one numerically. Existing same-numbered phase aborts (use a different
phase or remove the old one first).

Usage:
  python append_phase_note.py --feature feature-search --specs-root .claude/specs \\
      --phase 1 --name "Foundation" --note "Spec under-specified caching layer."
  echo "..." | python append_phase_note.py --feature feature-search \\
      --specs-root .claude/specs --phase 2 --name "Core"
"""
import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

PHASE_NOTES_HEADER = "## Phase Notes"
PHASE_RE = re.compile(r"^###\s+Phase\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
NEXT_TOPLEVEL_RE = re.compile(r"^##\s+", re.MULTILINE)


def insert_phase_block(text: str, phase: int, name: str, note: str, today: str) -> str:
    if PHASE_NOTES_HEADER not in text:
        raise ValueError(f"section not found: {PHASE_NOTES_HEADER}")

    # Find start of `## Phase Notes` body.
    pn_idx = text.index(PHASE_NOTES_HEADER)
    body_start = text.find("\n", pn_idx) + 1

    # Find next top-level header after Phase Notes.
    rest = text[body_start:]
    nxt = NEXT_TOPLEVEL_RE.search(rest)
    body_end = body_start + (nxt.start() if nxt else len(rest))

    body = text[body_start:body_end]
    pre = text[:body_start]
    post = text[body_end:]

    # Detect existing phase numbers, refuse duplicates.
    existing = [int(m.group(1)) for m in PHASE_RE.finditer(body)]
    if phase in existing:
        raise ValueError(f"phase {phase} already present in Phase Notes")

    new_block = (
        f"### Phase {phase}: {name}\n"
        f"\n"
        f"_Recorded {today}_\n"
        f"\n"
        f"{note.rstrip()}\n"
        f"\n"
    )

    # Strip placeholder italics line if it's the only content.
    stripped = body.strip()
    placeholder_only = stripped.startswith("_(") and stripped.endswith(")_")
    if placeholder_only or not stripped:
        new_body = "\n" + new_block
        return pre + new_body + post

    # Insert in monotonic order: walk phase headers, place before the first
    # one with a larger number; else append at the end of the body.
    headers = list(PHASE_RE.finditer(body))
    insert_at = None
    for m in headers:
        if int(m.group(1)) > phase:
            insert_at = m.start()
            break
    if insert_at is None:
        new_body = body.rstrip() + "\n\n" + new_block
    else:
        new_body = body[:insert_at] + new_block + body[insert_at:]

    return pre + new_body + post


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--feature", required=True)
    p.add_argument("--specs-root", required=True, type=Path)
    p.add_argument("--phase", required=True, type=int,
                   help="positive integer phase number")
    p.add_argument("--name", required=True,
                   help="short phase name, e.g. Foundation, Core, Integration, Polish")
    p.add_argument("--note", default=None,
                   help="note body (default: read stdin)")
    p.add_argument("--today", default=None,
                   help="optional ISO date override (default: today)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.phase <= 0:
        print(f"error: --phase must be positive, got {args.phase}", file=sys.stderr)
        return 1
    if not args.name.strip():
        print("error: --name must not be empty", file=sys.stderr)
        return 1

    target = args.specs_root / args.feature / "README.md"
    if not target.exists():
        print(f"error: README not found: {target}", file=sys.stderr)
        return 1

    note = args.note if args.note is not None else sys.stdin.read()
    if not note.strip():
        print("error: note is empty (provide --note or pipe via stdin)", file=sys.stderr)
        return 1

    today = args.today or _dt.date.today().isoformat()
    text = target.read_text(encoding="utf-8")
    try:
        new_text = insert_phase_block(text, args.phase, args.name.strip(),
                                       note, today)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    target.write_text(new_text, encoding="utf-8")
    print(f"{target}: appended Phase {args.phase}: {args.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
