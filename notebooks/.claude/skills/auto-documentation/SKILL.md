---
name: auto-documentation
version: 2.0.0
description: |
  Capture business rules, technical patterns, and service-interface contracts discovered during analysis or implementation as structured markdown files under `.claude/docs/auto/<category>/`. Each file has YAML frontmatter (`title`, `category`, `tags`, `scope`, `source`, `date`) so future commands can grep them. Use when a discovered insight is reusable, non-obvious, and worth preserving — e.g., "document this business rule", "add this pattern to the docs", "save this API contract", "we just learned how Stripe's webhook timing works", or when running `/document-this`. Do NOT use for solved bug fixes (use `compound-docs`), architecture decisions (use `architecture-adr-generator`), project-wide context (use `steering-docs-creator`), spec/PRD requirements, or trivial inline comments — those belong elsewhere.
triggers:
  - "/document-this"
  - "auto document"
  - "document this business rule"
  - "document this pattern"
  - "document this interface"
  - "save this to auto docs"
  - "add this to the docs archive"
  - "capture this rule for future reference"
  - "we should write this down"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# auto-documentation

Capture a discovered insight as one structured markdown file under `.claude/docs/auto/<category>/`. Frontmatter (`title`, `category`, `tags`, `scope`, `source`, `date`) is what makes the file searchable. Categories are mechanical: `business-rule`, `technical-pattern`, `service-interface`, `domain-rule`. Deduplication runs before any write.

## Files

### Templates (`templates/`)
- `auto-doc.md.template` — Canonical markdown template for an auto-doc. Placeholders: `{{TITLE}}`, `{{CATEGORY}}`, `{{DATE}}`, `{{TAGS_YAML}}`, `{{SCOPE}}`, `{{SOURCE}}`, `{{DESCRIPTION_BODY}}`, `{{WHY_BODY}}`, `{{EXAMPLES_BODY}}`, `{{RELATED_BODY}}`. Used by `write_doc.py`.
- `payload.example.json` — Example JSON payload showing the exact shape `write_doc.py` consumes.

### Scripts (`scripts/`)
- `categorize.py` — Deterministic. Heuristic classifier for a free-text insight. Emits exactly one of `business-rule`, `technical-pattern`, `service-interface`, `domain-rule`. Args: `--text <str>`. Prints the category to stdout. Exit 0.
- `dedupe.py` — Deterministic. Given a candidate doc payload and an existing docs root, returns whether the new doc duplicates an existing one (similar title, overlapping tags, same scope hash). Args: `--payload <path>` `--docs-root <path>`. Prints JSON `{is_duplicate: bool, similar: [paths]}` to stdout. Exit 0.
- `write_doc.py` — Deterministic. Renders `auto-doc.md.template` from a JSON payload and writes the file to `.claude/docs/auto/<category>/<slug>.md`. Refuses to overwrite without `--force`. Args: `--payload <path-or-stdin>` `--docs-root <path>` `[--force]`. Exit 0 = wrote file (path printed to stdout).
- `validate_output.py` — Deterministic. Validates a written auto-doc: frontmatter has every required field, category is valid, body has the four required sections (`Description`, `Why`, `Examples`, `Related`) in order. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `categories.md` — The four categories with descriptions and what fits each. Read when classifying a new insight.
- `dedup-rules.md` — How similarity is measured (title overlap, tag intersection, scope hash) and when to merge vs create new. Read by humans extending the dedup rules.
- `frontmatter-schema.md` — Authoritative frontmatter schema: required fields, optional fields, format rules.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any auto-doc this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `tmp_docs_root`, `valid_payload`, `invalid_payload`.
- `unit/test_categorize.py` — Unit tests for the heuristic classifier across all four categories plus ambiguous text.
- `unit/test_dedupe.py` — Unit tests for the deduplicator: identical title, overlapping tags, scope-hash collision, no match.
- `unit/test_write_doc.py` — Unit tests for payload validation, template substitution, write semantics, `--force` behavior.
- `unit/test_validate_output.py` — Unit tests for the doc validator: happy path, missing section, bad category, malformed frontmatter.
- `integration/test_auto_documentation_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/auto_documentation_eval.py` — Three-case eval for the LLM extraction step (clear insight, sparse context, adversarial noise).
- `smoke/test_e2e.py` — End-to-end: `categorize.py` → `dedupe.py` → `write_doc.py` → `validate_output.py` against a fixture payload.

### Examples (`examples/`)
- `example-1/` — Worked example: a free-text insight (`input.txt`), the assembled payload (`payload.json`), and the rendered doc (`expected-output.md`). Demonstrates the `business-rule` path end-to-end.

## Contract

Given a discovered insight and a docs root, produce exactly one markdown file at `.claude/docs/auto/<category>/<slug>.md` such that:

1. The file path matches `^\.claude/docs/auto/(business-rule|technical-pattern|service-interface|domain-rule)/\d{4}-\d{2}-\d{2}-[a-z0-9-]{1,60}\.md$`.
2. YAML frontmatter parses and contains every required field: `title`, `category`, `date`, `tags`, `scope`, `source`.
3. `category` is one of the four canonical values.
4. The body contains four headed sections in order: `## Description`, `## Why`, `## Examples`, `## Related`.
5. `python scripts/validate_output.py --file <path>` exits 0.
6. Before writing, `dedupe.py` runs against the existing docs root and surfaces duplicates; if `is_duplicate` is true, the run halts and the existing file is reported instead.
7. No file other than the new auto-doc is created or modified.
8. If a file already exists at the target path, the run fails unless `--force` is passed.

## Knowledge

### What auto-docs are for
`.claude/docs/auto/` is a searchable archive of discovered insights — rules, patterns, and contracts that future commands can grep. Vague titles, missing tags, or wrong categories defeat retrieval. See `knowledge/categories.md` for the four buckets and `knowledge/frontmatter-schema.md` for field-level details.

### The four categories in one paragraph
**business-rule** — domain logic the business cares about (permissions, pricing, workflows, validation). **technical-pattern** — *how we build things* (caching strategy, error handling, repository pattern). **service-interface** — third-party API or webhook contracts (Stripe, Auth0, internal RPC). **domain-rule** — invariants and entity behaviors specific to the modeled domain (a `User` cannot reference itself; an `Order` cannot ship before paid).

### Why dedupe before write
The compounding-knowledge value comes from one canonical place per topic. Two near-identical files dilute search results and force readers to reconcile drift. `dedupe.py` checks title similarity and tag overlap so the LLM merges-or-rejects instead of multiplying.

### When NOT to auto-document
- A solved bug fix → `compound-docs` (different schema, different archive).
- An architecture decision → `architecture-adr-generator`.
- Stable project context (product, tech, structure) → `steering-docs-creator`.
- A spec requirement → put it in the PRD, not here.
- Trivial inline comments → leave it in the code.

## Steps

1. **Confirm there is an insight worth preserving.** Extract from context: the rule/pattern/contract, why it matters, where it applies (scope), and at least one concrete example. If any are missing, ask one focused question.

2. **Classify.** Run `python scripts/categorize.py --text "<insight summary>"`. The output is one of `business-rule`, `technical-pattern`, `service-interface`, `domain-rule`. If the heuristic returns the wrong bucket, override based on `knowledge/categories.md` — but log the override for the user.

3. **Assemble payload.** Build a JSON payload with frontmatter fields (`title`, `category`, `date`, `tags`, `scope`, `source`) and body sections (`description_body`, `why_body`, `examples_body`, `related_body`). The LLM writes the prose; everything else is mechanical. See `templates/payload.example.json`.

4. **Dedupe.** Run `python scripts/dedupe.py --payload <path> --docs-root <repo>/.claude/docs/auto/`. If `is_duplicate` is true, surface the matched file paths and stop — extending the existing doc is preferred over creating a duplicate.

5. **Write.** Run `python scripts/write_doc.py --payload <path> --docs-root <repo>/.claude/docs/auto/`. Refuse `--force` unless the user explicitly asks to overwrite.

6. **Validate output.** Run `python scripts/validate_output.py --file <output-path>`. Exit 0 required.

7. **Announce.**
   ```
   Auto-doc captured:
     <output-path>
   Category: <category>
   Tags: <tags>
   Scope: <scope>

   Searchable via grep on .claude/docs/auto/.
   ```

## Output

A single markdown file at `.claude/docs/auto/<category>/<slug>.md`, conforming to `templates/auto-doc.md.template`. No other side effects.

Filename pattern: `YYYY-MM-DD-<kebab-slug>.md`
Example: `.claude/docs/auto/service-interface/2026-05-08-stripe-webhook-retry-window.md`

## Antipatterns

- **Skipping dedupe.** Two files about the same rule split future search hits. Always run `dedupe.py` first.
- **Inventing a fifth category.** There are exactly four. If nothing fits, the insight may belong in a different skill (`compound-docs`, `architecture-adr-generator`, `steering-docs-creator`).
- **Vague titles or tags.** "Stripe stuff" is unsearchable. Title names the rule; tags name the technology, the layer, and the concept.
- **Embedding the template in SKILL.md.** Output template lives in `templates/auto-doc.md.template`. Editing prose inline drifts from the schema.
- **LLM picking the slug.** `write_doc.py` builds the slug deterministically from the title and date. The LLM does not get to override the filename.
- **Documenting open questions.** If the rule isn't yet decided, this is not the right place. Wait until the rule is settled.
- **Overwriting without consent.** `--force` requires explicit user direction; a duplicate slug means dedupe missed something — investigate before overwriting.
- **Bundling solved bugs.** A documented bug fix is a *solution* (use `compound-docs`), not an auto-doc. Different schema, different searchers.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. The auto-doc is unique under `.claude/docs/auto/` (verified by `dedupe.py`).

## Examples

- **`examples/example-1/`** — Worked example: a discovered business rule ("admins can edit any user post; non-admins only their own"). Includes the input free text, the assembled JSON payload, and the rendered doc under `business-rule/`. Demonstrates: tag granularity (`authorization`, `permissions`, `admin`), scope formatting (`UserPostController`), and the four body sections.
