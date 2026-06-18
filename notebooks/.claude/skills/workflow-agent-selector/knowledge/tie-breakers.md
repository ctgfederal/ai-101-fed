# Tie-Breakers

When two or more agents tie on score, `match_agents.py` already applies a
deterministic secondary sort: smaller `tools` list first, then alphabetical
`agent` name. That covers most cases. Use this file when the automatic order
still feels wrong.

## Rule 1 — Specificity wins

A specialist with a *narrower* description should be preferred over a
generalist whose description happens to mention the same keyword.

- `react-specialist` over `frontend-developer` for a complex hook task.
- `postgres-pro` over `database-administrator` for query-plan work.
- `nextjs-developer` over `react-specialist` for App Router / Server Actions.

If both descriptions mention the keyword equally, fall back to whichever
description has *fewer* unrelated technologies listed.

## Rule 2 — Smaller tool surface wins

Agents with a tightly focused `tools` list are typically more polished for
that exact niche. The matcher's secondary sort already enforces this.

## Rule 3 — Match the model to the task complexity

When two agents tie and the task is high-stakes (security, architecture,
data correctness), prefer the agent with the more capable `model` (`opus` >
`sonnet` > `haiku`). For routine work, prefer the cheaper model.

## Rule 4 — Check the steering docs

If the project has steering docs that name a default agent for a category
(e.g. `.claude/steering/tech.md` says "use `nextjs-developer` for all
frontend work"), follow it. Project conventions override the matcher.

## Rule 5 — Use multiple agents when tasks split

If the top two scores are close *and* they cover non-overlapping skills
(e.g. `backend-developer` + `react-specialist` for a fullstack feature),
return both — the caller can fan out work in parallel.
