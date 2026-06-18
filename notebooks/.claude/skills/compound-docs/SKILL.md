---
name: compound-docs
version: 2.0.0
description: |
  Capture solved problems as structured, searchable solution files in `.claude/solutions/`. Creates the compounding knowledge flywheel — solve once, apply forever — by writing one markdown file with YAML frontmatter that `/brainstorm`, `/build`, `/specify`, and `/review` automatically grep when working on related code. Use when the user asks to "document this solution", "save this fix", "compound this", or runs `/compound`. Do NOT use for trivial fixes (typos, formatting), for ongoing-investigation notes, or for documenting architecture/design decisions — those belong in ADRs (`architecture-adr-generator`) or steering docs (`steering-docs-creator`).
triggers:
  - "compound this"
  - "document this solution"
  - "save this fix to solutions"
  - "/compound"
  - "add to solutions archive"
  - "capture this in compound docs"
  - "write this up as a solution file"
  - "we should remember how we fixed this"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# compound-docs

Capture a solved problem as one structured markdown file under `.claude/solutions/<category>/`. The file's YAML frontmatter (`title`, `category`, `tags`, `module`, `symptom`, `root_cause`) is what makes it discoverable by future commands.

## Files

### Templates (`templates/`)
- `solution.md.template` — Canonical markdown template for a solution file. Use when assembling the final document. Contains placeholder tokens like `{{TITLE}}`, `{{CATEGORY}}`, `{{TAGS_YAML}}`, `{{SYMPTOM}}`, `{{ROOT_CAUSE}}`.
- `frontmatter.example.yaml` — Example frontmatter showing every required and optional field with sample values.

### Scripts (`scripts/`)
- `validate_frontmatter.py` — Deterministic. Parses a solution markdown file, validates frontmatter against the schema in `knowledge/frontmatter-schema.md`. Args: `--file <path>`. Exit 0 = valid, 1 = invalid (errors on stderr).
- `generate_slug.py` — Deterministic. Given a problem title and date, emits a filename of form `YYYY-MM-DD-<kebab-slug>.md`. Collapses whitespace, strips non-alphanumeric, truncates to 60 chars. Args: `--title <str>` `[--date YYYY-MM-DD]`. Prints filename to stdout.
- `search_solutions.py` — Deterministic. Greps `.claude/solutions/` by `--tag`, `--module`, `--symptom`, or `--category`. Returns matched file paths and matched frontmatter line. Args mutually exclusive (one filter at a time). Exit 0 always; empty result is normal.
- `write_solution.py` — Deterministic. Given a JSON payload of frontmatter + body fields, renders `solution.md.template`, validates the result, and writes to `.claude/solutions/<category>/<slug>.md`. Refuses to overwrite without `--force`. Args: `--payload <path-or-stdin>` `--solutions-root <path>` `[--force]`. Exit 0 = wrote file; prints output path.
- `validate_output.py` — Deterministic. Given an already-written solution file, runs `validate_frontmatter.py` AND checks the body has all required sections (Symptom, Investigation, Root Cause, Solution, Verification, Prevention). Args: `--file <path>`. Exit 0 = pass.

### Knowledge (`knowledge/`)
- `categories.md` — Canonical category list with description of each. Read when classifying a new problem. Categories are folder names under `.claude/solutions/`.
- `frontmatter-schema.md` — Authoritative schema: every required field, every optional field, allowed values for `severity`, format rules for `tags` and `date`. Read by `validate_frontmatter.py` (as docs) and by the LLM when assembling.
- `search-patterns.md` — How `/brainstorm`, `/build`, `/specify`, `/review` actually search this archive. Read when deciding which fields to populate richly.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any solution file produced by this skill.

### Tests (`tests/`)
- `unit/test_validate_frontmatter.py` — Unit tests for frontmatter parsing and schema validation. Covers happy path, missing field, wrong type, malformed YAML, unknown category.
- `unit/test_generate_slug.py` — Unit tests for slug generation. Covers ASCII, unicode, long titles, empty titles, dates.
- `unit/test_search_solutions.py` — Unit tests for the search filter. Builds a fixture archive in `tmp_path` and asserts each filter returns the expected files.
- `unit/test_write_solution.py` — Unit tests for payload validation, template substitution, write semantics, `--force` behavior.
- `integration/test_search_solutions_integration.py` — Runs against the real `.claude/solutions/` (gated by `RUN_INTEGRATION_TESTS=1`). Asserts the script exits 0 against real data.
- `evals/compound_docs_eval.py` — Evals for the LLM extraction step (symptom/root-cause/prevention prose). Three cases: happy (clear conversation), edge (sparse context), adversarial (red-herring noise).
- `smoke/test_e2e.py` — End-to-end: feeds a fixture payload to `write_solution.py`, asserts file written, runs `validate_output.py` against it, exit 0.
- `conftest.py` — Shared pytest fixtures: `tmp_solutions_root`, `valid_payload`, `invalid_payload`.

### Examples (`examples/`)
- `n-plus-one-query/` — A complete worked example: input conversation excerpt, intermediate payload JSON, final solution file at `.claude/solutions/performance-issues/2026-02-14-n-plus-one-brief-generation.md`.

## Contract

Given a solved problem identified in conversation context, produce exactly one markdown file at `.claude/solutions/<category>/<slug>.md` such that:

1. The file path matches `^\.claude/solutions/[a-z-]+/\d{4}-\d{2}-\d{2}-[a-z0-9-]{1,60}\.md$`.
2. YAML frontmatter parses and contains every required field from `knowledge/frontmatter-schema.md` (`title`, `category`, `date`, `tags`, `module`, `symptom`, `root_cause`).
3. `category` is one of the canonical values in `knowledge/categories.md`.
4. The body contains six headed sections in order: `## Symptom`, `## Investigation`, `## Root Cause`, `## Solution`, `## Verification`, `## Prevention`. `## Related` is optional but recommended.
5. `python scripts/validate_output.py --file <path>` exits 0.
6. No other files are created or modified.
7. If a file already exists at the target path, the run fails unless `--force` is passed; previous content is never silently overwritten.

## Knowledge

### What the solutions archive is for
`.claude/solutions/` is grepped automatically by `/brainstorm`, `/build`, `/specify`, and `/review` to surface known fixes for related problems. The point of writing here is **future retrieval** — every field is a hook for `grep`. Vague titles, missing tags, or unclassified categories defeat the whole mechanism.

### Why these six body sections
- **Symptom** — exact error string / observable behavior, so future grep matches work.
- **Investigation** — what was tried *and rejected*, so future you doesn't retry the same dead ends.
- **Root Cause** — the mechanism, not the fix. Separates "what" from "why".
- **Solution** — the working fix with code.
- **Verification** — how to confirm the fix held.
- **Prevention** — tests/lints/patterns that would have caught it.

See `knowledge/frontmatter-schema.md` for field-level details and `knowledge/categories.md` for the category list.

### When NOT to compound
- Typos, formatting, trivial one-liners — git history is enough.
- Open investigations — write when the problem is *solved*.
- Architecture decisions — those go in ADRs, not solutions.

## Steps

1. **Confirm there is a solved problem.** Extract from context: symptom (exact errors), what was tried, what worked, why. If any of these are missing, ask one focused question. If the problem is still open, refuse and tell the user to come back when it's solved.

2. **Search for duplicates.** Run `python scripts/search_solutions.py --tag <primary-tag>` and `--symptom <key-phrase>` against the existing archive. If a hit covers the same root cause, surface it and stop — extending an existing solution is preferred over a duplicate.

3. **Classify the problem.** Read `knowledge/categories.md`. Pick the single best category. If nothing fits, propose adding a new category and stop for user confirmation.

4. **Generate filename.** Run `python scripts/generate_slug.py --title "<title>"`. Use today's date by default.

5. **Assemble payload.** Build a JSON payload with all frontmatter fields plus the six body sections. The LLM writes the prose in Investigation/Root Cause/Solution/Prevention; everything else is mechanical. See `templates/frontmatter.example.yaml` for shape.

6. **Validate frontmatter.** Run `python scripts/validate_frontmatter.py --file <stdin or temp>` against the assembled payload. Fix any errors before continuing.

7. **Write file.** Run `python scripts/write_solution.py --payload <path> --solutions-root <repo>/.claude/solutions/`. Refuse `--force` unless the user explicitly asks to overwrite.

8. **Validate output.** Run `python scripts/validate_output.py --file <output-path>`. Exit 0 required.

9. **Announce.** Print:
   ```
   Solution documented:
     <output-path>
   Category: <category>
   Tags: <tags>

   Auto-referenced by: /brainstorm, /build, /specify, /review.
   Run /memorize to also promote to Claude Memory.
   ```

## Output

A single markdown file at `.claude/solutions/<category>/<slug>.md`, conforming to `templates/solution.md.template`. No other side effects.

Filename pattern: `YYYY-MM-DD-<kebab-slug>.md`
Example: `.claude/solutions/performance-issues/2026-02-14-n-plus-one-brief-generation.md`

## Antipatterns

- **Writing files from sub-agents.** If parallel research helpers are used, they return text only — only `scripts/write_solution.py` ever writes the final file. Multiple writers cause partial-write corruption.
- **Vague titles or missing tags.** "Fixed the bug" is unsearchable. Title must include the *what*; tags must include the technology, the pattern, and the module.
- **Documenting open problems.** If you don't know the root cause yet, you don't have a solution. Wait.
- **Embedding the template in SKILL.md.** The output template lives in `templates/solution.md.template`. Editing prose inline drifts from the schema.
- **Skipping validate_output.py.** A file the validator hasn't seen is not done. Always run it before announcing.
- **Free-form categories.** If you can't pick from `knowledge/categories.md`, propose adding one explicitly — don't invent on the fly.
- **Overwriting without consent.** `--force` requires explicit user direction; a duplicate slug means search the archive first.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0 (LLM extraction quality).
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0 against the real archive.
6. Every item in `validation/quality-checklist.md` is checked.
7. The solution file passes `python scripts/validate_frontmatter.py --file <output>` and the body has all six required sections.

## Examples

- **`examples/n-plus-one-query/`** — Full worked example: input conversation excerpt, the assembled payload JSON, and the final solution file written under `performance-issues/`. Demonstrates: tag granularity, investigation step format, code-fenced solution block, prevention via test.
