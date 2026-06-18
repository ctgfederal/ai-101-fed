# Architecture Research Protocol

Before writing any component, research the existing codebase. Designs that ignore conventions become technical debt.

## Where to look

| Question | Where |
|---|---|
| What's the project's layer convention? | `.claude/steering/structure.md` |
| What's the existing tech stack? | `.claude/steering/tech.md` |
| Are there similar features already built? | `grep -r <pattern> src/`, codebase explore |
| Are there prior solutions to similar problems? | `compound-docs/scripts/search_solutions.py --tag <tech>` |
| Are there prior decisions on this design space? | `.claude/decisions-log.md` (search by keyword) |

## What to capture

- **Existing patterns to follow** — folder layout, naming, error-handling style, logging style.
- **Existing components to reuse or extend** — don't reinvent.
- **Constraints that shape the design** — frameworks in use, infra limits.
- **Anti-patterns the team has hit before** — from the solutions archive.

## Use the research

- Architecture description names the existing patterns being followed.
- Component `dependencies` field references existing components by their actual names.
- Alternatives section explains why competing patterns were rejected (often: "doesn't match the project's existing layer model").
