# Example: PLAN with one ok task and two fail tasks

Demonstrates the full pipeline: `parse_tasks.py` → `validate_tasks.py` → `write_report.py` → `validate_output.py`.

## Files

- `input-plan.md` — fixture PLAN with three tasks.
- `input-prd.md` — fixture PRD defining REQ-101, REQ-102, REQ-103.
- `input-sdd.md` — fixture SDD defining COMP-001, COMP-002, COMP-003.
- `payload.json` — JSON output produced by `validate_tasks.py`.
- `expected-report.md` — rendered report produced by `write_report.py`.

## Flow

```bash
python ../../scripts/parse_tasks.py --plan input-plan.md > /tmp/tasks.json
python ../../scripts/validate_tasks.py --tasks /tmp/tasks.json --prd input-prd.md --sdd input-sdd.md --plan input-plan.md > /tmp/payload.json
python ../../scripts/write_report.py --payload /tmp/payload.json --out /tmp/report.md
python ../../scripts/validate_output.py --file /tmp/report.md --payload /tmp/payload.json
```

## What this demonstrates

- **T-001 → ok** — clean foundation task, all fields present, acceptance is measurable (`passes`).
- **T-002 → fail** — missing `_TDD:_` line, so `tdd_step` is empty and validation fails.
- **T-003 → fail** — acceptance text "should work end to end" is rejected by the measurable-acceptance rubric.
- **Verdict FAIL** — at least one fail forces FAIL per the verdict ladder.
