# spec-requirement-tracer

Build and validate a traceability matrix at `.claude/specs/<feature>/TRACEABILITY.md` proving every PRD `REQ-NNN` flows through ≥1 SDD `COMP-NNN`, ≥1 PLAN `T-NNN`, and ≥1 code/test reference.

```
spec-requirement-tracer/
├── SKILL.md
├── templates/{traceability-matrix.md.template,payload.example.json}
├── scripts/{extract_ids,build_matrix,write_matrix,validate_output}.py
├── knowledge/{README,traceability-rules,coverage-statuses,reading-the-matrix}.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/trace, trace requirements, traceability matrix, show coverage matrix, are all requirements covered, requirement coverage report, REQ to code mapping, is every REQ implemented

## Tools
Read, Write, Edit, Bash, Grep, Glob

## Model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation
```bash
python /Users/joshschultz/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/ tests/evals/
```
