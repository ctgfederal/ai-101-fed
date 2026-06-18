# spec-plan-generator

Generate `.claude/specs/<feature>/PLAN.md` with phased TDD tasks covering every PRD `REQ-NNN` and SDD `COMP-NNN`.

```
spec-plan-generator/
├── SKILL.md
├── templates/{plan.md.template,payload.example.json}
├── scripts/{init_plan,extract_ids,allocate_task_ids,write_plan,validate_output}.py
├── knowledge/{README,plan-schema,tdd-cycle,phase-ordering}.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/specify, create the PLAN, generate the implementation plan, PLAN for, task plan for, TDD plan, spec the tasks

## Tools
Read, Write, Edit, Bash, Grep, Glob

## Model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation
```bash
python /Users/joshschultz/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/
```
