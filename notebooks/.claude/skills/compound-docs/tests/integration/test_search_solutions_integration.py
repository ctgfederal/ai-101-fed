"""Integration tests against the real .claude/solutions/ archive.

Gated by RUN_INTEGRATION_TESTS=1 because it requires the real repo state.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to run",
)


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "search_solutions.py"


def test_real_archive_smoke():
    """Search the real archive for a tag that may not exist; must exit 0."""
    repo_root = Path(__file__).resolve().parents[5]  # heuristic: walk up to repo root
    archive = repo_root / ".claude" / "solutions"
    if not archive.is_dir():
        pytest.skip(f"no archive at {archive}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--solutions-root", str(archive), "--tag", "nonexistent-test-tag"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
