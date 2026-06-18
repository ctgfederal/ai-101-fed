# Selection Rules

The match algorithm in `scripts/match_agents.py` computes one score per agent
and sorts descending. Use this file to understand *why* a given agent appears
where it does, and to debug surprising rankings.

## Match Tiers (best to worst)

| Tier | Trigger | Weight | Reason string |
|------|---------|--------|---------------|
| 1 | Keyword equals agent name exactly | `1.00` | `exact name match` |
| 2 | Keyword is a token in the agent name (kebab-split) | `0.70` | `name token match` |
| 3 | Keyword is a substring of the agent name (≥3 chars) | `0.56` | `name substring match` |
| 4 | Keyword is a token in the agent description | `0.30` | `description token match` |
| 5 | Keyword is a substring of the description (≥3 chars) | `0.18` | `description substring match` |
| 6 | Keyword matches one of the agent's `tools` | `0.15` | `tool match` |

A keyword matches at most once per agent — the highest tier wins.

## Normalization

Final score = `sum_of_keyword_scores / (max(W_NAME_EXACT, W_NAME_TOKEN) * len(keywords))`,
clipped to `[0, 1]`. With `W_NAME_EXACT=1.0`, the cap is `1.0 * N` for `N`
keywords. So a single exact-name match against a 3-keyword query yields
`1.0 / 3 ≈ 0.33`, not `1.0`. This keeps multi-keyword queries from
under-scoring relative to single-keyword ones.

## Tool-availability filter

The matcher does *not* hard-filter on tools — a missing tool only reduces
score. Hard filtering is the caller's job; it can drop any returned row
where `tools` does not contain a required tool.

## When to override

Two cases call for a manual override of the top-scored agent:

1. **A required tool is missing.** Drop that row and pick the next.
2. **A specialized agent ties with a generalist.** Prefer the specialist
   (see `tie-breakers.md`).
