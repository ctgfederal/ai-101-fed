# Example 1 — `business-rule` end-to-end

A worked example showing a discovered business rule getting captured.

## Files
- `input.txt` — The free-text discovery as it was surfaced during `/implement` on USR-014.
- `payload.json` — The assembled JSON payload after extraction.
- `expected-output.md` — The rendered auto-doc.

## Reproduce

```bash
# 1. classify (sanity check)
python scripts/categorize.py --text "$(cat examples/example-1/input.txt)"
# → business-rule

# 2. dedupe (empty archive — no duplicates)
python scripts/dedupe.py \
  --payload examples/example-1/payload.json \
  --docs-root /tmp/auto-docs

# 3. write
python scripts/write_doc.py \
  --payload examples/example-1/payload.json \
  --docs-root /tmp/auto-docs

# 4. validate
python scripts/validate_output.py \
  --file /tmp/auto-docs/business-rule/2026-05-08-admins-can-edit-any-user-post-non-admins-only-their-own.md
# → OK
```

## What this demonstrates

- Tag granularity: `authorization`, `permissions`, `admin`, `user-posts` — technology-agnostic, layered, and concept-specific.
- Scope formatting: `UserPostController#update` (Ruby class#method).
- The four body sections in order: Description → Why → Examples → Related.
- Source provenance: a pair session, not "I just figured it out".
