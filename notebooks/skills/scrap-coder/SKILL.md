---
name: scrap-coder
version: 1.0.0
description: |
  Categorize a shift’s scrap log into the 7 standard scrap codes (S1-S7) and total the cost. Use when an operator or supervisor asks to "code this scrap log", "total tonight’s scrap", or "categorize the shift’s rejects". Produces a per-code breakdown and a dollar total. Do NOT use for rework tracking, downtime coding, or quality-escape (RMA) analysis — those are separate skills with their own code sets.
triggers:
  - "code this scrap log"
  - "total tonight's scrap"
  - "categorize the shift's rejects"
tools:
  - bash_tool
  - view
model: claude-sonnet-4-6
---

# scrap-coder

Turn a shift's free-text scrap log into coded line items and a cost total.

## Files
- `scripts/total_cost.py` — **Deterministic.** `categorize(rows)` codes each
  row and totals cost. Call this; do not redo the math inline.
- `knowledge/scrap_codes.md` — the 7 codes, trigger phrases, unit costs.
  Load only when a row is ambiguous and you need the rule.
- `templates/shift_report.md` — the output shape.
- `validation/quality-checklist.md` — pre-bump checklist.
- `examples/simple/` — smallest worked example; pattern-match against it.

## Contract
Given a list of scrap-log rows, produce a result such that:
1. Every non-rework row is assigned exactly one code in S1..S7.
2. The more specific code wins on ambiguity (S5 machine-fault > S7 unknown).
3. Rows containing "rework" are excluded from the cost total.
4. Quantity defaults to 1 when a row states no count.
5. `total_cost` equals the sum of (unit_cost * qty) over coded rows, rounded
   to cents.

## Knowledge
The authoritative code list, trigger phrases, and unit costs live in
`knowledge/scrap_codes.md`. Read it only for an ambiguous row.

## Steps
1. Collect the shift's scrap rows (caller supplies them).
2. Call `total_cost.categorize(rows)` for codes + totals.
3. For any row coded S7 (unknown), re-check against `knowledge/scrap_codes.md`.
4. Render the result into `templates/shift_report.md`.

## Output
A breakdown table (code, name, units, cost) plus a dollar total and an
excluded-rework count, as in `templates/shift_report.md`.

## Antipatterns
- Doing the cost arithmetic in the model's head instead of calling
  `total_cost.categorize` — it drifts and is unauditable.
- Counting "rework" rows toward scrap cost.
- Inventing a code outside S1..S7.

## Validation
- Run `pytest tests/unit/` — must exit 0.
- Walk `validation/quality-checklist.md` cold against the artifact.

## Examples
- `examples/simple/` — setup + dimensional + machine-fault + one rework.
  Expected total $55.90, 1 excluded.
