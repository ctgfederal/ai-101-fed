# Quality Checklist — steering-docs-creator

## YAML Metadata
- [ ] `name` matches folder
- [ ] `description` includes when-to-use AND do-not-use, ≥80 chars
- [ ] `version` semver
- [ ] `triggers` ≥ 5
- [ ] `tools` listed; only those used in Steps
- [ ] `model` is real

## Required Sections
- [ ] All 8 in order: Files, Contract, Knowledge, Steps, Output, Antipatterns, Validation, Examples
- [ ] Files lists every templates / scripts / knowledge / validation / examples / tests file
- [ ] Contract numbered, testable

## Deterministic-First Audit
- [ ] Scaffolding in `init_steering.py`, not LLM
- [ ] Section replacement in `update_doc.py`, not LLM
- [ ] Validation in `validate_steering.py` and `validate_output.py`, not LLM
- [ ] Templates live in `templates/` (not embedded in SKILL.md)
- [ ] Schema reference in `knowledge/steering-schema.md`
- [ ] Anchor contract documented in `knowledge/usage-by-other-skills.md`

## File Integrity
- [ ] Every Files-section file exists
- [ ] Every script has `__main__` and argparse
- [ ] Example exists at `examples/example-1/`
- [ ] Quality checklist exists (this file)

## Tests
- [ ] Each script has a unit test
- [ ] LLM evals exist
- [ ] Smoke test exists
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] All four files exist at `.claude/steering/`
- [ ] Each file has its required sections in the order set by `knowledge/steering-schema.md`
- [ ] No `[NEEDS CLARIFICATION]` markers in shipped docs
- [ ] `validate_steering.py --steering-root .claude/steering` exits 0
- [ ] `validate_output.py` exits 0 for each of the four docs
- [ ] `init_steering.py` is idempotent (re-run without `--force` is a no-op exit 0)
- [ ] `update_doc.py` preserves surrounding sections and the heading byte-for-byte
