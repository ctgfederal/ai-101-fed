# Quality Checklist — spec-prd-generator

## YAML Metadata
- [ ] `name` matches folder
- [ ] `description` includes Use-when AND Do-NOT-use, ≥80 chars
- [ ] `version` semver
- [ ] `triggers` ≥ 5
- [ ] `tools` listed; only those used in Steps
- [ ] `model` is real

## Required Sections
- [ ] All 8 in order
- [ ] Files lists every file
- [ ] Contract numbered, testable

## Deterministic-First Audit
- [ ] Path computation in `init_prd.py`, not LLM
- [ ] ID allocation in `allocate_req_ids.py`, not LLM
- [ ] Render in `write_prd.py`, not LLM
- [ ] Validation in `validate_output.py`, not LLM
- [ ] Templates in `templates/`
- [ ] Schema reference in `knowledge/prd-schema.md`

## File Integrity
- [ ] Every Files-section file exists
- [ ] Every script has `__main__` and argparse
- [ ] Example exists
- [ ] Quality checklist exists

## Tests
- [ ] Each script has unit tests
- [ ] LLM evals exist
- [ ] Smoke test exists
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific
- [ ] PRD path matches `^\.claude/specs/[a-z][a-z0-9-]+/PRD\.md$`
- [ ] All 9 body sections in correct order
- [ ] Every requirement has REQ-NNN, EARS pattern, MoSCoW priority
- [ ] REQ-NNN IDs are contiguous in the allocated batch
- [ ] No `[NEEDS CLARIFICATION]` markers
- [ ] Steering anchor links present
- [ ] MoSCoW values are one of: Must, Should, Could, Won't
- [ ] Requirements reference user-story IDs that exist in the PRD
