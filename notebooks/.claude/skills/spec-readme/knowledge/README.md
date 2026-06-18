# Knowledge Index — spec-readme

Load these files on demand when answering specific questions about how the README is shaped, what statuses are allowed, or where a learning belongs.

| File | Load when |
|---|---|
| `readme-schema.md` | Defining or extending which `##` sections are required, what status values are allowed, what link formats the README must use. |
| `phase-notes-format.md` | Writing or editing a phase note — what to include, what to exclude, how long, what tone. |
| `learnings-vs-decisions.md` | Deciding whether to record an insight in the spec README, in `.claude/decisions-log.md`, or in global memory via `/memorize`. |

Default loading: SKILL.md only. These files are referenced from SKILL.md so the LLM (and humans) can drill in when needed without paying the context cost upfront.
