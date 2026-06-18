# Example: Parallel Build (auth + billing)

Demonstrates the full `agent-delegation` flow on a two-agent parallel build that's collision-free.

## Files in this example
- `auth-payload.json` — payload for the auth agent (owns `src/auth/` and `tests/auth/`).
- `billing-payload.json` — payload for the billing agent (owns `src/billing/` and `tests/billing/`).
- `payloads.json` — both payloads in a JSON list, fed to `check_collisions.py`.
- `auth-prompt.expected.md` — what `render_prompt.py` produces for the auth payload.
- `billing-prompt.expected.md` — what `render_prompt.py` produces for the billing payload.
- `collision-report.expected.json` — the expected `safe: true` output from `check_collisions.py`.

## Flow

```bash
# 1. Validate each payload
python ../../scripts/validate_delegation.py --payload auth-payload.json
python ../../scripts/validate_delegation.py --payload billing-payload.json

# 2. Render each prompt
python ../../scripts/render_prompt.py --payload auth-payload.json --out /tmp/auth-prompt.md
python ../../scripts/render_prompt.py --payload billing-payload.json --out /tmp/billing-prompt.md

# 3. Validate the rendered prompts
python ../../scripts/validate_output.py --file /tmp/auth-prompt.md
python ../../scripts/validate_output.py --file /tmp/billing-prompt.md

# 4. Check parallel-safety BEFORE launching anything
python ../../scripts/check_collisions.py --payloads-json payloads.json
# → {"collisions": [], "safe": true}
```

If `safe` were `false`, the orchestrator would re-scope or sequence the agents instead of launching in parallel.
