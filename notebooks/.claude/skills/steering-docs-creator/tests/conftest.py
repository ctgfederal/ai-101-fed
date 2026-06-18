"""Shared fixtures for steering-docs-creator tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_steering_root(tmp_path: Path) -> Path:
    """An empty directory acting as `.claude/steering/`."""
    root = tmp_path / "steering"
    root.mkdir()
    return root


@pytest.fixture
def valid_section_body() -> str:
    return (
        "| Layer | Tech | Version |\n"
        "|-------|------|---------|\n"
        "| Language | Python | 3.12 |\n"
    )
