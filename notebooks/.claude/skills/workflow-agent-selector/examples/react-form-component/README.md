# Example: Selecting an Agent for a React Form Component

Walks through a full pass of `workflow-agent-selector` for a typical
frontend task.

## The Task

> "Build a `RegisterForm` React component with React Hook Form and Zod
> validation. Wire it up to our existing Supabase auth client."

## Files in this example

- `task.md` — the raw task description fed in.
- `query.json` — the keyword query passed to `match_agents.py`.
- `expected-output.md` — the rendered match-results report.

## Reproduce

```bash
cd ~/.claude/skills/workflow-agent-selector
python scripts/validate_match_query.py --file examples/react-form-component/query.json
python scripts/match_agents.py \
  --keywords-json examples/react-form-component/query.json \
  --agents-root ~/.claude/agents
python scripts/validate_output.py \
  --file examples/react-form-component/expected-output.md
```

All three commands should exit 0.
