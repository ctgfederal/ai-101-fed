# Traceability Rules

A traceability link only counts as evidence if it comes from a deterministic, text-matching source. This document spells out what counts at each layer.

## SDD layer (REQ → COMP)

A `REQ-NNN` is linked to a `COMP-NNN` if and only if the SDD has a structured map line such as:

```
REQ-001 -> COMP-001, COMP-002
REQ-002: COMP-003
| REQ-003 | COMP-004, COMP-005 |
```

The pattern: a line containing `REQ-NNN` followed by `->`, `:`, or `|`, followed by one or more `COMP-NNN` tokens. Free-prose mentions of REQs in the SDD do **not** count — only the traceability map.

## PLAN layer (REQ → Task)

A `T-NNN` covers a `REQ-NNN` if and only if the task block lists that REQ under a `Requirements:` line:

```
- **T-001** (red): Migration
  - Components: COMP-001
  - Requirements: REQ-001, REQ-002
  - Acceptance: ...
```

The pattern: within the textual range of a task entry, find a `Requirements:` field containing `REQ-NNN` tokens. Tasks without a `Requirements:` line are excluded.

## Code layer (REQ → source file)

A non-test source file links to a `REQ-NNN` if and only if the file contains the literal string `REQ-NNN` somewhere in its text (typically in a comment such as `# REQ-001`, `// REQ-001`, or `/* REQ-001 */`).

Test/code classification is path-based:
- Test paths contain any of: `test_`, `_test`, `/tests/`, `/test/`, `.test.`, `.spec.`
- Anything else is treated as code.

## Test layer (REQ → test file)

A test file links to a `REQ-NNN` if and only if the file contains the literal string `REQ-NNN` somewhere in its text (in a docstring, test name, decorator, or comment). The file is identified as a test file by the same path heuristics above.

## What does NOT count

- LLM judgment that "this code probably implements REQ-001" — out.
- Implicit traceability through file names alone — out.
- Documentation prose that mentions a REQ without an explicit map — out.
- Commit messages that reference a REQ — out (not in scope; could be added later).

## Why mechanical

The matrix is a contract. If the LLM can declare "covered" without an inspectable text marker, the contract is unfalsifiable. Every status in this skill is reproducible byte-for-byte from the same inputs.
