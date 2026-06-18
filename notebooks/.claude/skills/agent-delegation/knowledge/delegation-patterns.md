# Delegation Patterns

## Research-only

The agent reads code and produces a report — no edits. Used by `/swarm-analyze`, codebase-locator-style work.

```json
{
  "agent_type": "codebase-analyzer",
  "task": "Trace how authentication flows from src/api/middleware.py through to the user table.",
  "focus_files": ["src/api/", "src/auth/", "db/migrations/"],
  "exclude_files": [],
  "success_criteria": ["Returns a markdown report with file paths and line numbers"],
  "return_format": "Markdown report with sections: Entry Points, Auth Path, DB Touches, Gotchas."
}
```

EXCLUDE can be empty here — there are no edits to scope.

## Focused build (single dir owner)

One agent owns one directory end-to-end.

```json
{
  "agent_type": "auth-builder",
  "task": "Implement JWT auth in src/auth/.",
  "focus_files": ["src/auth/", "tests/auth/"],
  "exclude_files": ["src/billing/", "src/users/", "docs/"],
  "success_criteria": ["pytest tests/auth/ exits 0", "ruff check src/auth/ exits 0"],
  "return_format": "Markdown summary."
}
```

EXCLUDE the *adjacent* areas the agent might wander into.

## Parallel build (collision-free)

N agents, each with disjoint FOCUS sets. **Always run `check_collisions.py` before launch.**

```json
[
  {"agent_type": "auth", "focus_files": ["src/auth/", "tests/auth/"], ...},
  {"agent_type": "billing", "focus_files": ["src/billing/", "tests/billing/"], ...}
]
```

If `check_collisions.py` reports `safe: false`, re-scope or sequence.

## Sequential handoff

Agent B needs Agent A's output. Run them sequentially; B's prompt should reference A's deliverables in TASK.

Don't try to parallelize when there's a real dependency. Two agents writing the same file in parallel = corruption.

## Retry on scope creep

When an agent returns work that violated EXCLUDE:
1. Tighten EXCLUDE — list the exact paths the agent touched.
2. Make TASK more specific about *what* to do.
3. Re-render the prompt and re-run.

If three retries fail, the task is too big — break it into smaller delegations.
