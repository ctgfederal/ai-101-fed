"""Shared pytest fixtures for spec-reflexion tests."""
import sys
from pathlib import Path

import pytest

# Make scripts/ importable for direct module-level tests.
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture
def tmp_memory_root(tmp_path):
    """A clean memory directory ready to receive promoted learnings."""
    root = tmp_path / "memory"
    root.mkdir()
    return root


@pytest.fixture
def sample_readme() -> str:
    """A spec README with both local and global learnings."""
    return """# Spec README — feature-123

## Overview

Add typed error responses to the public API.

## Decisions

- D-007: Use explicit error subclasses; reject Result<T, E>.

## Learnings

### Phase T-005 — Error wrapper rollout

- T-005 | REQ-104 was renumbered after the merge from main | spec-reality-mismatch | three downstream files updated
- Explicit ApiError extends Error subclass; clear stack traces.

### For /memorize (Global Learnings)

- [ ] Josh prefers explicit error types over Result wrappers — keeps stack traces clean and the type system honest. → type: `user`
- [ ] Always renumber REQ ids before merging branches → type: `feedback`
"""


@pytest.fixture
def empty_readme() -> str:
    """A spec README with no learnings sections."""
    return """# Spec README — feature-empty

## Overview

Just a placeholder.
"""


@pytest.fixture
def valid_promotion_payload(tmp_memory_root):
    return {
        "text": "Josh prefers explicit error types over Result wrappers — keeps stack traces clean and the type system honest.",
        "type_": "user",
        "name": "josh_explicit_error_types",
        "memory_root": tmp_memory_root,
    }
