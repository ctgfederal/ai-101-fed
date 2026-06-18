# Coverage Statuses

Every row in the traceability matrix has exactly one status, computed mechanically from the four layers.

## covered

A REQ is **covered** when it has ≥1 link at every one of these layers:
- SDD: at least one `COMP-NNN` mapped to it via the SDD traceability dict.
- PLAN: at least one `T-NNN` lists it in its `Requirements:` line.
- Code: at least one non-test source file contains the REQ ID.
- Test: at least one test file contains the REQ ID.

`covered` means *all four links exist*. It does not mean the implementation is correct, complete, or performant — only that the chain is observable.

## partial

A REQ is **partial** when ≥1 layer has a link but at least one layer is empty. Examples:
- SDD maps REQ-001 to COMP-002, PLAN has T-005 covering REQ-001, but no code or test file mentions REQ-001 → partial (missing: code, test).
- Code and tests mention REQ-002 but the SDD has no entry for it → partial (missing: SDD).

The Gaps section of the matrix lists which layers are missing for each partial row, so remediation is targeted.

## uncovered

A REQ is **uncovered** when zero layers have any links. The REQ is defined in the PRD but does not appear in the SDD traceability dict, no PLAN task references it, no source file mentions it, and no test file mentions it.

Uncovered REQs are typically:
- Dropped from scope but not removed from PRD.
- Newly added requirements without downstream work yet.
- Placeholder requirements awaiting refinement.

## Decision table

| SDD | PLAN | Code | Test | Status |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | covered |
| ✓ | ✓ | ✓ | — | partial |
| ✓ | ✓ | — | ✓ | partial |
| ✓ | ✓ | — | — | partial |
| ✓ | — | * | * | partial |
| — | ✓ | * | * | partial |
| — | — | ✓ | * | partial |
| — | — | * | ✓ | partial |
| — | — | — | — | uncovered |

(`✓` = ≥1 link; `—` = 0 links; `*` = either)

## Promotion rules

- Adding a missing layer can only move a row "up" (uncovered → partial → covered).
- A row never moves down on subsequent runs unless inputs change (PRD adds a REQ, SDD removes a map, etc.).
- The matrix is regenerated each run; there is no persistent state between runs.
