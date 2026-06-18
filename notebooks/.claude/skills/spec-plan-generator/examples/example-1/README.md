# Example: Feature Search PLAN

End-to-end PLAN generation. Demonstrates 4-phase TDD-shaped tasks with full coverage.

```bash
python ../../scripts/init_plan.py --feature feature-search --specs-root /tmp/specs
python ../../scripts/allocate_task_ids.py --specs-root /tmp/specs --count 8
python ../../scripts/write_plan.py --payload payload.json --out /tmp/specs/feature-search/PLAN.md --prd /tmp/specs/feature-search/PRD.md --sdd /tmp/specs/feature-search/SDD.md
python ../../scripts/validate_output.py --file /tmp/specs/feature-search/PLAN.md --prd /tmp/specs/feature-search/PRD.md --sdd /tmp/specs/feature-search/SDD.md
```
