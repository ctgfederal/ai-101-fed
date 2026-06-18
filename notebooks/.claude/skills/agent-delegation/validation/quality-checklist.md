# Quality Checklist — agent-delegation

## YAML Metadata
- [ ] `name` matches the folder name (`agent-delegation`)
- [ ] `description` includes both "Use when" and "Do NOT use for", ≥80 chars
- [ ] `version` is set (semver)
- [ ] `triggers` has at least 5 specific phrases
- [ ] `tools` lists only tools actually used in Steps
- [ ] `model` is a real Claude model identifier

## Required Sections
- [ ] All 8 in order: Files, Contract, Knowledge, Steps, Output, Antipatterns, Validation, Examples
- [ ] Files lists every file in the folder
- [ ] Contract is numbered and testable
- [ ] Steps reference scripts by relative path
- [ ] Output describes file path and structure concretely
- [ ] Antipatterns has at least 3 items

## Deterministic-First Audit
- [ ] Payload validation in `validate_delegation.py`, not LLM
- [ ] Prompt rendering in `render_prompt.py`, not LLM
- [ ] Collision detection in `check_collisions.py`, not LLM
- [ ] Output validation in `validate_output.py`, not LLM
- [ ] Prompt template lives in `templates/delegation-prompt.md.template`, not inline
- [ ] FOCUS/EXCLUDE rules live in `knowledge/focus-exclude-rules.md`, not inline

## File Integrity
- [ ] Every file mentioned in Files section exists
- [ ] Every script in `scripts/` has `if __name__ == "__main__"` and argparse
- [ ] At least one example exists under `examples/`
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] `tests/` directory exists
- [ ] Every script has a corresponding `tests/unit/test_<script>.py`
- [ ] Unit tests cover happy + edge + error paths
- [ ] LLM-extraction evals exist (happy / edge / adversarial)
- [ ] End-to-end smoke test exists and passes
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific Checks
- [ ] Rendered prompt has all 5 required sections in order: FOCUS, EXCLUDE, TASK, SUCCESS, RETURN
- [ ] FOCUS list has at least one entry
- [ ] SUCCESS list has at least one entry
- [ ] No path appears in both FOCUS and EXCLUDE
- [ ] `validate_output.py` exits 0 on the rendered prompt
- [ ] For parallel launches, `check_collisions.py` reports `safe: true`

## Capability Check
- [ ] The skill never writes code on behalf of the delegated agent — it only emits the prompt.
- [ ] `--force` is required to overwrite an existing prompt path.
