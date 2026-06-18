"""Integration: run against the real ~/.claude/agents/ tree.

Gated by RUN_INTEGRATION_TESTS=1 because the agent set is user-specific.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from match_agents import rank
from parse_agent_frontmatter import parse_agents


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to enable",
)


def test_real_agents_load():
    real_root = Path.home() / ".claude" / "agents"
    if not real_root.is_dir():
        pytest.skip(f"no real agents tree at {real_root}")
    agents = parse_agents(real_root)
    assert len(agents) > 5, "real tree should have many agents"


def test_real_agents_ranking_for_react():
    real_root = Path.home() / ".claude" / "agents"
    if not real_root.is_dir():
        pytest.skip(f"no real agents tree at {real_root}")
    agents = parse_agents(real_root)
    out = rank(["react"], agents, max_results=5, min_score=0.0)
    assert out, "expected at least one react-related agent"
    for r in out:
        assert 0.0 <= r["score"] <= 1.0
