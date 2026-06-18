# Learnings vs. Decisions vs. Memory

Three places to capture insight. Use the one that matches the **scope** of the insight, not the urgency.

## Decision tree

```
Is this insight…
├── …feature-specific (only matters in this spec)? ─────────►  spec README → ## Learnings
├── …a cross-feature design choice with rationale? ────────►  .claude/decisions-log.md (via /build)
└── …a globally reusable pattern, anti-pattern, or rule? ──►  ~/.claude/projects/<cwd>/memory/ (via /memorize)
```

## Three places, three lifetimes

### 1. Spec README — `## Learnings`

- **Scope:** This feature only.
- **Lifetime:** Lives with the feature; archived when the spec folder is archived.
- **Examples:**
  - "The user-search endpoint required a 30s timeout; default 10s was too aggressive on cold cache."
  - "We had to revert the Postgres trigger approach — it broke replication. Used app-layer event log instead."
- **Anti-examples:**
  - "Always prefer app-layer events over DB triggers." (Too general — that's a global rule.)
  - "We picked Postgres for the project." (Project-wide — that's a decision-log entry.)

### 2. `.claude/decisions-log.md` — managed by `/build`

- **Scope:** Cross-feature; affects multiple specs in this project.
- **Lifetime:** Append-only; never edited or deleted, only deprecated by a newer entry.
- **Examples:**
  - "D-014: Picked Redis 7 over Memcached because we need streams for the audit pipeline."
  - "D-022: All new services use OpenTelemetry from day one (was previously optional)."
- **Anti-examples:**
  - "We bumped the Stripe library." (Implementation detail — phase note or PR description.)
  - "Use snake_case for Python." (Style — coding-standards rule, not a decision.)

### 3. Global memory — `~/.claude/projects/<cwd>/memory/` via `/memorize`

- **Scope:** Reusable across projects, weeks, sessions; useful to any future Claude.
- **Lifetime:** Persistent across the project; surfaces automatically at session start.
- **Examples:**
  - "Pattern: When integrating a third-party webhook, always assume non-idempotent and add dedupe table keyed on event ID."
  - "Anti-pattern: Don't use `git rebase -i` in CI; the `-i` flag is interactive-only and silently hangs."
- **Anti-examples:**
  - "Project X uses Postgres." (Project-specific fact — steering doc.)
  - "User prefers concise replies." (User preference — auto-memory captures these.)

## Promotion path

Local learnings often *become* global memories. The promotion happens during `/review` or `/memorize`:

```
spec README ## Learnings
       │
       │  /memorize  (after the pattern repeats across 2+ features)
       ▼
~/.claude/projects/<cwd>/memory/<typed-file>.md
```

Don't promote prematurely. A pattern is global only after it shows up in at least two features. Until then, keep it local.

## When in doubt

Ask: "If a teammate joined next month and read this, would they care?"
- **Yes, only on this feature** → spec README.
- **Yes, generally** → decisions log or memory.
- **No** → don't write it.
