# Example: N+1 Query in Brief Generation

Demonstrates the full `compound-docs` flow on a realistic Rails N+1 fix.

## Files in this example
- `conversation.md` — the conversation excerpt the LLM extracts from.
- `payload.json` — the assembled JSON payload passed to `scripts/write_solution.py`.
- `expected-output.md` — the final solution file as it should land at
  `.claude/solutions/performance-issues/2026-02-14-n-1-query-in-brief-generation.md`.

## Flow

```bash
# 1. Generate filename
python ../../scripts/generate_slug.py --title "N+1 query in brief generation" --date 2026-02-14
# → 2026-02-14-n-1-query-in-brief-generation.md

# 2. Validate the assembled payload would render valid frontmatter
python ../../scripts/write_solution.py --payload payload.json --solutions-root /tmp/sol
# → /tmp/sol/performance-issues/2026-02-14-n-1-query-in-brief-generation.md

# 3. Validate the output
python ../../scripts/validate_output.py --file /tmp/sol/performance-issues/2026-02-14-n-1-query-in-brief-generation.md
# → OK
```
