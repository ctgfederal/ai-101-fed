# Solution Design Document: Feature Search

## Context References

- **Tech stack:** [.claude/steering/tech.md](../../steering/tech.md)
- **Project structure:** [.claude/steering/structure.md](../../steering/structure.md)
- **PRD:** [PRD.md](./PRD.md)

## Overview

A read-heavy synchronous search service backed by Postgres with JSONB + tsvector + pg_trgm.

## Architecture

Layered: Controller → SearchService → SearchRepository → Postgres. Caching via Redis with 60s TTL.

## Components

### COMP-001: SearchController
**Responsibility:** HTTP entry point; param validation; rate-limit check.
**Dependencies:** SearchService
**Inputs:** GET /search?q=<query>&type=<filter>&limit=<n>
**Outputs:** JSON {results, total, page}

### COMP-002: SearchService
**Responsibility:** Orchestrate search; merge results across entity types; apply ranking.
**Dependencies:** SearchRepository, RankingPolicy, RedisCache
**Inputs:** SearchQuery {q, types, limit}
**Outputs:** list[SearchResult]

### COMP-003: SearchRepository
**Responsibility:** Postgres queries with pg_trgm and tsvector; per-query statement timeout.
**Dependencies:** Postgres
**Inputs:** SearchQuery
**Outputs:** list[Row]

### COMP-004: RankingPolicy
**Responsibility:** Score results by relevance + recency; return ordered list.
**Dependencies:** _(none)_
**Inputs:** list[Row]
**Outputs:** list[SearchResult] (ordered)


## Data Model

tsvector column on briefs.search_doc; GIN index. JSONB metadata column. trigram index on briefs.title.

## External Integrations

_(none — single store)_

## Traceability

| Requirement | Components |
|---|---|
| REQ-001 | COMP-001 |
| REQ-002 | COMP-002 |

## Alternatives Considered

Considered Elasticsearch (rejected: operational overhead). Considered SQLite FTS (rejected: insufficient at our scale).

## Risks and Mitigations

DB failover causes search outage. Mitigation: circuit-break with cached partial results.

## Open Questions

- Trigram threshold tuning?
