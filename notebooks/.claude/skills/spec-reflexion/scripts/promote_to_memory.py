#!/usr/bin/env python3
"""promote_to_memory.py — promote a global learning to native auto-memory.

Writes a typed memory file at <memory_root>/<type>_<name>.md with YAML
frontmatter (`name`, `description`, `type`) and updates MEMORY.md so the
new file is indexed.

Memory file shape (matches the format used by Claude Code's auto-memory):

    ---
    name: <human-readable title>
    description: <one-line summary>
    type: <feedback|project|reference|user>
    ---

    <body>

MEMORY.md is appended/updated with a bullet pointing at the new file.
Existing entries for the same filename are replaced (not duplicated).

Usage:
  python promote_to_memory.py \\
      --text "Josh prefers explicit error types over Result wrappers" \\
      --type user \\
      --name josh_explicit_error_types \\
      --memory-root ~/.claude/projects/<sanitized-cwd>/memory

Args:
  --text         the learning body (required)
  --type         one of feedback | project | reference | user (required)
  --name         slug for the filename — kebab/snake-case (required)
  --memory-root  absolute path to the project memory directory (required)
  --title        optional explicit YAML `name`; defaults to first sentence of --text
  --description  optional YAML `description`; defaults to first sentence of --text
  --force        overwrite an existing file
"""
import argparse
import re
import sys
from pathlib import Path


ALLOWED_TYPES = {"feedback", "project", "reference", "user"}
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9_]*[a-z0-9])?$")


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s[:60] or "learning"


def _first_sentence(text: str, max_chars: int = 100) -> str:
    text = text.strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    m = re.match(r"^(.*?[.!?])(\s|$)", text)
    if m:
        sentence = m.group(1).strip()
    else:
        sentence = text
    if len(sentence) > max_chars:
        sentence = sentence[: max_chars - 1].rstrip() + "…"
    return sentence


def render_memory_file(name: str, description: str, type_: str, body: str) -> str:
    body = body.strip()
    return (
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"type: {type_}\n"
        "---\n"
        "\n"
        f"{body}\n"
    )


def _filename(type_: str, slug: str) -> str:
    return f"{type_}_{slug}.md"


def update_memory_index(index_path: Path, filename: str, description: str) -> None:
    """Insert or update the bullet in MEMORY.md for `filename`."""
    if index_path.exists():
        text = index_path.read_text(encoding="utf-8")
    else:
        text = "# Memory Index\n\n"
    if "# Memory Index" not in text:
        text = "# Memory Index\n\n" + text

    new_line = f"- [{filename}]({filename}) - {description}"
    pattern = re.compile(
        rf"^- \[{re.escape(filename)}\]\([^)]+\)[^\n]*$",
        re.MULTILINE,
    )
    if pattern.search(text):
        text = pattern.sub(new_line, text)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += new_line + "\n"
    index_path.write_text(text, encoding="utf-8")


def write_memory(
    text: str,
    type_: str,
    name: str,
    memory_root: Path,
    title: str | None = None,
    description: str | None = None,
    force: bool = False,
) -> Path:
    if type_ not in ALLOWED_TYPES:
        raise ValueError(f"type must be one of {sorted(ALLOWED_TYPES)}; got {type_!r}")
    slug = _slugify(name)
    if not SLUG_RE.match(slug):
        raise ValueError(f"name resolves to invalid slug: {slug!r}")
    if not text.strip():
        raise ValueError("text is empty")

    memory_root.mkdir(parents=True, exist_ok=True)
    filename = _filename(type_, slug)
    out = memory_root / filename
    if out.exists() and not force:
        raise FileExistsError(f"{out} exists (use --force)")

    derived_title = title or _first_sentence(text, max_chars=80)
    derived_desc = description or _first_sentence(text, max_chars=120)

    rendered = render_memory_file(derived_title, derived_desc, type_, text)
    out.write_text(rendered, encoding="utf-8")

    index_path = memory_root / "MEMORY.md"
    update_memory_index(index_path, filename, derived_desc)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--text", required=True)
    p.add_argument("--type", dest="type_", required=True, choices=sorted(ALLOWED_TYPES))
    p.add_argument("--name", required=True)
    p.add_argument("--memory-root", required=True, type=Path)
    p.add_argument("--title", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        out = write_memory(
            text=args.text,
            type_=args.type_,
            name=args.name,
            memory_root=args.memory_root,
            title=args.title,
            description=args.description,
            force=args.force,
        )
        print(str(out))
        return 0
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
