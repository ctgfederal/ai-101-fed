# Task Schema

A task is a `- [ ] T-NNN <Title>` bullet under a `## Phase N: <Name>` heading inside `PLAN.md`. Below the bullet, indented child lines describe implementation. Four tagged lines provide the structured fields the validator reads.

## Tagged lines

```
- [ ] T-001 Implement search index loader
  - Load fixture data on module init
  - Memoize until file mtime changes
  _Acceptance:_ test_loader_caches_until_mtime_changes passes
  _Requirements:_ REQ-101, REQ-102
  _Components:_ COMP-001
  _TDD:_ red
```

## Required fields per task

| Field | Source | Required | Example |
|---|---|---|---|
| `id` | bullet | yes | `T-001` |
| `title` | bullet | yes | `Implement search index loader` |
| `phase` | parent `## Phase N: <Name>` heading | yes | `Foundation` |
| `acceptance` | `_Acceptance:_` line | yes | `test_loader_caches_until_mtime_changes passes` |
| `tdd_step` | `_TDD:_` line | yes | `red` |
| `reqs` | `_Requirements:_` line | optional (may be empty list) | `["REQ-101", "REQ-102"]` |
| `comps` | `_Components:_` line | optional (may be empty list) | `["COMP-001"]` |

## ID format

- Task IDs match `^T-\d{3,}$` (e.g., `T-001`, `T-1023`).
- Requirement IDs match `^REQ-\d+$`.
- Component IDs match `^COMP-\d+$`.
- All three are extracted with the same regex `[A-Z]{2,4}-\d+` from the relevant tagged line; case matters.

## Allowed phases

`Foundation`, `Core`, `Integration`, `Polish`. Phases outside this set fail the task. Phase ordering is enforced by `spec-plan-generator`, not here.

## Allowed TDD step values

`red`, `green`, `refactor`. Any other value (or missing line) fails the task.

## Why these fields

- `id` + `title`: human-readable handle, monotonic across `.claude/specs/*/PLAN.md`.
- `phase`: forces ordering discipline (foundation before core before integration before polish).
- `acceptance`: the "done" condition; must be measurable so `/implement` knows when to stop.
- `reqs` / `comps`: traceability — every PRD requirement must be served by ≥1 task; every SDD component must be touched by ≥1 task.
- `tdd_step`: which leg of the red/green/refactor cycle this task is in.
