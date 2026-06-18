# Execution State Schema

State lives at `.claude/specs/<feature>/execution-state.json` and survives between sessions.
`state_manager.py init` creates it from PLAN.md; `update` merges patches; `read` prints it.

## Shape

```json
{
  "feature": "feature-search",
  "current_task": "T-003",
  "tasks": {
    "T-001": {
      "description": "Set up project skeleton",
      "status": "done",
      "history": [
        {"step": "red",      "result": "fail", "note": "import error expected", "duration_s": 30,  "timestamp": "2026-05-08T09:01:00"},
        {"step": "green",    "result": "pass", "note": "",                       "duration_s": 240, "timestamp": "2026-05-08T09:05:00"},
        {"step": "refactor", "result": "pass", "note": "extracted helper",       "duration_s": 90,  "timestamp": "2026-05-08T09:08:00"}
      ],
      "blockers": [],
      "depends_on": []
    },
    "T-002": {
      "description": "...",
      "status": "in-progress",
      "history": [],
      "blockers": [],
      "depends_on": ["T-001"]
    }
  },
  "task_order": ["T-001", "T-002", "T-003"],
  "meta": {
    "last_updated": "2026-05-08",
    "sessions": 2,
    "total_tasks": 3
  }
}
```

## Field reference

### Top level

| Field          | Type     | Required | Notes                                                          |
|----------------|----------|----------|----------------------------------------------------------------|
| `feature`      | string   | yes      | Folder name under `.claude/specs/`.                            |
| `current_task` | string?  | yes      | T-NNN id of the task in flight, or `null` between tasks.       |
| `tasks`        | dict     | yes      | One entry per T-NNN extracted from PLAN.md.                    |
| `task_order`   | string[] | yes      | Original document order from PLAN.md.                          |
| `meta`         | dict     | yes      | Audit fields.                                                  |

### `tasks[T-NNN]`

| Field         | Type     | Notes                                                                                            |
|---------------|----------|--------------------------------------------------------------------------------------------------|
| `description` | string   | Plain-English description from the PLAN.md line.                                                 |
| `status`      | string   | One of: `pending`, `in-progress`, `done`, `blocked`, `failed`.                                   |
| `history`     | dict[]   | Append-only TDD-cycle records (see `tdd-loop.md`).                                               |
| `blockers`    | string[] | Free-form notes describing why a task is stuck. Required to be non-empty when status=`blocked`.  |
| `depends_on`  | string[] | T-NNN ids that must reach `status=done` before this task is eligible (`next_task.py` honors it). |

### Status semantics

| Status        | Meaning                                                               |
|---------------|-----------------------------------------------------------------------|
| `pending`     | Not yet started. Default after `init`.                                |
| `in-progress` | At least one history entry exists; not yet `done`.                    |
| `done`        | Green and (optionally) refactored. PLAN.md checkbox can be ticked.    |
| `blocked`     | Cannot proceed; `blockers` describes why. Excluded from `next_task`.  |
| `failed`      | Three strikes — root cause is architectural; needs a deviation or replan. |

## Rules

- `history` is append-only. Never edit prior entries; record a new one.
- `task_order` is set at init time and never reordered (preserves PLAN.md trace).
- `meta.total_tasks` is set at init from the PLAN.md task count and is not auto-updated; if PLAN.md changes, re-init by deleting state and starting over (or use a manual patch).
- `current_task` is informational; the source of truth is per-task `status`.
- Patches are merged with `deep_merge`: dicts merge, lists/scalars overwrite.
