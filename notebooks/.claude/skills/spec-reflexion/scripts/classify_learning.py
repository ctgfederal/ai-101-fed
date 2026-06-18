#!/usr/bin/env python3
"""classify_learning.py — classify a single learning text as 'local' or 'global'.

Heuristic-based. Local indicators (project-specific):
  - First-person plural pronouns ("our X", "we use", "we ran into")
  - Specific path patterns (.claude/specs/<feat>, src/foo/bar.py)
  - Pinned tickets / IDs (REQ-NNN, T-NNN, D-NNN, JIRA-123)
  - Sentence references "this spec", "this feature", "the team"
  - PascalCase or snake_case identifiers that look like internal modules

Global indicators (universally useful):
  - Framework / language nouns (React, Next.js, TypeScript, Python, etc.)
  - Pattern-language verbs (always X, never Y, prefer X over Y, when X then Y)
  - User-preference markers ("Josh prefers", "user prefers", "I prefer")
  - Generic best-practice phrasing (no project nouns at all)

Tiebreaker: if both signals fire, the **stronger** of the two wins. If the
signal counts are equal we default to **local** — promotion to global memory
should be conservative.

Usage:
  python classify_learning.py --text "Josh prefers explicit error types"
  echo "Use includes() to avoid N+1 in ActiveRecord" | python classify_learning.py

Output: prints exactly one of `local` or `global` followed by a newline.
Exit 0 always (unless I/O fails).
"""
import argparse
import re
import sys
from typing import Tuple


LOCAL_PATTERNS = [
    r"\bour\s+\w+",
    r"\bwe\s+(?:use|ran|saw|tried|chose|need|had|hit)\b",
    r"\bthis\s+(?:spec|feature|project|repo|file|module|sprint)\b",
    r"\bthe\s+team\b",
    r"\.claude/(?:specs|brainstorms|builds)/",
    r"\b(?:REQ|US|D|T)-\d+\b",
    r"\b[A-Z]+-\d+\b",
    r"src/[\w/.-]+\.py",
    r"\b[a-z]+_[a-z]+(?:_[a-z]+)*\b",
]

GLOBAL_PATTERNS = [
    r"\b(?:React|Next\.?js|TypeScript|JavaScript|Python|Ruby|Rails|Django|FastAPI|Vue|Svelte|Angular|Node\.?js|Go(?:lang)?|Rust|Java|Kotlin|Swift|PHP|Laravel|Express|GraphQL|REST|HTTP|HTTPS|JWT|OAuth|JSON|YAML|XML|SQL|NoSQL|Postgres(?:QL)?|MySQL|SQLite|Redis|MongoDB|Docker|Kubernetes|AWS|GCP|Azure|Git|GitHub|GitLab|CI/?CD|TDD|BDD)\b",
    r"\balways\s+\w+",
    r"\bnever\s+\w+",
    r"\bprefer\s+\w+\s+over\s+\w+",
    r"\bwhen\s+.{1,40}\s+then\s+",
    r"\b(?:Josh|user|I)\s+prefers?\b",
    r"\b(?:anti-?pattern|best\s+practice|convention|rule|principle)\b",
    r"\bdon'?t\s+\w+",
]


def _count(patterns, text: str) -> int:
    n = 0
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            n += 1
    return n


def classify(text: str) -> Tuple[str, dict]:
    """Return ('local'|'global', debug_signals)."""
    text = text.strip()
    if not text:
        return "local", {"reason": "empty input"}
    local_score = _count(LOCAL_PATTERNS, text)
    global_score = _count(GLOBAL_PATTERNS, text)

    if global_score > local_score:
        scope = "global"
    elif local_score > global_score:
        scope = "local"
    else:
        scope = "local"  # conservative default

    return scope, {"local_score": local_score, "global_score": global_score}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--text", default=None,
                   help="learning text; omit to read from stdin")
    p.add_argument("--debug", action="store_true",
                   help="also emit signal counts on stderr")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()
    scope, signals = classify(text)
    if args.debug:
        print(f"signals: {signals}", file=sys.stderr)
    print(scope)
    return 0


if __name__ == "__main__":
    sys.exit(main())
