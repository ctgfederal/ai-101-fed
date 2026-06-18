---
description: "Create feature specifications with intelligent intake validation, type detection, and confidence-based routing"
argument-hint: "feature description [--type=api|ui|db|integration] [--fast-track]"
allowed-tools: ["Task"]
---

# /specify - 10X Feature Specification Workflow

**Feature**: $ARGUMENTS

## Coding Identity

Apply the **principled-coder** framework (`@agents/principled-coder.md`) to every requirement, design choice, and task in PRD/SDD/PLAN. The four pillars govern in order:

1. **Simplicity** — boring patterns, works out of the box, readable cold
2. **Modularity** — hard boundaries across TUI, commands, CLI, teams, agents, run; explicit contracts; no cross-module logic bleed
3. **Security** — open-by-default or locked-by-default via config; fed on-prem capable (DOE, National Labs, NASA)
4. **Scalability** — stateless, horizontal; 10k+ tx/min across 10–20 coordinated instances

Each requirement must have an acceptance criterion tied to at least one pillar. Module boundaries must be explicit in the SDD. Tasks in PLAN should not cross module boundaries. When priorities conflict, resolve in this order.

## What This Does

Creates comprehensive feature specifications (PRD → SDD → PLAN) with intelligent automation:

**10X Features**:
- ✓ **Intake Validation** - Analyzes clarity and completeness
- ✓ **Type Detection** - Auto-selects templates (API, UI, DB, Integration)
- ✓ **Confidence Routing** - Fast-track for simple features
- ✓ **Deterministic Scripts** - Zero AI tokens for setup/validation
- ✓ **Smart Templates** - Type-specific guidance and checklists

## How It Works

```
Feature Description
   ↓
Detect Prior Work:
   ├─ .claude/brainstorms/ → requirements, scope, approach
   ├─ .claude/decisions-log.md → design decisions (search for feature section)
   ├─ .claude/solutions/ → relevant past solutions
   └─ (deepened content embedded in decisions.md)
   ↓
Validate & Score (AI) — boosted by prior context
   ↓
Detect Type (AI) → Select Template
   ↓
Route by Confidence:
   - High (>70%) → Fast-track (single review)
   - Medium (40-70%) → Standard (phase approvals)
   - Low (<40%) → Enhanced (extra validation)
   ↓
Initialize (Script) → Generate Specs (AI) → Lint (Script)
   ↓
4 Files Created
```

## Arguments

**Basic**: `/specify <feature-description>`
- Auto-validates and detects type
- Confidence-based routing

**With Type**: `/specify <description> --type=api`
- Skip type detection
- Use specific template
- Options: `api`, `ui`, `db`, `integration`

**Fast-Track**: `/specify <description> --fast-track`
- Skip confidence check
- Generate all docs at once
- Single approval gate
- Best for: CRUD, simple features

## Prior Work Detection

Before intake validation, auto-detect outputs from earlier workflow stages:

### Brainstorm Detection
```bash
ls .claude/brainstorms/*{feature}* 2>/dev/null
```
If found: Load chosen approach, scope decisions, requirements, and open questions. Feed into PRD generation — don't re-ask what's already decided.

### Build Decisions Detection
```bash
grep -l "## ${feature}" .claude/decisions-log.md 2>/dev/null
```
If found: Load all logged decisions for this feature from `.claude/decisions-log.md` (architecture, data model, API, security, etc.). Feed into SDD generation — every D-NNN decision maps to a design section. If deepened (contains `### Research Insights`), include research findings.

### Solutions Archive Search
```bash
# Search for relevant past solutions
grep -rl "tags:.*{relevant-tech}" .claude/solutions/ 2>/dev/null
grep -rl "module:.*{feature-module}" .claude/solutions/ 2>/dev/null
```
If found: Reference in PRD (known pitfalls) and SDD (proven patterns). Link in README.md.

### Context Boost

Prior work increases intake confidence:
- Brainstorm exists → +15% confidence
- Build decisions exist → +20% confidence
- Both exist → +30% confidence (likely fast-track eligible)

## Prerequisites

**Steering docs must exist** - Run `/create-steering-docs` first.

## Templates by Type

| Type | Template | Best For |
|------|----------|----------|
| **api** | PRD-api.md | REST/GraphQL endpoints, services |
| **ui** | PRD-ui.md | Pages, components, user interactions |
| **db** | PRD-db.md | Schema changes, migrations, data models |
| **integration** | PRD-integration.md | External APIs, third-party systems |
| **generic** | PRD.md | Mixed or unclear features |

## Confidence-Based Routing

| Intake Score | Type Score | Workflow |
|--------------|------------|----------|
| >70% | >80% | Fast-track: 1 review |
| >70% | 50-80% | Standard: 3 reviews |
| 40-70% | Any | Standard: 3 reviews |
| <40% | Any | Request clarification |

## Scripts vs AI

**Scripts (deterministic, fast)**:
- Steering doc validation
- Spec ID generation
- Directory creation
- Template variable substitution
- Completeness linting

**AI (intelligent, flexible)**:
- Intake validation & scoring
- Feature type detection
- Requirements generation
- Design decisions
- Task breakdown

## Output Location

```
.claude/specs/{ID}-{feature-name}/
├── README.md    # Metadata, decisions, learnings
├── PRD.md       # Requirements (type-specific)
├── SDD.md       # Solution design
└── PLAN.md      # Implementation tasks
```

## Examples

**High Confidence (Fast-track)**:
```bash
/specify Create REST API endpoint for user registration with email/password login and JWT tokens
```
→ Detected as API, 85% confidence, fast-track enabled

**Medium Confidence (Standard)**:
```bash
/specify Add user authentication
```
→ Needs clarification, will suggest improvements

**With Type Override**:
```bash
/specify Improve dashboard performance --type=ui
```
→ Uses UI template, standard workflow

**Explicit Fast-Track**:
```bash
/specify Add delete button to user profile --fast-track
```
→ Skips routing, generates all docs at once

## Git Workflow (Recommended)

After spec is created, create a feature branch:

```bash
# Create feature branch for this spec
git checkout develop 2>/dev/null || git checkout main
git checkout -b "feature/{ID}-{feature-name}"

# Commit the spec
git add ".claude/specs/{ID}-{feature-name}/"
git commit -m "spec({ID}): Add specification for {feature-name}

- PRD: Product requirements
- SDD: System design
- PLAN.md: Implementation phases"
```

This keeps spec work isolated until implementation is complete.

## Next Steps

After specifications approved:
- **Implement**: `/implement {ID}` - Execute the plan (on feature branch)
- **Validate**: `/validate {ID}` - Check spec quality
- **Review**: `/review {ID}` - Post-implementation review (commits changes)
- **Compound**: `/compound` - Document solutions discovered during implementation

## Prior Steps (Optional)

Before specification:
- **Brainstorm**: `/brainstorm {topic}` - Explore ideas and requirements
- **Build**: `/build {feature}` - Walk through every design decision
- **Deepen**: `/deepen {feature}` - Enrich decisions with research

## Notes

- Intake validation catches unclear requests early
- Type detection selects optimal template
- Scripts handle 40% of workflow (zero AI cost)
- Fast-track saves 60% time for simple features
- All templates managed by skills, not this command
- Auto-detects brainstorm/build/deepen outputs to avoid re-asking decided questions
- Solutions archive searched for relevant past learnings
