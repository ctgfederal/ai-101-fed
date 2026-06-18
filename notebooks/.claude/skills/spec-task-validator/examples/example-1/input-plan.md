# Implementation Plan: feature-search

## Context References

- PRD: input-prd.md
- SDD: input-sdd.md

## Phase 1: Foundation

- [ ] T-001 Implement search index loader
  - Load fixture data on module init
  - Memoize until file mtime changes
  _Acceptance:_ test_loader_caches_until_mtime_changes passes
  _Requirements:_ REQ-101
  _Components:_ COMP-001
  _TDD:_ red

## Phase 2: Core

- [ ] T-002 Implement query parser
  - Parse `field:value` syntax
  _Acceptance:_ parser returns AST with one Filter node
  _Requirements:_ REQ-102
  _Components:_ COMP-002

- [ ] T-003 Implement scoring algorithm
  - BM25 with k1=1.2, b=0.75
  _Acceptance:_ should work end to end
  _Requirements:_ REQ-103
  _Components:_ COMP-003
  _TDD:_ green
