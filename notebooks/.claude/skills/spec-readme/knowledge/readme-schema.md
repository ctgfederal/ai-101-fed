# README Schema

Authoritative shape of `.claude/specs/<feature>/README.md`. The validator (`scripts/validate_output.py`) enforces every rule on this page.

## Required `##` sections, in order

1. `## Status`
2. `## Steering References`
3. `## Decision Log Snippets`
4. `## Phase Notes`
5. `## Learnings`
6. `## Open Questions`

Additional `##` sections may be added between these — the validator only enforces presence and relative order — but doing so is discouraged. Six sections is enough for an index file; more, and humans stop reading.

## Status table

Exactly three rows in this order: PRD, SDD, PLAN.

```
| Doc | Status | Last Update |
|---|---|---|
| PRD | <status> | <iso-date> |
| SDD | <status> | <iso-date> |
| PLAN | <status> | <iso-date> |
```

Allowed status values (closed set):

| Status | Meaning |
|---|---|
| `draft` | In progress; do not build against this. |
| `approved` | Signed off by humans; safe to build against. |
| `deprecated` | Replaced; see successor doc. |

No other values. No emoji, no "wip", no "in-review", no "blocked". If you need a fourth state, add it here first, then teach the validator.

## Steering References

Use **relative paths** from the spec folder, never absolute and never duplicated content:

```
- Product: [`../../steering/product.md`](../../steering/product.md)
```

The path `../../steering/<file>.md` is mandatory for at least one steering doc — the validator requires it.

## Decision Log Snippets

Cross-feature decisions live in `.claude/decisions-log.md` (one global, append-only file managed by `/build`). The README only **references** them by ID, not by content:

```
- [D-014](../../decisions-log.md#d-014) — picked Postgres over SQLite for full-text search.
```

If a decision is local to this feature only and never reused, write it as a phase note instead — not a decision-log entry.

## Phase Notes

`### Phase <int>: <name>` headers inside `## Phase Notes`. Monotonic ascending by phase number; no duplicates. Phase numbers are positive integers. Names are short — Foundation, Core, Integration, Polish are the canonical four. Append via `scripts/append_phase_note.py`, never by direct edit.

## Learnings

Free-form bullets. Feature-specific only. Globally reusable patterns belong in memory, not here. See `learnings-vs-decisions.md`.

## Open Questions

Free-form bullets. Items here block forward motion. Move them to phase notes once resolved.
