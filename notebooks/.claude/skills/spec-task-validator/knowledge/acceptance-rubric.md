# Acceptance Rubric

The acceptance criterion answers one question: **how does the implementer know the task is done?** The validator enforces this mechanically.

## Pass: contains an observation verb + concrete condition

The acceptance string passes if it contains at least one of these tokens:

| Category | Tokens |
|---|---|
| Test outcome | `passes`, `pass`, `asserts`, `assert` |
| Function output | `returns`, `return`, `produces`, `produce`, `outputs`, `output` |
| Match / comparison | `matches`, `match`, `equals`, `equal` |
| Error path | `raises`, `raise`, `exits`, `exit` |
| Numeric comparison | `<=`, `>=`, `==`, `<`, `>`, `=` |

## Fail: vague / aspirational

The acceptance fails if it contains any of these substrings (case-insensitive):

- `should work`
- `looks good`
- `tbd`
- `works fine`

It also fails if it is empty or whitespace-only.

## Examples

| Acceptance | Verdict | Why |
|---|---|---|
| `test_loader_caches_until_mtime_changes passes` | OK | "passes" + concrete test name |
| `parser returns AST with 3 children` | OK | "returns" + concrete count |
| `function exits with code 0 on missing file` | OK | "exits" + concrete code |
| `latency < 200ms at p99` | OK | `<` + concrete metric |
| `should work end to end` | FAIL | vague |
| `looks good in the demo` | FAIL | vague |
| `(empty)` | FAIL | empty |
| `TBD` | FAIL | placeholder |

## When to extend

If your project legitimately needs a new observation verb (e.g., `emits`, `logs`, `dispatches`), add it to the `OBSERVATION_TOKENS` list in `scripts/validate_tasks.py` AND update this rubric. Keep the list short — every added token is a chance to false-positive a vibes-based acceptance.
