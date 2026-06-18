# Steering Schema

The four steering docs each have a fixed set of `## ` section headings. Section headings define the public anchor surface that downstream skills link to. **Renaming a heading is a breaking change.**

## Anchor convention

Section headings slugify to GitHub-style anchors: lowercase, alphanumerics preserved, spaces become hyphens, all other punctuation dropped.

Examples:
- `## User Personas` → `product.md#user-personas`
- `## Tech Stack` → `tech.md#tech-stack`
- `## Layer Model` → `structure.md#layer-model`
- `## Current Phase` → `roadmap.md#current-phase`

## product.md — required sections (in order)

1. `## Mission`
2. `## User Personas`
3. `## Business Constraints`
4. `## Success Metrics Framework`
5. `## Domain Glossary`

## tech.md — required sections (in order)

1. `## Tech Stack`
2. `## Conventions`
3. `## Library Choices`
4. `## Build & CI`
5. `## Observability`

## structure.md — required sections (in order)

1. `## Layer Model`
2. `## Folder Layout`
3. `## Naming Rules`
4. `## Dependency Direction`
5. `## Module Boundaries`

## roadmap.md — required sections (in order)

1. `## Current Phase`
2. `## Phase Definitions`
3. `## Milestones`
4. `## Out-of-Scope`

## What "in order" means

The validator (`validate_steering.py` and `validate_output.py`) requires the headings appear in the listed order. Adding a new section between existing ones requires updating this schema first.

## Adding a new section

1. Update this file (add the heading at the right position).
2. Update the matching template in `templates/`.
3. Update `usage-by-other-skills.md` if any downstream skill should now link to it.
4. Run `pytest tests/unit/test_validate_steering.py` and adjust expectations.
