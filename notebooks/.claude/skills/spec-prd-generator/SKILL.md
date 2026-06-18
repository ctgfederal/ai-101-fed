---
name: spec-prd-generator
version: 3.0.0
description: |
  Generate a Product Requirements Document at `.claude/specs/<feature>/PRD.md` with EARS-format acceptance criteria, monotonic requirement IDs (`REQ-NNN`), MoSCoW prioritization, and references to steering docs (`.claude/steering/product.md`, `roadmap.md`). Use when a user runs `/specify`, asks to create a PRD, or needs formal requirements before SDD/PLAN. Do NOT use for design decisions (those go in SDD via `spec-sdd-generator`), implementation tasks (those go in PLAN via `spec-plan-generator`), brainstorming, or ad-hoc product notes.
triggers:
  - "/specify"
  - "create a PRD"
  - "generate requirements doc"
  - "PRD for"
  - "write the PRD"
  - "EARS requirements"
  - "spec the requirements"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-prd-generator

Render `PRD.md` from a JSON payload of stories, EARS criteria, and metrics. Allocates monotonic `REQ-NNN` IDs across the entire `.claude/specs/` tree.

## Files

### Templates (`templates/`)
- `prd.md.template` — Canonical PRD layout with placeholders for vision, problem, personas link, user stories with EARS, MoSCoW, metrics, risks.
- `payload.example.json` — Example PRD payload showing every required field.

### Scripts (`scripts/`)
- `init_prd.py` — Deterministic. Creates `.claude/specs/<feature>/` if absent and returns target PRD path. Args: `--feature <name>` `--specs-root <path>` `[--force]`. Exit 0.
- `allocate_req_ids.py` — Deterministic. Walks `.claude/specs/*/PRD.md`, finds max `REQ-NNN`, allocates next batch. Args: `--specs-root <path>` `--count <int>`. Exit 0.
- `write_prd.py` — Deterministic. Renders `prd.md.template` from JSON payload and writes file. Validates payload schema. Args: `--payload <path-or-stdin>` `--out <path>` `[--force]`. Exit 0.
- `validate_output.py` — Deterministic. Validates a written PRD: required sections present in order, every requirement has `REQ-NNN` ID + EARS pattern + MoSCoW priority, no `[NEEDS CLARIFICATION]` markers. Args: `--file <path>`. Exit 0.

### Knowledge (`knowledge/`)
- `README.md` — Index.
- `ears-format.md` — The 5 EARS patterns (Ubiquitous / Event-driven / State-driven / Optional / Complex) with examples and which to pick.
- `prd-schema.md` — Required and optional fields, MoSCoW values, REQ-ID format.
- `steering-references.md` — Which steering doc anchors PRD must link (personas, constraints, metrics framework, current phase).

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any PRD.

### Tests (`tests/`)
- `unit/test_init_prd.py` — Path computation, force overwrite, root creation.
- `unit/test_allocate_req_ids.py` — Empty tree, multiple existing PRDs, gaps in numbering.
- `unit/test_write_prd.py` — Schema validation, render substitution, EARS-pattern requirement, file write.
- `unit/test_validate_output.py` — Happy, missing section, missing REQ-ID, NEEDS CLARIFICATION marker.
- `integration/test_spec_prd_generator_integration.py` — Placeholder.
- `evals/spec_prd_generator_eval.py` — LLM evals: turning a brainstorm into EARS criteria (clear / ambiguous / overspecified).
- `smoke/test_e2e.py` — End-to-end: init → allocate → write → validate.
- `conftest.py` — Shared fixtures.

### Examples (`examples/`)
- `example-1/` — `payload.json` and `expected-output.md` for a `feature-search` PRD with 3 user stories and 8 EARS criteria.

## Contract

Given a payload of feature requirements, produce one file at `.claude/specs/<feature>/PRD.md` such that:

1. Path matches `^\.claude/specs/[a-z][a-z0-9-]+/PRD\.md$`.
2. Body has these sections in order: `## Context References`, `## Product Overview`, `## Personas`, `## User Stories`, `## Functional Requirements`, `## MoSCoW Priorities`, `## Success Metrics`, `## Risks and Constraints`, `## Open Questions`.
3. Every requirement has `REQ-NNN` ID, an EARS-pattern body, and a MoSCoW priority (`Must`, `Should`, `Could`, `Won't`).
4. `REQ-NNN` IDs in this PRD are contiguous in the range allocated by `allocate_req_ids.py`.
5. No `[NEEDS CLARIFICATION]` markers remain.
6. References to `.claude/steering/` use anchor links (e.g., `product.md#user-personas`).
7. `python scripts/validate_output.py --file <path>` exits 0.

## Knowledge

### EARS in one paragraph
Each requirement must follow one of: **Ubiquitous** (`SHALL ...`), **Event-driven** (`WHEN ... THEN SHALL ...`), **State-driven** (`WHILE ... SHALL ...`), **Optional** (`WHERE ... SHALL ...`), **Complex** (`IF ... THEN SHALL ...`). See `knowledge/ears-format.md`.

### REQ-NNN allocation
One global monotonic counter across the entire `.claude/specs/` tree. Find max via grep; allocate next batch. See `knowledge/prd-schema.md`.

### Steering references, not duplications
Personas, business constraints, success-metrics framework, and current phase live in `.claude/steering/`. The PRD links to them with anchor URLs — never copies the content.

## Steps

1. **Load steering.** Read `.claude/steering/product.md` and `.claude/steering/roadmap.md`. If absent, halt and tell user to run `steering-docs-creator` first.
2. **Init.** Run `python scripts/init_prd.py --feature <name> --specs-root .claude/specs`.
3. **Allocate IDs.** Run `python scripts/allocate_req_ids.py --specs-root .claude/specs --count <N>`.
4. **Assemble payload.** Build JSON: vision, problem, value, personas (referenced), user stories with EARS criteria + MoSCoW priority + REQ-ID, metrics (referenced framework + targets), risks, open questions.
5. **Write.** Run `python scripts/write_prd.py --payload <path> --out <init-output>`.
6. **Validate.** Run `python scripts/validate_output.py --file <output>`. Exit 0.
7. **Handoff.** Surface next steps: `/specify`-continue to SDD, refine PRD, done.

## Output

`.claude/specs/<feature>/PRD.md` matching `templates/prd.md.template`. No other side effects.

## Antipatterns

- **Duplicating steering content.** Personas, constraints, metrics framework: link, never copy.
- **Skipping EARS.** Every functional requirement is EARS-formatted. "User can search" is not a requirement.
- **Reusing REQ-IDs.** IDs are append-only and globally unique across all specs.
- **Leaving `[NEEDS CLARIFICATION]`.** Resolve before validation; the validator rejects them.
- **Embedding the template in SKILL.md.** Lives in `templates/`.
- **Inventing MoSCoW values.** Exactly four allowed: Must, Should, Could, Won't.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.

## Examples

- **`examples/example-1/`** — Worked example: feature-search PRD with 3 user stories, 8 EARS-formatted requirements `REQ-101..REQ-108`, MoSCoW assigned, steering links populated.
