# Specification: Feature Search

**Feature:** `feature-search`
**Created:** 2026-05-08

## Status

| Doc | Status | Last Update |
|---|---|---|
| PRD | approved | 2026-05-08 |
| SDD | draft | 2026-05-08 |
| PLAN | draft | 2026-05-08 |

## Steering References

- Product: [`../../steering/product.md`](../../steering/product.md)
- Tech: [`../../steering/tech.md`](../../steering/tech.md)
- Structure: [`../../steering/structure.md`](../../steering/structure.md)
- Roadmap: [`../../steering/roadmap.md`](../../steering/roadmap.md)

## Decision Log Snippets

Cross-feature decisions referenced from [`../../decisions-log.md`](../../decisions-log.md):

_(none yet — link decisions as `[D-NNN](../../decisions-log.md#d-nnn)` when they apply to this feature)_

## Phase Notes

### Phase 1: Foundation

_Recorded 2026-05-08_

Spec under-specified the caching layer. Picked Redis with 60s TTL because the
search index update cadence is ~30s and we wanted at least one cache hit per
generation. Added one open question for SDD update.

## Learnings

Feature-specific insights captured here. Global / reusable patterns go to memory via `/memorize`.

_(none yet)_

## Open Questions

_(none yet)_
