# Specification Compliance Report

## Spec

- PRD: `PRD.md`
- SDD: `SDD.md`

## Repository

`repo`

## Status

**partial**

Some components or requirements have no evidence in the repo. See `## Deviations` for the gaps. Resolve each before declaring done.

## Components

| Component | Name | Expected | Found | Status |
|---|---|---|---|---|
| COMP-001 | SearchService | `src/search/service.py` | `src/search/service.py` | PRESENT |
| COMP-002 | RankingEngine | `src/search/ranking.py` | _(none)_ | MISSING |

## Requirements

| Requirement | Referenced In | Status |
|---|---|---|
| REQ-001 | `src/search/service.py`, `tests/test_search.py` | REFERENCED |
| REQ-002 | _(none)_ | UNREFERENCED |

## Deviations

- **missing-component** (COMP-002) — RankingEngine: no file at src/search/ranking.py
- **unreferenced-requirement** (REQ-002) — REQ-002 not referenced in any source or test file

## Summary

- Components: 1/2 present
- Requirements: 1/2 referenced
- Deviations: 2
