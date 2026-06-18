# Lockdown Tiers

The system has **one codebase**. Tiers differ by config + optional pip extras, never by code branches.

## Install + config

```bash
pip install arcagent                  # personal — core only
pip install arcagent[enterprise]      # + SSO, audit export, compliance reporting
pip install arcagent[federal]         # + FIPS crypto, Vault, mTLS deps, SBOM tooling
```

```toml
[security]
tier = "federal"   # "federal" | "enterprise" | "personal"
```

## Enforcement

| Tier | Install | Violations | UX |
|---|---|---|---|
| `federal` | `[federal]` extras | **Block** — hard errors, operations denied | Strict. Locked down by default. |
| `enterprise` | `[enterprise]` extras | **Warn** — logged warnings, compliant defaults, overridable | Professional. Configurable. |
| `personal` | Base | **Info** — logged at info level, nothing enforced | Open. Lightweight. No friction. |

## Architecture rules

- Same code paths everywhere — no `if tier == "federal"` in business logic.
- Single policy enforcement point — reads tier, gates behavior (block / warn / allow).
- Optional deps only for extras — FIPS crypto, Vault, mTLS, SBOM live in extras.
- Config, not code — switching tiers = TOML edit + optional `pip install`. No rebuild.
- Personal never feels federal — no compliance noise unless opted in.
- Federal locks down immediately — install extras, set tier, done.

## Per-decision tier notes

For every decision, answer: *"What does the policy layer do at each tier?"*

> **Federal**: blocks without X. **Enterprise**: warns if missing X, defaults to Y. **Personal**: no enforcement.

If a capability requires an optional dependency, name which extras package provides it.
