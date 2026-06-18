# Example: Feature Search Traceability

End-to-end run. Demonstrates a 3-REQ matrix with one row per status:
- REQ-001 → covered (full SDD/PLAN/code/test chain)
- REQ-002 → partial (SDD/PLAN only, no code/test)
- REQ-003 → uncovered (PRD only)

```bash
# 1. Extract IDs and grep code
python ../../scripts/extract_ids.py \
    --prd PRD.md --sdd SDD.md --plan PLAN.md \
    --code-root code > /tmp/ids.json

# 2. Build the matrix
python ../../scripts/build_matrix.py \
    --ids-json /tmp/ids.json \
    --feature feature-search > /tmp/matrix.json

# 3. Render the report
python ../../scripts/write_matrix.py \
    --payload /tmp/matrix.json \
    --out /tmp/TRACEABILITY.md

# 4. Validate
python ../../scripts/validate_output.py \
    --file /tmp/TRACEABILITY.md \
    --prd PRD.md
```

## Files
- `PRD.md` — fixture PRD with 3 REQs.
- `SDD.md` — fixture SDD with traceability map.
- `PLAN.md` — fixture PLAN with 2 tasks.
- `code/` — code tree where REQ-001 has full coverage and REQ-002 has none.
- `payload.json` — expected output of `build_matrix.py`.
- `expected-output.md` — expected rendered report.
