# Example: AI-powered code review for solo devs

A worked end-to-end run of the brainstorming skill.

## Files
- `payload.json` — the assembled JSON consumed by `scripts/write_brainstorm.py`.
- `expected-output.md` — the captured brainstorm at `.claude/brainstorms/2026-02-14-ai-powered-code-review-for-solo-devs.md`.

## Flow

```bash
# 1. Initialize
python ../../scripts/init_brainstorm.py \
  --topic "AI-powered code review for solo devs" \
  --brainstorms-root /tmp/sample-brainstorms \
  --date 2026-02-14
# → /tmp/sample-brainstorms/2026-02-14-ai-powered-code-review-for-solo-devs.md

# 2. Write
python ../../scripts/write_brainstorm.py \
  --payload payload.json \
  --out /tmp/sample-brainstorms/2026-02-14-ai-powered-code-review-for-solo-devs.md

# 3. Validate
python ../../scripts/validate_output.py \
  --file /tmp/sample-brainstorms/2026-02-14-ai-powered-code-review-for-solo-devs.md
# → OK
```

## What this demonstrates
- All 8 required sections in correct order.
- `Scope: Out` is non-empty (catches the most common drift).
- Open questions list seeded for `/build` to pick up.
- Related solutions placeholder for first-time topic.
- No design decisions captured (no Postgres/Rails/Rust mentions in `Principles`).
