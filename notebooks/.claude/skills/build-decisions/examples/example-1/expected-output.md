# Decisions Log

Centralized append-only log of all design decisions across all features and phases. **ID convention**: globally-unique `D-NNN` from a single monotonic counter. Once assigned, IDs never change.

---

## Feature Search — Build Decisions (2026-02-14)

**Phase**: build | **Status**: complete | **Total decisions**: 8 (5 user, 3 auto-applied)
**ID range**: D-042 to D-049
**Priority framework**: simplicity → modularity → security → scalability

### Summary
Cross-entity search across briefs, customers, and notes. Read-heavy, sync, single-store.

### Auto-Applied (Federal Mandates)
| ID | Category | Decision | Mandated Answer | Citation |
|---|---|---|---|---|
| D-042 | Security | Encryption at rest | AES-256 or FIPS 140-2/3 equivalent. | NIST 800-53 SC-28; FIPS 140-3 |
| D-043 | Security | Encryption in transit | TLS 1.2 minimum. | NIST 800-52r2; SC-8 |
| D-044 | Audit | Audit log retention | Minimum 1 year; recommended 3. | NIST 800-53 AU-11 |

### Architecture

#### D-045: Service pattern
**Decision**: Synchronous layered service.
**Priority**: simplicity
**Alternatives**: event-driven w/ search-index sync; CQRS
**Rationale**: Read-heavy, low write volume; sync keeps the API surface narrow.
**Tiers**: Federal: policy gate enforces input validation | Enterprise: warns on missing auth | Personal: info logs only

### Data Model

#### D-046: Storage engine
**Decision**: Postgres with JSONB for flexible search columns.
**Priority**: simplicity
**Alternatives**: sqlite (insufficient FTS); elasticsearch (operational overhead)
**Rationale**: Single store; tsvector + JSONB cover today's search needs.
**Tiers**: Federal: FIPS-validated PG cluster required | Enterprise: TLS to PG, encrypted at rest | Personal: local PG, encryption optional

### API Design

#### D-047: Query endpoint
**Decision**: GET /search?q=...&type=brief|customer|note&limit=20
**Priority**: simplicity
**Alternatives**: GraphQL; POST with JSON query body
**Rationale**: REST keeps clients simple; GET is cacheable.
**Tiers**: Federal: rate limit 60/min, mTLS | Enterprise: rate limit 600/min | Personal: no rate limit

### Security

#### D-048: Authn
**Decision**: JWT with vault-rotated signing key.
**Priority**: security
**Alternatives**: session cookies; API keys
**Rationale**: Short-lived JWTs match the tier mandate (NIST 800-63B); vault provides rotation.
**Tiers**: Federal: Vault required; 15min token life | Enterprise: Vault recommended; 1h token life | Personal: static signing key OK; 1d life

### Performance

#### D-049: Caching
**Decision**: Per-query Redis cache with 60s TTL.
**Priority**: scalability
**Alternatives**: no cache; in-process LRU
**Rationale**: Search hits are repetitive; 60s gives stale-data tolerance for the use case.
**Tiers**: Federal: Redis must be local; no cloud egress | Enterprise: managed Redis OK | Personal: in-process LRU OK


### Open Questions
- What's the canonical typo-tolerance approach — pg_trgm or postgres ILIKE on prefix?
- Do customer notes need separate ACL filtering or is brief-level enough?

### Related Solutions
- performance-issues/2026-02-14-n-plus-one-brief-generation.md

