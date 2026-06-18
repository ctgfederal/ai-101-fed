# Memory Format

Matches Claude Code's native auto-memory protocol (the `# auto memory` section
of the user's global `CLAUDE.md`). All memory files live under:

    ~/.claude/projects/<sanitized-cwd>/memory/

For this user, the path is:

    ~/.claude/projects/<sanitized-cwd>/memory/

## Memory file shape

```markdown
---
name: <human-readable title, ≤80 chars>
description: <one-line summary used by the index, ≤120 chars>
type: <feedback|project|reference|user>
---

<body — markdown, no length limit, but be concise>
```

### Filename convention

    <type>_<slug>.md

- `<type>` is one of `feedback`, `project`, `reference`, `user`.
- `<slug>` is lowercase, underscore-separated, ≤60 chars.
- Examples:
  - `feedback_iso9001_bare_minimum.md`
  - `project_superhuman_diet.md`
  - `user_explicit_error_types.md`
  - `reference_aws_lambda_limits.md`

The `<type>_` prefix is what makes the index readable at a glance — types
sort together.

### Frontmatter rules

- All three fields are **required**: missing any one fails validation.
- `name` and `description` may not be empty.
- `type` is exactly one of the four allowed values; case-sensitive.
- No additional fields are required, but `originSessionId` is allowed if
  Claude Code's harness adds it.

## MEMORY.md index

A single `MEMORY.md` file at the root of the memory directory indexes every
file. Format:

```markdown
# Memory Index

- [feedback_iso9001_bare_minimum.md](feedback_iso9001_bare_minimum.md) - ISO 9001 manual sections: bare minimum compliance, TL;DR action guides, no aspirational language
- [project_superhuman_diet.md](project_superhuman_diet.md) - /plan-next-week-health uses superhuman-diet skill (replaces shredmaxxing/nutrition-programming)
```

Rules:
- One bullet per memory file. The link **target equals the filename** (no
  subfolders).
- Bullet description **equals the file's frontmatter description**.
- Adding a duplicate filename **replaces** the existing line; never duplicate.
- Index is grep-friendly — keep descriptions one line, no markdown formatting.

## Why this format

Claude Code's harness reads the top 200 lines of `MEMORY.md` automatically at
session start. Files themselves are read on demand when the harness greps for
relevance. This means:

- The **index description** is what catches Claude's attention later.
- The **filename prefix** lets `grep ^- \[user_` find every user-preference
  learning at once.
- The **body** can be richer than the description — it loads only when needed.

Don't put behaviour-changing content in the body that isn't summarised in the
description. If it's worth remembering, it's worth indexing well.
