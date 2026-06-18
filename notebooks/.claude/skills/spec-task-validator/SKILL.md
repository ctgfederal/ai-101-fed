---
name: spec-task-validator
version: 3.0.0
description: |
  Validate one or more `T-NNN` tasks from a `PLAN.md` against the requirements (`REQ-NNN` in PRD) and design (`COMP-NNN` in SDD) they reference. Each task is graded on ID format, valid cross-references, presence of a non-empty acceptance criterion that is mechanically *measurable* (verbs of observation: passes, returns, matches, exits, equals), an explicit TDD step (red/green/refactor), and an allowed phase. Renders a per-task validation report with `ok` / `warn` / `fail` verdicts, a summary, and a list of remediation issues. Use when a user runs `/validate` against a PLAN, asks "is this task ready to implement", asks "validate task T-NNN", or needs to gate `/implement` on per-task readiness. Do NOT use for free-form code review (use `/review-code`), 3Cs spec scoring (use `spec-validation`), spec-vs-implementation comparison (use `spec-compliance`), or to *write* the tasks being validated — this skill grades, it does not author.
triggers:
  - "/validate task"
  - "validate task"
  - "validate this task"
  - "is this task ready"
  - "task validation"
  - "validate PLAN tasks"
  - "check task readiness"
  - "validate T-"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-task-validator

Parse a `PLAN.md`, validate every `T-NNN` task against the PRD's `REQ-NNN` set and the SDD's `COMP-NNN` set, and render a markdown report. Each task gets a verdict (`ok` / `warn` / `fail`) computed deterministically from a fixed rubric — the LLM does not invent verdicts.

## Files

### Templates (`templates/`)
- `task-validation-report.md.template` — Canonical layout for the rendered report. Placeholders: `{{PLAN}}`, `{{TOTAL}}`, `{{OK}}`, `{{WARN}}`, `{{FAIL}}`, `{{TASK_ROWS}}`, `{{ISSUES}}`, `{{VERDICT}}`. Used by `write_report.py`.
- `payload.example.json` — Example JSON payload showing the exact shape `validate_tasks.py` emits and `write_report.py` consumes.

### Scripts (`scripts/`)
- `parse_tasks.py` — Deterministic. Reads a `PLAN.md` and emits a JSON list of structured task dicts, each with `id, title, phase, comps, reqs, acceptance, tdd_step`. Args: `--plan <path>`. Exit 0 on parse, 1 on I/O failure.
- `validate_tasks.py` — Deterministic. Given parsed tasks plus optional PRD reqs and SDD comps, validates each task: ID format, that referenced `REQ-NNN` / `COMP-NNN` IDs exist, that acceptance is non-empty AND contains at least one observation verb, that `tdd_step` is in `{red, green, refactor}`, that `phase` is in the allowed set. Args: `--tasks <json>` `[--prd <path>]` `[--sdd <path>]`. Prints JSON `{tasks: [{id, status, issues}], summary: {ok, warn, fail, total}, verdict}`.
- `write_report.py` — Deterministic. Renders `task-validation-report.md.template` from the JSON payload emitted by `validate_tasks.py`. Args: `--payload <path>` `--out <path>` `[--force]`. Exit 0 on write.
- `validate_output.py` — Deterministic. Validates a rendered report: required sections present, every input task has a row in the task table, summary numbers consistent (sum of ok+warn+fail equals total), verdict line valid. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `task-schema.md` — Required task fields, ID format (`T-NNN`), allowed phases, allowed `tdd_step` values, and the `_Requirements:` / `_Components:` reference syntax.
- `acceptance-rubric.md` — What makes acceptance "measurable" (observation verb + specific condition; rejects "should work", "looks good", "TBD").
- `verdict-thresholds.md` — Task status rules: `ok` = no issues; `warn` = stylistic / non-blocking issues; `fail` = missing required field, broken ID reference, or unmeasurable acceptance. Plus the overall PLAN verdict (PASS / WARN / FAIL).

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any task validation report this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `good_plan`, `bad_plan`, `good_prd`, `good_sdd`, `valid_payload`.
- `unit/test_parse_tasks.py` — Unit tests for the parser: well-formed PLAN, missing fields, multiple phases, multiple tasks, no `_Requirements:` line.
- `unit/test_validate_tasks.py` — Unit tests for the validator: valid task → ok, missing TDD step → fail, bad ID format → fail, dangling REQ → fail, unmeasurable acceptance → fail, stylistic issue → warn.
- `unit/test_write_report.py` — Unit tests for template substitution, payload validation, write semantics, `--force` behavior.
- `unit/test_validate_output.py` — Unit tests for the report validator: happy path, missing section, mismatched summary, missing task row.
- `integration/test_spec_task_validator_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_task_validator_eval.py` — Three-case eval: clean PLAN (all ok), one warn task, one fail task. Verifies eval harness shape.
- `smoke/test_e2e.py` — End-to-end: `parse_tasks.py` → `validate_tasks.py` → `write_report.py` → `validate_output.py` against a fixture PLAN.

### Examples (`examples/`)
- `example-1/` — Worked example: a fixture `PLAN.md` (`input-plan.md`) with three tasks (one ok, one warn, one fail), a matching PRD/SDD, the validator's JSON output (`payload.json`), and the rendered report (`expected-report.md`).

## Contract

Given a `PLAN.md` (and optionally a `PRD.md` / `SDD.md`), produce one task validation report file such that:

1. The report path is exactly `--out` from the invocation.
2. The body has these `##` sections in order: `## PLAN`, `## Summary`, `## Tasks`, `## Issues`, `## Verdict`.
3. The `## Tasks` table contains exactly one row per task in the input PLAN, in the order they appear.
4. Each row shows: task ID, phase, status (`ok` / `warn` / `fail`), issue count.
5. Summary numbers satisfy `ok + warn + fail == total`.
6. Overall `Verdict` is one of `PASS` (all ok), `WARN` (no fails, ≥1 warn), `FAIL` (≥1 fail), computed deterministically from the per-task statuses per `knowledge/verdict-thresholds.md`.
7. Every task with status `warn` or `fail` has at least one entry under `## Issues` referencing its task ID.
8. `python scripts/validate_output.py --file <path>` exits 0.
9. Per-task statuses are computed by `validate_tasks.py`; the LLM does not modify them.

## Knowledge

### What a task is
A task is a `- [ ] T-NNN <Title>` bullet under a `## Phase N: <Name>` heading. Below it: indented bullets describing implementation, an `_Acceptance:_` line, an `_Requirements:_` line (zero or more `REQ-NNN`), an `_Components:_` line (zero or more `COMP-NNN`), and a `_TDD:_` line (one of `red`, `green`, `refactor`). See `knowledge/task-schema.md`.

### Why mechanical
A verdict the LLM invents is unfalsifiable. Every per-task status comes from a fixed set of pass/fail checks. The LLM's job is to *narrate* the issues, not to decide the verdict. See `knowledge/acceptance-rubric.md` and `knowledge/verdict-thresholds.md`.

### Acceptance must be measurable
Acceptance is "measurable" when it contains at least one observation verb (`passes`, `returns`, `matches`, `exits`, `equals`, `produces`, `outputs`, `raises`, `asserts`, `<=`, `>=`, `<`, `>`, `=`) and a concrete condition. "Should work", "looks good", "TBD", and bare "works" are rejected.

### Verdict ladder
`ok` = no issues. `warn` = stylistic-only issues (e.g., title in lowercase, no Components listed but the task is in Polish phase). `fail` = blocking issues (bad ID format, dangling REQ/COMP, missing TDD step, non-measurable acceptance, missing acceptance).

## Steps

1. **Resolve target.** Confirm the `PLAN.md` to validate. Common cases: a path under `.claude/specs/<feature>/`, or a feature ID (resolve to its `PLAN.md`).

2. **Parse tasks.** Run `python scripts/parse_tasks.py --plan <path>`. Capture the JSON list.

3. **Resolve PRD / SDD context (optional).** If PRD.md / SDD.md siblings exist, capture their paths so the validator can check that referenced IDs exist.

4. **Validate.** Run `python scripts/validate_tasks.py --tasks <tasks.json> [--prd PRD.md] [--sdd SDD.md]`. Capture the JSON payload.

5. **Save payload.** Write the JSON to a temp file (e.g., `/tmp/task-validation-payload.json`).

6. **Render report.** Run `python scripts/write_report.py --payload <payload> --out <report-path>`. Default report path: `<plan-stem>.task-validation.md` next to the PLAN.

7. **Validate report.** Run `python scripts/validate_output.py --file <report-path>`. Must exit 0.

8. **Narrate the issues.** For each issue the validator reported, the LLM may add a one-line human-readable explanation under `## Issues`. The LLM does **not** change the status of any task.

9. **Announce.** Print the verdict, summary, and report path. Example:
   ```
   Task Validation: <plan>
   Total: 12   ok: 9   warn: 2   fail: 1
   Verdict: FAIL

   Report: <report-path>
   ```

## Output

A single markdown report rendered from `templates/task-validation-report.md.template`. No other side effects. Suggested filename: `<plan-stem>.task-validation.md`.

## Antipatterns

- **LLM sets the per-task status.** Statuses come from `validate_tasks.py`. The LLM only narrates and may suggest fixes, never override.
- **Skipping `validate_output.py`.** A report the validator hasn't seen is not done.
- **Validating a draft PLAN.** If `PLAN.md` is mid-write, results are meaningless. Confirm "this is the version to grade" before validating.
- **Treating PASS as approval.** PASS means *mechanically clean*; product judgment is still the human's job.
- **Embedding the report template in SKILL.md.** Lives in `templates/task-validation-report.md.template`.
- **Validating without PRD/SDD.** Allowed (the validator degrades gracefully) but cross-reference checks become best-effort. Always pass PRD/SDD when available.
- **Inventing new task fields.** The schema lives in `knowledge/task-schema.md`. Adding fields requires updating the parser.
- **Bundling spec scoring.** This skill grades tasks against their references. 3Cs spec scoring goes to `spec-validation`.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. Per-task statuses in the report match the JSON output of `validate_tasks.py` byte-for-byte.

## Examples

- **`examples/example-1/`** — Worked example. A fixture `PLAN.md` with three tasks: T-001 (clean → ok), T-002 (no TDD step → fail), T-003 (acceptance "should work" → fail). Demonstrates: parser extracts all three, validator marks two as fail, report shows summary `ok: 1, fail: 2`, verdict `FAIL`. Includes `input-plan.md`, `input-prd.md`, `input-sdd.md`, `payload.json`, and `expected-report.md`.
