---
name: spec-deviation
version: 2.0.0
description: |
  Capture an implementation deviation from an approved spec and append a structured `## Deviations` block to the target SDD. Use when `/implement` discovers that a `REQ-NNN`, `COMP-NNN`, or `D-NNN` decision cannot be followed as written — because of a technical blocker, scope clarification, dependency conflict, performance constraint, or security constraint — and the deviation needs an approval trail. Allocates a monotonic `DEV-NNN` ID, validates the payload against the deviation schema, renders the deviation block from a template, and appends it to the SDD. Do NOT use for trivial differences (track those as TODOs in the PLAN), for free-form architecture changes (run `/build` again), to rewrite the spec wholesale (regenerate via `/specify`), or to bypass approval — a deviation in `proposed` status is a request, not a fait accompli.
triggers:
  - "/deviation"
  - "spec deviation"
  - "log a deviation"
  - "log deviation"
  - "deviate from spec"
  - "implementation can't follow spec"
  - "DEV-"
  - "record a spec deviation"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-deviation

Capture a spec deviation as a structured block appended to the target SDD. Every deviation is `DEV-NNN`, has a single `reason_category`, references the original `REQ-NNN` / `COMP-NNN` / `D-NNN`, carries an approval status, and survives validation. The LLM narrates; the scripts validate, allocate IDs, and render the block.

## Files

### Templates (`templates/`)
- `deviation-block.md.template` — Canonical layout for one deviation block. Placeholders: `{{DEV_ID}}`, `{{DATE}}`, `{{SPEC_ID}}`, `{{REASON_CATEGORY}}`, `{{ORIGINAL_DECISION}}`, `{{DESCRIPTION}}`, `{{PROPOSED_CHANGE}}`, `{{IMPACT}}`, `{{STATUS}}`, `{{APPROVER}}`. Used by `append_deviation.py`.
- `payload.example.json` — Example deviation payload showing the exact shape `validate_deviation.py` accepts and `append_deviation.py` consumes.

### Scripts (`scripts/`)
- `validate_deviation.py` — Deterministic. Reads a deviation JSON payload (path or stdin), validates against the schema (required keys, `DEV-NNN` format, allowed `reason_category`, allowed `status`, original-decision ID format). Args: `--payload <path>` (omit to read stdin). Exit 0 = valid; non-zero = schema violation, error printed to stderr.
- `allocate_deviation_id.py` — Deterministic. Scans every `.claude/specs/*/SDD.md` under a specs root, finds the largest existing `DEV-NNN`, and prints the next `--count` IDs (one per line) starting from max+1. Args: `--specs-root <path>` `--count <int>`. Exit 0 on success.
- `append_deviation.py` — Deterministic. Renders `templates/deviation-block.md.template` from a validated payload and appends the rendered block to the target SDD under a `## Deviations` section (created if absent). Refuses to overwrite an existing `DEV-NNN` block unless `--force`. Args: `--payload <path>` `--sdd <path>` `[--force]`. Exit 0 on append.
- `validate_output.py` — Deterministic. Validates the appended SDD: every deviation block has all required fields, every `DEV-NNN` is unique, every `status` is allowed, every `reason_category` is allowed. Args: `--sdd <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `deviation-schema.md` — Required and optional fields; allowed values for `reason_category` and `status`; ID formats.
- `approval-workflow.md` — `proposed` → `approved` / `rejected` lifecycle; who approves what; how rejected deviations are documented and not deleted.
- `when-to-deviate.md` — Guardrails: deviation is for *forced* changes (technical blocker, dependency conflict, etc.), not preference. Trivial differences belong in PLAN TODOs, not deviations.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any deviation block this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `valid_payload`, `clean_sdd`, `populated_sdd`, `bad_payload`.
- `unit/test_validate_deviation.py` — Unit tests for the schema validator: happy path, every required field missing, bad enums, malformed IDs.
- `unit/test_allocate_deviation_id.py` — Unit tests for ID allocation: empty specs root, single SDD with one DEV, multiple SDDs with gaps, count > 1.
- `unit/test_append_deviation.py` — Unit tests for the appender: append to clean SDD, append to SDD with existing Deviations section, refuse-overwrite without `--force`, force-overwrite.
- `unit/test_validate_output.py` — Unit tests for output validation: clean SDD with valid deviations, duplicate DEV-NNN, bad status value, missing required field.
- `integration/test_spec_deviation_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_deviation_eval.py` — Three-case eval: technical-blocker forces deviation (proposed), scope-clarification approved, performance-required rejected. Verifies eval shape.
- `smoke/test_e2e.py` — End-to-end: `validate_deviation.py` → `allocate_deviation_id.py` → `append_deviation.py` → `validate_output.py` against a fixture SDD.

### Examples (`examples/`)
- `example-1/` — Worked example: a fixture SDD (`input-sdd.md`), an inbound deviation JSON payload (`payload.json`), and the expected appended SDD (`expected-sdd.md`). Demonstrates a `technical-blocker` deviation moving from `proposed` to a logged block.

## Contract

Given a validated deviation payload and a target SDD path, produce one updated SDD such that:

1. The SDD path is exactly `--sdd` from the invocation; no other files are written.
2. The SDD contains a `## Deviations` section. If it did not exist, the section is appended at end-of-file.
3. The new deviation block has these `###` sub-headings in order: `### {{DEV_ID}}`, then bold-labelled lines for `Date`, `Reason Category`, `Original Decision`, `Status`, `Approver`, plus prose blocks for `Description`, `Proposed Change`, `Impact`.
4. `DEV_ID` matches `^DEV-\d{3}$` and is **unique** across the SDD.
5. `reason_category` is one of: `technical-blocker`, `scope-clarification`, `dependency-conflict`, `performance-required`, `security-required`.
6. `status` is one of: `proposed`, `approved`, `rejected`.
7. `original_decision` matches one of: `REQ-NNN`, `COMP-NNN`, `D-NNN` (where N is a digit).
8. `python scripts/validate_output.py --sdd <path>` exits 0 after the append.
9. The block is rendered by `append_deviation.py`; the LLM does not freehand-write the block.

## Knowledge

### Deviations vs TODOs in one paragraph
A **deviation** is a forced change to an approved decision — a technical blocker, scope clarification surfaced mid-implementation, dependency conflict, or hard performance / security constraint. It needs an approval trail because the spec has already been signed off. A **TODO** is a non-blocking gap a developer chose to defer. If the implementation could match the spec but the developer preferred something else, that is a `/build` re-run, not a deviation. See `knowledge/when-to-deviate.md`.

### Approval workflow
A deviation enters as `proposed`. The approver (the human who owns the spec) marks it `approved` or `rejected`. **Rejected deviations are not deleted** — they stay as historical record. Re-attempts allocate a new `DEV-NNN`. See `knowledge/approval-workflow.md`.

### Why the LLM does not write the block
The block is a structured artifact with required fields, enum-constrained values, and a uniqueness constraint on the ID. Letting the LLM freehand it leads to silently-skipped fields, invented `reason_category` values, and duplicate IDs. The scripts make those impossible. See `knowledge/deviation-schema.md`.

## Steps

1. **Confirm the deviation is forced.** Read `knowledge/when-to-deviate.md`. If the difference is preferential or trivial, stop and add a TODO instead.

2. **Locate the target SDD.** Common path: `.claude/specs/<feature>/SDD.md`. If the user gave a feature ID, resolve it.

3. **Identify the original decision.** Find the `REQ-NNN`, `COMP-NNN`, or `D-NNN` in the SDD that the implementation cannot follow.

4. **Allocate a deviation ID.** Run `python scripts/allocate_deviation_id.py --specs-root .claude/specs --count 1`. Capture the `DEV-NNN`.

5. **Build the payload.** Construct a JSON payload with all required fields. Set `status` to `proposed` for new deviations. Save it to a temp file (e.g. `/tmp/deviation.json`).

6. **Validate the payload.** Run `python scripts/validate_deviation.py --payload /tmp/deviation.json`. Must exit 0. Fix and re-validate on any error.

7. **Append.** Run `python scripts/append_deviation.py --payload /tmp/deviation.json --sdd <path-to-SDD>`. Must exit 0.

8. **Validate the SDD.** Run `python scripts/validate_output.py --sdd <path-to-SDD>`. Must exit 0.

9. **Announce.** Print the new `DEV-NNN`, status, original decision, and SDD path. Example:
   ```
   Deviation logged: DEV-014
   Status:           proposed
   Original:         REQ-042 (in PRD), implemented as COMP-007
   Reason:           technical-blocker
   SDD:              .claude/specs/feature-search/SDD.md

   Awaiting approver decision.
   ```

10. **Notify the approver.** This skill does not send notifications. The user must obtain `approved` or `rejected` and re-run with the updated payload (forced overwrite of the `DEV-NNN` block) to flip the status.

## Output

A single updated SDD with one new deviation block appended under `## Deviations`. No other side effects.

## Antipatterns

- **LLM freehand-writes the block.** The block is rendered by `append_deviation.py` from `templates/deviation-block.md.template`. The LLM provides the payload, never the block prose.
- **Inventing a `reason_category`.** The five enums in `knowledge/deviation-schema.md` are the entire allowed set. Need a sixth? That is a skill change, not a freehand override.
- **Skipping `validate_output.py`.** A deviation that the validator hasn't seen is not done.
- **Deleting a rejected deviation.** Rejected deviations are kept as historical record. A re-attempt is a new `DEV-NNN`, not an edit.
- **Logging trivial differences.** If the implementation could have matched the spec, this is not a deviation. Add a TODO to the PLAN instead.
- **Editing the spec in place.** This skill appends to `## Deviations`. It does not silently mutate `REQ-NNN`, `COMP-NNN`, or `D-NNN`. The decision being deviated from stays as-written; the deviation references it.
- **Treating `proposed` as approval.** Status `proposed` means *requested*. Implementation should not proceed on a proposed deviation without the approver flipping it to `approved`.
- **Bundling approvals.** One block per deviation. If two `REQ-NNN`s need deviations for the same reason, allocate two `DEV-NNN`s.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --sdd <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. The appended block matches the rendered template byte-for-byte (no LLM rewrites).

## Examples

- **`examples/example-1/`** — Worked example: a fixture SDD missing a `## Deviations` section, an inbound `technical-blocker` deviation referencing `REQ-101` (cannot use WebSockets, deployment platform unsupported), and the resulting SDD with a freshly appended `## Deviations` section containing one `DEV-001` block in `proposed` status. Includes `input-sdd.md`, `payload.json`, and `expected-sdd.md`.
