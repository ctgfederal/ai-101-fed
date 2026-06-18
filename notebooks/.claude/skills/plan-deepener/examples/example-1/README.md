# Example: Deepen feature-search build decisions

End-to-end deepening of a build-decisions section.

## Files
- `target-before.md` — input document (a build-decisions extract).
- `findings.json` — fixture parallel-research output (what the spawned agents would return).
- `target-after.md` — the same document with `## Deepening Summary` and `### Research Insights` blocks added.

## Flow

```bash
# 1. Parse the target to extract sections + technologies
python ../../scripts/parse_target.py --file target-before.md

# 2. Match available skills to the parsed technologies
python ../../scripts/parse_target.py --file target-before.md \
  | jq '.technologies' \
  | python ../../scripts/match_skills.py --skills-root ~/.claude/skills

# 3. (LLM step) spawn parallel Explore agents per section, build findings.json
#    See knowledge/research-protocol.md for the per-section prompt

# 4. Merge findings into the target
python ../../scripts/merge_research.py \
  --target target-before.md \
  --findings-json findings.json

# 5. Validate
python ../../scripts/validate_output.py --target target-before.md
# → OK
```

## What this demonstrates

- Original section bodies preserved character-for-character.
- One `### Research Insights` block per section, with all 5 required subsections.
- `## Deepening Summary` block at the top with key findings and new risks.
- Solutions archive links cross-referenced inline.
- Idempotent: running merge again without `--force` skips already-deepened sections.
