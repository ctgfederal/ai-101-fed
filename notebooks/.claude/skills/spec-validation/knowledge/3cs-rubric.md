# 3Cs Rubric

This is the mechanical rubric used by `scripts/score_3cs.py`. Each C is scored 0-10. Each check is worth a fixed number of points; missed checks deduct from the starting score of 10.

## Completeness — "Is the content all there?"

Starts at 10. Deductions:

| Check | Deduction | Detection |
|---|---|---|
| Required `##` section missing | -2 per section | Heuristic: if file looks like a PRD, expects sections like `## Functional Requirements`, `## Success Metrics`. If SDD: `## Components`, `## Traceability`. If unsure, only counts a base set: at least three `##` sections present. |
| `[NEEDS CLARIFICATION]` marker present | -3 (capped once) | Substring search |
| `TODO` / `FIXME` / `XXX` marker present | -1 (capped once) | Word-boundary regex |
| Empty section (heading with no body) | -1 per empty | Heading immediately followed by another heading |

Floor: 0.

## Consistency — "Does it agree with itself?"

Starts at 10. Deductions:

| Check | Deduction | Detection |
|---|---|---|
| Cross-reference to a `REQ-NNN` / `D-NNN` / `T-NNN` / `US-N` ID that is not defined in the same file | -2 per dangling ref (capped at -6) | Regex extract definitions (`**REQ-001**` style) and references (any other `REQ-001` mention); subtract |
| Duplicate ID definition | -3 per duplicate (capped at -6) | Same regex; counts repeated definitions |
| Verdict / score inside the body that contradicts what the file claims to be (e.g., status: DRAFT but title says FINAL) | -1 | String compare on simple cases; usually 0 |

Floor: 0.

## Correctness — "Is the format valid?"

Starts at 10. Deductions:

| Check | Deduction | Detection |
|---|---|---|
| Requirement-looking line missing EARS pattern | -2 per offender (capped at -6) | Lines starting `**REQ-NNN**` that contain none of: SHALL, WHEN, WHILE, WHERE, IF |
| MoSCoW value outside `{Must, Should, Could, Won't}` | -2 per offender (capped at -4) | Regex on parenthesised priority |
| Feature path not kebab-case | -1 | Regex on header line |

Floor: 0.

## Overall

`overall = round((completeness + consistency + correctness) / 3)`. No weighting; if you want weighting, fork the rubric.

## Files where the rubric does NOT apply cleanly

If the target is a code file or a non-PRD/SDD/PLAN markdown file, the scorer applies only the generic checks (NEEDS CLARIFICATION, TODO/FIXME, IDs unique). The Correctness checks are skipped (no deduction, but no positive evidence either) and the score reflects what could be measured. Always state this caveat in the narrative.
