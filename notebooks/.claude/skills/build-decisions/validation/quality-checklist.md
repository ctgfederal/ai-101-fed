# Quality Checklist — build-decisions

## YAML Metadata
- [ ] `name` matches folder (`build-decisions`)
- [ ] `description` includes Use-when AND Do-NOT-use
- [ ] `version` semver
- [ ] `triggers` ≥ 5 specific phrases
- [ ] `tools` includes `AskUserQuestion`
- [ ] `model` is real

## Required Sections
- [ ] All 8 sections present in order
- [ ] Files lists every file in folder
- [ ] Contract numbered and testable
- [ ] Steps reference scripts by relative path
- [ ] Antipatterns ≥ 5 items

## Deterministic-First Audit
- [ ] State management is in `scripts/state_manager.py`, not LLM prose
- [ ] ID allocation is in `scripts/allocate_ids.py`, not LLM prose
- [ ] Federal mandate lookup is in `scripts/federal_mandates.py`, not embedded in SKILL.md
- [ ] Append rendering is in `scripts/append_decisions.py`, not LLM prose
- [ ] Validation is in `scripts/validate_output.py`, not just a checklist
- [ ] Mandate table is `knowledge/federal-mandates.json`, not inline in SKILL.md
- [ ] Templates are in `templates/`, not inline

## File Integrity
- [ ] Every Files-section file exists
- [ ] Every script has `__main__` and argparse
- [ ] Example exists
- [ ] `validation/quality-checklist.md` exists

## Tests
- [ ] `tests/` exists
- [ ] Each script has unit tests (every branch)
- [ ] Tests do NOT reimplement script logic
- [ ] LLM evals exist
- [ ] Smoke test exists
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific
- [ ] Every D-NNN ID in the appended section is in the contiguous range that `allocate_ids.py` returned
- [ ] Auto-Applied table is present (or explicitly `_(none)_`)
- [ ] Each documented category has at least one decision OR explicit "_(no decisions ...)_"
- [ ] Each user decision has: id, title, decision, priority, alternatives, rationale, tiers
- [ ] Open questions section exists (may be `_(none)_`)
- [ ] State file at `.claude/builds/<feature>/state.json` is updated
- [ ] No D-NNN renumbering across runs
- [ ] No code is written by this skill (decisions only)
