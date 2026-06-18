# Quality Checklist — auto-documentation

Walk through every item before declaring an auto-doc file done.

## YAML Metadata
- [ ] `name` matches the folder name (`auto-documentation`)
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
- [ ] Every step that COULD be a script IS a script (categorize, dedupe, write, validate_output)
- [ ] No frontmatter assembly logic embedded in SKILL.md prose
- [ ] Output template lives in `templates/auto-doc.md.template`, not inline
- [ ] Category list lives in `knowledge/categories.md`, not inline
- [ ] Dedup rules live in `knowledge/dedup-rules.md`, not inline

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
- [ ] Output path is `.claude/docs/auto/<category>/<filename>`
- [ ] `category` is one of the 4 canonical categories in `knowledge/categories.md`
- [ ] `tags` has 2–8 items; each is lowercase, no spaces
- [ ] `scope` names a specific class / route / module — not "the codebase"
- [ ] `source` is re-verifiable (PR, conversation, external doc)
- [ ] Body contains all four required sections in order: Description → Why → Examples → Related
- [ ] Code blocks are language-fenced (```ruby, ```sql, etc.)
- [ ] No file other than the new auto-doc is created or modified

## Capability Check
- [ ] This auto-doc does not duplicate an existing entry under `.claude/docs/auto/` (verified via `dedupe.py`)
- [ ] The insight is *settled* — not an open question
- [ ] The insight does not belong in a different skill (compound-docs for solved bugs, ADR for architecture decisions, steering-docs for project context)
