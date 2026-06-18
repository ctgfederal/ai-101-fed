# brainstorming

Explore the WHY and FOR WHOM behind an idea — inspiration, audience, use cases, desired outcomes, and guiding principles — through one-question-at-a-time interactive dialogue, then capture the result as a structured markdown file under `.claude/brainstorms/YYYY-MM-DD-<topic>.md` for use by `/build` and `/specify`. Do NOT use for making design decisions (that's `/build`), writing formal specs (that's `/specify`), or any task where the WHY is already settled.

## Quick Start

```
brainstorming/
├── SKILL.md                     # Read this first
├── templates/
│   ├── brainstorm.md.template   # Output template
│   └── question-progression.md  # 8-question reference
├── scripts/
│   ├── init_brainstorm.py       # Compute target file path
│   ├── write_brainstorm.py      # Render template + write file
│   └── validate_output.py       # Validate frontmatter + body
├── knowledge/
│   ├── question-flow.md         # Clarity assessment + dialogue rules
│   ├── brainstorm-schema.md     # Field schema + antipatterns
│   └── handoff.md               # Next-step options
├── validation/
│   └── quality-checklist.md
├── tests/
│   ├── unit/                    # Per-script tests
│   ├── evals/                   # Clarity-classification evals
│   └── smoke/                   # End-to-end
└── examples/
    └── example-1/               # AI code review for solo devs
```

## Triggers
- /brainstorm
- let's brainstorm
- I want to explore an idea
- help me think through
- I have a vague idea about
- what could we build for
- shape this concept
- explore the why

## Tools required
- Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion

## Recommended model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation

```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/
```
