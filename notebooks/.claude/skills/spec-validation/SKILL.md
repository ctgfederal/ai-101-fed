---
name: spec-validation
version: 2.0.0
description: |
  Score a specification, implementation, or piece of understanding against the **3 Cs framework** — Completeness, Consistency, Correctness — by running mechanical checks (sections present, cross-references resolve, no `[NEEDS CLARIFICATION]` markers, EARS format used, IDs unique) and emitting a markdown report with 0-10 sub-scores plus an overall score and remediation issues. Use when the user runs `/validate`, asks "is this spec ready?", asks for a 3Cs score, wants to compare an implementation against its spec, or needs a readiness check before approval. Do NOT use for free-form code review (use `/review-code`), security review (use `security-review`), test-coverage analysis (use `testing-coverage-gap-finder`), or to *write* the spec being validated — this skill grades, it does not author.
triggers:
  - "/validate"
  - "validate this spec"
  - "3 Cs check"
  - "score the spec"
  - "is this spec ready"
  - "completeness consistency correctness"
  - "check spec quality"
  - "validate the implementation against the spec"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-validation

Score a target file (typically a PRD, SDD, or PLAN) against the 3 Cs framework using deterministic checks, then render a markdown report. The score is the contract — the LLM does not invent it. Pass thresholds live in `knowledge/score-thresholds.md`.

## Files

### Templates (`templates/`)
- `3cs-report.md.template` — Canonical layout for the rendered report. Placeholders: `{{TARGET}}`, `{{COMPLETENESS}}`, `{{CONSISTENCY}}`, `{{CORRECTNESS}}`, `{{OVERALL}}`, `{{VERDICT}}`, `{{ISSUES}}`. Used by `write_report.py`.
- `payload.example.json` — Example JSON payload showing the exact shape `score_3cs.py` emits and `write_report.py` consumes.

### Scripts (`scripts/`)
- `score_3cs.py` — Deterministic. Reads a target spec file and scores Completeness, Consistency, Correctness on a 0-10 scale by mechanical checks. Args: `--file <path>`. Prints JSON `{target, completeness, consistency, correctness, overall, issues, verdict}` to stdout. Exit 0 always (the *content* of the JSON is the result; non-zero is reserved for I/O failure).
- `write_report.py` — Deterministic. Renders `3cs-report.md.template` from a JSON payload (the output of `score_3cs.py`) and writes the report to disk. Args: `--payload <path>` `--out <path>` `[--force]`. Exit 0 on write.
- `validate_output.py` — Deterministic. Validates a rendered 3Cs report: all three sub-sections present, every score is `[0-10]`, an `Overall` score is shown, every score below 10 has at least one issue listed. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `3cs-rubric.md` — Authoritative rubric: which mechanical checks count toward each C. Read by humans extending the rubric and by the LLM when explaining a score.
- `score-thresholds.md` — Pass / warn / fail bands and the verdict matrix (≥8 each = pass, 5-7 = warn, <5 = fail).

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any 3Cs report this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `good_spec`, `bad_spec`, `valid_payload`.
- `unit/test_score_3cs.py` — Unit tests for the scorer: every sub-score function, edge cases (missing sections, NEEDS CLARIFICATION markers, dangling cross-refs, duplicate IDs).
- `unit/test_write_report.py` — Unit tests for template substitution, payload validation, write semantics, `--force` behavior.
- `unit/test_validate_output.py` — Unit tests for the report validator: happy path, missing section, score out of range, score < 10 with no issue listed.
- `integration/test_spec_validation_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_validation_eval.py` — Three-case eval: clear spec (high score), ambiguous spec (warn), broken spec (fail). Verifies eval harness shape.
- `smoke/test_e2e.py` — End-to-end: `score_3cs.py` → `write_report.py` → `validate_output.py` against a fixture spec.

### Examples (`examples/`)
- `example-1/` — Worked example: a fixture PRD (`input-spec.md`), the scorer's JSON output (`payload.json`), and the rendered report (`expected-report.md`).

## Contract

Given a target spec file, produce one 3Cs report file such that:

1. The report path is exactly `--out` from the invocation.
2. The body has these `##` sections in order: `## Target`, `## Scores`, `## Completeness`, `## Consistency`, `## Correctness`, `## Issues`, `## Verdict`.
3. Each of `Completeness`, `Consistency`, `Correctness`, `Overall` is a single integer in `[0, 10]`.
4. `Verdict` is one of `PASS`, `WARN`, `FAIL`, computed deterministically from the sub-scores per `knowledge/score-thresholds.md`.
5. Every sub-score below 10 has at least one entry under `## Issues` referencing it.
6. `python scripts/validate_output.py --file <path>` exits 0.
7. The score is computed by `score_3cs.py`; the LLM does not modify the integer scores.

## Knowledge

### The 3 Cs in one paragraph
**Completeness** — required sections present and non-empty, no `[NEEDS CLARIFICATION]` markers, no `TODO` / `FIXME` markers, validation checklists complete. **Consistency** — cross-references resolve (every `REQ-NNN`, `D-NNN`, `T-NNN` referenced exists), IDs are unique, terminology is stable. **Correctness** — formats are valid (EARS for requirements, kebab-case feature names, semver for versions), no contradictions in stated values, allowed enum values used.

### Why mechanical
A 3Cs score the LLM invents is unfalsifiable. Every sub-score in this skill comes from a counted set of pass/fail checks; the LLM's job is to *narrate* the score, not to set it. See `knowledge/3cs-rubric.md`.

### Pass / warn / fail
Per `knowledge/score-thresholds.md`: every C must hit ≥8 for `PASS`. Any C in 5-7 gives `WARN`. Any C <5 gives `FAIL`. This is advisory — the user decides whether to ship.

## Steps

1. **Resolve target.** Confirm the file to validate. Common cases: a path under `.claude/specs/<feature>/`, a PRD/SDD/PLAN markdown file. If the user passes a feature ID, locate the most recent spec file inside that folder.

2. **Score.** Run `python scripts/score_3cs.py --file <target>`. Capture the JSON output.

3. **Save payload.** Write the JSON to a temp file (e.g., `/tmp/3cs-payload.json`).

4. **Render report.** Run `python scripts/write_report.py --payload <payload> --out <report-path>`. Default report path: `<target>.3cs-report.md` next to the target.

5. **Validate report.** Run `python scripts/validate_output.py --file <report-path>`. Must exit 0.

6. **Narrate the issues.** For each issue the scorer reported, the LLM may add a one-line human-readable explanation under `## Issues`. The LLM does **not** change the integer scores.

7. **Announce.** Print the verdict, sub-scores, and report path. Example:
   ```
   3Cs Validation: <target>
   Completeness: 9/10
   Consistency:  8/10
   Correctness:  10/10
   Overall:      9/10
   Verdict:      PASS

   Report: <report-path>
   ```

## Output

A single markdown report rendered from `templates/3cs-report.md.template`. No other side effects. Suggested filename: `<target-stem>.3cs-report.md`.

## Antipatterns

- **LLM sets the scores.** The integer sub-scores come from `score_3cs.py`. The LLM only narrates and may suggest fixes, never override.
- **Skipping `validate_output.py`.** A report the validator hasn't seen is not done.
- **Validating an in-progress draft.** If the file is mid-write, the score is meaningless. Confirm "this is the version to grade" before scoring.
- **Treating PASS as approval.** PASS means *mechanically clean*; product judgment is still the human's job.
- **Embedding the report template in SKILL.md.** Lives in `templates/3cs-report.md.template`.
- **Inventing new C-names.** Exactly three: Completeness, Consistency, Correctness. Other axes (e.g., feasibility, security) are out of scope — use the right specialist skill.
- **Bundling code review.** This skill grades structured documents. Free-form code review goes to `/review-code`.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. Sub-scores in the report match the JSON output of `score_3cs.py` byte-for-byte.

## Examples

- **`examples/example-1/`** — Worked example. A fixture PRD with one missing section and one dangling `REQ-NNN` cross-reference. Demonstrates: Completeness drops (missing section), Consistency drops (dangling ref), Correctness stays high. Final verdict: WARN. Includes `input-spec.md`, `payload.json`, and `expected-report.md`.
