# Handoff Schema

Authoritative schema for a single handoff payload. `validate_handoff.py` enforces this; do not bypass.

## Required Fields

| Field | Type | Constraint |
|---|---|---|
| `from_agent` | string | Non-empty. Must differ from `to_agent`. |
| `to_agent` | string | Non-empty. Must differ from `from_agent`. |
| `task` | string | Non-empty. Imperative, single-sentence preferred. |
| `context_files` | list of strings | May be empty. Each item is a path the receiver should read. |
| `success_criteria` | list of strings | Non-empty. Each item is independently verifiable. |
| `return_format` | string | Non-empty. Describes the *shape* of what the receiver returns (e.g., "unified diff", "JSON `{count, items}`", "list of file paths"). |

## Optional Fields

| Field | Type | Purpose |
|---|---|---|
| `deadline` | string | Free-form deadline (e.g., "Phase 2 boundary", "before next standup"). When present, rendered as `## DEADLINE` in the prompt. |
| `output_type` | string | Used by `check_chain.py` to verify the next step accepts what this step produces. Examples: `code-diff`, `test-list`, `report-md`, `data-csv`. |
| `expected_input_type` | string | Used by `check_chain.py` to verify the previous step's `output_type` matches. Same example values. |

## Type Vocabulary (recommended, not enforced)

`output_type` and `expected_input_type` are free-form strings — `check_chain.py` only checks string equality. To stay interoperable across chains, prefer values from this list:

- `task-spec` — a structured task description
- `code-diff` — a unified diff or set of file edits
- `test-list` — a list of new tests to add
- `report-md` — a markdown report
- `findings-json` — structured findings JSON
- `data-csv` — tabular data
- `summary-text` — short prose summary
- `none` — receiver returns nothing measurable (avoid)

Mismatches are deterministic: if step `i.output_type = "code-diff"` and step `i+1.expected_input_type = "test-list"`, the chain fails fast.

## Validation Contract

`validate_handoff.py` returns:
```json
{"valid": true | false, "errors": ["...", ...]}
```

Exit 0 = valid; non-zero = invalid. The LLM does not override this.

## Why this schema

Every required field exists because, when missing, an agent silently does the wrong thing:
- No `task` → agent guesses scope.
- No `context_files` → agent re-reads the world or skips needed files.
- No `success_criteria` → "done" becomes subjective.
- No `return_format` → caller can't merge results from parallel children.
- Same `from_agent` / `to_agent` → instant cycle.
