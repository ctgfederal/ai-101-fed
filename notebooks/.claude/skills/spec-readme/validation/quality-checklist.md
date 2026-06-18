# Quality Checklist — spec-readme

## YAML Metadata
- [ ] `name` matches folder name (`spec-readme`)
- [ ] `description` includes both "use when" and "do not use" clauses, ≥80 chars
- [ ] `version` is semver
- [ ] `triggers` lists ≥ 5 entries
- [ ] `tools` lists only tools used in Steps
- [ ] `model` is real (`claude-sonnet-4-6`)

## Required Sections
- [ ] All 8 in order: Files, Contract, Knowledge, Steps, Output, Antipatterns, Validation, Examples
- [ ] Files documents every directory: templates, scripts, knowledge, validation, tests, examples
- [ ] Contract is numbered and testable

## Deterministic-First Audit
- [ ] README initialization lives in `init_readme.py`, not LLM
- [ ] Status updates live in `update_status.py`, not LLM
- [ ] Phase-note appending lives in `append_phase_note.py`, not LLM
- [ ] README validation lives in `validate_output.py`, not LLM
- [ ] README layout lives in `templates/readme.md.template`
- [ ] Schema (sections, statuses, link rules) lives in `knowledge/readme-schema.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder under `examples/`
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/` (`test_init_readme.py`, `test_update_status.py`, `test_append_phase_note.py`, `test_validate_output.py`)
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_readme_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] README has all 6 `##` sections in order
- [ ] Status table has exactly three rows (PRD, SDD, PLAN)
- [ ] Each status is one of: draft, approved, deprecated
- [ ] Steering links use relative paths under `../../steering/`
- [ ] No unsubstituted `{{TOKEN}}` placeholders
- [ ] Phase notes (if any) are in monotonic ascending order
- [ ] No phase number appears twice
