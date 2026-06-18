# Delegation: auth-agent

## FOCUS

- src/auth/
- tests/auth/

## EXCLUDE

- src/billing/
- src/users/profile.py
- docs/

## TASK

Implement JWT authentication in src/auth/. Add login, logout, refresh endpoints with bcrypt password hashing.

## SUCCESS

- pytest tests/auth/ exits 0 with at least 3 test cases
- src/auth/login.py defines login(email, password)
- ruff check src/auth/ exits 0
- git diff --name-only shows only files under src/auth/ or tests/auth/

## RETURN

Markdown summary: files created, tests added, blockers, next steps.
