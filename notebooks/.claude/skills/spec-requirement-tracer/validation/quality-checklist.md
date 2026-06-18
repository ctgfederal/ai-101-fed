# Quality Checklist — spec-requirement-tracer

## YAML
- [ ] All 6 fields; description ≥80 chars w/ Use-when AND Do-NOT-use; ≥5 triggers.

## Sections
- [ ] All 8 in order; Files lists every file.

## Deterministic-First
- [ ] ID extraction in `extract_ids.py`
- [ ] Matrix construction in `build_matrix.py`
- [ ] Render in `write_matrix.py`
- [ ] Validation in `validate_output.py`
- [ ] Templates in `templates/`

## File integrity
- [ ] Every Files-section file exists
- [ ] Every script has `if __name__ == "__main__":` + argparse
- [ ] At least one example folder

## Tests
- [ ] Unit tests for each script
- [ ] LLM evals
- [ ] Smoke
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0
- [ ] `pytest tests/evals/` exits 0

## Output-Specific
- [ ] All 5 body sections in correct order: Feature, Summary, Coverage Matrix, Gaps, Totals
- [ ] Every PRD REQ-NNN has a row
- [ ] Every status is one of `covered`, `partial`, `uncovered`
- [ ] Totals reconcile: covered + partial + uncovered == total PRD REQs
- [ ] No unsubstituted `{{...}}` template tokens
- [ ] Every `partial` / `uncovered` row appears in the Gaps section
