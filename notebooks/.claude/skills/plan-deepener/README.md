# plan-deepener

Enrich a build-decisions or PLAN document with parallel research findings — best practices, edge cases, solutions archive matches, external documentation, and matched skills — by spawning Explore sub-agents per major section, deduplicating their findings, and appending a `### Research Insights` block under each section while preserving original content. Do NOT use to *create* decisions or plans (those are `/build` and `/specify`), to write code, or as a substitute for actually solving the design problems — this skill annotates existing thinking, it doesn't replace it.

## Quick Start

```
plan-deepener/
├── SKILL.md                        # Read this first
├── templates/
│   ├── research-insights.md.template       # Per-section block
│   └── deepening-summary.md.template       # Top-of-doc summary
├── scripts/
│   ├── parse_target.py             # Extract sections, tech, categories, open questions
│   ├── match_skills.py             # Match keywords against ~/.claude/skills frontmatter
│   ├── merge_research.py           # Insert insights blocks + summary
│   └── validate_output.py          # Validate the deepened doc
├── knowledge/
│   ├── research-protocol.md        # Parallel-research dispatch rules
│   ├── solutions-search.md         # Use compound-docs/search_solutions
│   └── dedup-rules.md              # How to merge findings cleanly
├── validation/
│   └── quality-checklist.md
├── tests/
│   ├── unit/                       # Per-script tests
│   ├── evals/                      # Synthesis-quality evals
│   └── smoke/                      # End-to-end
└── examples/
    └── example-1/                  # feature-search before/after
```

## Triggers
- /deepen
- deepen this plan
- enrich the decisions
- research insights for
- add research to plan
- deepen build decisions
- find related solutions
- what should I know about this design

## Tools required
- Read, Write, Edit, Bash, Grep, Glob, Task

## Recommended model
`claude-sonnet-4-6`

## Version
2.0.0

## Validation

```bash
python ~/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/
```
