# Quality Checklist — swarm-delegation

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
- [ ] Schema validation lives in `validate_handoff.py`, not LLM
- [ ] Prompt rendering lives in `render_handoff.py`, not LLM
- [ ] Chain checking lives in `check_chain.py`, not LLM
- [ ] Output validation lives in `validate_output.py`, not LLM
- [ ] Prompt layout lives in `templates/handoff.md.template`
- [ ] Schema lives in `knowledge/handoff-schema.md`
- [ ] Patterns live in `knowledge/chain-patterns.md`
- [ ] Failure modes live in `knowledge/failure-modes.md`

## File Integrity
- [ ] Every Files-section path exists on disk
- [ ] Every script has `if __name__ == "__main__":` and argparse
- [ ] At least one example folder
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] Each script has unit tests in `tests/unit/`
- [ ] Smoke test in `tests/smoke/test_e2e.py` runs the full pipeline
- [ ] Eval shape test in `tests/evals/swarm_delegation_eval.py`
- [ ] Integration placeholder in `tests/integration/`
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] Rendered prompt has all 6 required `##` sections in order: FROM, TO, TASK, CONTEXT, SUCCESS, RETURN
- [ ] Optional `## DEADLINE` only present when payload provides one
- [ ] No unsubstituted `{{TOKEN}}` placeholders
- [ ] `validate_handoff.py` returns `valid: true` for the source payload
- [ ] `validate_output.py` exits 0 for the rendered prompt
- [ ] If multi-step, `check_chain.py` exits 0 (no cycles, no type mismatches)
