"""Shared fixtures for spec-readme tests."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def specs_root(tmp_path) -> Path:
    """A temp specs root."""
    root = tmp_path / "specs"
    root.mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture
def valid_feature() -> str:
    return "feature-search"


@pytest.fixture
def seeded_readme(specs_root, valid_feature) -> Path:
    """Initialize a fresh README via init_readme.py and return its path."""
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "init_readme.py"),
            "--feature", valid_feature,
            "--specs-root", str(specs_root),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())
