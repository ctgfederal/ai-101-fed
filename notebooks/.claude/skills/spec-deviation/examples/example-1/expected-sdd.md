# Solution Design Document: Feature Search

## Context

Cross-entity search.

## Components

- **COMP-001**: Query parser.
- **COMP-002**: Result ranker.
- **COMP-003**: Real-time updates over WebSocket.

## Traceability

| PRD | SDD |
|---|---|
| REQ-101 | COMP-003 |
| REQ-102 | COMP-002 |

## Deviations

### DEV-001

- **Date**: 2026-05-08
- **Spec**: feature-search
- **Reason Category**: technical-blocker
- **Original Decision**: REQ-101
- **Status**: proposed
- **Approver**: Josh Schultz

**Description**

REQ-101 specifies real-time updates over WebSockets. The chosen deployment platform (Cloud Run) does not support long-lived persistent connections; WebSocket sessions are dropped on container scale events.

**Proposed Change**

Use Server-Sent Events (SSE) for one-way real-time push, with a polling fallback for clients that need bidirectional updates.

**Impact**

Same user-facing latency profile (~ms-level updates). SSE is broadly supported. PRD success metrics unchanged. Slight added complexity from the polling fallback path.
