#!/usr/bin/env python3
"""check_compliance.py — verify spec components and requirements have evidence in a repo.

Reads a parsed-spec JSON (output of parse_spec.py) and a repo root, then:
  - For each component: checks if any `expected_paths` entry exists
    relative to the repo root. Glob patterns are supported.
  - For each requirement: greps recursively for the literal `REQ-NNN`
    token across the repo. Records every file that mentions it.
  - Catalogues deviations: missing components, unreferenced requirements,
    and scope creep (REQ-NNN tokens in code that are not in the parsed PRD).

Output JSON shape (printed to stdout):
  {
    "prd": "...", "sdd": "...", "repo_root": "...",
    "status": "compliant" | "partial" | "non-compliant",
    "components": {
      "COMP-001": {
        "name": "...",
        "expected_paths": [...],
        "found_paths": [...],
        "missing": false
      }
    },
    "requirements": {
      "REQ-001": {
        "referenced_in": [...],
        "unreferenced": false
      }
    },
    "deviations": [
      {"type": "missing-component", "id": "COMP-002", "detail": "..."},
      ...
    ],
    "summary": {
      "components_total": ...,
      "components_found": ...,
      "requirements_total": ...,
      "requirements_referenced": ...,
      "deviation_count": ...
    }
  }

Usage:
  python check_compliance.py --spec-json parsed.json --repo-root .
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

# files we never scan (vendored / generated)
SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
}

# only grep text-ish files — avoids binary scan
TEXT_EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".rb", ".go", ".rs",
    ".java", ".kt", ".swift", ".cs", ".php", ".scala", ".clj", ".ex", ".exs",
    ".md", ".rst", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".html", ".css", ".scss", ".vue", ".sql", ".sh", ".bash", ".zsh",
}

REQ_TOKEN_RE = re.compile(r"\b(REQ-\d+)\b")


def iter_repo_files(root: Path) -> Iterable[Path]:
    """Yield text-ish files under root, skipping vendored / cache dirs."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        yield path


def resolve_paths(root: Path, expected: List[str]) -> List[str]:
    """For each expected path, return the matching paths that actually exist.

    Supports glob patterns (`*`, `**`, `?`). Returns relative-to-root paths,
    de-duplicated, in the order they were declared.
    """
    found: List[str] = []
    for spec in expected:
        spec = spec.strip()
        if not spec:
            continue
        if any(ch in spec for ch in "*?["):
            for match in root.glob(spec):
                if match.exists():
                    rel = match.relative_to(root).as_posix()
                    if rel not in found:
                        found.append(rel)
        else:
            candidate = root / spec
            if candidate.exists():
                rel = candidate.relative_to(root).as_posix()
                if rel not in found:
                    found.append(rel)
    return found


def scan_for_req_tokens(root: Path) -> dict:
    """Return {REQ-NNN: [relative file paths, sorted]} for every REQ token in the repo."""
    refs: dict = {}
    # sort the file walk for reproducible output across platforms
    files = sorted(iter_repo_files(root))
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in REQ_TOKEN_RE.finditer(text):
            rid = m.group(1)
            rel = path.relative_to(root).as_posix()
            bucket = refs.setdefault(rid, [])
            if rel not in bucket:
                bucket.append(rel)
    # final sort for stable JSON output regardless of walk order
    return {k: sorted(v) for k, v in refs.items()}


def compute_status(comps: dict, reqs: dict) -> str:
    """compliant / partial / non-compliant per the rubric."""
    if not comps and not reqs:
        return "non-compliant"
    any_comp = any(not c["missing"] for c in comps.values())
    all_comp = all(not c["missing"] for c in comps.values()) if comps else True
    any_req = any(not r["unreferenced"] for r in reqs.values())
    all_req = all(not r["unreferenced"] for r in reqs.values()) if reqs else True
    if all_comp and all_req:
        return "compliant"
    if any_comp and any_req:
        return "partial"
    return "non-compliant"


def check(spec: dict, repo_root: Path, repo_root_label: str | None = None) -> dict:
    components: dict = {}
    for comp in spec["comps"]:
        cid = comp["id"]
        found = resolve_paths(repo_root, comp.get("expected_paths", []))
        components[cid] = {
            "name": comp.get("name", ""),
            "expected_paths": comp.get("expected_paths", []),
            "found_paths": found,
            "missing": len(found) == 0,
        }

    repo_refs = scan_for_req_tokens(repo_root)

    requirements: dict = {}
    for rid in spec["reqs"]:
        files = repo_refs.get(rid, [])
        requirements[rid] = {
            "referenced_in": files,
            "unreferenced": len(files) == 0,
        }

    deviations: list = []
    for cid, info in components.items():
        if info["missing"]:
            paths_str = ", ".join(info["expected_paths"]) or "(no expected paths)"
            deviations.append({
                "type": "missing-component",
                "id": cid,
                "detail": f"{info['name']}: no file at {paths_str}",
            })
    for rid, info in requirements.items():
        if info["unreferenced"]:
            deviations.append({
                "type": "unreferenced-requirement",
                "id": rid,
                "detail": f"{rid} not referenced in any source or test file",
            })

    spec_req_set = set(spec["reqs"])
    for rid, files in repo_refs.items():
        if rid not in spec_req_set:
            deviations.append({
                "type": "scope-creep",
                "id": rid,
                "detail": f"{rid} found in code ({', '.join(files)}) but not defined in PRD",
            })

    summary = {
        "components_total": len(components),
        "components_found": sum(1 for c in components.values() if not c["missing"]),
        "requirements_total": len(requirements),
        "requirements_referenced": sum(1 for r in requirements.values() if not r["unreferenced"]),
        "deviation_count": len(deviations),
    }

    return {
        "prd": spec.get("prd", ""),
        "sdd": spec.get("sdd", ""),
        "repo_root": repo_root_label if repo_root_label is not None else str(repo_root),
        "status": compute_status(components, requirements),
        "components": components,
        "requirements": requirements,
        "deviations": deviations,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--spec-json", required=True, type=Path,
                   help="JSON output of parse_spec.py")
    p.add_argument("--repo-root", required=True, type=Path,
                   help="repository root to scan")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not args.spec_json.exists():
        print(f"error: spec JSON not found: {args.spec_json}", file=sys.stderr)
        return 1
    if not args.repo_root.exists() or not args.repo_root.is_dir():
        print(f"error: repo root not a directory: {args.repo_root}", file=sys.stderr)
        return 1
    try:
        spec = json.loads(args.spec_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid spec JSON: {e}", file=sys.stderr)
        return 1
    # use the user-supplied path verbatim in the output for reproducibility,
    # but resolve internally for reliable scanning
    payload = check(spec, args.repo_root.resolve(), repo_root_label=str(args.repo_root))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
