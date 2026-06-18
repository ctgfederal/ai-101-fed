"""Shared pytest fixtures for compound-docs tests."""
import json
import sys
from datetime import date
from pathlib import Path

import pytest

# make scripts/ importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def tmp_solutions_root(tmp_path):
    """A clean .claude/solutions/ tree with category folders."""
    root = tmp_path / "solutions"
    root.mkdir()
    for cat in ("performance-issues", "build-errors", "runtime-errors"):
        (root / cat).mkdir()
    return root


@pytest.fixture
def valid_payload():
    """A complete, valid JSON payload for write_solution.py."""
    return {
        "title": "N+1 query in brief generation",
        "category": "performance-issues",
        "date": date.today().isoformat(),
        "tags": ["activerecord", "rails", "n+1", "query-optimization"],
        "module": "BriefGenerator",
        "symptom": "Brief generation taking 12s for 50 records.",
        "root_cause": "BriefGenerator iterated and accessed .author per row.",
        "severity": "high",
        "symptom_body": "12s render for 50 briefs. SQL log shows one SELECT per row.",
        "investigation_body": "1. Profiled with rack-mini-profiler — confirmed N+1.\n2. Tried memoization — did not help (different objects).",
        "root_cause_body": "ActiveRecord lazy-loads `author` on each access.",
        "solution_body": "```ruby\nbriefs.includes(:author).each { |b| ... }\n```",
        "verification_body": "Render dropped to 0.3s for 50 briefs. Query count: 51 → 2.",
        "prevention_body": "- Bullet gem in dev to flag N+1.\n- Test asserting query count for index actions.",
        "related_body": "- See `runtime-errors/2025-12-01-stale-author-cache.md`",
    }


@pytest.fixture
def invalid_payload(valid_payload):
    """Same shape but with a missing required key."""
    p = dict(valid_payload)
    del p["module"]
    return p


@pytest.fixture
def fixture_solution_file(tmp_path):
    """Write a sample solution file and return its path."""
    f = tmp_path / "sample.md"
    f.write_text("""---
title: "Sample N+1"
category: performance-issues
date: 2026-02-14
tags:
  - activerecord
  - n+1
module: "BriefGenerator"
symptom: "12s render"
root_cause: "lazy load"
severity: high
---

# Sample N+1

## Symptom
12s render.

## Investigation
1. Profiled.

## Root Cause
Lazy load.

## Solution
includes(:author)

## Verification
Down to 0.3s.

## Prevention
Bullet gem.
""", encoding="utf-8")
    return f
