---
name: spec-plan-generator
version: 3.0.0
description: |
  Generate an implementation plan at `.claude/specs/<feature>/PLAN.md` from an approved SDD: ordered TDD-style tasks with monotonic IDs (`T-NNN`), each task references one or more SDD components and PRD requirements, organized into phases (Foundation, Core, Integration, Polish). Use when a user runs `/specify` after SDD approval, asks "create the PLAN", or needs a tactical task list before `/implement`. Do NOT use to write requirements (PRD) or design decisions (SDD), to write code, or to create ad-hoc todo lists outside of approved specs.
triggers:
  - "/specify"
  - "create the PLAN"
  - "generate the implementation plan"
  - "PLAN for"
  - "task plan for"
  - "TDD plan"
  - "spec the tasks"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-plan-generator

Render `PLAN.md` from a JSON payload of phased tasks. Validates that every SDD `COMP-NNN` is touched by ≥1 task and every PRD `REQ-NNN` is covered.

## Files

### Templates (`templates/`)
- `plan.md.template` — PLAN layout: phases, tasks, traceability matrix.
- `payload.example.json` — Worked example.

### Scripts (`scripts/`)
- `init_plan.py` — Compute target `.claude/specs/<feature>/PLAN.md` path.
- `extract_ids.py` — Extract `REQ-NNN` from PRD and `COMP-NNN` from SDD. Args: `--prd <path>` `--sdd <path>`. Prints JSON `{reqs: [...], comps: [...]}`.
- `allocate_task_ids.py` — Allocate next `T-NNN` IDs starting from max+1 across all PLAN.md files in `.claude/specs/`.
- `write_plan.py` — Render template; validate phases, task IDs unique, every COMP referenced ≥1 task, every REQ has ≥1 task touching a component that covers it.
- `validate_output.py` — Validate written PLAN: required sections, unique task IDs, coverage matrix.

### Knowledge (`knowledge/`)
- `README.md` — Index.
- `plan-schema.md` — Phase names, task fields, ID conventions.
- `tdd-cycle.md` — Red-Green-Refactor expectation per task.
- `phase-ordering.md` — Foundation → Core → Integration → Polish guidance.

### Validation (`validation/`)
- `quality-checklist.md`.

### Tests (`tests/`)
- `unit/test_init_plan.py`
- `unit/test_extract_ids.py`
- `unit/test_allocate_task_ids.py`
- `unit/test_write_plan.py`
- `unit/test_validate_output.py`
- `integration/test_spec_plan_generator_integration.py` — Placeholder.
- `evals/spec_plan_generator_eval.py` — LLM evals: SDD-to-task decomposition.
- `smoke/test_e2e.py`
- `conftest.py`

### Examples (`examples/`)
- `example-1/` — feature-search PLAN with 4 phases and 12 tasks covering 4 components and 8 requirements.

## Contract

Given a PRD + SDD + payload, produce `.claude/specs/<feature>/PLAN.md` such that:

1. Path matches `^\.claude/specs/[a-z][a-z0-9-]+/PLAN\.md$`.
2. Body has these sections in order: `## Context References`, `## Phase 1: Foundation`, `## Phase 2: Core`, `## Phase 3: Integration`, `## Phase 4: Polish`, `## Traceability`, `## Open Questions`.
3. Every task has `T-NNN` ID, title, phase, component refs (`COMP-NNN`), requirement refs (`REQ-NNN`), acceptance criteria, and TDD step (red/green/refactor).
4. Every SDD `COMP-NNN` is referenced by ≥1 task.
5. Every PRD `REQ-NNN` is covered (transitively via component refs).
6. Task IDs are globally unique across `.claude/specs/*/PLAN.md`.
7. `python scripts/validate_output.py` exits 0.

## Knowledge

### Tasks are TDD-shaped
Each task names: which test to write first (red), what code makes it pass (green), what to clean up (refactor). See `knowledge/tdd-cycle.md`.

### Phases are ordered
Foundation (data model, scaffolding), Core (business logic, components), Integration (external systems, end-to-end), Polish (perf, telemetry, edge cases). See `knowledge/phase-ordering.md`.

### Coverage is the contract
Every COMP in SDD must have ≥1 task. Every REQ in PRD is covered transitively (a task touches a COMP that the SDD traceability maps to that REQ).

## Steps

1. **Read PRD + SDD.** Extract IDs via `python scripts/extract_ids.py --prd PRD.md --sdd SDD.md`.
2. **Init.** Run `python scripts/init_plan.py --feature <name> --specs-root .claude/specs`.
3. **Allocate task IDs.** Run `python scripts/allocate_task_ids.py --specs-root .claude/specs --count <N>`.
4. **Decompose.** For each phase, write tasks. Each task: id, title, phase, comps[], reqs[], acceptance, tdd_step.
5. **Write.** `python scripts/write_plan.py --payload <p> --out <path> --prd <prd> --sdd <sdd>`.
6. **Validate.** `python scripts/validate_output.py --file <path> --prd <prd> --sdd <sdd>`.
7. **Handoff.** Continue to `/implement` with the validated PLAN.

## Output

`.claude/specs/<feature>/PLAN.md` matching `templates/plan.md.template`. No other side effects.

## Antipatterns

- **Tasks without component refs.** Every task touches at least one `COMP-NNN`.
- **Tasks without requirement coverage.** Each task lists every `REQ-NNN` it serves.
- **Single-phase plans.** Phases force ordering discipline; merging them defeats the structure.
- **Missing TDD step.** Skipping red→green→refactor leads to untestable tasks.
- **Reusing T-NNN IDs.** Globally unique across all PLAN.md files; allocate via the script.

## Validation

Pass criteria:
1. `validate_output.py` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.

## Examples

- **`examples/example-1/`** — feature-search PLAN: 4 phases, 12 tasks `T-001..T-012`, full coverage matrix.
