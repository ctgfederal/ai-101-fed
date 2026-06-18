# Example: orchestrator → backend-developer → test-implementation

A two-step linear chain. Demonstrates the full pipeline:
1. `validate_handoff.py` — schema check on each handoff payload.
2. `render_handoff.py` — produce the prompt the receiving agent reads.
3. `check_chain.py` — verify the chain has no cycles and types match between steps.
4. `validate_output.py` — confirm each rendered prompt has all six required sections.

## Files
- `chain.json` — full chain payload with two consecutive handoffs.
- `handoff-1.json` — first handoff: orchestrator → backend-developer.
- `handoff-2.json` — second handoff: backend-developer → test-implementation.
- `handoff-1.md` — rendered prompt for handoff-1.
- `handoff-2.md` — rendered prompt for handoff-2.
- `chain-validation.json` — output of `check_chain.py` (valid: true, pattern: linear).

## Flow

```bash
# Validate each handoff payload
python ../../scripts/validate_handoff.py --file handoff-1.json
python ../../scripts/validate_handoff.py --file handoff-2.json

# Render each prompt
python ../../scripts/render_handoff.py --payload handoff-1.json --out handoff-1.md
python ../../scripts/render_handoff.py --payload handoff-2.json --out handoff-2.md

# Check the chain end-to-end
python ../../scripts/check_chain.py --chain-json chain.json

# Validate each rendered prompt
python ../../scripts/validate_output.py --file handoff-1.md
python ../../scripts/validate_output.py --file handoff-2.md
```

## What this demonstrates
- Required fields populated for both steps.
- `output_type` of step 1 (`code-diff`) matches `expected_input_type` of step 2 (`code-diff`).
- No cycle: `orchestrator -> backend-developer -> test-implementation`.
- Pattern: `linear`.
- Both rendered prompts have all six required sections; handoff-1 includes the optional `## DEADLINE`.
