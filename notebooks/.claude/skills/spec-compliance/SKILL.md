---
name: spec-compliance
description: |
  Verify a working implementation matches its approved spec by parsing the PRD's `REQ-NNN` requirements and the SDD's `COMP-NNN` components, scanning the repository for evidence of each (file paths exist at the SDD-declared location, REQ-IDs are referenced in source / tests, component names are imported), then emitting a markdown compliance report listing per-component evidence, per-requirement coverage, and any deviations (missing components, requirements with no implementation reference, scope creep). Use when the user runs `/compliance`, asks "does the implementation match the spec?", asks for a compliance check between PRD/SDD and code, or needs a gap report before declaring a feature done. Do NOT use to write or grade the spec itself (use `spec-prd-generator`, `spec-sdd-generator`, or `spec-validation`), to do free-form code review (use `/review-code`), to run tests (use `/test`), or to author new requirements — this skill compares spec to code and reports gaps, it does not change either side.
version: 2.0.0
triggers:
  - "/compliance"
  - "check spec compliance"
  - "does the implementation match the spec"
  - "verify implementation against spec"
  - "compliance report"
  - "PRD compliance check"
  - "SDD compliance check"
  - "spec to code gap analysis"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-compliance

Compare an approved spec (PRD `REQ-NNN`s + SDD `COMP-NNN`s) against a repository of code. Report which components are present, which requirements are implemented, and which deviations exist. The verdict is mechanical — the LLM may narrate but does not invent compliance status.

## Files

### Templates (`templates/`)
- `compliance-report.md.template` — Canonical layout for the compliance report. Placeholders: `{{PRD}}`, `{{SDD}}`, `{{REPO}}`, `{{STATUS}}`, `{{COMPONENTS_TABLE}}`, `{{REQUIREMENTS_TABLE}}`, `{{DEVIATIONS}}`, `{{SUMMARY}}`. Used by `write_report.py`.
- `payload.example.json` — Example JSON payload showing the exact shape `check_compliance.py` emits and `write_report.py` consumes.

### Scripts (`scripts/`)
- `parse_spec.py` — Deterministic. Reads a PRD file and an SDD file, extracts REQ-IDs from the PRD, COMP-IDs from the SDD, and the expected file paths declared next to each component. Args: `--prd <path> --sdd <path>`. Prints JSON `{reqs: [...], comps: [{id, name, expected_paths: [...]}], file_globs: [...]}` to stdout. Exit 0 always; non-zero is reserved for I/O failure.
- `check_compliance.py` — Deterministic. Given the parsed-spec JSON and a repo root, scans the repo for evidence of each component (does a file exist at any expected path?) and each requirement (is `REQ-NNN` referenced anywhere under `--repo-root`?). Args: `--spec-json <path> --repo-root <path>`. Prints JSON `{components: {COMP-ID: {name, expected_paths, found_paths, missing: bool}}, requirements: {REQ-ID: {referenced_in: [...], unreferenced: bool}}, deviations: [...], status: "compliant"|"partial"|"non-compliant"}` to stdout.
- `write_report.py` — Deterministic. Renders `compliance-report.md.template` from the JSON output of `check_compliance.py`. Args: `--payload <path> --out <path> [--force]`. Exit 0 on write.
- `validate_output.py` — Deterministic. Validates a rendered compliance report: required `##` sections present in order, every COMP-ID and REQ-ID from the parsed spec listed in their tables, status is one of `compliant`/`partial`/`non-compliant`, no unsubstituted `{{TOKEN}}` placeholders. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `compliance-rubric.md` — What counts as evidence (file at expected path, REQ-ID grepped in source, component name imported). Mechanical rules used by `check_compliance.py`.
- `deviation-types.md` — Catalogue of deviation kinds (missing component, renamed component, requirement not implemented, scope creep) and how each is detected and reported.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any compliance report this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `sample_prd`, `sample_sdd`, `sample_repo`, `valid_payload`.
- `unit/test_parse_spec.py` — Unit tests for the spec parser: REQ-ID extraction, COMP-ID extraction, expected-paths extraction, malformed input handling.
- `unit/test_check_compliance.py` — Unit tests for the compliance checker: component evidence detection, requirement reference detection, status computation, deviation classification.
- `unit/test_write_report.py` — Unit tests for template substitution, payload validation, write semantics, `--force` behavior.
- `unit/test_validate_output.py` — Unit tests for the report validator: happy path, missing section, missing COMP-ID, invalid status, leftover template tokens.
- `integration/test_spec_compliance_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_compliance_eval.py` — Three-case eval: clean compliance (all components present, all reqs referenced), partial compliance (one component missing), broken compliance (multiple gaps). Verifies eval harness shape.
- `smoke/test_e2e.py` — End-to-end: `parse_spec.py` → `check_compliance.py` → `write_report.py` → `validate_output.py` against a fixture spec + fixture repo.

### Examples (`examples/`)
- `example-1/` — Worked example: a fixture PRD (`PRD.md`), a fixture SDD (`SDD.md`), a tiny fixture repo (`repo/`), the parsed-spec JSON (`parsed.json`), the compliance JSON (`payload.json`), and the rendered report (`expected-report.md`).

## Contract

Given a PRD path, an SDD path, and a repo root, produce one compliance report file such that:

1. The report path is exactly `--out` from the invocation.
2. The body has these `##` sections in order: `## Spec`, `## Repository`, `## Status`, `## Components`, `## Requirements`, `## Deviations`, `## Summary`.
3. The `## Status` value is exactly one of `compliant`, `partial`, `non-compliant` and is computed deterministically from the per-component / per-requirement evidence.
4. Every COMP-ID parsed from the SDD appears in the `## Components` table.
5. Every REQ-ID parsed from the PRD appears in the `## Requirements` table.
6. `python scripts/validate_output.py --file <path>` exits 0.
7. The report contents are produced by the scripts; the LLM does not modify the integer counts or the status value.

## Knowledge

### What evidence counts
- **Component present** — at least one of the SDD-declared `expected_paths` (a file path from the component's section) exists relative to the repo root. Glob patterns are accepted (e.g. `src/auth/*.py`).
- **Requirement implemented** — the literal token `REQ-NNN` appears anywhere under the repo root (source files or tests). Tests-only references count, with a hint in the report.
- **Component imported** — optional secondary evidence; if a component name is found in an `import`/`from` line, the component is "linked".

### Status bands
- **`compliant`** — every COMP-ID has at least one `found_path` AND every REQ-ID is referenced at least once.
- **`partial`** — at least one COMP-ID is found AND at least one REQ-ID is referenced, but at least one of either is missing.
- **`non-compliant`** — no COMP-ID found OR no REQ-ID referenced.

See `knowledge/compliance-rubric.md` for the exact rules.

### Deviations
Four catalogued kinds (see `knowledge/deviation-types.md`):
- **missing-component** — COMP-ID has no `found_paths`.
- **renamed-component** — COMP-ID has no `found_paths` but a file exists at a *similar* path; flagged as a hint, not a hard miss.
- **unreferenced-requirement** — REQ-ID appears nowhere in the repo.
- **scope-creep** — file in repo references a `REQ-NNN` ID that does not appear in the parsed PRD.

## Steps

1. **Resolve inputs.** Confirm the PRD path, SDD path, and repo root. Common cases: `.claude/specs/<feature>/PRD.md`, `.claude/specs/<feature>/SDD.md`, project root. If the user passes a feature ID, locate the spec folder and use its PRD + SDD.

2. **Parse spec.** Run `python scripts/parse_spec.py --prd <prd> --sdd <sdd>`. Capture the JSON. Save to `/tmp/parsed-spec.json`.

3. **Check compliance.** Run `python scripts/check_compliance.py --spec-json /tmp/parsed-spec.json --repo-root <root>`. Capture the JSON output. Save to `/tmp/compliance.json`.

4. **Render report.** Run `python scripts/write_report.py --payload /tmp/compliance.json --out <report-path>`. Default report path: `<spec-folder>/COMPLIANCE.md` next to the PRD/SDD.

5. **Validate report.** Run `python scripts/validate_output.py --file <report-path>`. Must exit 0. If it does not, fix the upstream input or report a script bug — never hand-edit the report.

6. **Narrate gaps.** For each entry in the `## Deviations` section, the LLM may add a one-line human-readable explanation under it. The LLM does **not** change the status value or the table contents.

7. **Announce.** Print the status, counts, and report path. Example:
   ```
   Compliance: <feature>
   Status:        partial
   Components:    7/8 present
   Requirements:  12/14 referenced
   Deviations:    2

   Report: <report-path>
   ```

## Output

A single markdown report rendered from `templates/compliance-report.md.template`. No other side effects. Suggested filename: `<spec-folder>/COMPLIANCE.md`.

## Antipatterns

- **LLM sets the status.** The status comes from `check_compliance.py`. The LLM only narrates and may suggest fixes, never override.
- **Skipping `validate_output.py`.** A report the validator hasn't seen is not done.
- **Treating `compliant` as "ship it".** `compliant` means *every component has evidence and every requirement is referenced*. It does not mean the tests pass, the security review passed, or the product judgment is correct.
- **Hand-editing the report.** Edit the spec or the code, then re-run the pipeline. Never modify the report directly — the validator will catch byte-level drift.
- **Ignoring `scope-creep`.** A `REQ-NNN` referenced in code but not in the PRD is a real deviation. Either add it to the PRD or remove it from the code.
- **Bundling code review.** This skill verifies presence and reference, not quality. Free-form code review goes to `/review-code`.
- **Validating during a refactor.** If files are mid-rename, `missing-component` and `renamed-component` deviations are noisy. Run after the move is done.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. Status, components-table, and requirements-table in the report match the JSON output of `check_compliance.py` byte-for-byte.

## Examples

- **`examples/example-1/`** — Worked example. A fixture PRD with two requirements, an SDD with two components, and a tiny fixture repo where one component is implemented and one is missing. Demonstrates: status `partial`, one `missing-component` deviation, one `unreferenced-requirement` deviation. Includes `PRD.md`, `SDD.md`, `repo/`, `parsed.json`, `payload.json`, and `expected-report.md`.
