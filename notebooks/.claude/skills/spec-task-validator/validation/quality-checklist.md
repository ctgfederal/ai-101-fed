# Quality Checklist — spec-task-validator

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
- [ ] Task parsing lives in `parse_tasks.py`, not LLM
- [ ] Per-task validation lives in `validate_tasks.py`, not LLM
- [ ] Report rendering lives in `write_report.py`, not LLM
- [ ] Report validation lives in `validate_output.py`, not LLM
- [ ] Report layout lives in `templates/task-validation-report.md.template`
- [ ] Schema lives in `knowledge/task-schema.md`
- [ ] Acceptance rubric lives in `knowledge/acceptance-rubric.md`
- [ ] Verdict thresholds live in `knowledge/verdict-thresholds.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_task_validator_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Report has all 5 `##` sections in order: PLAN, Summary, Tasks, Issues, Verdict
- [ ] Every input task has a row in the Tasks table
- [ ] Summary numbers satisfy `ok + warn + fail == total`
- [ ] Verdict is exactly one of: PASS, WARN, FAIL
- [ ] No unsubstituted `{{TOKEN}}` placeholders
- [ ] Every task with status `warn` or `fail` has at least one entry under `## Issues`
- [ ] Per-task statuses match the JSON output of `validate_tasks.py` byte-for-byte
