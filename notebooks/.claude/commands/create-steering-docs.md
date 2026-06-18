---
description: "Creates steering documents (product.md, tech.md, structure.md, roadmap.md) that give Claude persistent knowledge about your project"
allowed-tools: ["Skill", "Task", "Read", "Write", "Bash", "Grep", "Glob", "AskUserQuestion"]
---

# Create Steering Docs

Creates project-level steering documents that provide persistent context for all feature specifications.

## Invoke Skill

```
Skill(skill: "steering-docs-creator")
```

The skill contains:
- Full procedures for analyzing codebase and creating docs
- Templates for each steering document
- Validation checklists
- Guidelines for when to ask vs infer

## Quick Reference

**Output location**: `{project}/.claude/steering/`

**Documents created**:
| Document | Purpose |
|----------|---------|
| `product.md` | Vision, personas, metrics framework, constraints |
| `tech.md` | Stack, commands, quality thresholds, patterns |
| `structure.md` | Architecture, directories, boundaries |
| `roadmap.md` | Current phase, execution framework |

**Templates location**: `.claude/skills/steering-docs-creator/templates/`

## Next Steps After Creation

1. Review each doc and fill in any remaining `[NEEDS CLARIFICATION]` markers
2. Run `/specify [feature]` to create feature specifications
