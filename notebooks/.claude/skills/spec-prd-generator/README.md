# spec-prd-generator

Generate a Product Requirements Document at `.claude/specs/<feature>/PRD.md` with EARS-format acceptance criteria, monotonic `REQ-NNN` IDs, MoSCoW prioritization, and references to steering docs. Do NOT use for design decisions, implementation tasks, or brainstorming.

## Quick Start

```
spec-prd-generator/
├── SKILL.md
├── templates/
│   ├── prd.md.template
│   └── payload.example.json
├── scripts/
│   ├── init_prd.py
│   ├── allocate_req_ids.py
│   ├── write_prd.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── ears-format.md
│   ├── prd-schema.md
│   └── steering-references.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/specify, create a PRD, generate requirements doc, PRD for, write the PRD, EARS requirements, spec the requirements

## Tools required
Read, Write, Edit, Bash, Grep, Glob

## Recommended model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation
```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/
```
