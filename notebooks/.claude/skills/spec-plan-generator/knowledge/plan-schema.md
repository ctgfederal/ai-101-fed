# PLAN Schema

## Required payload fields

| Field | Type | Notes |
|---|---|---|
| `feature` | string | Kebab-case |
| `feature_title` | string | Human-readable |
| `tasks` | list | ≥1 |
| `open_questions` | list | May be empty |

## Task fields (all required)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `T-NNN` (globally unique across all PLAN.md) |
| `title` | string | Imperative one-liner |
| `phase` | string | One of: Foundation, Core, Integration, Polish |
| `comps` | list | ≥1 SDD `COMP-NNN` IDs this task touches |
| `reqs` | list | PRD `REQ-NNN` IDs this task serves (may be empty if pure infrastructure) |
| `acceptance` | string | Verifiable success condition |
| `tdd_step` | string | `red`, `green`, or `refactor` |

## Coverage rules
- Every SDD `COMP-NNN` must be referenced by ≥1 task.
- Every PRD `REQ-NNN` must be covered by ≥1 task.
- Tasks reference only IDs that exist in PRD/SDD.
