# Local vs Global — classification heuristics

`scripts/classify_learning.py` uses simple regex signal-counting. The same
heuristics drive the human decision when a borderline item appears.

## Local indicators (stay in spec README)

A learning is **local** if any of these are true:

- **Project nouns**: `our X`, `we use`, `we tried`, `we ran into`
- **Specific paths**: `.claude/specs/<feat>`, `src/foo/bar.py`, `pipelines/foo`
- **Pinned IDs**: `REQ-NNN`, `T-NNN`, `D-NNN`, `JIRA-123`, `PROJ-456`
- **Demonstratives**: `this spec`, `this feature`, `the team`, `this project`
- **Internal module names**: `BriefGenerator`, `catalog_loader.py`,
  `superhuman-diet`

Local learnings answer the question:
> "What did we figure out *about this specific feature* that future spec-X
> readers need to know?"

They live forever in `.claude/specs/<feature>/README.md`.

## Global indicators (promote to memory)

A learning is **global** if any of these are true:

- **Framework / language nouns**: React, Next.js, Python, Postgres, JWT, REST
- **Pattern verbs**: *always X*, *never Y*, *prefer X over Y*, *when X then Y*
- **User-preference markers**: "Josh prefers", "I prefer", "user wants"
- **Best-practice phrasing**: "anti-pattern", "convention", "rule", "principle"
- **No project nouns at all** in the sentence

Global learnings answer the question:
> "Will I want to remember this on the *next* spec, the next project, or in
> three months?"

They become memory files at
`~/.claude/projects/<sanitized-cwd>/memory/<type>_<slug>.md`.

## Tiebreakers

If the signals are evenly balanced, the classifier defaults to **local**.
Promotion is conservative — it's much cheaper to leave a useful learning in a
spec README than to clutter the global memory index with one-offs.

You can override the classifier any time:
- Run `classify_learning.py` yourself and ignore the result.
- Pass an explicit `--type` and `--name` to `promote_to_memory.py`.

## Examples

| Learning | Scope | Why |
|---|---|---|
| "BriefGenerator hits an N+1 — use `includes(:author)`" | local | Specific module, specific fix |
| "ActiveRecord lazy-loads associations; prefer `includes` for collections" | global | Framework-level pattern |
| "We chose tRPC over REST for this spec" | local | "We" + "this spec" |
| "Josh prefers tRPC over REST for typed RPC" | global | About Josh, framework-level |
| "REQ-014 was renumbered after merge" | local | Pinned ID |
| "Always renumber requirements before merging branches" | global | Generic rule |
| "The `/specify` command auto-detects brainstorm output" | global | Tool behaviour, not project state |
