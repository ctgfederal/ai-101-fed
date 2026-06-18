# spec-task-validator

Validate `T-NNN` tasks from a `PLAN.md` against the requirements (`REQ-NNN` in PRD) and design (`COMP-NNN` in SDD) they reference. Each task is graded on ID format, valid cross-references, presence of measurable acceptance, an explicit TDD step, and an allowed phase. Renders a per-task validation report with `ok` / `warn` / `fail` verdicts. Do NOT use for free-form code review, 3Cs spec scoring, or to author tasks.

## Quick Start

```
spec-task-validator/
├── SKILL.md
├── templates/
│   ├── task-validation-report.md.template
│   └── payload.example.json
├── scripts/
│   ├── parse_tasks.py
│   ├── validate_tasks.py
│   ├── write_report.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── task-schema.md
│   ├── acceptance-rubric.md
│   └── verdict-thresholds.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/validate task, validate task, validate this task, is this task ready, task validation, validate PLAN tasks, check task readiness, validate T-

## Tools required
Read, Write, Edit, Bash, Grep, Glob

## Recommended model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation
```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/ tests/evals/
```
