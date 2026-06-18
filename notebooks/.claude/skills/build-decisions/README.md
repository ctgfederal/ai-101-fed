# build-decisions

Walk every design decision a feature requires — interactively, one at a time — through 12 ordered categories. Auto-applies federal mandates. Ranks options by Simplicity → Modularity → Security → Scalability. Allocates monotonic global decision IDs (`D-NNN`). Appends every choice to `.claude/decisions-log.md`. State persists in `.claude/builds/<feature>/state.json` so sessions can be paused and resumed. Do NOT use for shaping vision (that's `/brainstorm`), writing the formal spec (that's `/specify`), implementation, or pure architecture review.

## Quick Start

```
build-decisions/
├── SKILL.md                       # Read this first
├── templates/
│   ├── feature-section.md.template       # Top-level section in decisions-log.md
│   ├── decision-section.md.template      # Per-category sub-section
│   └── state.example.json                # Example state-file shape
├── scripts/
│   ├── state_manager.py                  # init/read/update state JSON
│   ├── allocate_ids.py                   # Monotonic D-NNN allocation
│   ├── federal_mandates.py               # Lookup table (auto-apply)
│   ├── append_decisions.py               # Render + append section
│   └── validate_output.py                # Validate appended section
├── knowledge/
│   ├── decision-categories.md            # 12 ordered categories
│   ├── federal-mandates.json             # Machine-readable mandate table
│   ├── priority-framework.md             # Ranking rules
│   ├── lockdown-tiers.md                 # personal/enterprise/federal model
│   └── id-convention.md                  # D-NNN rules
├── validation/
│   └── quality-checklist.md
├── tests/
│   ├── unit/                             # Per-script tests
│   ├── evals/                            # Option-presentation evals
│   └── smoke/                            # End-to-end
└── examples/
    └── example-1/                        # feature-search worked example
```

## Triggers
- /build
- let's walk the design decisions
- build decisions for
- design decisions before specify
- make build choices
- walk the architecture
- design walkthrough
- go through the build decisions

## Tools required
- Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion

## Recommended model
`claude-sonnet-4-6`

## Version
3.0.0

## Validation

```bash
python /Users/joshschultz/.claude/skills/skill-creator/scripts/validate_skill.py --skill-dir .
pytest tests/unit/ tests/smoke/
```
