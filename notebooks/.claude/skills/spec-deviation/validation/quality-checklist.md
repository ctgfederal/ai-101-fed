# Quality Checklist — spec-deviation

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
- [ ] Payload validation lives in `validate_deviation.py`, not LLM
- [ ] ID allocation lives in `allocate_deviation_id.py`, not LLM
- [ ] Block rendering / appending lives in `append_deviation.py`, not LLM
- [ ] Output validation lives in `validate_output.py`, not LLM
- [ ] Block layout lives in `templates/deviation-block.md.template`
- [ ] Schema lives in `knowledge/deviation-schema.md`
- [ ] Workflow lives in `knowledge/approval-workflow.md`
- [ ] Guardrails live in `knowledge/when-to-deviate.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_deviation_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Every appended block starts with `### DEV-NNN`
- [ ] Every block has Date, Spec, Reason Category, Original Decision, Status, Approver bullets
- [ ] Every block has Description, Proposed Change, Impact prose subheadings
- [ ] Every `status` is one of: proposed, approved, rejected
- [ ] Every `reason_category` is one of the five enums
- [ ] No two `DEV-NNN` IDs collide in the same SDD
- [ ] No unsubstituted `{{TOKEN}}` placeholders
