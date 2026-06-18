---
name: spec-requirement-tracer
version: 3.0.0
description: |
  Build and validate a traceability matrix at `.claude/specs/<feature>/TRACEABILITY.md` proving every PRD `REQ-NNN` flows through ≥1 SDD `COMP-NNN`, ≥1 PLAN `T-NNN`, and ≥1 code/test reference (REQ-ID grepped from source). Renders a per-requirement coverage report (`covered`, `partial`, `uncovered`) and lists gaps for remediation. Use when a user runs `/trace`, asks "trace requirements", "show coverage matrix", "are all requirements covered", needs a pre-merge readiness check, or wants to verify the spec→code chain. Do NOT use to write or score the spec itself (use `spec-validation`), to author requirements (`spec-prd-generator`), to generate tasks (`spec-plan-generator`), to run tests, or to do free-form code review — this skill only proves coverage exists, it does not judge quality.
triggers:
  - "/trace"
  - "trace requirements"
  - "traceability matrix"
  - "show coverage matrix"
  - "are all requirements covered"
  - "requirement coverage report"
  - "REQ to code mapping"
  - "is every REQ implemented"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-requirement-tracer

Render `TRACEABILITY.md` from deterministic ID extraction, an SDD traceability map, a PLAN coverage map, and grep-discovered code/test references. The matrix is the contract — the LLM does not invent links. Coverage statuses live in `knowledge/coverage-statuses.md`.

## Files

### Templates (`templates/`)
- `traceability-matrix.md.template` — Canonical layout for the rendered matrix. Placeholders: `{{FEATURE_TITLE}}`, `{{SUMMARY_TABLE}}`, `{{ROWS}}`, `{{GAPS}}`, `{{TOTALS}}`. Used by `write_matrix.py`.
- `payload.example.json` — Example JSON payload showing the exact shape `build_matrix.py` emits and `write_matrix.py` consumes.

### Scripts (`scripts/`)
- `extract_ids.py` — Deterministic. Reads PRD, SDD, PLAN, then greps a code root for REQ-NNN occurrences in source/test files. Args: `--prd <path>` `--sdd <path>` `--plan <path>` `--code-root <path>` `[--code-globs "*.py,*.test.py"]`. Prints JSON `{prd_reqs, sdd_comps, plan_tasks, sdd_traceability, plan_task_reqs, code_refs, test_refs}` to stdout. Exit 0 always (the JSON content is the result).
- `build_matrix.py` — Deterministic. Builds the per-requirement matrix from extracted IDs, the SDD traceability dict, and the PLAN task→reqs map. Args: `--ids-json <path>`. Emits JSON `{feature, rows: [{req, comps, tasks, code_refs, tests_refs, status}]}` where status is one of `covered|partial|uncovered`.
- `write_matrix.py` — Deterministic. Renders `traceability-matrix.md.template` from the build_matrix payload and writes the matrix to disk. Args: `--payload <path>` `--out <path>` `[--force]`. Exit 0 on write.
- `validate_output.py` — Deterministic. Validates the rendered matrix: required sections present, every PRD REQ has a row, every status is in `{covered, partial, uncovered}`, totals row reconciles with row counts. Args: `--file <path>` `--prd <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `traceability-rules.md` — What counts as evidence at each layer (SDD references via traceability dict; PLAN references via task `reqs[]` list; code refs via grep of `REQ-NNN` in comments and test names; etc.).
- `coverage-statuses.md` — `covered` = ≥1 link at each of: SDD, PLAN, code, test. `partial` = some links missing. `uncovered` = no links beyond PRD.
- `reading-the-matrix.md` — How to interpret the rendered report; what to do about partial / uncovered rows.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any traceability matrix this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `fake_prd`, `fake_sdd`, `fake_plan`, `fake_code_root`, `valid_ids_payload`, `valid_matrix_payload`.
- `unit/test_extract_ids.py` — Unit tests for ID extraction and code grep.
- `unit/test_build_matrix.py` — Unit tests for matrix construction and status assignment.
- `unit/test_write_matrix.py` — Unit tests for template substitution and write semantics.
- `unit/test_validate_output.py` — Unit tests for the matrix validator.
- `integration/test_spec_requirement_tracer_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_requirement_tracer_eval.py` — Three-case eval: full coverage, partial coverage, uncovered REQ. Verifies eval harness shape.
- `smoke/test_e2e.py` — End-to-end: `extract_ids.py` → `build_matrix.py` → `write_matrix.py` → `validate_output.py`.

### Examples (`examples/`)
- `example-1/` — Worked example: a fixture PRD, SDD, PLAN, and code tree, plus the matrix payload and rendered report.

## Contract

Given a PRD, SDD, PLAN, and code root, produce one TRACEABILITY.md file such that:

1. The report path is exactly `--out` from the invocation.
2. The body has these `##` sections in order: `## Feature`, `## Summary`, `## Coverage Matrix`, `## Gaps`, `## Totals`.
3. Every PRD `REQ-NNN` has exactly one row in the matrix.
4. Each row's `status` field is one of `covered`, `partial`, `uncovered`.
5. A row is `covered` only when it has ≥1 link at every layer: SDD COMP, PLAN task, code ref, test ref.
6. The Gaps section enumerates every `partial` and `uncovered` row.
7. The Totals reconcile: `covered + partial + uncovered == total PRD REQs`.
8. `python scripts/validate_output.py --file <path> --prd <prd>` exits 0.
9. Links in the matrix come from `extract_ids.py` and `build_matrix.py`; the LLM does not invent rows.

## Knowledge

### What evidence counts
**SDD layer** — A `REQ-NNN` is linked to a `COMP-NNN` if the SDD has a traceability dict that maps them (e.g., a `## Traceability` section with `REQ-001 -> COMP-001, COMP-002`). **PLAN layer** — A task covers a REQ if the task's `reqs[]` list contains that REQ. **Code layer** — A code ref counts if a non-test source file contains the REQ ID (typically as a comment marker like `# REQ-001` or `// REQ-001`). **Test layer** — A test ref counts if a test file contains the REQ ID (in a docstring, test name, or comment). See `knowledge/traceability-rules.md`.

### Statuses are mechanical
- **covered** — ≥1 SDD COMP, ≥1 PLAN task, ≥1 code ref, ≥1 test ref.
- **partial** — appears in PRD with ≥1 layer linked but missing ≥1 layer.
- **uncovered** — appears in PRD with no SDD/PLAN/code/test links.

See `knowledge/coverage-statuses.md`.

### Why mechanical
Coverage the LLM invents is unfalsifiable. Every link comes from text-matching deterministic scripts; the LLM's job is to *narrate* gaps and recommend remediation, not to declare coverage. The matrix is byte-exact reproducible from the same inputs.

## Steps

1. **Resolve inputs.** Confirm paths to PRD, SDD, PLAN, and the code root (typically the repo root or `src/`). If the user passes a feature ID, locate `.claude/specs/<feature>/{PRD,SDD,PLAN}.md`.

2. **Extract.** Run `python scripts/extract_ids.py --prd <prd> --sdd <sdd> --plan <plan> --code-root <root>`. Capture the JSON output to a temp file (e.g., `/tmp/trace-ids.json`).

3. **Build matrix.** Run `python scripts/build_matrix.py --ids-json <ids.json>`. Capture the JSON to a temp file (e.g., `/tmp/trace-matrix.json`).

4. **Render report.** Run `python scripts/write_matrix.py --payload <matrix.json> --out <report-path>`. Default report path: `.claude/specs/<feature>/TRACEABILITY.md`.

5. **Validate.** Run `python scripts/validate_output.py --file <report-path> --prd <prd>`. Must exit 0.

6. **Narrate gaps.** For each `partial` or `uncovered` row, the LLM may add a one-line remediation suggestion in the conversation (not in the file). The LLM does **not** modify the matrix.

7. **Announce.** Print summary totals and report path. Example:
   ```
   Traceability: <feature>
   Total REQs:  12
   Covered:     8
   Partial:     3
   Uncovered:   1

   Report: .claude/specs/<feature>/TRACEABILITY.md
   ```

## Output

A single markdown report rendered from `templates/traceability-matrix.md.template`. No other side effects. Suggested filename: `.claude/specs/<feature>/TRACEABILITY.md`.

## Antipatterns

- **LLM invents links.** Every link comes from `extract_ids.py` and `build_matrix.py`. The LLM may narrate but never edit rows.
- **Skipping `validate_output.py`.** A matrix the validator hasn't seen is not done.
- **Treating `covered` as approval.** `covered` means *links exist*; whether the implementation is correct is a different question (use `spec-validation` and `spec-compliance`).
- **Embedding the template in SKILL.md.** Lives in `templates/traceability-matrix.md.template`.
- **Coverage from grep alone.** SDD/PLAN links require structured maps (the SDD traceability section and PLAN task `reqs[]` list); raw grep is only allowed at the code/test layer.
- **Tracing without a feature folder.** This skill assumes `.claude/specs/<feature>/` layout. Ad-hoc files won't have the traceability dict.
- **Confusing tracing with quality.** This skill verifies links exist, not that the linked code does the right thing. Free-form review goes to `/review-code`.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output> --prd <prd>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. Row counts in the rendered Totals match `build_matrix.py` output byte-for-byte.

## Examples

- **`examples/example-1/`** — Worked example. A fixture PRD with three REQs, one SDD COMP per REQ, a PLAN with mixed task coverage, and a code tree where one REQ has full coverage, one is partial, and one is uncovered. Demonstrates how the matrix renders and what the Gaps section looks like.
