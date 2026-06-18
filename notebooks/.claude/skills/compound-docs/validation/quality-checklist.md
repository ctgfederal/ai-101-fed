# Quality Checklist — compound-docs

Walk through every item before declaring a solution file done.

## YAML Metadata
- [ ] `name` matches the folder name (`compound-docs`)
- [ ] `description` is one paragraph and includes both "Use when" and "Do NOT use for"
- [ ] `version` is set (semver)
- [ ] `triggers` has at least 5 specific phrases
- [ ] `tools` lists only tools actually used in Steps
- [ ] `model` is a real Claude model identifier

## Required Sections
- [ ] Files section lists every file in the folder
- [ ] Contract section is numbered and testable
- [ ] Knowledge section is present with pointers to `knowledge/`
- [ ] Steps are numbered and reference scripts/files by relative path
- [ ] Output section describes file path and structure concretely
- [ ] Antipatterns section has at least 3 items
- [ ] Validation section references this checklist
- [ ] Examples section points to at least one worked example

## Deterministic-First Audit
- [ ] Every step that COULD be a script IS a script (validate, slug, search, write, validate_output)
- [ ] No frontmatter assembly logic embedded in SKILL.md prose
- [ ] Output template lives in `templates/solution.md.template`, not inline
- [ ] Category list lives in `knowledge/categories.md`, not inline

## File Integrity
- [ ] Every file mentioned in Files section actually exists
- [ ] Every script in `scripts/` has `if __name__ == "__main__"` and argparse
- [ ] At least one example exists under `examples/`
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] `tests/` directory exists
- [ ] Every script in `scripts/` has a corresponding `tests/unit/test_<script>.py`
- [ ] Unit tests cover happy + edge + error paths for each script
- [ ] Tests do NOT reimplement the script's logic — they hard-code expected values
- [ ] LLM-extraction evals exist (happy / edge / adversarial)
- [ ] End-to-end smoke test exists and passes
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific Checks
- [ ] Output filename matches `^\d{4}-\d{2}-\d{2}-[a-z0-9-]{1,60}\.md$`
- [ ] Output path is `.claude/solutions/<category>/<filename>`
- [ ] `category` is one of the 12 canonical categories in `knowledge/categories.md`
- [ ] `tags` has 2–8 items; each is lowercase, no spaces
- [ ] `symptom` quotes the actual error string when one exists
- [ ] Body contains all six required sections in order: Symptom → Investigation → Root Cause → Solution → Verification → Prevention
- [ ] Code blocks are language-fenced (```ruby, ```sql, etc.)
- [ ] No file other than the new solution file is created or modified

## Capability Check
- [ ] This solution does not duplicate an existing entry under `.claude/solutions/` (verified via `search_solutions.py --tag` and `--symptom`)
- [ ] The problem is *solved* — not in active investigation
