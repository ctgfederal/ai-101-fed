# Quality Checklist — spec-sdd-generator

## YAML Metadata
- [ ] All 6 fields present
- [ ] Description has Use-when AND Do-NOT-use, ≥80 chars
- [ ] Triggers ≥ 5

## Required Sections
- [ ] All 8 in order
- [ ] Files lists every file

## Deterministic-First Audit
- [ ] Path computation in `init_sdd.py`
- [ ] REQ extraction in `extract_req_ids.py`
- [ ] Render + traceability validation in `write_sdd.py`
- [ ] Output validation in `validate_output.py`
- [ ] Templates in `templates/`
- [ ] Schema in `knowledge/sdd-schema.md`

## File Integrity
- [ ] Every Files-section file exists
- [ ] Every script has __main__ + argparse
- [ ] Example exists

## Tests
- [ ] Each script has unit tests
- [ ] LLM evals exist
- [ ] Smoke test exists
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific
- [ ] SDD path matches `^\.claude/specs/[a-z][a-z0-9-]+/SDD\.md$`
- [ ] All 10 body sections in order
- [ ] Every component has `COMP-NNN` ID, name, responsibility, dependencies, contract (inputs+outputs)
- [ ] No duplicate `COMP-NNN` IDs within this SDD
- [ ] Traceability table covers EVERY PRD `REQ-NNN`
- [ ] Every traceability target references an existing `COMP-NNN`
- [ ] Steering anchor links present
- [ ] No `[NEEDS CLARIFICATION]` markers
- [ ] Alternatives section is non-empty (forces honest tradeoff)
