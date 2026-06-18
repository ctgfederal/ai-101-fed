# Solutions Archive Search

Use `compound-docs/scripts/search_solutions.py` for every primary tag and module mentioned in the parsed document. The archive is your highest-yield source — known fixes for known problems.

## Patterns

```bash
# By technology / pattern tag
python /Users/joshschultz/.claude/skills/compound-docs/scripts/search_solutions.py \
  --solutions-root .claude/solutions --tag postgres

# By module
python /Users/joshschultz/.claude/skills/compound-docs/scripts/search_solutions.py \
  --solutions-root .claude/solutions --module SearchService

# By symptom keyword (covers both frontmatter and body)
python /Users/joshschultz/.claude/skills/compound-docs/scripts/search_solutions.py \
  --solutions-root .claude/solutions --symptom "n+1"
```

## What to do with hits

- Read each hit's frontmatter (`title`, `root_cause`, `severity`).
- Read the body's `## Solution` and `## Prevention` sections.
- Surface as "From Solutions Archive" entries: `<title> (<path>) — <one-sentence why-relevant>`.

## What NOT to do

- Don't include hits that are clearly off-topic. The point is signal, not exhaustiveness.
- Don't paraphrase the solution. Link to the file; let the user read it themselves.
