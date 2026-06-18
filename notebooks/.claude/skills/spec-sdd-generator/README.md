# spec-sdd-generator

Generate `.claude/specs/<feature>/SDD.md` bridging PRD requirements to components with full traceability.

```
spec-sdd-generator/
├── SKILL.md
├── templates/{sdd.md.template,payload.example.json}
├── scripts/{init_sdd,extract_req_ids,write_sdd,validate_output}.py
├── knowledge/{README,sdd-schema,architecture-research,steering-references}.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/specify, create the SDD, generate solution design, SDD for, design doc for, write the design, spec the design

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
