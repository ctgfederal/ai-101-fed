# spec-validation

Score a specification, implementation, or piece of understanding against the **3 Cs framework** — Completeness, Consistency, Correctness — using mechanical checks. Emits a markdown report with 0-10 sub-scores, an overall score, and a verdict (PASS / WARN / FAIL). Do NOT use for free-form code review, security review, or to author the spec.

## Quick Start

```
spec-validation/
├── SKILL.md
├── templates/
│   ├── 3cs-report.md.template
│   └── payload.example.json
├── scripts/
│   ├── score_3cs.py
│   ├── write_report.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── 3cs-rubric.md
│   └── score-thresholds.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/example-1/
```

## Triggers
/validate, validate this spec, 3 Cs check, score the spec, is this spec ready, completeness consistency correctness, check spec quality, validate the implementation against the spec

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
