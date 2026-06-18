# Feature Search

## Deepening Summary

**Deepened on:** 2026-02-14
**Sections enhanced:** 2
**Solutions referenced:** 2
**Skills matched:** postgres-pro, compound-docs, architecture-pattern-enforcer

### Key Findings
- pg_trgm + GIN index outperforms LIKE/ILIKE by ~5x for fuzzy search at 1M+ rows
- JSONB index bloat compounds without scheduled VACUUM; budget for it

### New Risks Discovered
- Slow query during DB failover; circuit-break the search endpoint
- JSONB schema drift — no enforced shape means migrations are scripted reads not ALTERs


## Architecture

### Service pattern
**Decision**: Synchronous layered service.
**Priority**: simplicity
**Rationale**: Read-heavy, low write volume; sync keeps the API surface narrow.

### Research Insights

**From Solutions Archive:**
- performance-issues/2026-02-14-n-plus-one-brief-generation.md — eager-load search-result associations

**Best Practices:**
- Connection pooling via pgbouncer in transaction-pooling mode (per pgbouncer docs)
- Per-request statement timeout — never share global timeouts (per Postgres docs SET LOCAL)

**Edge Cases:**
- Slow query during DB failover — circuit-break search to a 'partial results' fallback
- Read-replica lag — search may miss writes < replica lag (typically < 200ms)

**Performance:**
- p99 < 200ms target with 100 concurrent searchers on 1M-row dataset

**References:**
- https://www.pgbouncer.org/usage.html
- https://www.postgresql.org/docs/current/sql-set.html

## Data Model

### Storage engine
**Decision**: Postgres with JSONB for flexible search columns.
**Priority**: simplicity
**Rationale**: Single store; tsvector + JSONB cover today's search needs.

### Research Insights

**From Solutions Archive:**
- database-issues/2025-11-02-jsonb-bloat.md — VACUUM tuning required for JSONB-heavy tables

**Best Practices:**
- GIN index on JSONB columns used for filters (per Postgres docs)
- tsvector column generated from key text fields with trigger-driven update
- pg_trgm extension for fuzzy/typo-tolerant matching

**Edge Cases:**
- Schema drift in JSONB columns — no ALTER TABLE; require app-level shape validation
- Index bloat on high-update JSONB columns — schedule VACUUM (FULL) monthly

**Performance:**
- pg_trgm 5x faster than ILIKE on 1M rows (benchmark: in-house perf-test-2025-11)
- tsvector with GIN index supports 10k qps on the search hot path

**References:**
- https://www.postgresql.org/docs/current/datatype-json.html
- https://www.postgresql.org/docs/current/pgtrgm.html

