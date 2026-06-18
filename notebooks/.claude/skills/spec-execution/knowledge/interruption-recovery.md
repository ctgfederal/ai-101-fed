# Interruption & Recovery

A spec-execution run can take days. Sessions get interrupted: the user closes the
laptop, a test hangs, a dependency breaks. State persists in `execution-state.json`
so the next session resumes where the previous one stopped.

## Resume protocol

1. **Read state.**
   ```
   python scripts/state_manager.py read --feature F --specs-root .claude/specs
   ```
   Surface to the user:
   - `feature`
   - count of tasks in each status
   - `current_task` if not null
   - `meta.sessions` (will be incremented this session)

2. **Validate state.**
   ```
   python scripts/validate_output.py --file .claude/specs/F/execution-state.json \
       --plan .claude/specs/F/PLAN.md
   ```
   Must exit 0. If not, surface the errors before doing anything else — a
   corrupt state file should be fixed by hand, not patched over.

3. **Inspect the in-progress task (if any).**
   - Read its history.
   - Last entry tells you where you are: post-red (write code), post-green (refactor or close), post-refactor (close).
   - If the last entry is `red→fail`, the next step is to make the test pass.
   - If the last entry is `green→pass`, you can refactor or mark done.

4. **Or pick the next task.**
   ```
   python scripts/next_task.py --feature F --specs-root .claude/specs
   ```
   Empty JSON `{}` means everything pending is either done, blocked, or has
   unmet dependencies — surface the blocked tasks to the user.

## Blocked tasks

A `blocked` task records *why* it's blocked in `blockers`. Common reasons:

- External dependency unavailable (third-party API down, missing credentials).
- Upstream task incomplete and not reflected in `depends_on`.
- Spec deviation needed — implementation can't honor PRD/SDD without changes.
- Awaiting a human decision.

To unblock:

1. Resolve the blocker out of band.
2. Patch the task to clear `blockers` and reset `status` to `pending` (or
   `in-progress` if mid-cycle):
   ```bash
   echo '{"tasks": {"T-007": {"status": "pending", "blockers": []}}}' \
     | python scripts/state_manager.py update --feature F \
         --specs-root .claude/specs
   ```

## Failed tasks

A `failed` task means three TDD-cycle attempts produced no working green.
Per the systematic-debugging rule, this is an architectural signal, not a
patch-it-harder signal. The recovery is **not** a fourth attempt:

1. Mark the task `blocked` with a blocker note describing the architectural mismatch.
2. Open a spec deviation (see `spec-deviation` skill).
3. Get user approval, update SDD/PLAN, re-init or patch state.

## Crash mid-write

If the harness crashes between a green-pass and the `state_manager.py update`
call, you'll have working code but state shows `in-progress`. That is fine:

- Re-run the test suite to confirm green.
- Record a green→pass step if missing.
- Patch status to `done`.

The history is the source of truth, not the user's memory.
