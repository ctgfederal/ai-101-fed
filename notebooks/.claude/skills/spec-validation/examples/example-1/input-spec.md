# Product Requirements Document: Feature Search

## Context References

- See `.claude/steering/product.md`.

## Product Overview

Cross-entity search returns results in under 200ms.

## User Stories

- **US-1**: As a brief author, I want to search briefs.

## Functional Requirements

- **REQ-101** (story US-1, Must): WHEN a user submits a query THEN the system SHALL return matching results within 200ms.
- **REQ-102** (story US-1, Should): The system SHALL rank results by relevance.
- See REQ-104 for the full ranking algorithm.

## Success Metrics

p99 latency < 200ms.
