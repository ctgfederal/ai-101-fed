---
name: steering-docs-creator
version: 2.0.0
description: |
  Creates project-level steering documents (PRODUCT, TECH, STRUCTURE, ROADMAP) at `.claude/steering/` that provide persistent project context for all downstream feature specifications. Each doc has a documented schema with stable section anchors that PRD, SDD, and PLAN generators link to (e.g., `product.md#user-personas`). Use when the user runs `/create-steering-docs`, sets up a new project, completes a major refactor, onboards Claude to an existing codebase, or wants the annual context refresh. Do NOT use for feature-specific requirements (those go in PRD via `spec-prd-generator`), design decisions (those go in SDD via `spec-sdd-generator`), implementation plans (PLAN via `spec-plan-generator`), ad-hoc project notes, or to rewrite arbitrary markdown.
triggers:
  - "/create-steering-docs"
  - "create steering docs"
  - "set up steering"
  - "scaffold .claude/steering"
  - "initialize project context"
  - "annual steering refresh"
  - "onboard Claude to this project"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# steering-docs-creator

Scaffold and maintain the four project-level steering documents at `.claude/steering/`: `product.md`, `tech.md`, `structure.md`, `roadmap.md`. Each conforms to a fixed schema so downstream skills (`spec-prd-generator`, `spec-sdd-generator`, `spec-plan-generator`) can link to stable anchors.

## Files

### Templates (`templates/`)
- `product.md.template` — Sections: Mission, User Personas, Business Constraints, Success Metrics Framework, Domain Glossary.
- `tech.md.template` — Sections: Tech Stack, Conventions, Library Choices, Build & CI, Observability.
- `structure.md.template` — Sections: Layer Model, Folder Layout, Naming Rules, Dependency Direction, Module Boundaries.
- `roadmap.md.template` — Sections: Current Phase, Phase Definitions, Milestones, Out-of-Scope.

### Scripts (`scripts/`)
- `init_steering.py` — Deterministic. Creates `.claude/steering/` and scaffolds the four docs from templates if absent. Refuses to overwrite without `--force`. Args: `--steering-root <path>` `[--force]` `[--only product|tech|structure|roadmap]`. Exit 0 = scaffolded (or already present), 1 = error.
- `validate_steering.py` — Deterministic. Validates that all four docs exist and each has its required sections per `knowledge/steering-schema.md`. Args: `--steering-root <path>`. Prints a per-doc summary; exit 0 = pass, 1 = fail.
- `update_doc.py` — Deterministic. Replaces the body of one section heading inside a single steering doc. Args: `--steering-root <path>` `--doc <product|tech|structure|roadmap>` `--section <heading>` `--body <str-or-stdin>` `[--force]`. Refuses to write if section heading is not found. Exit 0 = wrote, 1 = error.
- `validate_output.py` — Deterministic. Validates one specific steering doc file against its required sections. Args: `--file <path>` `--doc <product|tech|structure|roadmap>`. Exit 0 = pass, 1 = fail.

### Knowledge (`knowledge/`)
- `README.md` — Index.
- `steering-schema.md` — Authoritative per-doc schema: required section headings, anchor-link conventions, and the link contract that downstream skills depend on.
- `when-to-update.md` — Annual refresh cadence plus event triggers (major refactor, new product line, persona research, phase change).
- `usage-by-other-skills.md` — Which downstream skills consume which steering anchors and what they break if those anchors disappear.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for the steering doc set produced by this skill.

### Tests (`tests/`)
- `unit/test_init_steering.py` — Path computation, `--force` behavior, `--only` selector, idempotent re-run.
- `unit/test_validate_steering.py` — All four present and valid, missing doc, missing section, bad doc.
- `unit/test_update_doc.py` — Section body replacement, missing section refusal, stdin input, `--force`.
- `unit/test_validate_output.py` — Per-doc happy path, missing required section, unknown doc kind.
- `integration/test_steering_docs_creator_integration.py` — Placeholder gated by `RUN_INTEGRATION_TESTS=1`.
- `evals/steering_docs_creator_eval.py` — LLM evals: filling persona / tech-stack / phase fields from sparse context.
- `smoke/test_e2e.py` — End-to-end: init → validate → update one section → re-validate.
- `conftest.py` — Shared fixtures (`tmp_steering_root`, `valid_section_body`).

### Examples (`examples/`)
- `example-1/` — A worked example showing the four scaffolded docs after `init_steering.py`, plus an `update_doc.py` invocation that fills the Tech Stack section, plus `expected-output/` with the resulting `tech.md`.

## Contract

Given an empty or partial project, produce a `.claude/steering/` directory containing exactly four files such that:

1. The directory matches `^\.claude/steering/$` and contains `product.md`, `tech.md`, `structure.md`, `roadmap.md` and no other files.
2. Each doc contains its required `## ` section headings in the order specified by `knowledge/steering-schema.md`.
3. Each section heading slugifies to a stable anchor that downstream skills link to (e.g., `product.md#user-personas`).
4. Running `python scripts/validate_steering.py --steering-root .claude/steering` exits 0.
5. Running `python scripts/validate_output.py --file <path> --doc <kind>` for any of the four docs exits 0.
6. `init_steering.py` is idempotent without `--force`: re-running on a populated tree exits 0 and changes nothing.
7. `update_doc.py` replaces only the body under one named section heading; surrounding sections, frontmatter, and the heading itself are preserved byte-for-byte.

## Knowledge

### Why four docs and not one
Each doc owns one stable concern and one stable set of anchors. Splitting them prevents downstream skills from pinning to a giant moving file: `spec-prd-generator` only depends on `product.md` and `roadmap.md` anchors; `spec-sdd-generator` only depends on `tech.md` and `structure.md` anchors; `spec-plan-generator` depends on `roadmap.md`. See `knowledge/usage-by-other-skills.md`.

### Anchor-link contract
Section headings are slugified by GitHub's standard rule (lowercase, alphanumerics + hyphens). Once a section heading ships, renaming it is a breaking change for every downstream skill that links to it. See `knowledge/steering-schema.md` for the canonical heading list per doc.

### When to scaffold vs update
Scaffold once at project start (or after major refactor that invalidates prior context). Update sections individually as facts change — never tear down and re-init unless the entire stack changed. See `knowledge/when-to-update.md`.

## Steps

1. **Decide scaffold or update.** If `.claude/steering/` is empty or missing, scaffold. If it exists and the user wants to refresh one fact, update.

2. **Scaffold path.** Run `python scripts/init_steering.py --steering-root .claude/steering`. Use `--only` to scaffold a single doc; use `--force` only when the user explicitly asks to overwrite.

3. **Validate scaffold.** Run `python scripts/validate_steering.py --steering-root .claude/steering`. Exit 0 required.

4. **Update path.** For each section the user has new content for, run `python scripts/update_doc.py --steering-root .claude/steering --doc <kind> --section "<heading>" --body -` and pipe the new body via stdin.

5. **Per-doc validation.** Run `python scripts/validate_output.py --file .claude/steering/<doc>.md --doc <kind>` after every write. Exit 0 required.

6. **Final validation.** Run `python scripts/validate_steering.py --steering-root .claude/steering` once more. Exit 0 required.

7. **Handoff.** Tell the user which downstream skills now have stable anchors to link to: `spec-prd-generator` (personas, metrics, current phase), `spec-sdd-generator` (tech stack, layer model), `spec-plan-generator` (current phase, milestones).

## Output

Four markdown files at `.claude/steering/`:

- `.claude/steering/product.md`
- `.claude/steering/tech.md`
- `.claude/steering/structure.md`
- `.claude/steering/roadmap.md`

Each conforms to its template in `templates/`. No other side effects. No sub-agents write files; only `init_steering.py` and `update_doc.py` ever touch disk.

## Antipatterns

- **Renaming section headings.** Headings are part of the public anchor contract. Renaming `## User Personas` to `## Personas` breaks every PRD that linked to `product.md#user-personas`.
- **Writing one mega-doc.** The four-doc split is load-bearing. Do not merge them.
- **Letting `[NEEDS CLARIFICATION]` markers ship.** They block the validator. Resolve or remove before final validation.
- **Inventing new sections.** Add a section to `knowledge/steering-schema.md` first; downstream skills must learn about it before it appears in a doc.
- **Embedding content in `SKILL.md`.** All renderable text lives in `templates/`. SKILL.md only orchestrates.
- **Sub-agent file writes.** All four files are produced by `init_steering.py` only. Parallel writers race and corrupt the set.
- **Silent overwrite.** `init_steering.py` and `update_doc.py` refuse to clobber without `--force`.

## Validation

Pass criteria:
1. `python scripts/validate_steering.py --steering-root <path>` exits 0.
2. `python scripts/validate_output.py --file <doc> --doc <kind>` exits 0 for each of the four docs.
3. `pytest tests/unit/` exits 0.
4. `pytest tests/smoke/` exits 0.
5. `pytest tests/evals/` exits 0.
6. Every item in `validation/quality-checklist.md` is checked.

## Examples

- **`examples/example-1/`** — Worked example: scaffold all four docs, then run `update_doc.py` to fill `tech.md`'s Tech Stack section. Shows the input body string, the resulting `tech.md`, and a passing validator run.
