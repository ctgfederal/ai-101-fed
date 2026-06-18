# When to Update Steering

Steering docs are **stable context**. They change when the underlying facts change — not on every feature.

## Cadence

| Cadence | Action |
|---------|--------|
| Project start | Scaffold all four docs. Fill all `[NEEDS CLARIFICATION]` markers. |
| Annual | Review every section; refresh stale facts. |
| Per-event | Update only the section affected (see triggers below). |

## Event triggers

| Trigger | Doc | Section |
|---------|-----|---------|
| New tech stack adopted | `tech.md` | Tech Stack |
| New library standardized | `tech.md` | Library Choices |
| CI gate threshold change | `tech.md` | Build & CI |
| New persona discovered | `product.md` | User Personas |
| New compliance regime | `product.md` | Business Constraints |
| Major refactor (folder move) | `structure.md` | Folder Layout |
| Module split | `structure.md` | Module Boundaries |
| Phase transition | `roadmap.md` | Current Phase + Phase Definitions |
| New milestone | `roadmap.md` | Milestones |

## When NOT to update

- Per-feature requirements — those go in `.claude/specs/<feature>/PRD.md`.
- Per-feature design decisions — those go in `.claude/specs/<feature>/SDD.md`.
- Per-feature tasks — those go in `.claude/specs/<feature>/PLAN.md`.
- Architecture decisions about a single feature — those are ADRs.

## Update mechanics

Use `update_doc.py`, never hand-edit:

```bash
python scripts/update_doc.py \
  --steering-root .claude/steering \
  --doc tech \
  --section "Tech Stack" \
  --body - <<'EOF'
[new content here]
EOF
```

`update_doc.py` replaces only the body under the named heading; surrounding sections, frontmatter, and the heading itself are preserved.
