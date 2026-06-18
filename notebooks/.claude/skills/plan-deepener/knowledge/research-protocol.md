# Parallel Research Protocol

Spawn one `Explore` (or equivalent) sub-agent per major section. All in one tool-call message so they run concurrently.

## Per-section task framing

```
Research best practices for: <section heading + 1-line context from body>

Return text only. Do NOT write any files.

Cover:
  - 3 best practices specific to this design choice (concrete, citable)
  - 2-3 edge cases with handling strategies
  - Performance considerations (numbers if you have them)
  - References (URLs, RFCs, specific docs pages)

Format your reply as JSON with keys:
  best_practices, edge_cases, performance, references

Each value is a list of strings.
```

## Hard rules

- **One agent per section** — don't try to research everything in one big agent.
- **All agents in one message** — concurrent dispatch, not sequential.
- **Sub-agents return text only** — only `merge_research.py` writes files.
- **Cap each list at 5 items** — over-fitting findings buries the signal.
- **Cite sources** — if a finding can't be cited, drop it.

## Synthesis

After all agents return:
1. Concatenate per section.
2. Run dedup rules (`knowledge/dedup-rules.md`).
3. Cross-reference solutions archive hits (already collected before research).
4. Build the findings JSON for `merge_research.py`.
