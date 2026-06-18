---
description: "Explore the WHY — inspiration, audience, use cases, outcomes, and guiding principles"
argument-hint: "[idea, spark, or topic to explore]"
allowed-tools: ["Read", "Grep", "Glob", "AskUserQuestion", "Write"]
---

# /brainstorm - Explore Why to Build

**Idea**: $ARGUMENTS

## What This Does

Explores the WHY and FOR WHOM through collaborative dialogue. Captures inspiration, audience, use cases, desired outcomes, and guiding principles. Does NOT make design decisions — that's `/build`.

## How It Works

```
Idea Description
   |
Check for existing solutions (.claude/solutions/)
   |
Assess clarity — is brainstorming even needed?
   |
Collaborative dialogue (one question at a time):
   - Inspiration (what triggered this?)
   - Projects (what are you imagining?)
   - Audience (who cares?)
   - Use Cases (how will people use it?)
   - Outcomes (what changes when this exists?)
   - Principles (what matters most?)
   - Constraints & Scope
   |
Capture to .claude/brainstorms/
```

## Execution

### 1. Load Brainstorming Skill

Load `.claude/skills/brainstorming/SKILL.md` and follow its procedures.

### 2. Check Solutions Archive

Search `.claude/solutions/` for previously solved similar problems. If relevant solutions exist, surface them.

### 3. Assess Clarity

If the idea already has clear vision, audience, and outcomes:
- Offer to skip straight to `/build` or `/specify`

### 4. Collaborative Dialogue

Use AskUserQuestion — one question at a time:
- Inspiration and motivation
- Specific projects being imagined
- Audience and personas
- Use cases and scenarios
- Desired outcomes
- Guiding principles
- Constraints and scope

### 5. Capture

Write to `.claude/brainstorms/YYYY-MM-DD-{topic}.md`

## Output

```
.claude/brainstorms/YYYY-MM-DD-{topic}.md
```

## Next Steps

- `/build` — Walk through design decisions interactively
- `/specify` — Jump straight to formal spec (for clear ideas)

## Notes

- WHY and FOR WHOM, not HOW (design decisions belong in /build)
- One question at a time — follow the user's energy
- Capture the motivation — it guides decisions later
- Auto-detected by `/build` and `/specify`
