# PLAN — feature-search

## Phase 1: Foundation

- [ ] **T-001**: Create `search/` package with `__init__.py`
- [ ] **T-002**: Add `Index` dataclass with `documents` field

## Phase 2: Core

- [ ] **T-003**: Implement `Index.add(doc)` — append to documents
- [ ] **T-004**: Implement `Index.query(q)` — return docs whose text contains q

## Phase 3: Integration

- [ ] **T-005**: Add HTTP `GET /search?q=...` endpoint that uses Index
