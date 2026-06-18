# Implementation Plan: Feature Search

## Context References

- **PRD:** [PRD.md](./PRD.md)
- **SDD:** [SDD.md](./SDD.md)
- **Tech stack:** [.claude/steering/tech.md](../../steering/tech.md)
- **Roadmap:** [.claude/steering/roadmap.md](../../steering/roadmap.md)

## Phase 1: Foundation

- **T-001** (red): Add tsvector column + GIN index migration
  - Components: COMP-003
  - Requirements: REQ-001
  - Acceptance: Migration applies cleanly; index exists on briefs.search_doc
- **T-002** (red): SearchRepository unit tests for tsvector queries
  - Components: COMP-003
  - Requirements: REQ-001
  - Acceptance: Tests describe query shape with statement timeout

## Phase 2: Core

- **T-003** (green): SearchRepository implementation
  - Components: COMP-003
  - Requirements: REQ-001
  - Acceptance: All Foundation tests pass; query honors timeout
- **T-004** (green): RankingPolicy unit tests + impl
  - Components: COMP-004
  - Requirements: REQ-002
  - Acceptance: Results ordered by score desc, recency tiebreak
- **T-005** (green): SearchService orchestration
  - Components: COMP-002
  - Requirements: REQ-001, REQ-002
  - Acceptance: Service calls repo, applies ranking, returns results

## Phase 3: Integration

- **T-006** (green): SearchController + HTTP routing
  - Components: COMP-001
  - Requirements: REQ-001
  - Acceptance: GET /search returns JSON; param validation in place
- **T-007** (green): End-to-end smoke test
  - Components: COMP-001, COMP-002, COMP-003, COMP-004
  - Requirements: REQ-001, REQ-002
  - Acceptance: POST→200ms p99 against fixture data

## Phase 4: Polish

- **T-008** (refactor): Refactor: extract query builder
  - Components: COMP-003
  - Requirements: REQ-001
  - Acceptance: All tests still green; query builder reusable

## Traceability

| Requirement | Tasks |
|---|---|
| REQ-001 | T-001, T-002, T-003, T-005, T-006, T-007, T-008 |
| REQ-002 | T-004, T-005, T-007 |

## Open Questions

_(none)_
