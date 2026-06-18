# Quality Checklist — plan-deepener

## YAML Metadata
- [ ] `name` matches folder (`plan-deepener`)
- [ ] `description` includes Use-when AND Do-NOT-use
- [ ] `version` semver
- [ ] `triggers` ≥ 5
- [ ] `tools` includes `Task`
- [ ] `model` is real

## Required Sections
- [ ] All 8 in order
- [ ] Files lists every file
- [ ] Contract numbered
- [ ] Antipatterns ≥ 5

## Deterministic-First Audit
- [ ] Section parsing is in `scripts/parse_target.py`, not LLM prose
- [ ] Skill matching is in `scripts/match_skills.py`, not LLM prose
- [ ] Document merge is in `scripts/merge_research.py`, not LLM prose
- [ ] Output validation is in `scripts/validate_output.py`
- [ ] Templates live in `templates/`

## File Integrity
- [ ] Every Files-section file exists
- [ ] Every script has `__main__` and argparse
- [ ] Example exists
- [ ] `validation/quality-checklist.md` exists

## Tests
- [ ] Each script has unit tests (every branch)
- [ ] Tests don't reimplement script logic
- [ ] LLM evals exist
- [ ] Smoke test exists
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific
- [ ] `## Deepening Summary` block at top of deepened document
- [ ] Every section that has findings has `### Research Insights`
- [ ] Every Research Insights block has all 5 subsections (Solutions, Best Practices, Edge Cases, Performance, References)
- [ ] Original section bodies are byte-identical to baseline
- [ ] Idempotent: re-running without `--force` skips already-deepened sections
- [ ] Solutions archive was searched before parallel research
- [ ] Each best-practice has at least one citation
