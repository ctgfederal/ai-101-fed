#!/usr/bin/env python3
"""parse_target.py — extract sections, technologies, categories, open-questions from a markdown doc.

Usage:
  python parse_target.py --file path.md

Prints JSON to stdout:
  {
    "sections": [{"heading": "...", "level": 2, "body": "..."}],
    "technologies": ["postgres", "redis", ...],
    "categories": ["Architecture", "Data Model", ...],
    "open_questions": ["...", "..."]
  }

Exit 0 = parsed.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

# crude tech vocabulary; expand as needed
TECH_VOCAB = {
    "postgres", "postgresql", "mysql", "sqlite", "redis", "memcached",
    "kafka", "rabbitmq", "nats", "pulsar",
    "react", "vue", "svelte", "next.js", "nextjs", "remix",
    "node", "nodejs", "python", "rust", "go", "ruby", "java", "typescript",
    "rails", "django", "flask", "fastapi", "express",
    "kubernetes", "k8s", "docker", "terraform",
    "elasticsearch", "opensearch", "neo4j", "mongodb",
    "graphql", "rest", "grpc", "websocket",
    "openai", "anthropic", "huggingface", "vector-db",
    "vault", "oauth", "oidc", "jwt",
}


def split_sections(text: str) -> List[dict]:
    """Split on `##` and `###` headings (preserves level)."""
    lines = text.splitlines()
    sections: List[dict] = []
    current = None
    for line in lines:
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections.append(current)
            current = {"heading": m.group(2).strip(), "level": len(m.group(1)), "body": ""}
        else:
            if current is not None:
                current["body"] += line + "\n"
    if current is not None:
        sections.append(current)
    return sections


def extract_technologies(text: str) -> List[str]:
    found = set()
    lower = text.lower()
    for tech in TECH_VOCAB:
        if re.search(rf"\b{re.escape(tech)}\b", lower):
            found.add(tech)
    # also pick up code-fenced language hints
    for m in re.finditer(r"```([a-z+]+)", lower):
        lang = m.group(1)
        if lang in {"python", "ruby", "rust", "go", "typescript", "javascript", "sql", "shell", "bash"}:
            found.add(lang if lang != "javascript" else "node")
    return sorted(found)


def extract_categories(sections: List[dict]) -> List[str]:
    return sorted({s["heading"] for s in sections if s["level"] == 3
                   and s["heading"] not in {"Open Questions", "Related Solutions",
                                            "Research Insights", "Auto-Applied (Federal Mandates)"}})


def extract_open_questions(sections: List[dict]) -> List[str]:
    out = []
    for s in sections:
        if s["heading"].lower() == "open questions":
            for line in s["body"].splitlines():
                if line.strip().startswith("- "):
                    out.append(line.lstrip("- ").strip())
    return out


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", required=True, type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    text = args.file.read_text(encoding="utf-8")
    sections = split_sections(text)
    out = {
        "sections": sections,
        "technologies": extract_technologies(text),
        "categories": extract_categories(sections),
        "open_questions": extract_open_questions(sections),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
