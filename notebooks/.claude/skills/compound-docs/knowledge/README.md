# compound-docs — knowledge

Reference files this skill loads on demand. SKILL.md stays small; everything detailed lives here.

| File | What it contains | When to load |
|---|---|---|
| `categories.md` | The 12 canonical solution categories with descriptions | When classifying a new problem (Steps §3) |
| `frontmatter-schema.md` | Authoritative field schema: required, optional, formats, validation rules | When assembling a payload (Steps §5) and when debugging a `validate_frontmatter.py` failure |
| `search-patterns.md` | The grep patterns `/brainstorm`, `/build`, `/specify`, `/review` actually use | When deciding which fields to populate richly so the file is *retrievable* |

## Read order for a fresh agent

1. SKILL.md — orchestration only.
2. `categories.md` — pick the category before touching anything else.
3. `frontmatter-schema.md` — populate every required field correctly.
4. `search-patterns.md` — sanity-check that what you wrote will be findable.
