# Feature Search

## Architecture

### Service pattern
**Decision**: Synchronous layered service.
**Priority**: simplicity
**Rationale**: Read-heavy, low write volume; sync keeps the API surface narrow.

## Data Model

### Storage engine
**Decision**: Postgres with JSONB for flexible search columns.
**Priority**: simplicity
**Rationale**: Single store; tsvector + JSONB cover today's search needs.
