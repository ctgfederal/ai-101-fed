# Decision ID Convention

## Format
**Globally unique `D-NNN`** (zero-padded to 3 digits, growing to 4+ as needed).

## Rules
- **One global counter across the entire decisions log.** No per-feature numbering. No category prefixes (no `A-1`, `S-1`, `O-1`, `AUTO-1`, `API-1`). Category lives in the section heading and the markdown sub-heading, never in the ID.
- **Append-only.** Once an ID is assigned, it never changes — even if the decision is later superseded, deleted, or split.
- **Supersede instead of renumber.** Use `[superseded by D-NNN]` annotations.
- **Cross-feature follow-ups reuse IDs.** Deepening insights, implementation notes, learnings published later for the same feature reference the original `D-NNN`s — they never reallocate.
- **External citations are not decision IDs.** NIST controls (`AU-2`, `SC-8`, `IA-5`), CVE references, FIPS references, OMB circulars (`OMB A-123`), spec IDs (`SPEC-019`) stay as-is. Never rewrite them.

## Allocation

Before assigning IDs to a new batch:

1. Read `.claude/decisions-log.md`.
2. Find the highest existing `D-NNN` (regex: `\bD-(\d+)\b`, max value).
3. Allocate the next IDs starting from `max + 1`.
4. Auto-applied federal mandates and user-decided items share the same counter — both are decisions.

`scripts/allocate_ids.py` does this automatically.

Example: if the log's max ID is `D-195`, the next four decisions get `D-196`, `D-197`, `D-198`, `D-199`.
