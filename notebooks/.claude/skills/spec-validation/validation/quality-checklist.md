# Quality Checklist — spec-validation

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
- [ ] Sub-score computation lives in `score_3cs.py`, not LLM
- [ ] Report rendering lives in `write_report.py`, not LLM
- [ ] Report validation lives in `validate_output.py`, not LLM
- [ ] Report layout lives in `templates/3cs-report.md.template`
- [ ] Rubric lives in `knowledge/3cs-rubric.md`
- [ ] Thresholds live in `knowledge/score-thresholds.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_validation_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Report has all 7 `##` sections in order
- [ ] Each of Completeness, Consistency, Correctness, Overall is an integer in [0, 10]
- [ ] Verdict is exactly one of: PASS, WARN, FAIL
- [ ] No unsubstituted `{{TOKEN}}` placeholders
- [ ] Every sub-score < 10 has at least one matching issue under `## Issues`
- [ ] Sub-scores match the JSON output of `score_3cs.py` byte-for-byte
