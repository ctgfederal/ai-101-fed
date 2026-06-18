# Example — Promote a user-preference learning

A worked example that walks the full spec-reflexion pipeline.

## Scenario

While implementing spec `feature-123`, the user reflects at the T-005 phase
boundary:

> "I keep reaching for explicit error types over `Result<T, E>`. The Result
> wrapper hides stack traces and forces us to thread `.unwrap()` everywhere.
> Future Claude: prefer explicit error subclasses unless we have a real reason."

The reflection is appended to `.claude/specs/feature-123/README.md` under the
`### For /memorize` heading.

## Files in this example

| File | Role |
|---|---|
| `input-readme.md` | The spec README before this skill runs |
| `extracted.json` | Output of `extract_learnings.py --readme input-readme.md` |
| `classification.txt` | Output of `classify_learning.py` for the global bullet |
| `expected-memory.md` | The memory file produced by `promote_to_memory.py` |
| `expected-index.md` | What the resulting `MEMORY.md` looks like |

## Pipeline

```bash
# 1. Extract
python scripts/extract_learnings.py --readme examples/josh-error-types/input-readme.md \
  > /tmp/extracted.json

# 2. Classify the candidate global bullet
echo "Josh prefers explicit error types over Result wrappers" \
  | python scripts/classify_learning.py
# → global

# 3. Promote
python scripts/promote_to_memory.py \
  --text "Josh prefers explicit error types over Result wrappers — keeps stack traces clean and the type system honest." \
  --type user \
  --name josh_explicit_error_types \
  --memory-root /tmp/example-memory

# 4. Validate
python scripts/validate_output.py \
  --file /tmp/example-memory/user_josh_explicit_error_types.md
```

## What's demonstrated

- Local bullets ("REQ-104 was renumbered" etc.) stay in the spec README.
- The global bullet is detected by the classifier (framework noun + user-preference marker).
- Memory file is named `user_<slug>.md`, with frontmatter derived from the text.
- `MEMORY.md` gets exactly one new bullet, no duplicates.
- `validate_output.py` exits 0.
