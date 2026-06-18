# Usage by Other Skills

Steering anchors are a public contract. Downstream skills link to specific section anchors. Renaming or deleting a section breaks every PRD, SDD, and PLAN that referenced it.

## Skill → consumed anchors

### `spec-prd-generator`

| Anchor | Used in PRD section |
|--------|---------------------|
| `product.md#user-personas` | Personas |
| `product.md#business-constraints` | Risks and Constraints |
| `product.md#success-metrics-framework` | Success Metrics |
| `roadmap.md#current-phase` | Context References |

### `spec-sdd-generator`

| Anchor | Used in SDD section |
|--------|---------------------|
| `tech.md#tech-stack` | Tech Choices |
| `tech.md#conventions` | Conventions |
| `tech.md#library-choices` | Library Choices |
| `structure.md#layer-model` | Layered Architecture |
| `structure.md#folder-layout` | Directory Map |
| `structure.md#dependency-direction` | Component Boundaries |
| `structure.md#module-boundaries` | Component Boundaries |

### `spec-plan-generator`

| Anchor | Used in PLAN section |
|--------|----------------------|
| `roadmap.md#current-phase` | Context References |
| `roadmap.md#milestones` | Phase milestones |
| `tech.md#build--ci` | Quality gates |

## Breakage cost of renames

| Change | What breaks |
|--------|-------------|
| Rename a heading | Every existing PRD/SDD/PLAN linking to the old anchor 404s on click. |
| Delete a heading | Same as above, plus future spec generation cannot link the missing concept. |
| Reorder headings | Validator fails; spec generators may emit warnings. |
| Add a heading | Safe IF schema is updated first AND no downstream skill assumes the old set is exhaustive. |

## Consequence

If you must rename:
1. Update `steering-schema.md` first.
2. Update all downstream skill templates that referenced the old anchor.
3. Run a repo-wide search for `steering/<doc>.md#<old-anchor>` and update each hit.
4. Communicate the rename in the next phase transition note.
