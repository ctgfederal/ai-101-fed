# Product Requirements Document: Feature Search

## Context References

- **Personas:** [.claude/steering/product.md#user-personas](../../steering/product.md#user-personas)
- **Constraints:** [.claude/steering/product.md#business-constraints](../../steering/product.md#business-constraints)
- **Metrics Framework:** [.claude/steering/product.md#success-metrics-framework](../../steering/product.md#success-metrics-framework)
- **Current Phase:** [.claude/steering/roadmap.md#current-phase](../../steering/roadmap.md#current-phase)

## Product Overview

### Vision
Cross-entity search across briefs, customers, and notes returns results in under 200ms.

### Problem Statement
Users currently grep across three pages and lose context.

### Value Proposition
Reduces time-to-context from minutes to seconds; raises engagement on existing data.

## Personas

See `.claude/steering/product.md#user-personas`. Primary: Brief Author. Secondary: CSM.

## User Stories

- **US-1**: As a brief author, I want to search briefs by author and topic, so that I can re-use prior work..

## Functional Requirements

- **REQ-101** (story US-1, Must): WHEN a user submits a search query THEN the system SHALL return matching briefs, customers, and notes within 200ms p99.
- **REQ-102** (story US-1, Must): The system SHALL rank results by relevance score and recency.

## MoSCoW Priorities

| Priority | Requirements |
|---|---|
| Must | REQ-101, REQ-102 |
| Should | _(none)_ |
| Could | _(none)_ |
| Won't | _(none)_ |

## Success Metrics

p99 search latency < 200ms; weekly active searchers > 60%; null-result rate < 5%.

## Risks and Constraints

DB failover causes search timeout; mitigation: circuit-break to partial results.

## Open Questions

_(none)_
