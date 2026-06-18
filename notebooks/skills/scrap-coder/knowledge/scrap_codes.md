# Scrap codes — standard 7 (Line 4, swing shift)

Every scrap event maps to exactly one of these codes. Cost is USD per unit
scrapped (material + labor already burned at the scrap point).

| Code | Name              | Trigger phrase in the log              | Unit cost (USD) |
|------|-------------------|----------------------------------------|-----------------|
| S1   | Setup / first-off | "setup", "first off", "first article"  | 4.50            |
| S2   | Dimensional       | "out of tol", "oversize", "undersize"  | 12.00           |
| S3   | Surface defect    | "scratch", "burr", "porosity", "pit"   | 9.25            |
| S4   | Material flaw     | "inclusion", "void", "bad stock"       | 18.75           |
| S5   | Machine fault     | "spindle", "crash", "tool break"       | 27.40           |
| S6   | Operator error    | "wrong program", "misload", "fat finger"| 15.00          |
| S7   | Unknown / other   | anything that matches none of the above | 6.00           |

Rules:
- One code per row. If two could apply, the more specific wins (S5 > S7).
- "rework" is NOT scrap — exclude it from the total.
- Quantity defaults to 1 if the row does not state a count.
