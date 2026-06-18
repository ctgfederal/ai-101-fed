---
description: "Interactive decision walker — walks through every design decision with tradeoffs, logs choices, produces decision document for /specify. Ranks all outputs by simplicity → security → scalability → compliance."
argument-hint: "[feature name, brainstorm file path, or 'resume' to continue]"
allowed-tools: ["Read", "Grep", "Glob", "AskUserQuestion", "Write"]
---

# /build - Interactive Design Decision Walker

**Feature**: $ARGUMENTS

## Coding Identity

Apply the **principled-coder** framework (`@agents/principled-coder.md`) to every decision, tradeoff, and recommendation. The four pillars govern in this order:

1. **Simplicity** — boring patterns, works out of the box, readable cold
2. **Modularity** — hard boundaries across TUI, commands, CLI, teams, agents, run; no logic bleed
3. **Security** — open-by-default or locked-by-default controlled by config; fed on-prem capable (DOE, National Labs, NASA)
4. **Scalability** — stateless, horizontal; 10k+ tx/min across 10–20 coordinated instances

When priorities conflict, resolve in this order.

## What This Does

Walks through every design decision a feature requires — interactively, one at a time. Presents tradeoffs, asks for your call, logs decisions with reasoning. Produces a decision document that `/specify` and `/deepen` consume.

Inspired by the arcllm builder pattern: **Concept → Decision → Log → Next**.

## Priority Framework

All decisions are evaluated and ranked by the principled-coder pillars, in order:

1. **Simplicity** — fewest dependencies, lowest complexity, easiest to read and maintain
2. **Modularity** — hard domain boundaries (TUI, commands, CLI, teams, agents, run); swappable components with explicit contracts
3. **Security** — zero-trust, least-privilege, defense in depth; open-by-default or locked-by-default via config; fed on-prem ready (FedRAMP, NIST 800-53, CMMC, FISMA apply here)
4. **Scalability** — horizontal scale, stateless, shared-nothing; 10k+ tx/min × 10–20 instances

Options presented to the user are ordered by this ranking. When tradeoffs exist between priorities, explain the tension explicitly.

## Federal Auto-Apply Rule

When a federal mandate (FedRAMP, NIST 800-53, CMMC, FISMA, ITAR, EAR, or OWASP Agentic Top 10) dictates exactly one correct answer, **do not ask the question**. Instead:

1. State the decision
2. Cite the mandate (e.g., "NIST 800-53 AU-6: required")
3. Log it as `auto-applied: federal-mandate`
4. Move to the next decision

Examples of auto-applied decisions:
- Audit log retention period → NIST 800-53 AU-11 (minimum 1 year, recommended 3)
- Budget/cost tracking frequency → Daily + monthly (OMB A-123, FITARA)
- Credential storage → Never on filesystem (NIST 800-53 IA-5)
- Encryption at rest → AES-256 or equivalent (FIPS 140-2/3)
- Encryption in transit → TLS 1.2+ minimum (NIST 800-52r2)
- Authentication tokens → Short-lived, vault-backed (NIST 800-63B)
- Audit trail → Every state-changing operation (NIST 800-53 AU-2)
- Log integrity → Tamper-evident / append-only (NIST 800-53 AU-9)
- Inter-agent comms → mTLS required (NIST 800-53 SC-8)

The user should only be asked questions where genuine tradeoffs exist.

## Lockdown Model

The system has **one codebase** across all deployment contexts. Lockdown is achieved entirely through **TOML configuration + optional package extras** — never through code branches, feature flags in source, or conditional compilation.

### How It Works

```
pip install arcagent                     # Core — works for personal use
pip install arcagent[federal]            # Adds FIPS crypto, Vault, mTLS deps, SBOM tooling
pip install arcagent[enterprise]         # Adds SSO, audit export, compliance reporting
```

Then in the project's TOML config:
```toml
[security]
tier = "federal"    # "federal" | "enterprise" | "personal"
```

Setting `tier = "federal"` activates all mandated behaviors. Setting `tier = "personal"` disables enforcement — warnings only, user decides. Enterprise sits in between: enforces sensible defaults, allows override.

This applies uniformly across **arcllm**, **arcrun**, and **arcagent**. Each package reads the same tier from config and adjusts its behavior.

### Three Tiers

| Tier | Install | Config | Enforcement | UX |
|------|---------|--------|-------------|-----|
| `federal` | `[federal]` extras | `tier = "federal"` | Block — violations are hard errors, operations denied | Strict. User never sees optional features unless explicitly enabled. |
| `enterprise` | `[enterprise]` extras | `tier = "enterprise"` | Warn + default-on — violations log warnings, defaults are compliant but overridable | Professional. Compliance-ready out of the box, configurable. |
| `personal` | Base install | `tier = "personal"` | Warn + default-off — violations log info, nothing enforced, user opts in | Open. Feels lightweight. No friction unless user adds it. |

### Design Principles

- **Same code paths** — the core logic is identical across tiers. No `if tier == "federal"` scattered through business logic.
- **Policy layer** — a single policy enforcement point reads tier config and gates behavior (block / warn / allow).
- **Graduated strictness** — federal blocks, enterprise warns, personal informs.
- **Optional deps only for extras** — FIPS-validated crypto, Vault client, mTLS certs, SBOM generators. The core has zero dependency on these.
- **Config, not code** — switching tiers is a TOML change + optional `pip install`. No rebuild, no redeploy of different code.
- **Personal users never feel federal** — no compliance noise, no mandatory approvals, no audit overhead unless they want it.
- **Federal users get locked down by default** — install extras, set tier, done. No manual hardening checklist.

### How This Affects Build Decisions

Every decision in `/build` should answer: **What does the policy layer do at each tier?**

Format:
> "Federal: blocked without X. Enterprise: warns if missing X, defaults to Y. Personal: no enforcement, user configures if desired."

If a capability requires an optional dependency (e.g., FIPS crypto, Vault), note which extras package provides it.

## How It Works

```
Check for brainstorm output
   ↓
Search solutions archive for prior art
   ↓
Load or create build state (.claude/builds/{feature}/state.json)
   ↓
Walk through decisions one at a time:
   ├─ Check: Is this federally mandated? → Auto-apply if yes
   ├─ Explain concept (what and why)
   ├─ Present 2-4 options ranked by priority framework
   ├─ Note lockdown tier variations
   ├─ Ask user to decide (AskUserQuestion)
   ├─ Log decision with reasoning
   └─ Next decision
   ↓
Append decisions to .claude/decisions-log.md
   ↓
Handoff to /deepen or /specify
```

## Execution

### 1. Load Build Decisions Skill

Load `.claude/skills/build-decisions/SKILL.md` and follow its procedures.

### 2. Auto-Detect Prior Work

Check for brainstorm output:
```bash
ls .claude/brainstorms/*{feature}* 2>/dev/null | head -5
```

Check for existing build state (session tracking only):
```bash
ls .claude/builds/{feature}/state.json 2>/dev/null
```

If resuming, announce position and surface notes from previous session.

### 3. Decision Categories

Walk through decisions in this order. Be exhaustive within each category — ask every decision that could affect the feature. Skip entire categories only if truly irrelevant.

1. **Architecture** — Patterns, boundaries, data flow, dependency structure, module boundaries
2. **Data Model** — Entities, relationships, storage engine, schema, migrations
3. **API Design** — Endpoints, contracts, auth, versioning, rate limiting
4. **Observability** — Telemetry, tracing, metrics, structured logging, OTEL integration
5. **Audit & Compliance** — Audit trail, log retention, tamper evidence, classification, data sovereignty
6. **Security** — AuthN, AuthZ, encryption, input validation, secret management, threat model
7. **Integration** — External services, protocols, circuit breakers, retry, message bus
8. **Performance** — Caching, scaling, resource limits, cold start, memory budgets
9. **Extensibility** — Module system, plugin boundaries, feature toggles, tier configuration
10. **Testing** — Strategy, coverage targets, fixtures, mocks, CI/CD, security tests
11. **Deployment** — Migration, rollout, monitoring, alerting, rollback
12. **UI/UX** — Components, interactions, states (skip if not applicable)

### 4. Output

```
.claude/decisions-log.md          # All decisions (all features, all phases)
.claude/builds/{feature}/
└── state.json                    # Session state tracking only
```

Each decision in the log includes:
- Priority ranking (which of the 4 priorities drove the choice)
- Lockdown tier notes (federal/enterprise/personal variations)
- `auto-applied: federal-mandate` tag where applicable

## Arguments

- `/build my-feature` — Start new build for feature
- `/build resume` — Resume last active build
- `/build status` — Show progress overview
- `/build path/to/brainstorm.md` — Start from brainstorm output

## Next Steps

- `/deepen {feature}` — Enrich with parallel research
- `/specify {feature}` — Create formal spec (auto-reads build decisions)

## Notes

- One decision at a time — don't rush
- Always present tradeoffs — never default silently (unless federally mandated)
- Log ALL decisions — even auto-applied ones have rationale
- State persists across sessions
- Solutions archive searched for prior art at each decision
- Ask every possible question — be exhaustive, not efficient
- Rank options by: simplicity → security → scalability → compliance
- Tag tier variations on every decision where behavior differs
