# Brainstorm Schema

## Frontmatter (required)

| Field | Type | Format |
|---|---|---|
| `topic` | string | Quoted. Descriptive title, 8–120 chars. |
| `date` | date | `YYYY-MM-DD` — today by default. |
| `status` | string | `complete` once captured, `in-progress` if user paused mid-walk. |

## Body sections (required, in order)

| Section | What goes here | Word ceiling |
|---|---|---|
| `## Inspiration` | What sparked the idea — motivation and context | 200 |
| `## Projects` | Specific products/projects being imagined | 200 |
| `## Audience` | Who this is for — personas, their pain, their context | 250 |
| `## Use Cases` | Real scenarios — bulleted, concrete | 300 |
| `## Desired Outcomes` | What changes when this exists — observable | 250 |
| `## Guiding Principles` | What matters most — ranked or weighted | 200 |
| `## Constraints` | Tech, time, budget, compliance limits | 200 |
| `## Scope` | Two paragraphs: **In:** and **Out:** | 200 each |

## Body sections (optional)

| Section | What goes here |
|---|---|
| `## Open Questions` | Anything unresolved — must be answered before `/build` |
| `## Related Solutions` | Links to `.claude/solutions/<category>/<file>.md` if relevant |

## Antipatterns

- **Listing features in `Use Cases`.** Use cases describe scenarios from the user's POV ("a solo dev gets a PR review in 30s"), not the system's features.
- **Confusing principles with constraints.** Principles are "what we'd choose", constraints are "what we can't do".
- **Empty `Scope: Out`.** Always name what's out — that's where the spec discipline lives.
- **Putting design decisions in `Guiding Principles`.** "Use Postgres" is a build decision; "favor durability over speed" is a principle.
- **Vague `Inspiration`.** "Wanted to build something cool" tells `/build` nothing. Be specific about the trigger.
