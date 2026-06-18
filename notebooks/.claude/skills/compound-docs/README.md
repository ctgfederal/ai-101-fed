# compound-docs

Capture solved problems as structured, searchable solution files in `.claude/solutions/`. Creates the compounding knowledge flywheel — solve once, apply forever — by writing one markdown file with YAML frontmatter that `/brainstorm`, `/build`, `/specify`, and `/review` automatically grep when working on related code. Do NOT use for trivial fixes (typos, formatting), open investigations, or architecture decisions (those go in ADRs / steering docs).

## Quick Start

```
compound-docs/
├── SKILL.md                      # Read this first
├── templates/
│   ├── solution.md.template      # Output template for a solution file
│   └── frontmatter.example.yaml  # Reference frontmatter shape
├── scripts/
│   ├── validate_frontmatter.py   # Validates a solution frontmatter against schema
│   ├── generate_slug.py          # Builds YYYY-MM-DD-<slug>.md filename
│   ├── search_solutions.py       # Greps the archive by tag/module/symptom/category
│   ├── write_solution.py         # Renders template, validates, writes the file
│   └── validate_output.py        # End-to-end validation of a written file
├── knowledge/
│   ├── categories.md             # Canonical 12-category list
│   ├── frontmatter-schema.md     # Authoritative field schema
│   └── search-patterns.md        # How other commands search this archive
├── validation/
│   └── quality-checklist.md      # Pass criteria for any output
├── tests/
│   ├── unit/                     # Per-script unit tests
│   ├── integration/              # Real-archive tests (gated by env var)
│   ├── evals/                    # LLM extraction evals
│   └── smoke/                    # End-to-end smoke
└── examples/
    └── n-plus-one-query/         # Full worked example (Rails N+1 fix)
```

## Triggers
- compound this
- document this solution
- save this fix to solutions
- /compound
- add to solutions archive
- capture this in compound docs
- write this up as a solution file
- we should remember how we fixed this

## Tools required
- Read
- Write
- Edit
- Bash
- Grep
- Glob

## Recommended model
`claude-sonnet-4-6`

## Version
2.0.0

## Validation

```bash
# Validate the skill itself
python ~/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .

# Run unit + smoke tests
pytest tests/unit/ tests/smoke/

# Validate a specific output file the skill produced
python scripts/validate_output.py --file <path-to-solution.md>
```
