# Example: Technical-blocker deviation on REQ-101

Demonstrates the full pipeline: `validate_deviation.py` → `allocate_deviation_id.py` → `append_deviation.py` → `validate_output.py`.

## Files
- `input-sdd.md` — fixture SDD with no `## Deviations` section.
- `payload.json` — inbound deviation: REQ-101 specified WebSockets, but the chosen runtime cannot host persistent connections. Status: `proposed`.
- `expected-sdd.md` — the SDD after `append_deviation.py` runs, with a fresh `## Deviations` section containing one `DEV-001` block.

## Flow

```bash
# allocate (in a real run; the fixture pre-allocates DEV-001)
python ../../scripts/allocate_deviation_id.py --specs-root /tmp/empty --count 1
# DEV-001

# validate the payload
python ../../scripts/validate_deviation.py --payload payload.json

# append to the target SDD
python ../../scripts/append_deviation.py \
  --payload payload.json \
  --sdd /tmp/working-sdd.md

# validate the result
python ../../scripts/validate_output.py --sdd /tmp/working-sdd.md
```

## What this demonstrates
- A `## Deviations` section being created from scratch (the input SDD had none).
- A `technical-blocker` deviation with all required fields.
- Status `proposed` — implementation should pause until the approver flips to `approved` or `rejected`.
- Block rendering is byte-deterministic — the LLM never freehand-writes the block.
