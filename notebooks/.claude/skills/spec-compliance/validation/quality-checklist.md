# Quality Checklist — spec-compliance

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
- [ ] Spec parsing lives in `parse_spec.py`, not LLM
- [ ] Compliance computation lives in `check_compliance.py`, not LLM
- [ ] Report rendering lives in `write_report.py`, not LLM
- [ ] Report validation lives in `validate_output.py`, not LLM
- [ ] Report layout lives in `templates/compliance-report.md.template`
- [ ] Rubric lives in `knowledge/compliance-rubric.md`
- [ ] Deviation taxonomy lives in `knowledge/deviation-types.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_compliance_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Report has all 7 `##` sections in order
- [ ] Status is exactly one of: compliant, partial, non-compliant
- [ ] No unsubstituted `{{TOKEN}}` placeholders
- [ ] Every COMP-ID from the SDD appears in the Components table
- [ ] Every REQ-ID from the PRD appears in the Requirements table
- [ ] Status, components-table, and requirements-table match the JSON output of `check_compliance.py` byte-for-byte
