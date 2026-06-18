---
name: spec-sdd-generator
version: 3.0.0
description: |
  Generate a Solution Design Document at `.claude/specs/<feature>/SDD.md` that bridges PRD requirements to implementation: codebase research, architectural decisions, component breakdown, traceability matrix mapping every PRD `REQ-NNN` to one or more SDD components, and references to steering docs (`.claude/steering/tech.md`, `structure.md`). Use when a user runs `/specify` after PRD approval, asks "create the SDD", or needs a design doc before implementation planning. Do NOT use to write requirements (those live in PRD via `spec-prd-generator`), implementation tasks (those go in PLAN via `spec-plan-generator`), free-form architecture notes, or to make design decisions without a PRD.
triggers:
  - "/specify"
  - "create the SDD"
  - "generate solution design"
  - "SDD for"
  - "design doc for"
  - "write the design"
  - "spec the design"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-sdd-generator

Render `SDD.md` from a JSON payload of design decisions + components + traceability. Validates that every PRD `REQ-NNN` is covered by at least one SDD component.

## Files

### Templates (`templates/`)
- `sdd.md.template` — SDD layout: overview, architecture, components, data model, integrations, traceability matrix, alternatives, risks.
- `payload.example.json` — Worked example payload.

### Scripts (`scripts/`)
- `init_sdd.py` — Deterministic. Computes target `.claude/specs/<feature>/SDD.md` path. Refuses overwrite without `--force`. Args: `--feature` `--specs-root` `[--force]`.
- `extract_req_ids.py` — Deterministic. Extracts every `REQ-NNN` ID from `.claude/specs/<feature>/PRD.md`. Args: `--prd <path>`. Prints space-separated IDs.
- `write_sdd.py` — Deterministic. Renders `sdd.md.template` from payload, validates the traceability matrix covers all PRD requirements, writes file. Args: `--payload <path>` `--out <path>` `--prd <path>` `[--force]`.
- `validate_output.py` — Deterministic. Validates: required sections, traceability covers every PRD REQ, components have unique `COMP-NNN` IDs, steering anchor links. Args: `--file <path>` `--prd <path>`.

### Knowledge (`knowledge/`)
- `README.md` — Index.
- `sdd-schema.md` — Required fields, component ID format, traceability rules.
- `architecture-research.md` — How to research the codebase before writing SDD (where to look, what to summarize).
- `steering-references.md` — Required anchor links to `tech.md` and `structure.md`.

### Validation (`validation/`)
- `quality-checklist.md`.

### Tests (`tests/`)
- `unit/test_init_sdd.py`
- `unit/test_extract_req_ids.py`
- `unit/test_write_sdd.py`
- `unit/test_validate_output.py`
- `integration/test_spec_sdd_generator_integration.py` — Placeholder.
- `evals/spec_sdd_generator_eval.py` — LLM evals: PRD-to-component decomposition.
- `smoke/test_e2e.py`
- `conftest.py`

### Examples (`examples/`)
- `example-1/` — `feature-search` SDD with 4 components (`COMP-001..COMP-004`) covering 8 PRD requirements.

## Contract

Given a payload + a corresponding PRD, produce `.claude/specs/<feature>/SDD.md` such that:

1. Path matches `^\.claude/specs/[a-z][a-z0-9-]+/SDD\.md$`.
2. Body has these sections in order: `## Context References`, `## Overview`, `## Architecture`, `## Components`, `## Data Model`, `## External Integrations`, `## Traceability`, `## Alternatives Considered`, `## Risks and Mitigations`, `## Open Questions`.
3. Every component has a `COMP-NNN` ID, name, responsibility, dependencies, and contract (inputs/outputs).
4. The traceability matrix maps EVERY `REQ-NNN` from the PRD to ≥1 `COMP-NNN`.
5. References to `.claude/steering/` use anchor links.
6. `python scripts/validate_output.py --file <path> --prd <prd>` exits 0.

## Knowledge

### Traceability is the contract
Every PRD requirement must have at least one SDD component covering it. `validate_output.py` enforces this — a missing requirement is a hard fail.

### Components have IDs
`COMP-NNN` (zero-padded to 3, growing as needed). Local to the SDD (per-spec); not globally unique.

### Steering, not duplication
Tech-stack standards and project-structure conventions live in `.claude/steering/tech.md` and `structure.md`. Link to them; don't paraphrase.

See `knowledge/sdd-schema.md` for full schema and `knowledge/architecture-research.md` for the research protocol.

## Steps

1. **Read the PRD.** Extract `REQ-NNN` list via `python scripts/extract_req_ids.py --prd .claude/specs/<feature>/PRD.md`.
2. **Load steering.** Read `.claude/steering/tech.md` and `structure.md`. If absent, halt and tell user to run `steering-docs-creator`.
3. **Research the codebase.** Read `knowledge/architecture-research.md`. Find existing components related to the feature; note conventions to follow.
4. **Init.** Run `python scripts/init_sdd.py --feature <name> --specs-root .claude/specs`.
5. **Decompose.** Map every REQ → 1+ component. Assemble payload with `components` (each: id, name, responsibility, dependencies, contract) and `traceability` (each REQ → list of COMP IDs).
6. **Write.** Run `python scripts/write_sdd.py --payload <path> --out <init-output> --prd <prd-path>`. The script asserts traceability covers every REQ before writing.
7. **Validate.** Run `python scripts/validate_output.py --file <output> --prd <prd>`.
8. **Handoff.** Continue to PLAN via `spec-plan-generator`.

## Output

`.claude/specs/<feature>/SDD.md` matching `templates/sdd.md.template`. No other side effects.

## Antipatterns

- **Components without contracts.** Inputs/outputs must be explicit. "Handles search" is not a contract.
- **Untraced requirements.** Every REQ has at least one COMP. Missing coverage is a hard fail.
- **Embedding tech.md content.** Link to steering anchors.
- **Re-using requirement IDs in SDD.** REQ-IDs come from the PRD; SDD only references them.
- **Designing without research.** Read the codebase first; SDD that ignores existing patterns is technical debt waiting.
- **Skipping alternatives.** "Considered X, rejected because Y" forces honest tradeoff thinking.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <out> --prd <prd>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.

## Examples

- **`examples/example-1/`** — feature-search SDD: 4 components (`COMP-001..COMP-004`) covering 8 PRD requirements (`REQ-001..REQ-008`); traceability matrix complete.
