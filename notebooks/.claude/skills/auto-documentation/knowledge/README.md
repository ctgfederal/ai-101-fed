# auto-documentation — knowledge

Reference files this skill loads on demand. SKILL.md stays small; everything detailed lives here.

| File | What it contains | When to load |
|---|---|---|
| `categories.md` | The four canonical categories with descriptions and what fits each | When classifying a new insight (Steps §2) |
| `dedup-rules.md` | How similarity is measured and when to merge vs create new | When `dedupe.py` reports a near-match (Steps §4) |
| `frontmatter-schema.md` | Authoritative field schema: required, optional, formats, validation rules | When assembling a payload (Steps §3) and when debugging a `validate_output.py` failure |

## Read order for a fresh agent

1. SKILL.md — orchestration only.
2. `categories.md` — pick the category before touching anything else.
3. `frontmatter-schema.md` — populate every required field correctly.
4. `dedup-rules.md` — only when dedupe surfaces a candidate match.
