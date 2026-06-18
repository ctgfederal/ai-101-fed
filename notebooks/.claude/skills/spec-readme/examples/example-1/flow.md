# Example: feature-search after init + PRD approval + one phase note

Demonstrates the full pipeline: `init_readme.py` → `update_status.py` → `append_phase_note.py` → `validate_output.py`.

## Files
- `README.md` — the rendered spec README after all three actions.

## Flow

```bash
# 1. Initialize the spec README.
python ../../scripts/init_readme.py \
  --feature feature-search \
  --specs-root /tmp/example-specs

# 2. Mark the PRD approved.
python ../../scripts/update_status.py \
  --feature feature-search \
  --specs-root /tmp/example-specs \
  --doc prd \
  --status approved

# 3. Append a phase-1 note.
python ../../scripts/append_phase_note.py \
  --feature feature-search \
  --specs-root /tmp/example-specs \
  --phase 1 \
  --name "Foundation" \
  --note "Spec under-specified the caching layer. Picked Redis 60s TTL."

# 4. Validate.
python ../../scripts/validate_output.py \
  --file /tmp/example-specs/feature-search/README.md
```

## What this demonstrates

- **Init populates all six required sections** (Status, Steering References, Decision Log Snippets, Phase Notes, Learnings, Open Questions) with placeholders that pass validation.
- **`update_status` flips PRD `draft` → `approved`** and updates the row's `Last Update` to today; SDD and PLAN remain `draft`.
- **`append_phase_note` adds `### Phase 1: Foundation`** under `## Phase Notes`, replacing the placeholder italics and inserting a timestamp + the note body.
- **`validate_output` exits 0** because: 6 sections present in order, 3 status rows valid, steering link present, no leftover template tokens, phase notes monotonic.
