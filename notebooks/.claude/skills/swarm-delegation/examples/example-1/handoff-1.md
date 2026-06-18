# Agent Handoff

## FROM

orchestrator

## TO

backend-developer

## TASK

Implement the GET /users/:id endpoint with authentication.

## CONTEXT

- src/api/users/router.ts
- src/auth/middleware.ts
- .claude/specs/users/PRD.md

## SUCCESS

- Endpoint returns 200 with user payload for authenticated requests
- Endpoint returns 401 for missing or invalid token
- Coverage for new code is at least 80%

## RETURN

Unified diff and the path of any new test files.

## DEADLINE

Phase 2 boundary
