# 12 Decision Categories (Ordered)

Walk these in order. Be exhaustive within each — every sub-bullet is a potential question. Skip entire categories only if the feature genuinely doesn't touch the domain (and document the skip explicitly).

## 1. Architecture
- Overall pattern (event-driven, layered, hexagonal, CQRS)
- Component boundaries and responsibilities
- Data flow direction (push/pull, sync/async)
- Dependency structure and inversion
- Module boundaries (TUI / commands / CLI / teams / agents / run)
- Extension points and plugin interfaces
- Error propagation strategy
- Configuration management approach

## 2. Data Model
- Entities and relationships
- Storage engine (SQL, NoSQL, file, event store)
- Schema design
- Migration strategy
- Validation boundary (where Pydantic models live)
- Serialization format
- Data lifecycle (create / mutate / archive / delete)
- Multi-tenancy / namespace isolation

## 3. API Design
- Endpoint structure and naming
- Request / response contracts
- Authn / authz approach
- Versioning strategy
- Rate limiting / throttling
- Error response format
- Pagination
- Idempotency

## 4. Observability & Telemetry
- OTEL span design (what gets traced, naming, attributes)
- Metrics (counters, histograms, gauges)
- Structured logging format and levels
- Trace context propagation
- LLM call telemetry (model, tokens, latency, cost)
- Tool invocation telemetry
- Correlation IDs
- Dashboard / alerting strategy
- Telemetry export targets
- Sampling strategy

## 5. Audit & Compliance
- Audit event schema
- Audit trail storage
- Data classification / labeling
- PII / CUI detection
- Data sovereignty / residency
- Compliance report generation
- Access control audit
- Change management tracking
- Retention (auto-applied per NIST AU-11; storage strategy is a choice)
- Human approval gates

## 6. Security
- Authn mechanism (mTLS, JWT, OIDC)
- Authz model (RBAC, ABAC, policy engine)
- Input validation boundary
- Output sanitization (LLM output handling)
- Secret management (Vault, rotation)
- Threat model alignment (OWASP LLM Top 10, OWASP Agentic Top 10)
- Agent identity (DID, keypairs, certs)
- Privilege scoping
- Sandboxing
- Supply chain (signing, SBOM)

## 7. Integration
- External service connections
- Protocol choices (REST, gRPC, WebSocket, NATS)
- Message bus (topics, subjects, queues)
- Error handling for external deps
- Circuit breaker / retry
- Timeout / deadline propagation
- Service discovery
- Inter-agent communication

## 8. Performance
- Caching (in-memory, distributed, TTL)
- Connection pooling
- Async execution (asyncio, uvloop, thread pool)
- Resource limits (memory, CPU, FDs)
- Cold start budget
- Batch processing
- Backpressure
- Horizontal scaling

## 9. Extensibility & Lockdown Configuration
- Module / plugin system
- Feature toggles
- Tier configuration (`[security] tier` propagation)
- Policy enforcement point design (single block / warn / allow gate)
- Optional pip extras packaging
- Hook points for custom behavior
- Third-party extension boundaries
- Module lifecycle (load, verify, activate, deactivate)
- API stability for extension points
- Tier-specific defaults

## 10. Testing
- Test strategy mix (unit / integration / e2e / security / perf)
- Fixture and mock approach
- Coverage targets
- Security test categories
- Performance benchmarks
- CI/CD integration
- Test data management
- Chaos / resilience testing

## 11. Deployment
- Migration / rollout plan
- Feature flags
- Monitoring / alerting thresholds
- Rollback strategy
- Blue/green or canary
- Environment parity
- Infra as code approach

## 12. UI/UX (skip if not applicable)
- Component hierarchy
- State management
- User interaction patterns
- Responsive / accessibility
- Real-time update mechanism
