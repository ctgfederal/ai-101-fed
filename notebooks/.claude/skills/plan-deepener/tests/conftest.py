"""Shared fixtures for plan-deepener tests."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def sample_target_md():
    return """# Feature Search

## Architecture

### Service pattern
**Decision**: Layered service.
**Rationale**: Sync, read-heavy.

## Data Model

### Storage
**Decision**: Postgres with JSONB.
"""


@pytest.fixture
def sample_findings():
    return {
        "summary": {
            "date": "2026-02-14",
            "sections_count": 2,
            "solutions_count": 1,
            "skills_list": ["compound-docs"],
            "key_findings": ["Postgres pg_trgm beats LIKE for fuzzy search"],
            "new_risks": ["JSONB index bloat over time"],
        },
        "sections": {
            "Service pattern": {
                "solutions": ["performance-issues/2026-02-14-n-plus-one.md"],
                "best_practices": ["Use connection pooling (per pgbouncer docs)"],
                "edge_cases": ["Slow query during DB failover — circuit-break the search"],
                "performance": ["p99 < 200ms target with 100 concurrent"],
                "references": ["https://www.postgresql.org/docs/current/sql-select.html"],
            },
            "Storage": {
                "solutions": [],
                "best_practices": ["GIN index on JSONB tsvector column"],
                "edge_cases": ["VACUUM tuning needed for high-update tables"],
                "performance": ["pg_trgm 5x faster than ILIKE for fuzzy match"],
                "references": ["https://www.postgresql.org/docs/current/datatype-json.html"],
            },
        },
    }


@pytest.fixture
def fake_skills_root(tmp_path):
    root = tmp_path / "skills"
    for name, desc in [
        ("postgres-pro", "PostgreSQL specialist for query optimization"),
        ("react-specialist", "React 18 patterns"),
        ("compound-docs", "Capture solved problems for postgres and other technologies"),
    ]:
        d = root / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\nversion: 1.0.0\ndescription: {desc}\n---\n\n# {name}\n",
            encoding="utf-8",
        )
    return root
