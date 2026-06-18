# PRD Schema

## Required fields (payload)

| Field | Type | Notes |
|---|---|---|
| `feature` | string | Kebab-case. Used as folder name. |
| `feature_title` | string | Human-readable. |
| `vision` | string | One sentence; future state. |
| `problem` | string | What's painful today; consequences. |
| `value` | string | Why solving it matters. |
| `personas` | string | Reference to `.claude/steering/product.md#user-personas` plus feature-specific notes. |
| `user_stories` | list | Each: `{id, as, i_want, so_that}`. ≥1. |
| `requirements` | list | Each: `{id, story, moscow, ears}`. ≥1. |
| `metrics` | string | Reference framework + targets. |
| `risks` | string | Risks and mitigations. |
| `open_questions` | list | May be empty. |

## REQ-ID format
- `REQ-NNN` (zero-padded to 3, growing as needed).
- Globally unique across `.claude/specs/*/PRD.md`.
- Allocated by `scripts/allocate_req_ids.py`.

## MoSCoW values (exactly four)
- `Must` — release-blocking.
- `Should` — high-value, may slip a release.
- `Could` — nice-to-have.
- `Won't` — explicitly out of scope this cycle (note why).

## Story IDs
- `US-N` (e.g., `US-1`, `US-2`). Local to the PRD; not globally unique.
- Each requirement references one story by ID.
