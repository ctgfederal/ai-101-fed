# Quality Checklist — spec-reflexion

## YAML Metadata
- [ ] `name` matches folder
- [ ] `description` includes when-to-use AND do-not-use clauses, ≥80 chars
- [ ] `version` semver
- [ ] `triggers` ≥ 5
- [ ] `tools` listed; only those used in Steps
- [ ] `model` is real

## Required Sections
- [ ] All 8 in order: Files, Contract, Knowledge, Steps, Output, Antipatterns, Validation, Examples
- [ ] Files documents every directory: templates, scripts, knowledge, tests, validation, examples
- [ ] Contract is numbered and testable

## Deterministic-First Audit
- [ ] Learning extraction lives in `extract_learnings.py`, not LLM
- [ ] Local/global classification lives in `classify_learning.py`, not LLM
- [ ] Memory file rendering and index update live in `promote_to_memory.py`, not LLM
- [ ] Output validation lives in `validate_output.py`, not LLM
- [ ] Memory file template lives in `templates/memory-file.md.template`
- [ ] Heuristics are documented in `knowledge/local-vs-global.md`
- [ ] Type definitions live in `knowledge/learning-types.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder under `examples/`
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/spec_reflexion_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Promoted memory file has frontmatter with `name`, `description`, `type`
- [ ] `type` is exactly one of `feedback`, `project`, `reference`, `user`
- [ ] Body is non-empty
- [ ] MEMORY.md has a corresponding bullet pointing at the file's basename
- [ ] No duplicate index entries for the same filename
- [ ] Filename matches `<type>_<slug>.md` convention
