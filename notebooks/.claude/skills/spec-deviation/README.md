# spec-deviation

Capture implementation deviations from approved specs as structured `## Deviations` blocks appended to the SDD. Allocates monotonic `DEV-NNN` IDs, validates payloads against the deviation schema, and renders blocks deterministically. Do NOT use for trivial differences (track as PLAN TODOs), wholesale spec rewrites (regenerate via `/specify`), or to bypass approval.

## Quick Start

```
spec-deviation/
├── SKILL.md
├── templates/
│   ├── deviation-block.md.template
│   └── payload.example.json
├── scripts/
│   ├── validate_deviation.py
│   ├── allocate_deviation_id.py
│   ├── append_deviation.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── deviation-schema.md
│   ├── approval-workflow.md
│   └── when-to-deviate.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/deviation, spec deviation, log a deviation, log deviation, deviate from spec, implementation can't follow spec, DEV-, record a spec deviation

## Tools required
Read, Write, Edit, Bash, Grep, Glob

## Recommended model
`claude-sonnet-4-6`

## Version
2.0.0

## Validation
```bash
python /Users/joshschultz/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/ tests/evals/
```
