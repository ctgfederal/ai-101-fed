# Priority Framework

When presenting options for a decision, rank by:

1. **Simplicity** — fewest dependencies, lowest complexity, easiest to read and maintain. Boring wins.
2. **Modularity** — hard domain boundaries (TUI, commands, CLI, teams, agents, run); swappable components with explicit input/output contracts; no logic bleed; one-way dependency flow.
3. **Security** — zero-trust, least-privilege, defense in depth; open-by-default or locked-by-default via config; fed on-prem capable; FedRAMP, NIST 800-53, CMMC, FISMA compliance lives here. Observability/telemetry/audit are security.
4. **Scalability** — horizontal scale, stateless, shared-nothing; 10k+ tx/min across 10–20 coordinated instances. Backpressure, idempotency, concurrency-safe primitives.

## Application

- The recommended option must be the one that best satisfies these priorities **in this order**.
- If the highest-priority option fails on a lower priority, name the tension explicitly: *"This is the simplest design but adds 200ms p99 latency at scale; we accept that to keep the read path readable."*
- Never "average" priorities. Order them and pick.
- When two options tie on simplicity, decide on modularity. When tied on modularity, decide on security. Etc.

## Anti-patterns

- Recommending Option B because it's "more elegant" when Option A is simpler.
- Hiding a security concession in a footnote.
- Optimizing for scale on a feature that handles 10 req/min.
