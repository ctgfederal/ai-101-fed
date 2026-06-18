# TDD Loop — Red → Green → Refactor

The execution unit is **one task** (`T-NNN`). The cycle for one task is fixed:

## 1. Red — write a failing test

- Pick exactly **one** acceptance criterion or behavior that the task targets.
- Write the smallest test that asserts the desired behavior.
- Run the test. **It must fail.**
- Failure must be because the production code does not exist or does not behave correctly — **not** because of:
  - a syntax error in the test
  - a missing import
  - a wrong fixture path
- Record the step:
  ```
  python scripts/record_tdd_step.py --feature F --specs-root R \
      --task-id T-NNN --step red --result fail --note "<reason>"
  ```

A red step where the test passes accidentally is not red — fix the test, do not move on.

## 2. Green — make the test pass

- Write the **smallest** production change that turns the failing test green.
- No extra features. No premature optimization. No "while I'm in here…".
- Run the test suite (not just the one new test).
- Record:
  ```
  python scripts/record_tdd_step.py --feature F --specs-root R \
      --task-id T-NNN --step green --result pass
  ```

If green takes more than ~30 minutes of code edits, the task is too big. Split it
in PLAN.md (back to `/specify`) before continuing.

## 3. Refactor — improve quality with tests staying green

- Optional but encouraged. Skip only when the green code is already clean.
- Allowed: rename for clarity, extract helper, deduplicate, tighten types.
- **Not allowed**: change behavior, add new feature, broaden test coverage to a
  different criterion (that is the next task's red step).
- Run the full test suite after every refactor edit.
- Record:
  ```
  python scripts/record_tdd_step.py --feature F --specs-root R \
      --task-id T-NNN --step refactor --result pass
  ```

## Done

A task is **done** when:

1. At least one `red→fail` history entry exists.
2. At least one `green→pass` history entry exists with no later `green→fail` entry.
3. The full test suite (project-level, not just the new test) passes after the
   final green or refactor step.
4. Status is set to `done` via `state_manager.py update`.
5. The PLAN.md checkbox for the task is marked `[x]` (handled outside this skill —
   see `/implement` workflow or the legacy `checkbox-update` step).

## Warning signs

- Skipping the red step ("the test would have failed if I'd written it") — STOP.
- Bundling multiple red steps before any green — STOP.
- Editing the test to make it pass — STOP, that defeats the cycle.
- Writing more than one task's worth of code in one green step — STOP, split the task.
