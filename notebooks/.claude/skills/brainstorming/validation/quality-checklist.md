# Quality Checklist — brainstorming

## YAML Metadata
- [ ] `name` matches the folder name (`brainstorming`)
- [ ] `description` is one paragraph and includes both "Use when" and "Do NOT use for"
- [ ] `version` is set (semver)
- [ ] `triggers` has at least 5 specific phrases
- [ ] `tools` includes `AskUserQuestion`
- [ ] `model` is a real Claude model identifier

## Required Sections
- [ ] Files section lists every file in the folder
- [ ] Contract section is numbered and testable
- [ ] Knowledge section pointers to `knowledge/`
- [ ] Steps numbered, reference scripts by relative path
- [ ] Output section concrete (path pattern, sections)
- [ ] Antipatterns ≥ 3 items
- [ ] Validation references this checklist
- [ ] Examples points to at least one worked example

## Deterministic-First Audit
- [ ] Slug + path computation is in `scripts/init_brainstorm.py`, not LLM prose
- [ ] File write is in `scripts/write_brainstorm.py`, not LLM prose
- [ ] Output validation is in `scripts/validate_output.py`, not a checklist alone
- [ ] Output template lives in `templates/`, not inline

## File Integrity
- [ ] Every file mentioned in Files exists
- [ ] Every script has `if __name__ == "__main__"` and argparse
- [ ] At least one example exists
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] `tests/` directory exists
- [ ] Each script has a corresponding `tests/unit/test_<script>.py`
- [ ] Unit tests cover happy + edge + error paths
- [ ] Tests do NOT reimplement the script's logic
- [ ] LLM evals exist (clarity assessment classes)
- [ ] End-to-end smoke test exists and passes
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific Checks
- [ ] Output filename matches `^\d{4}-\d{2}-\d{2}-[a-z0-9-]{1,60}\.md$`
- [ ] Output path is `.claude/brainstorms/<filename>`
- [ ] Body has all 8 required sections in order
- [ ] No design or technical decisions are recorded
- [ ] `Scope: Out` is non-empty
- [ ] No section exceeds 300 words
- [ ] Solutions archive was searched before exploring (see Related Solutions)

## Capability Check
- [ ] No duplication with `/build` (no design decisions captured here)
- [ ] No duplication with `/specify` (no formal requirements captured here)
