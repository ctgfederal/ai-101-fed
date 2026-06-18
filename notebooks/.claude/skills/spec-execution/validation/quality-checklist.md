# Quality Checklist — spec-execution

## YAML Metadata
- [ ] `name` matches folder
- [ ] `description` includes Use-when AND Do-NOT-use, ≥80 chars
- [ ] `version` semver
- [ ] `triggers` ≥ 5
- [ ] `tools` listed; only those used in Steps
- [ ] `model` is real

## Required Sections
- [ ] All 8 in order: Files, Contract, Knowledge, Steps, Output, Antipatterns, Validation, Examples
- [ ] Files documents every directory: templates, scripts, knowledge, validation, tests, examples
- [ ] Contract is numbered and testable

## Deterministic-First Audit
- [ ] State init/read/update lives in `state_manager.py`, not LLM
- [ ] Next-task selection lives in `next_task.py`, not LLM
- [ ] TDD-step recording lives in `record_tdd_step.py`, not LLM
- [ ] State validation lives in `validate_output.py`, not LLM
- [ ] State schema lives in `knowledge/state-schema.md`
- [ ] TDD protocol lives in `knowledge/tdd-loop.md`
- [ ] Recovery protocol lives in `knowledge/interruption-recovery.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_execution_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## State-Specific
- [ ] `feature`, `current_task`, `tasks`, `task_order`, `meta` keys present in every valid state
- [ ] Every task has: description, status, history, blockers, depends_on
- [ ] Every status is one of: pending, in-progress, done, blocked, failed
- [ ] history entries are append-only (never edit prior entries)
- [ ] task_order matches keys of tasks (no missing, no extras)
- [ ] `init` only succeeds when PLAN.md exists and contains at least one T-NNN
- [ ] `next_task.py` honors `depends_on` (returns nothing if a dep is not done)
