"""Evals for the keyword-extraction step that feeds match_agents.py.

These are pytest-style tests that exercise the *deterministic ranking* under
three scenarios meant to mimic LLM-extracted keyword sets:

  1. happy — clean, on-target keywords; expect the obvious specialist on top.
  2. edge  — sparse keywords (only one); the matcher must still rank sensibly.
  3. adversarial — noisy keywords (red herrings); the right agent must still surface.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from match_agents import rank
from parse_agent_frontmatter import parse_agents


@pytest.fixture
def agents(tmp_agents_root):
    return parse_agents(tmp_agents_root)


def test_happy_clean_keywords(agents):
    """Frontend React form task with on-target keywords."""
    keywords = ["react", "frontend", "form", "component"]
    out = rank(keywords, agents, max_results=3, min_score=0.0)
    assert out, "expected at least one match"
    top = out[0]["agent"]
    # react-specialist should win against frontend-developer for this set
    assert top == "react-specialist", f"top was {top!r}"


def test_edge_single_keyword(agents):
    """Only one keyword — matcher should still pick the specialist."""
    keywords = ["postgres"]
    out = rank(keywords, agents, max_results=3, min_score=0.0)
    assert out, "expected at least one match"
    assert out[0]["agent"] == "postgres-pro"


def test_adversarial_noisy_keywords(agents):
    """Red herrings included — the correct agent still ranks first."""
    keywords = ["react", "blockchain", "quantum", "kubernetes", "specialist"]
    out = rank(keywords, agents, max_results=3, min_score=0.0)
    assert out, "expected at least one match"
    # 'react' + 'specialist' should still elevate react-specialist over the
    # generic frontend-developer despite the red herrings.
    assert out[0]["agent"] == "react-specialist"


def test_no_match_returns_empty(agents):
    out = rank(["xyz_nonsense_term_999"], agents, max_results=3, min_score=0.0)
    assert out == []
