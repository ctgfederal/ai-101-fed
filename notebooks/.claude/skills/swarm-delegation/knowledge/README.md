# swarm-delegation — knowledge

| File | Contents | When to load |
|---|---|---|
| `handoff-schema.md` | Authoritative schema for a handoff payload: required fields, optional fields, allowed types | When assembling a payload, debugging a validation failure, or extending the schema |
| `chain-patterns.md` | Linear / fan-out / fan-in chain patterns and pitfalls of each | When planning a multi-step delegation, choosing between parallel vs sequential, or debugging `check_chain.py` results |
| `failure-modes.md` | Six known delegation failure modes (lost context, type mismatch, cycle, deadline gap, ambiguous return, undefined merge) | When a chain misbehaves at runtime, when reviewing a handoff before it ships, or when training new agents on the protocol |
