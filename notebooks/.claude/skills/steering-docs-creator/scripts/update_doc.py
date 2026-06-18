#!/usr/bin/env python3
"""update_doc.py — replace the body of one `## ` section in a steering doc.

The heading itself, the preceding content, and following sections are
preserved byte-for-byte. Only the body between the named heading and the
next `## ` (or EOF) is replaced.

Usage:
  python update_doc.py \\
      --steering-root .claude/steering \\
      --doc tech \\
      --section "Tech Stack" \\
      --body - <<'EOF'
  | Layer | Tech | Version |
  ...
  EOF

Or pass a literal string with --body "...". When --body is "-", the new
body is read from stdin.

Refuses to write if the section heading is not found in the doc, unless
--force is set (in which case the section is appended to the end).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOCS = ("product", "tech", "structure", "roadmap")


def replace_section(text: str, heading: str, new_body: str) -> tuple[str, bool]:
    """Return (new_text, found). If `heading` isn't found, returns (text, False).

    new_body should NOT include the `## heading` line.
    """
    # Find the section line: must be `## <heading>` exactly (trimmed).
    pattern = re.compile(r"^##\s+" + re.escape(heading) + r"\s*$", flags=re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return (text, False)

    body_start = m.end()
    # find next `## ` or EOF
    next_h2 = re.search(r"^##\s+", text[body_start:], flags=re.MULTILINE)
    if next_h2:
        body_end = body_start + next_h2.start()
    else:
        body_end = len(text)

    # Construct the replacement: a leading newline (so heading line is preserved
    # exactly), then the new body, then a trailing newline (so the next heading
    # starts on its own line). If we're at EOF, we don't need the trailing
    # newline beyond the body itself.
    new_body_block = "\n\n" + new_body.strip("\n") + "\n"
    if next_h2:
        new_body_block = new_body_block + "\n"
    new_text = text[:body_start] + new_body_block + text[body_end:]
    return (new_text, True)


def append_section(text: str, heading: str, new_body: str) -> str:
    """Append a new `## heading` section + body at the end of the file."""
    sep = "\n\n" if text.endswith("\n") else "\n\n"
    return text + sep + f"## {heading}\n\n{new_body.rstrip()}\n"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--steering-root", required=True, type=Path)
    p.add_argument("--doc", required=True, choices=DOCS)
    p.add_argument("--section", required=True,
                   help="exact heading text, without the '## ' prefix")
    p.add_argument("--body", required=True,
                   help="new body, or '-' to read from stdin")
    p.add_argument("--force", action="store_true",
                   help="if section is missing, append it instead of failing")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    target = args.steering_root / f"{args.doc}.md"
    if not target.is_file():
        print(f"error: doc not found: {target}", file=sys.stderr)
        return 1

    body = sys.stdin.read() if args.body == "-" else args.body
    if not body.strip():
        print("error: empty body", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")
    new_text, found = replace_section(text, args.section, body)
    if not found:
        if not args.force:
            print(f"error: section not found: ## {args.section} in {target}",
                  file=sys.stderr)
            return 1
        new_text = append_section(text, args.section, body)

    target.write_text(new_text, encoding="utf-8")
    print(str(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
