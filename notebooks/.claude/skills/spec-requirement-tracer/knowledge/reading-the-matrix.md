# Reading the Matrix

How to interpret a rendered `TRACEABILITY.md` and triage gaps.

## Section by section

### Summary
A short table of counts plus a coverage percentage. Good for an at-a-glance "are we ready to merge?"

### Coverage Matrix
One row per PRD `REQ-NNN`. Columns: SDD components, PLAN tasks, code files, test files, status. Use this section to drill into a specific requirement.

### Gaps
Lists every row that is not `covered`, with the missing layers called out. This is the action list.

### Totals
Reconciliation block. The validator checks that `covered + partial + uncovered == total PRD REQs`. If this fails, the matrix is broken.

## Triage by status

### covered
No action. The chain is observable end-to-end. Note that this does not mean the implementation is correct — use `spec-validation` and `spec-compliance` for quality.

### partial — missing SDD
Update the SDD's traceability section to map this REQ to one or more components. If the REQ truly has no design coverage, the design is incomplete.

### partial — missing PLAN
Add a task to the PLAN whose `Requirements:` line includes this REQ. Or if the REQ is already covered transitively by a task on a covering component, add the explicit `Requirements:` line so the tracer can see it.

### partial — missing code
Either the code hasn't been written yet, or the implementer did not annotate the file. The cheapest remediation is a one-line comment marker (`# REQ-001 — search filter`) in the implementing file.

### partial — missing test
Same as code: write the test, or add the REQ ID to an existing test's docstring or name.

### uncovered
The REQ exists in the PRD but has no downstream work at all. Either drop it from PRD, or schedule design + plan + implementation. Uncovered REQs are the highest-priority gap to close.

## Common pitfalls

- **"The code is there but it's not annotated."** The tracer only sees what it can grep. If you want a row to flip to `covered`, add the REQ ID somewhere greppable in the code/test file.
- **"My SDD describes the design but doesn't have a traceability section."** Add one. The format is permissive: a heading `## Traceability` followed by lines like `REQ-001 -> COMP-001, COMP-002` is enough.
- **"My PLAN tasks list components, not requirements."** Add `Requirements:` lines to each task. The tracer uses the explicit REQ list, not transitivity.

## When to re-run

Re-run after:
- Edits to PRD (REQ added/removed).
- Edits to SDD traceability section.
- Edits to PLAN task `Requirements:` lines.
- Implementation work that adds/changes REQ markers in source/test files.

The matrix has no state of its own; each run is byte-exact from the same inputs.
