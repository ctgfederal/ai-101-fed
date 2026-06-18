# SDD Schema

## Required payload fields

| Field | Type | Notes |
|---|---|---|
| `feature` | string | Kebab-case. |
| `feature_title` | string | Human-readable. |
| `overview` | string | One paragraph: what this is, at a glance. |
| `architecture` | string | The pattern + data flow. |
| `components` | list | Each: `{id, name, responsibility, dependencies, contract: {inputs, outputs}}`. ≥1. |
| `data_model` | string | Entities, indexes, relationships. |
| `integrations` | string | External services. May be `_(none)_`. |
| `traceability` | dict | `{REQ-NNN: [COMP-NNN, ...]}`. Must cover EVERY PRD REQ. |
| `alternatives` | string | Considered but rejected, with reasons. |
| `risks` | string | Risks and mitigations. |
| `open_questions` | list | May be empty. |

## COMP-ID format
- `COMP-NNN` (zero-padded to 3, growing as needed).
- Local to the SDD (per-spec); not globally unique.
- Must be unique within this SDD.

## Traceability rules
- Every PRD `REQ-NNN` appears as a key.
- Every value is a non-empty list of COMP-IDs that exist in `components`.
- One REQ can map to multiple components.
- One component can serve multiple REQs.

## What goes where

| Question | Answer |
|---|---|
| What does the system do? | PRD (requirements) |
| How is the system built? | SDD (this doc) |
| Who builds what when? | PLAN |
| Why this design? | SDD `Alternatives Considered` |
| Which decisions were made and when? | `.claude/decisions-log.md` (D-NNN) |
