# `.claude/` — Spec-Driven Development Workflow

This directory ships a complete Claude Code workflow: agents, commands, and
skills that turn AI-assisted coding from "vibes-based" into a repeatable,
auditable process.

**Use it two ways:**

1. **Read it** — Notebook 08 (`08_coding_workflow.ipynb`) walks through
   every file here, with real shipped artifacts in `examples/`.
2. **Adopt it** — Copy this entire directory into your own project's
   root as `.claude/`. Claude Code auto-discovers it and you get the
   commands, agents, and skills immediately.

```bash
# in your project root:
cp -R /path/to/ai-roadshow/.claude .
# now `/brainstorm`, `/build`, `/specify`, etc. are available
```

---

## What's here

```
.claude/
├── agents/          # 29 specialist agents
│   ├── principled-coder.md          # the identity that governs everything
│   ├── backend-developer.md         # implementation specialists
│   ├── frontend-developer.md        # (spawned by /implement)
│   ├── ...
│   ├── architect-reviewer.md        # review specialists
│   ├── security-engineer.md         # (spawned by /review)
│   ├── ...
│   └── spec-loader.md               # workflow utilities
├── commands/        # 7 workflow commands
│   ├── create-steering-docs.md      # one-time project context
│   ├── brainstorm.md                # PLAN — WHY
│   ├── build.md                     # PLAN — WHAT decisions
│   ├── deepen.md                    # PLAN — research enrichment
│   ├── specify.md                   # PLAN — HOW concrete (PRD → SDD → PLAN)
│   ├── implement.md                 # DO — TDD swarm
│   └── review.md                    # VALIDATE — parallel reviewers
├── skills/          # 44 skills with full templates and scripts
│   └── INDEX.md     # Complete skill registry
└── examples/        # Real shipped artifacts (study material)
    ├── steering/                    # arc's actual product/tech/structure docs
    ├── brainstorms/                 # NLIT 2026 brainstorm (real)
    ├── spec-kimi/                   # SPEC-001 PRD/SDD/PLAN (shipped)
    └── adrs/                        # ADR-017A (shipped)
```

---

## The chain at a glance

```
/create-steering-docs        ← run once per project
       ↓
/brainstorm <idea>           ← PLAN: WHY (audience, outcomes, principles)
       ↓
/build <feature>             ← PLAN: WHAT (decisions with tradeoffs)
       ↓
/deepen <feature>            ← PLAN: research enrichment in parallel
       ↓
/specify <feature>           ← PLAN: HOW (PRD → SDD → PLAN)
       ↓
/implement <spec-id>         ← DO (TDD swarm of specialists)
       ↓
/review <spec-id>            ← VALIDATE (parallel reviewers, ADRs, monitoring plan)
```

Five phases of plan, one of do, one of validate. **The ratio is the
point** — most teams flip it.

---

## The principled-coder identity

Every command in the chain references `agents/principled-coder.md` —
four ranked priorities that govern every decision:

1. **Simplicity** wins over cleverness
2. **Modularity** wins over monoliths
3. **Security** wins over convenience
4. **Scalability** wins over "fast enough"

Read the file. It's short. It's the identity that makes the rest of the
workflow consistent across sessions, agents, and people.

---

## Tier-aware decisions

Commands like `/build` apply **federal auto-apply**: when a NIST 800-53,
FedRAMP, CMMC, FISMA, ITAR, or OWASP Agentic Top 10 mandate dictates the
correct answer, the decision is auto-applied with the citation rather
than asked. This keeps lab/SCIF deployments compliant by default.

---

## Quickstart

After copying this `.claude/` into your project root:

```
# Set up project context (one-time)
/create-steering-docs

# Build a small feature end-to-end
/brainstorm  add token-budget warning to agent loop
/build       token-budget-warning
/deepen      token-budget-warning
/specify     token-budget-warning
/implement   <spec-id>
/review      <spec-id>
```

You'll find:
- A `.claude/brainstorms/<date>-token-budget-warning.md` — your WHY
- An entry in `.claude/decisions-log.md` — your WHAT
- A `.claude/specs/<spec-id>/{PRD,SDD,PLAN,README}.md` — your HOW
- Tests + code in your project — your DO
- ADRs + monitoring plan in `.claude/adrs/` — your VALIDATE

Every artifact is markdown, version-controlled, and reviewable as a PR.
