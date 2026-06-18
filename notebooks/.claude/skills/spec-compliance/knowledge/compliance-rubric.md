# Compliance Rubric

This is the mechanical rubric used by `scripts/check_compliance.py`. The output is binary per-component and per-requirement; the overall status is computed from those.

## What counts as evidence

### Component present

A component (`COMP-NNN`) is **present** when at least one of its `expected_paths` exists relative to the repo root.

- Plain paths must match exactly (e.g. `src/search/service.py`).
- Glob patterns are accepted (`*`, `**`, `?`, `[abc]`). Example: `src/auth/*.py` matches any `.py` file in `src/auth/`.
- A directory at the expected path counts as present.
- A symlink that resolves to an existing file counts as present.

If `expected_paths` is empty, the component is automatically marked **missing** — the SDD did not declare where it should live.

### Requirement implemented

A requirement (`REQ-NNN`) is **referenced** when the literal token `REQ-NNN` appears in any text-ish file under the repo root.

- Text-ish files: `.py`, `.js`, `.ts`, `.tsx`, `.go`, `.rs`, `.rb`, `.java`, `.kt`, `.swift`, `.cs`, `.php`, `.scala`, `.clj`, `.ex`, `.md`, `.rst`, `.json`, `.yaml`, `.toml`, `.html`, `.css`, `.sql`, `.sh`, etc. See `scripts/check_compliance.py` for the full list.
- Vendored / generated dirs are skipped: `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`, `.pytest_cache`, `.mypy_cache`, `.tox`.
- A reference inside a test file counts. Tests-only references are still references.
- A reference inside a comment counts. Comments are how humans link code to requirements.

If `REQ-NNN` is not found anywhere, the requirement is marked **unreferenced**.

## Status computation

| Status | Rule |
|---|---|
| **compliant** | Every COMP-ID has at least one `found_path` AND every REQ-ID is referenced at least once. |
| **partial** | At least one COMP-ID is found AND at least one REQ-ID is referenced, but at least one of either is missing. |
| **non-compliant** | No COMP-ID found OR no REQ-ID referenced. |

Edge case: if the spec has no components and no requirements, the status is `non-compliant` — there is nothing to check.

## What this rubric does NOT measure

- **Test pass rate.** A `compliant` status only means the surface matches; tests may still fail. Run the test suite separately.
- **Behavioral correctness.** A file existing at the expected path does not mean it does the right thing. That is the job of `/review-code` and the tests.
- **Quality.** Cyclomatic complexity, lint, security, performance — out of scope.
- **Documentation completeness.** Whether the spec is well-written is graded by `spec-validation`, not here.

## Tuning the rubric

If you want stricter checks (e.g. "the component file must `import` the component name"), extend `check_compliance.py` and add a corresponding entry to `deviation-types.md`. Keep the rules mechanical — anything the LLM has to interpret should not live in this rubric.
