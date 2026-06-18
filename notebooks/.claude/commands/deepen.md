---
description: "Enrich build decisions or plans with parallel research — best practices, edge cases, solutions archive, external docs"
argument-hint: "[feature name, build path, or spec ID]"
allowed-tools: ["Task", "Read", "Grep", "Glob", "Write"]
---

# /deepen - Research Enrichment

**Target**: $ARGUMENTS

## Coding Identity

Apply the **principled-coder** framework (`@agents/principled-coder.md`) to all research, recommendations, and enrichment. Every finding must be filtered through the four pillars in order:

1. **Simplicity** — boring patterns, works out of the box, readable cold
2. **Modularity** — hard boundaries across TUI, commands, CLI, teams, agents, run; no logic bleed
3. **Security** — open-by-default or locked-by-default via config; fed on-prem capable (DOE, National Labs, NASA)
4. **Scalability** — stateless, horizontal; 10k+ tx/min across 10–20 coordinated instances

Research outputs must explicitly call out: scalability ceiling, on-prem/air-gapped posture, and module-boundary implications. When priorities conflict, resolve in this order.

## What This Does

Spawns parallel research agents to enrich a build decision document or PLAN with best practices, edge cases, past solutions, and external documentation. Makes the 80/20 split real — heavy research BEFORE any code.

## How It Works

```
Load target (build decisions or PLAN.md)
   ↓
Search solutions archive for relevant learnings
   ↓
Parse sections → spawn parallel research per section
   ↓
Match and apply relevant skills
   ↓
Synthesize all findings
   ↓
Enhance document in-place
```

## Execution

### 1. Load Plan Deepener Skill

Load `.claude/skills/plan-deepener/SKILL.md` and follow its procedures.

### 2. Locate Target

Search in order:
1. `.claude/decisions-log.md` — find the section for `{feature}` (from `/build`)
2. `.claude/specs/{feature}/PLAN.md` (from `/specify`)
3. Direct path if provided

### 3. Search Solutions Archive

```bash
ls .claude/solutions/ 2>/dev/null
```

For each solution file, compare frontmatter tags against target content. Surface relevant past learnings.

### 4. Spawn Parallel Research

For each major section, spawn Task agents in parallel:

```
Task(subagent_type: "Explore", "Research best practices for: {section topic}")
Task(subagent_type: "Explore", "Research edge cases for: {section topic}")
```

### 5. Match Skills

Scan available skills for domain matches:
- API sections → api-designer patterns
- Security sections → security best practices
- Database sections → migration patterns
- Testing sections → test strategy patterns

### 6. Enhance Document

Add research insights to each section:
- Best practices with citations
- Edge cases and handling strategies
- Performance considerations
- Code examples from research
- Links to relevant solutions

### 7. Summary

Add enhancement summary at top of document.

## Output

Updates target document in-place with `### Research Insights` subsections.

## Next Steps

- `/specify {feature}` — Create formal spec using enriched decisions
- `/implement {ID}` — If enriching an existing PLAN

## Notes

- Uses Task agents for parallel research (exception to workflow rule)
- Solutions archive searched FIRST — don't rediscover known patterns
- Preserves all original content — only adds
- Can be run multiple times for deeper enrichment
