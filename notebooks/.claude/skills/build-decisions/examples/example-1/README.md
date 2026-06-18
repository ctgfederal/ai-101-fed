# Example: Feature Search

End-to-end build-decisions run for `feature-search` (cross-entity search across briefs/customers/notes).

## Files
- `payload.json` — payload consumed by `scripts/append_decisions.py`. Contains 3 auto-applied federal mandates and 5 user decisions across 5 categories.
- `expected-output.md` — the full `.claude/decisions-log.md` contents after appending. Demonstrates: monotonic D-NNN IDs starting at `D-042`, auto-applied table, per-category sections, tiers, open questions, related solutions cross-link.

## Flow

```bash
# 1. Init state
python ../../scripts/state_manager.py init \
  --feature feature-search \
  --builds-root /tmp/sample/builds

# 2. Allocate IDs (assume log already has D-001..D-041)
python ../../scripts/allocate_ids.py --log /tmp/sample/decisions-log.md --count 8
# → D-042 D-043 D-044 D-045 D-046 D-047 D-048 D-049

# 3. Append
python ../../scripts/append_decisions.py \
  --payload payload.json \
  --log /tmp/sample/decisions-log.md

# 4. Validate
python ../../scripts/validate_output.py \
  --log /tmp/sample/decisions-log.md \
  --feature "Feature Search"
# → OK
```

## What this demonstrates
- Auto-applied mandates batched in a table — never asked to user.
- 5 user decisions, each with priority, alternatives, rationale, and tier notes.
- Tier notes name what `federal` / `enterprise` / `personal` do for that decision.
- Open questions captured for downstream `/specify` to resolve.
- Related solutions cross-linked into the broader knowledge graph.
