# Quality Checklist — spec-plan-generator

## YAML
- [ ] All 6 fields; description ≥80 chars w/ Use-when AND Do-NOT-use; ≥5 triggers.

## Sections
- [ ] All 8 in order; Files lists every file.

## Deterministic-First
- [ ] Path in `init_plan.py`
- [ ] ID extraction in `extract_ids.py`
- [ ] Allocation in `allocate_task_ids.py`
- [ ] Render + coverage in `write_plan.py`
- [ ] Validation in `validate_output.py`
- [ ] Templates in `templates/`

## File integrity
- [ ] Every Files-section file exists
- [ ] Every script has __main__ + argparse
- [ ] Example exists

## Tests
- [ ] Unit tests for each script
- [ ] LLM evals
- [ ] Smoke
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific
- [ ] PLAN path matches `^\.claude/specs/[a-z][a-z0-9-]+/PLAN\.md$`
- [ ] All 7 body sections in correct order
- [ ] Every task has T-NNN, title, phase, comps, reqs, acceptance, tdd_step
- [ ] Every SDD COMP-NNN is referenced by ≥1 task
- [ ] Every PRD REQ-NNN is covered by ≥1 task
- [ ] Task IDs globally unique across all PLAN.md
- [ ] Phases are: Foundation, Core, Integration, Polish
- [ ] tdd_step values are: red, green, refactor
- [ ] No `[NEEDS CLARIFICATION]` markers
