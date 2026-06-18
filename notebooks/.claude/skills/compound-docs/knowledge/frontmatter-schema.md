# Solution Frontmatter Schema

Authoritative spec for the YAML frontmatter on every solution file. `validate_frontmatter.py` enforces this; the LLM should follow it when assembling.

## Required fields

| Field | Type | Format / rules |
|---|---|---|
| `title` | string | 8–120 chars. Imperative or descriptive: "N+1 query in brief generation", not "n+1 thing". Quote in YAML. |
| `category` | string | Exactly one of the values in `categories.md`. Lowercase, kebab. |
| `date` | date | `YYYY-MM-DD`. The date the problem was *resolved* (not when documented). |
| `tags` | list[string] | 2–8 items. Lowercase. Tag the *technology* (`postgres`, `rails`), the *pattern* (`n+1`, `race-condition`), and the *layer* (`api`, `worker`). No spaces — use hyphens. |
| `module` | string | The affected module / class / file. Free-form but specific: `BriefGenerator`, not `the brief code`. |
| `symptom` | string | One sentence, in quotes. Quote actual error text where possible: `"PG::QueryCanceled: canceling statement due to statement timeout"`. |
| `root_cause` | string | One sentence, in quotes. The *mechanism*, not the fix: `"Outer query held a row lock while inner job waited on the same row."` |

## Optional fields

| Field | Type | Format / rules |
|---|---|---|
| `severity` | string | One of `low`, `medium`, `high`, `critical`. Default: omit. Use `critical` only for prod incidents or data-loss bugs. |
| `spec_id` | string | If this fix relates to a spec under `.claude/specs/`. Format: `SPEC-YYYY-NNN`. |
| `pr` | string | The PR/MR that landed the fix: `"#412"` or `"!88"`. |
| `incident_id` | string | If a postmortem exists, link by ID. |

## Validation rules

1. YAML must parse cleanly (no embedded tabs, no smart quotes).
2. `date` is in the past or today — never the future.
3. `tags` contains no duplicates, all lowercase, no whitespace inside a tag.
4. `category` is in the canonical list (see `categories.md`).
5. `severity` (if present) is one of the four allowed strings.
6. No required field is the empty string.

## Common mistakes

- **`tags: ["fix", "bug", "issue"]`** — these are not tags, they're noise. Tag the technology and pattern.
- **`symptom: "it broke"`** — useless for grep. Use the actual error or behavior.
- **`module: "everywhere"`** — pick the originating module, not the blast radius.
- **`title: "fix"`** — see above. Be searchable.
- **`category: "other"`** — stop and propose a new category instead.
