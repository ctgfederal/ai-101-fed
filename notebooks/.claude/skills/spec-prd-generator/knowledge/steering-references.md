# Steering References

The PRD links to `.claude/steering/` rather than duplicating its content. Use anchor URLs.

## Required anchors

| In PRD | Steering anchor |
|---|---|
| Personas | `.claude/steering/product.md#user-personas` |
| Constraints | `.claude/steering/product.md#business-constraints` |
| Metrics framework | `.claude/steering/product.md#success-metrics-framework` |
| Current phase | `.claude/steering/roadmap.md#current-phase` |

## Why links not copies

Steering docs change. Inlined copies drift. Linked anchors stay consistent.

## When steering is missing

If `.claude/steering/product.md` or `roadmap.md` doesn't exist, halt the PRD generation and tell the user to run `steering-docs-creator` first. Don't fabricate personas or metrics frameworks.
