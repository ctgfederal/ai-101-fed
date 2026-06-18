# Success Criteria

A success criterion is a check the agent can run *itself* to know it's done. If the agent has to ask the orchestrator "is this good?", the criterion is too vague.

## Good criteria

Each item is one of:

- **A command exit code**: `pytest tests/auth/ exits 0`
- **A file existence check**: `src/auth/login.py exists`
- **A grep/match check**: `src/auth/login.py contains a function named login(email, password)`
- **A linter result**: `ruff check src/auth/ exits 0`
- **A scope check**: `git diff --name-only shows only files under src/auth/ or tests/auth/`

## Bad criteria

- "Looks good" — not testable.
- "All tests pass" — *which* tests? Be specific.
- "Code is clean" — define clean (lint? format? complexity?).
- "Implements the feature" — circular; the task already says that.
- "Ready for review" — not a check the agent can run.

## How many

3–6 criteria is usually right. Fewer than 2 means the agent has too much wiggle room. More than 8 means the task is too big — split it.

## Self-verifiable wins

The best criteria are ones the agent can run as the *last step* of its work, with the result determining whether it's done. This loops back to TDD: write the criterion first, then the work that satisfies it.
