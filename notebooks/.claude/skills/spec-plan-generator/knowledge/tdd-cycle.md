# TDD Cycle Per Task

Every task is one of `red`, `green`, or `refactor`.

| Step | What happens |
|---|---|
| `red` | Write a failing test that describes the desired behavior. The test fails because the feature doesn't exist yet. |
| `green` | Write the minimum code to make the test pass. No premature optimization. |
| `refactor` | Improve the code without changing behavior. All tests still green. |

## Sequencing in a phase

A typical sequence within a phase:
1. `red` — write the unit test for a component method.
2. `green` — implement the method.
3. `red` — write integration test.
4. `green` — wire it up.
5. `refactor` — extract helpers; rename; consolidate.

## When a task is "all three"

Mark the task by its dominant step. If the task is "implement service + tests + cleanup", split it into three tasks or pick the dominant step (usually `green`).

## Anti-patterns
- Writing all tests first, then all code (loses the discipline).
- Skipping `red` (writing the test after the code passes — measures nothing).
- `refactor` that changes behavior (that's a `green`/`red` change disguised).
