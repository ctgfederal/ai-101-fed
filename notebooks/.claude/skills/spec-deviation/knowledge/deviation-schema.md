# Deviation Schema

The deviation payload is a JSON object. Every field is required; every field is a non-empty string.

## Required fields

| Field | Format | Description |
|---|---|---|
| `spec_id` | kebab-case | The spec the deviation belongs to (e.g. `feature-search`). |
| `deviation_id` | `^DEV-\d{3,}$` | The allocated `DEV-NNN`. Allocate via `scripts/allocate_deviation_id.py`. |
| `reason_category` | enum (below) | One of five categories; nothing else is allowed. |
| `description` | prose | Why the spec cannot be followed as written. |
| `original_decision` | `^(REQ\|COMP\|D)-\d+$` | The PRD requirement, SDD component, or build decision being deviated from. |
| `proposed_change` | prose | What the implementation will do instead. |
| `impact` | prose | Functional, timeline, and risk impact. |
| `status` | enum (below) | `proposed`, `approved`, or `rejected`. |
| `approver` | string | Name of the human who approves / rejects. |
| `date` | `YYYY-MM-DD` | ISO date the deviation was logged. |

## Allowed `reason_category`

| Value | Use when |
|---|---|
| `technical-blocker` | Spec approach is not possible due to platform / runtime / library constraints (e.g. WebSockets unavailable on chosen host). |
| `scope-clarification` | Spec was ambiguous; implementation has surfaced the actual scope. |
| `dependency-conflict` | A required upstream / downstream system enforces a different shape than the spec. |
| `performance-required` | Spec approach hits a hard performance ceiling; alternate approach needed. |
| `security-required` | Spec approach has a security implication that requires a different design. |

If the situation does not match one of these five, the deviation does not belong here. Either pick the closest fit and explain in `description`, or escalate (could indicate the rubric needs a new category — that is a skill change, not a payload override).

## Allowed `status`

| Value | Meaning |
|---|---|
| `proposed` | Logged, awaiting approver decision. Implementation should NOT proceed on a proposed deviation. |
| `approved` | Approved by the spec owner. Implementation may proceed. |
| `rejected` | Rejected by the spec owner. Implementation must follow the original decision. The block is **kept**, not deleted. |

## ID format

`DEV-NNN` where N is a digit. Three or more digits. Allocated monotonically per repo (across every SDD in `.claude/specs/`). Use `scripts/allocate_deviation_id.py`.

## Original decision format

`REQ-NNN` (PRD requirement), `COMP-NNN` (SDD component), or `D-NNN` (build decision). N is one or more digits. Whitespace and case are strict — `REQ-001` is valid; `req-1` is not.
