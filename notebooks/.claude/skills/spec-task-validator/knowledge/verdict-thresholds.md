# Verdict Thresholds

Two layers: per-task status, then overall PLAN verdict.

## Per-task status

| Status | Rule |
|---|---|
| **ok** | Zero blocking issues AND zero stylistic issues. |
| **warn** | Zero blocking issues AND ≥1 stylistic issue. |
| **fail** | ≥1 blocking issue (anything in the list below). |

### Blocking issues (fail)

- Bad task ID format (does not match `^T-\d{3,}$`)
- Phase not in `{Foundation, Core, Integration, Polish}`
- Missing or invalid `tdd_step` (must be one of `red`, `green`, `refactor`)
- Missing acceptance line
- Acceptance not measurable per `acceptance-rubric.md`
- Reference to undefined `REQ-NNN` (only when PRD provided)
- Reference to undefined `COMP-NNN` (only when SDD provided)

### Stylistic issues (warn)

- Title is all-lowercase
- (Future: title shorter than N chars, etc.)

## Overall PLAN verdict

| Verdict | Rule |
|---|---|
| **PASS** | Every task is `ok`. |
| **WARN** | No `fail` AND ≥1 `warn`. |
| **FAIL** | ≥1 `fail`. |

## PASS is not approval

A `PASS` verdict means **mechanically clean**: every task has an ID, a phase, a TDD step, a measurable acceptance, and resolvable cross-references. It does **not** mean:

- The decomposition is right.
- The phase ordering is sensible.
- The acceptance criteria catch the *right* failure modes.
- A reviewer would approve.

That judgment stays with the human. This skill grades; humans approve.
