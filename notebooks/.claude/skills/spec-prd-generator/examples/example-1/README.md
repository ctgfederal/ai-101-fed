# Example: Feature Search PRD

Demonstrates the full pipeline: init → allocate → write → validate.

## Files
- `payload.json` — input.
- `expected-output.md` — generated PRD at `.claude/specs/feature-search/PRD.md`.

## Flow

```bash
python ../../scripts/init_prd.py --feature feature-search --specs-root /tmp/specs
python ../../scripts/allocate_req_ids.py --specs-root /tmp/specs --count 2
python ../../scripts/write_prd.py --payload payload.json --out /tmp/specs/feature-search/PRD.md
python ../../scripts/validate_output.py --file /tmp/specs/feature-search/PRD.md
```

Demonstrates: 9 sections in correct order, EARS-formatted requirements, MoSCoW table, steering anchor links.
