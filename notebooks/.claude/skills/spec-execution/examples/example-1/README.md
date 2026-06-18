# Example: feature-search execution mid-run

Demonstrates the full deterministic core of `spec-execution`: init from a PLAN,
read state, find the next task, record TDD steps, and validate the result.

## Files
- `PLAN.md` — fixture plan with 5 tasks across 3 phases.
- `execution-state.json` — fixture state mid-run: T-001 and T-002 done, T-003 in-progress (red recorded), T-004 and T-005 pending.

## Flow

```bash
# Init state (would be skipped here — state already exists)
python ../../scripts/state_manager.py init \
    --feature feature-search --specs-root /tmp/specs

# Read state
python ../../scripts/state_manager.py read \
    --feature feature-search --specs-root /tmp/specs

# Ask "what's next?" — returns T-003 (the in-progress task)
python ../../scripts/next_task.py \
    --feature feature-search --specs-root /tmp/specs

# Record green pass for T-003
python ../../scripts/record_tdd_step.py \
    --feature feature-search --specs-root /tmp/specs \
    --task-id T-003 --step green --result pass

# Validate state
python ../../scripts/validate_output.py \
    --file /tmp/specs/feature-search/execution-state.json \
    --plan /tmp/specs/feature-search/PLAN.md
```

## What this demonstrates

- **State persistence** — `T-001` and `T-002` keep their full TDD history.
- **`depends_on` enforcement** — `T-005` cannot be picked next while `T-004` is `pending`.
- **In-flight task** — `T-003` shows the resume case: a `red→fail` is recorded; the next session must produce a green.
- **PLAN ↔ state cross-check** — every `T-NNN` in `PLAN.md` is also a key in `tasks`; `validate_output.py --plan` exits 0.
