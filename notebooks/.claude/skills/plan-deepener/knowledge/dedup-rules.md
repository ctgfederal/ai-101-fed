# Deduplication Rules

Multiple sources will surface the same recommendation. Merge cleanly.

## Same recommendation, different sources

Merge to one entry, list all citations:

> "Use prepared statements for all parameterized queries (per OWASP, Postgres docs, and the project's existing `runtime-errors/2026-01-12-sql-injection.md`)."

## Same recommendation, contradictory framing

Disagreements stay as disagreements — don't pick a side:

> "Sources disagree on connection pool sizing: pgbouncer docs recommend `max_connections * 2`; the in-house `performance-issues/2025-11-08-pool-saturation.md` recommends `max_connections / 2` for our workload. Recommend benchmarking with this specific workload."

## Near-duplicates

If two findings differ only in phrasing, merge to the clearer one. If they differ in scope, keep both.

## Hashing for dedup

Lowercase + strip punctuation + first 80 chars → set membership. Anything that hashes the same is a duplicate.

## Order of sources

When citing multiple sources for the same point:
1. In-house solution archive (most relevant to the project)
2. Specific docs (RFC, language spec, framework reference)
3. General industry write-ups (last)
