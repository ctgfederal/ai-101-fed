"""Integration test placeholder.

Gated by RUN_INTEGRATION_TESTS=1 because it touches the user's actual
~/.claude/projects/.../memory directory. This skill has no other external
dependencies (no API calls, no databases). The integration layer exists so
that the skill format validator finds something to call.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="set RUN_INTEGRATION_TESTS=1 to run against the real memory dir",
)


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_output.py"


def test_real_memory_dir_smoke():
    """Validate the user's existing memory files (if any) — must not crash."""
    home = Path(os.path.expanduser("~"))
    candidates = list((home / ".claude" / "projects").glob("*/memory/*.md"))
    if not candidates:
        pytest.skip("no real memory files found")
    for f in candidates:
        if f.name == "MEMORY.md":
            continue
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--file", str(f)],
            capture_output=True, text=True,
        )
        assert result.returncode in (0, 1), result.stderr
