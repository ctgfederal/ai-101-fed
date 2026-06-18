# Adr Generator - Reference

## References

- [Link to documentation](url)
- [External resource](url)
- [Proof of concept](url)
- Design document: `.claude/specs/{feature}/design.md`

---

## Revision History

- {YYYY-MM-DD}: Created (Status: Proposed)
```

## ADR Categories and Tags

Use appropriate tags to categorize decisions:

### Architecture Tags
- `architecture` - System architecture decisions
- `scalability` - Scalability considerations
- `performance` - Performance-related decisions
- `security` - Security decisions

### Technology Tags
- `database` - Database choices
- `api` - API design decisions
- `frontend` - Frontend technology/patterns
- `backend` - Backend technology/patterns
- `infrastructure` - Infrastructure choices

### Process Tags
- `testing` - Testing strategy decisions
- `deployment` - Deployment strategy
- `monitoring` - Observability decisions
- `cicd` - CI/CD pipeline decisions

## Decision Significance Criteria

Create an ADR when the decision:

✅ **Structural Impact**
- Changes system architecture significantly
- Affects multiple components or services
- Establishes patterns others will follow

✅ **Long-Term Commitment**
- Difficult or expensive to reverse
- Locks in technology for significant time
- Creates long-term maintenance burden

✅ **Significant Trade-offs**
- Involves difficult trade-offs
- Has both significant pros and cons
- Multiple stakeholders with different priorities

✅ **Risk Management**
- Introduces significant technical risk
- Requires risk mitigation strategy
- Impacts system reliability or security

✅ **Cost Implications**
- Significant development cost
- Ongoing operational cost
- License or service fees

## ADR Status Lifecycle

```
Proposed → Accepted → [Deprecated | Superseded]
```

### Status Definitions

**Proposed**:
- ADR has been written
- Under discussion
- Not yet implemented
- May be modified

**Accepted**:
- Decision has been approved
- Implementation may begin
- Consider this the current approach

**Deprecated**:
- Decision is no longer recommended
- May still be in use in legacy code
- New work should not follow this

**Superseded**:
- Replaced by a newer ADR
- Link to the superseding ADR
- Provides historical context

## Generation Process

### Step 1: Gather Context
Ask clarifying questions if needed:
- What problem are we solving?
- What are the constraints?
- What alternatives exist?
- What are the success criteria?

### Step 2: Research Alternatives
For each alternative:
- Describe the approach
- List pros and cons
- Explain why rejected (if not chosen)

### Step 3: Document Decision
- Clear statement of what was decided
- Why this beats the alternatives
- What this enables or prevents

### Step 4: Analyze Consequences
- What gets easier?
- What gets harder?
- What new capabilities?
- What new constraints?

### Step 5: Implementation Planning
- Migration steps (if applicable)
- Dependencies
- Risks and mitigations
- Timeline considerations

### Step 6: Create File
- Determine next ADR number
- Create file: `architecture/adrs/ADR-{number}-{slug}.md`
- Update `architecture/adrs/README.md` index

## ADR Index Management

`architecture/adrs/README.md` should contain:

```markdown
# Architecture Decision Records (ADRs)

Index of all architecture decisions for this project.

## Active Decisions

| Number | Title | Status | Date | Tags |
|--------|-------|--------|------|------|
| ADR-045 | Payment Gateway Abstraction | Accepted | 2025-10-18 | architecture, api |
| ADR-044 | Database Migration Strategy | Accepted | 2025-10-15 | database, migration |
| ADR-043 | Repository Pattern for Data Access | Accepted | 2025-10-12 | architecture, patterns |

## Deprecated Decisions

| Number | Title | Status | Date | Reason |
|--------|-------|--------|------|--------|
| ADR-012 | Use REST for All APIs | Superseded by ADR-043 | 2025-06-10 | Moving to GraphQL for flexibility |

## By Category

### Architecture
- ADR-045: Payment Gateway Abstraction
- ADR-043: Repository Pattern for Data Access

### Database
- ADR-044: Database Migration Strategy

### API Design
- ADR-045: Payment Gateway Abstraction

## Decision Process

See [ADR template](template.md) for creating new ADRs.
```

## Examples

### Example 1: Database Choice

```markdown
# ADR-023: Use PostgreSQL for Primary Database

**Status**: Accepted
**Date**: 2025-10-18
**Deciders**: Principal Engineer, Backend Team
**Tags**: database, architecture

## Context

We need to choose a primary database for our application that will store:
- User accounts and profiles
- Application data with complex relationships
- Transactional data requiring ACID guarantees
- Potential for JSON/document storage needs

Requirements:
- Strong consistency
- Complex query support
- Good performance at scale (up to 10M users)
- Open-source preferred
- Strong ecosystem and tooling

## Decision

We will use PostgreSQL as our primary database.

## Rationale

1. **ACID Compliance**: Full ACID guarantees for transactional data
2. **Rich Feature Set**: JSON support, full-text search, spatial data, arrays
3. **Mature Ecosystem**: Excellent tools (pgAdmin, monitoring, backups)
4. **Performance**: Proven at scale with proper indexing
5. **Developer Experience**: Well-known, excellent documentation
6. **Cost**: Open-source, no licensing fees

## Alternatives Considered

### Alternative 1: MySQL
**Description**: Popular open-source relational database

**Pros**:
- Very mature and widely adopted
- Excellent replication support
- Simpler setup for basic use cases

**Cons**:
- Less rich feature set than PostgreSQL
- JSON support not as robust
- Full-text search less powerful

**Why Rejected**: PostgreSQL's advanced features (JSON, arrays, full-text search) align better with our needs

### Alternative 2: MongoDB
**Description**: Document-oriented NoSQL database

**Pros**:
- Flexible schema
- Excellent for document storage
- Good horizontal scaling

**Cons**:
- Lacks ACID transactions across documents (historically)
- Weaker consistency guarantees
- Complex joins less efficient

**Why Rejected**: Our data has clear relationships that benefit from relational model. We need strong consistency guarantees.

### Alternative 3: CockroachDB
**Description**: Distributed SQL database with PostgreSQL compatibility

**Pros**:
- PostgreSQL compatible
- Built-in distributed architecture
- Strong consistency at scale

**Cons**:
- Additional complexity
- Learning curve for operations
- Overkill for current scale

**Why Rejected**: Not needed at current scale. Can migrate later if we need distributed SQL.

## Consequences

### Positive Consequences
- Strong data integrity and consistency
- Rich query capabilities for complex reports
- JSON support for flexible data structures
- Excellent tooling and monitoring options
- Large talent pool familiar with PostgreSQL

### Negative Consequences
- Vertical scaling limits (though very high)
- Requires careful index management for performance
- More complex setup than simple document stores

### Neutral Consequences
- Standard SQL knowledge applies
- Similar operational requirements to other RDBMS

## Implementation Notes

**Setup**:
1. Use PostgreSQL 15+ for latest features
2. Set up connection pooling (pgBouncer)
3. Configure proper backup strategy
4. Set up monitoring (pg_stat_statements)

**Dependencies**:
- PostgreSQL 15+
- Connection pooler (pgBouncer)
- Backup solution (pg_dump + WAL archiving)

**Risks**:
- Single point of failure without replication
- **Mitigation**: Set up streaming replication for high availability

## Related Decisions

- ADR-024: Database Replication Strategy (pending)
- ADR-025: Backup and Recovery Strategy (pending)

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Performance Tuning Guide](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## Revision History

- 2025-10-18: Created (Status: Accepted)
```

### Example 2: API Design Pattern

```markdown
# ADR-031: RESTful API Design with HATEOAS

**Status**: Accepted
**Date**: 2025-10-18
**Deciders**: Principal Engineer, API Team
**Tags**: api, architecture, patterns

## Context

We're building a public-facing API that will be consumed by:
- Our own frontend applications
- Third-party integrations
- Mobile applications

We need to establish consistent API design patterns that:
- Are intuitive for developers
- Support evolution without breaking changes
- Provide good developer experience
- Scale to hundreds of endpoints

## Decision

We will design our REST APIs following RESTful principles with HATEOAS (Hypermedia as the Engine of Application State) for resource navigation.

Key standards:
- Resource-oriented URLs
- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Consistent error responses
- Hypermedia links for resource navigation
- Versioning via URL path (/v1/, /v2/)

## Rationale

1. **Industry Standard**: REST is well-understood and widely adopted
2. **HTTP Semantic**: Leverages HTTP methods meaningfully
3. **Caching**: HTTP caching works naturally
4. **Tooling**: Excellent tooling support (Postman, OpenAPI, etc.)
5. **Evolution**: HATEOAS enables API evolution without breaking clients
6. **Documentation**: Easy to document with OpenAPI/Swagger

## Alternatives Considered

### Alternative 1: GraphQL
**Description**: Query language for APIs with single endpoint

**Pros**:
- Clients request exactly what they need
- Strong typing
- No over-fetching
- Single endpoint

**Cons**:
- More complex to implement
- Caching is harder
- Learning curve for consumers
- Less mature tooling

**Why Rejected**: Added complexity not justified for our current needs. May reconsider for specific use cases.

### Alternative 2: RPC-style APIs
**Description**: Remote Procedure Call style (like gRPC)

**Pros**:
- Very efficient
- Strong typing (Protocol Buffers)
- Good for microservices

**Cons**:
- Less intuitive for HTTP developers
- Requires code generation
- Not as web-friendly

**Why Rejected**: We need web-friendly APIs accessible from browsers. gRPC better for service-to-service.

## Consequences

### Positive Consequences
- Intuitive API design
- Excellent HTTP caching support
- Standard tooling works out of box
- Easy to document
- Clients can navigate resources via links

### Negative Consequences
- Multiple requests may be needed for complex operations
- Over-fetching possible if not careful
- HATEOAS adds payload size

### Neutral Consequences
- Standard REST patterns well-known by developers
- OpenAPI specification can be generated

## Implementation Notes

**API Standards**:
```
# Resource URLs
GET    /api/v1/users           # List users
GET    /api/v1/users/{id}      # Get user
POST   /api/v1/users           # Create user
PUT    /api/v1/users/{id}      # Update user
PATCH  /api/v1/users/{id}      # Partial update
DELETE /api/v1/users/{id}      # Delete user

# Nested resources
GET    /api/v1/users/{id}/orders

# HATEOAS example response
{
  "id": "123",
  "name": "John Doe",
  "_links": {
    "self": "/api/v1/users/123",
    "orders": "/api/v1/users/123/orders",
    "profile": "/api/v1/users/123/profile"
  }
}
```

**Error Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

**Dependencies**:
- OpenAPI spec generation
- API documentation tool (Swagger UI)

**Risks**:
- Clients not following HATEOAS links
- **Mitigation**: Good documentation and examples

## Related Decisions

- ADR-032: API Versioning Strategy
- ADR-033: API Authentication (JWT)
- ADR-034: API Rate Limiting

## References

- [RESTful API Design](https://restfulapi.net/)
- [HATEOAS Explained](https://en.wikipedia.org/wiki/HATEOAS)
- [OpenAPI Specification](https://swagger.io/specification/)

---

## Revision History

- 2025-10-18: Created (Status: Accepted)
```

## Quality Checklist

Before finalizing an ADR:
- [ ] Title is clear and concise
- [ ] Context explains the problem well
- [ ] Decision is explicitly stated
- [ ] At least 2-3 alternatives documented
- [ ] Pros and cons for each alternative
- [ ] Clear rationale for chosen approach
- [ ] Consequences documented (positive and negative)
- [ ] Implementation notes included
- [ ] Related ADRs linked
- [ ] Proper tags added
- [ ] ADR index updated

## File Naming Convention

Format: `ADR-{number}-{kebab-case-title}.md`

Examples:
- `ADR-001-database-choice.md`
- `ADR-023-use-postgresql.md`
- `ADR-031-restful-api-design.md`
- `ADR-045-payment-gateway-abstraction.md`

## Remember

ADRs are historical documents. They capture decisions as they were made with the context at that time. Don't update old ADRs to reflect current thinking - create new ADRs that supersede them instead. This preserves the decision history and reasoning.