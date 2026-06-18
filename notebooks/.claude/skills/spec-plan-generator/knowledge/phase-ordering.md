# Phase Ordering

| Phase | Goal | Typical work |
|---|---|---|
| **Foundation** | Make the system buildable for this feature | DB migrations, scaffolding, contracts/types, fixtures |
| **Core** | Implement the business logic | Component-level code with unit tests |
| **Integration** | Wire components together; hit external boundaries | HTTP handlers, message-bus consumers, DB-backed integration tests |
| **Polish** | Performance, observability, edge cases | Caching, instrumentation, error-path tests, refactors |

## Rules

- Don't put business logic in Foundation.
- Don't put DB schema in Core (it's Foundation).
- Integration is only after Core has unit tests passing.
- Polish is last; it's where refactors live.

## When phases overlap

A task that spans Foundation+Core (e.g., "migration + repository") should be split into two tasks. Keeping phases pure makes status reporting honest.
