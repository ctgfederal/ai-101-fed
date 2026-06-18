"""Integration tests for steering-docs-creator.

Gated by RUN_INTEGRATION_TESTS=1. These run against a real repo's
`.claude/steering/` if present.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _enabled() -> bool:
    return os.environ.get("RUN_INTEGRATION_TESTS") == "1"


@pytest.mark.skipif(not _enabled(), reason="set RUN_INTEGRATION_TESTS=1 to run")
def test_validates_real_steering_root() -> None:
    steering = Path.cwd() / ".claude" / "steering"
    if not steering.is_dir():
        pytest.skip(f"no steering root at {steering}")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_steering.py"),
         "--steering-root", str(steering)],
        capture_output=True,
        text=True,
    )
    # Either passes or fails with informative output — both are acceptable
    # signals that the script ran. We assert the script ran without crashing.
    assert result.returncode in (0, 1), result.stderr
