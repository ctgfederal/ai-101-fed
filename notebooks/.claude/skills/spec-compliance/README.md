# spec-compliance

Verify a working implementation matches its approved spec by parsing the PRD's `REQ-NNN` requirements and the SDD's `COMP-NNN` components, scanning the repo for evidence, and emitting a markdown compliance report. Status is one of `compliant`, `partial`, `non-compliant`. Do NOT use to write or grade specs (use `spec-prd-generator`, `spec-sdd-generator`, or `spec-validation`), to do free-form code review, or to run tests.

## Quick Start

```
spec-compliance/
├── SKILL.md
├── templates/
│   ├── compliance-report.md.template
│   └── payload.example.json
├── scripts/
│   ├── parse_spec.py
│   ├── check_compliance.py
│   ├── write_report.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── compliance-rubric.md
│   └── deviation-types.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/compliance, check spec compliance, does the implementation match the spec, verify implementation against spec, compliance report, PRD compliance check, SDD compliance check, spec to code gap analysis

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
