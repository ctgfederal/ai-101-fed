#!/usr/bin/env python3
"""
dedupe.py — check whether a candidate auto-doc payload duplicates any existing
file under <docs-root>.

Signals (per knowledge/dedup-rules.md):
  - Title similarity (Jaccard on lowercased non-stopword tokens) >= 0.6
  - Tag overlap (Jaccard on tag sets) >= 0.5
  - Scope hash exact match

A candidate is flagged duplicate if ANY of:
  - Scope hash matches AND category matches AND tag overlap >= 0.3
  - Title similarity >= 0.6 AND category matches
  - Tag overlap >= 0.5 AND category matches AND title similarity >= 0.4

Usage:
  python dedupe.py --payload payload.json --docs-root .claude/docs/auto

Output:
  JSON to stdout: {"is_duplicate": bool, "similar": [paths]}

Exit codes:
  0  always (the JSON is the result)
  1  bad arguments / unreadable payload
"""

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

STOPWORDS = {
    "the", "a", "an", "of", "in", "for", "to", "and", "or", "on", "at", "is",
    "are", "be", "by", "with", "from", "as", "that", "this", "it",
}

TITLE_THRESHOLD = 0.6
TAG_THRESHOLD = 0.5
SCOPE_TAG_THRESHOLD = 0.3
TAG_TITLE_FALLBACK = 0.4


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )


def tokenize_title(title: str) -> Set[str]:
    norm = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    return {t for t in norm.split() if t and t not in STOPWORDS}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = a & b
    union = a | b
    if not union:
        return 0.0
    return len(inter) / len(union)


def scope_hash(scope: str) -> str:
    norm = re.sub(r"\s+", " ", scope.lower()).strip()
    norm = re.sub(r"[^a-z0-9]+", "", norm)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16] if norm else ""


# --- minimal frontmatter parsing (no PyYAML) ---

def split_frontmatter(text: str) -> Tuple[str, str]:
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return "", text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return "", text
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def parse_yaml(yaml_text: str) -> dict:
    data: dict = {}
    lines = yaml_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in raw:
            i += 1
            continue
        key, _, val = raw.partition(":")
        key = key.strip()
        val = val.strip()

        if val == "":
            data[key] = []
            i += 1
            while i < len(lines):
                line = lines[i]
                if not line.strip() or line.lstrip().startswith("#"):
                    i += 1
                    continue
                if line.startswith("  - ") or line.startswith("- "):
                    item = line.lstrip()[2:].strip()
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        item = item[1:-1]
                    data[key].append(item)
                    i += 1
                else:
                    break
            continue

        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()] if inner else []
            i += 1
            continue

        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        data[key] = val
        i += 1
    return data


def load_doc(path: Path) -> dict:
    """Return frontmatter dict (with 'tags' as list) for a doc file, or {}."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return {}
    yaml_text, _ = split_frontmatter(text)
    if not yaml_text:
        return {}
    data = parse_yaml(yaml_text)
    if "tags" in data and not isinstance(data["tags"], list):
        data["tags"] = []
    return data


def is_duplicate(candidate: dict, existing: dict) -> bool:
    """Apply the duplicate-flag rules to one (candidate, existing) pair."""
    if existing.get("category") != candidate.get("category"):
        return False

    cand_title = tokenize_title(str(candidate.get("title", "")))
    ex_title = tokenize_title(str(existing.get("title", "")))
    title_sim = jaccard(cand_title, ex_title)

    cand_tags = set(candidate.get("tags", []) or [])
    ex_tags = set(existing.get("tags", []) or [])
    tag_overlap = jaccard(cand_tags, ex_tags)

    cand_scope = scope_hash(str(candidate.get("scope", "")))
    ex_scope = scope_hash(str(existing.get("scope", "")))
    scope_match = bool(cand_scope) and cand_scope == ex_scope

    if scope_match and tag_overlap >= SCOPE_TAG_THRESHOLD:
        return True
    if title_sim >= TITLE_THRESHOLD:
        return True
    if tag_overlap >= TAG_THRESHOLD and title_sim >= TAG_TITLE_FALLBACK:
        return True
    return False


def find_similar(candidate: dict, docs_root: Path) -> List[Path]:
    hits: List[Path] = []
    if not docs_root.is_dir():
        return hits
    for f in docs_root.rglob("*.md"):
        if not f.is_file():
            continue
        existing = load_doc(f)
        if not existing:
            continue
        if is_duplicate(candidate, existing):
            hits.append(f)
    return hits


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--payload", required=True, type=Path, help="JSON payload file")
    p.add_argument("--docs-root", required=True, type=Path, help="path to .claude/docs/auto/")
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("dedupe")

    try:
        payload_text = args.payload.read_text(encoding="utf-8")
    except FileNotFoundError:
        log.error("payload not found: %s", args.payload)
        return 1
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as e:
        log.error("payload is not valid JSON: %s", e)
        return 1

    similar = find_similar(payload, args.docs_root)
    out = {
        "is_duplicate": bool(similar),
        "similar": [str(p) for p in similar],
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
