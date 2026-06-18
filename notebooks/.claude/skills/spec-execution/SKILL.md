---
name: spec-execution
version: 2.0.0
description: |
  Drive the TDD red→green→refactor cycle for tasks defined in a `PLAN.md` under `.claude/specs/<feature>/`, persist progress in `execution-state.json` so multi-day implementation runs survive interruptions, and validate state on every save. Provides deterministic scripts for `init` (build state from PLAN), `read` / `update` (status transitions with allowed-value enforcement), `next_task` (lowest pending T-NNN whose dependencies are done), `record_tdd_step` (append-only history per task), and `validate_output` (state schema + PLAN cross-check). Use when a user runs `/implement`, asks to "start executing the plan", "resume implementation", "what's the next task", "mark T-007 done", or wants TDD-cycle bookkeeping for an in-flight spec. Do NOT use to write specs (PRD/SDD/PLAN — see `spec-prd-generator`, `spec-sdd-generator`, `spec-plan-generator`), to validate spec quality (use `spec-validation`), to write production code itself (this skill schedules and tracks; the LLM still does the coding), or for ad-hoc todo lists outside an approved spec.
triggers:
  - "/implement"
  - "start executing the plan"
  - "resume implementation"
  - "what's the next task"
  - "mark T-007 done"
  - "record red green refactor"
  - "execute the spec"
  - "continue the implementation"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-execution

One T-NNN task at a time, red → green → refactor, with state persisted in `.claude/specs/<feature>/execution-state.json`. The script layer owns task selection, status transitions, and history; the LLM owns the actual code edits and the user-facing narration.

## Files

### Templates (`templates/`)
- `state.example.json` — Reference shape for `execution-state.json`. Mirrors the schema in `knowledge/state-schema.md`.
- `patch.example.json` — Reference shape for a JSON patch fed to `state_manager.py update`.

### Scripts (`scripts/`)
- `state_manager.py` — Deterministic. Init / read / update `execution-state.json`. Subcommands: `init` (parse PLAN.md and seed one task entry per `T-NNN`), `read` (print state to stdout), `update` (deep-merge a JSON patch — rejects status values outside `{pending, in-progress, done, blocked, failed}`). Args: `--feature` `--specs-root`. Exit 0 = success.
- `next_task.py` — Deterministic. Returns the lowest-document-order `T-NNN` that is `status=pending` and whose `depends_on` are all `status=done`. Args: `--feature` `--specs-root`. Prints task JSON or `{}` if nothing eligible. Exit 0 in both cases.
- `record_tdd_step.py` — Deterministic. Appends one `{step, result, note, duration_s, timestamp}` entry to `tasks[T-NNN].history`. Args: `--feature` `--specs-root` `--task-id` `--step <red|green|refactor>` `--result <pass|fail>` `[--note]` `[--duration-s]`. Exit 0 = appended, 1 = unknown task / missing state.
- `validate_output.py` — Deterministic. Validates `execution-state.json`: required keys present, every task has the expected fields, every status is in the allowed set, `task_order` matches `tasks` keys, optional `--plan` cross-checks every PLAN.md `T-NNN` is present in state. Args: `--file` `[--plan]`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `tdd-loop.md` — The red → green → refactor protocol per task and what counts as "done".
- `state-schema.md` — JSON shape of `execution-state.json`, field semantics, status meanings.
- `interruption-recovery.md` — How to resume mid-task, handle `blocked` tasks, and recover from `failed` (three-strikes) tasks via spec-deviation.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any spec-execution run.

### Tests (`tests/`)
- `conftest.py` — Shared fixtures: `tmp_specs_root`, `sample_plan_text`, `init_feature`, `sample_state`.
- `unit/test_state_manager.py` — Init from PLAN, idempotent init, read, update with status enforcement, bad JSON, missing PLAN.
- `unit/test_next_task.py` — Picks lowest pending, honors `depends_on`, skips `blocked`, document-order tiebreak, empty state.
- `unit/test_record_tdd_step.py` — Appends history entry, rejects unknown tasks, enforces step/result enums via argparse, records duration.
- `unit/test_validate_output.py` — Happy path, missing keys, invalid status, history-not-list, task_order mismatch, PLAN cross-check.
- `integration/test_spec_execution_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_execution_eval.py` — Three-case eval: post-red resume, dependency-blocked progress, three-strikes failure.
- `smoke/test_e2e.py` — End-to-end: init → next_task → record red → record green → update done → next_task → validate.

### Examples (`examples/`)
- `example-1/` — Worked example: a 5-task PLAN.md mid-run with T-001/T-002 done, T-003 in-progress (red recorded), T-004/T-005 pending. Demonstrates state persistence, `depends_on` enforcement, and the resume case.

## Contract

Given a feature folder containing `PLAN.md`, produce and maintain `execution-state.json` such that:

1. After `state_manager.py init`, the state contains exactly one entry under `tasks` for every `T-NNN` parsed from `PLAN.md`, all with `status=pending` and empty `history`.
2. `state_manager.py update` only accepts patches whose task `status` values are in `{pending, in-progress, done, blocked, failed}`. Any other status causes exit 1 and no write.
3. `record_tdd_step.py` appends to `tasks[T-NNN].history` and never edits prior entries — history is append-only.
4. `next_task.py` returns either an eligible task or `{}`; it never returns a task whose `depends_on` includes a task that is not `done`.
5. `validate_output.py --file <state> --plan <plan>` exits 0 iff:
   - all required top-level keys are present (`feature`, `current_task`, `tasks`, `task_order`, `meta`),
   - every task entry has `description`, `status`, `history` (list), `blockers` (list), `depends_on` (list),
   - every status is in the allowed set,
   - `task_order` is exactly the keys of `tasks`,
   - every `T-NNN` in PLAN.md is present in `state.tasks`.
6. State writes are atomic enough to survive interruption — a crashed run leaves the file at its last valid version.

## Knowledge

### TDD loop
One task = one red→green→refactor cycle. Red **must fail** for the right reason (missing implementation), green is the **smallest** change that passes, refactor is optional and never changes behavior. See `knowledge/tdd-loop.md`.

### State schema
State lives at `.claude/specs/<feature>/execution-state.json` and persists across sessions. The shape is fixed (`feature`, `current_task`, `tasks`, `task_order`, `meta`), task statuses are an enum, and history is append-only. See `knowledge/state-schema.md`.

### Interruption recovery
On resume: read state, validate it, surface counts by status and the in-progress task (if any). If a task is `blocked`, the `blockers` list explains why. If a task is `failed` (three strikes), do **not** retry — escalate to spec-deviation. See `knowledge/interruption-recovery.md`.

## Steps

1. **Locate the spec.** Resolve `--specs-root` to `.claude/specs` (or wherever the project keeps specs) and confirm the feature folder exists with a `PLAN.md`.

2. **Init state (or resume).** Run `python scripts/state_manager.py init --feature <name> --specs-root <root>`. If state already exists, `init` is idempotent — read existing state instead and surface counts by status and any `current_task`.

3. **Validate state.** Run `python scripts/validate_output.py --file <root>/<feature>/execution-state.json --plan <root>/<feature>/PLAN.md`. Must exit 0 before doing any work. If it fails, fix the corruption by hand — do not patch over.

4. **Pick the next task.** Run `python scripts/next_task.py --feature <name> --specs-root <root>`. If output is `{}`, every remaining `pending` task is blocked by an unmet dependency — surface the `blocked` and `pending`-with-unmet-deps tasks to the user.

5. **Mark task in-progress.** Patch state:
   ```bash
   echo '{"current_task": "T-NNN", "tasks": {"T-NNN": {"status": "in-progress"}}}' \
     | python scripts/state_manager.py update --feature <name> --specs-root <root>
   ```

6. **Red.** Write the failing test. Run it. Confirm it fails for the right reason. Then:
   ```bash
   python scripts/record_tdd_step.py --feature <name> --specs-root <root> \
       --task-id T-NNN --step red --result fail --note "<why it fails>"
   ```

7. **Green.** Write the smallest production change. Run the full test suite. Then:
   ```bash
   python scripts/record_tdd_step.py --feature <name> --specs-root <root> \
       --task-id T-NNN --step green --result pass
   ```

8. **Refactor (optional).** Improve quality. Run the full test suite again. Then:
   ```bash
   python scripts/record_tdd_step.py --feature <name> --specs-root <root> \
       --task-id T-NNN --step refactor --result pass
   ```

9. **Mark task done.** Patch state:
   ```bash
   echo '{"current_task": null, "tasks": {"T-NNN": {"status": "done"}}}' \
     | python scripts/state_manager.py update --feature <name> --specs-root <root>
   ```

10. **Loop.** Go back to step 4 until `next_task.py` returns `{}` and no tasks are `blocked`.

11. **Validate at finish.** Run `validate_output.py` again with `--plan`. Surface final status counts to the user.

## Output

Two persistent artifacts:

1. `.claude/specs/<feature>/execution-state.json` — updated through every step, structured per `knowledge/state-schema.md`.
2. Append-only `history` entries per task — the audit trail of every red/green/refactor step.

No other files are touched by this skill. Production code edits, test edits, and PLAN.md checkbox updates are handled by the orchestrating workflow (`/implement`), not by spec-execution itself.

## Antipatterns

- **LLM picks the next task.** Selection is deterministic via `next_task.py`. The LLM only narrates which task is next and why.
- **Editing prior history entries.** History is append-only. Mistakes are recorded by appending a new entry, not by mutating an old one.
- **Writing production code before recording a red→fail.** The cycle starts with a failing test. Skipping the red step makes the audit trail a lie.
- **Ignoring `depends_on`.** If `next_task.py` says nothing is eligible, the answer is to unblock or revisit `depends_on`, not to manually pick a different task.
- **Patching status to `done` without a green→pass in history.** Done means demonstrably green. The validator does not currently enforce this, but the audit trail must.
- **Fourth attempt on a `failed` task.** Three strikes = architectural problem. Open a spec deviation; do not patch a fourth time.
- **Embedding the schema in SKILL.md.** Lives in `knowledge/state-schema.md` so scripts and humans read the same source.
- **Writing specs in this skill.** PRD/SDD/PLAN authoring is `spec-prd-generator`, `spec-sdd-generator`, `spec-plan-generator`. This skill executes against an already-approved PLAN.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <state> --plan <plan>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0.
6. Every item in `validation/quality-checklist.md` is checked.
7. Every task referenced in PLAN.md is present in state.tasks (via `--plan` cross-check).

## Examples

- **`examples/example-1/`** — Worked example: feature `feature-search` with 5 tasks across 3 phases. Shows state mid-run: T-001 and T-002 `done` (with full red/green history), T-003 `in-progress` with one `red→fail` recorded, T-004 and T-005 `pending` with chained `depends_on`. Demonstrates the resume case (`next_task.py` returns T-003 because dependencies are met) and the dependency-block case (T-005 cannot be picked while T-004 is pending).
