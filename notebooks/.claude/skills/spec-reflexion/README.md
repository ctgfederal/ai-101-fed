# spec-reflexion

Two-part learning capture during spec-driven development. Part 1 appends
phase-boundary insights to a spec's `README.md` (local). Part 2 filters
globally-useful items and promotes them to typed auto-memory files at
`~/.claude/projects/<sanitized-cwd>/memory/<type>_<slug>.md` with an updated
`MEMORY.md` index. Do NOT use for free-form journaling, to author the spec
itself, or to capture solved-problem solutions (use `compound-docs`).

## Quick Start

```
spec-reflexion/
├── SKILL.md
├── templates/
│   ├── memory-file.md.template
│   ├── spec-readme-learnings.md.template
│   └── payload.example.json
├── scripts/
│   ├── extract_learnings.py
│   ├── classify_learning.py
│   ├── promote_to_memory.py
│   └── validate_output.py
├── knowledge/
│   ├── README.md
│   ├── learning-types.md
│   ├── local-vs-global.md
│   └── memory-format.md
├── validation/quality-checklist.md
├── tests/{unit,integration,evals,smoke}/
└── examples/josh-error-types/
```

## Triggers
/reflect, phase boundary reflection, save this learning, promote to memory, capture spec learnings, what did we learn from this spec, update spec README with learnings, memorize this insight

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
