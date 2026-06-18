# Example: partial compliance with one missing component and one unreferenced requirement

Demonstrates the full pipeline: `parse_spec.py` → `check_compliance.py` → `write_report.py` → `validate_output.py`.

## Files
- `PRD.md` — fixture PRD with REQ-001 and REQ-002.
- `SDD.md` — fixture SDD with COMP-001 (SearchService at `src/search/service.py`) and COMP-002 (RankingEngine at `src/search/ranking.py`).
- `repo/` — fixture repo where COMP-001 is implemented (`src/search/service.py`, references REQ-001), COMP-002 is missing, and REQ-002 is referenced nowhere.
- `parsed.json` — JSON output produced by `parse_spec.py` from PRD + SDD.
- `payload.json` — JSON output produced by `check_compliance.py` from `parsed.json` + `repo/`.
- `expected-report.md` — rendered report produced by `write_report.py` from `payload.json`.

## Flow

```bash
python ../../scripts/parse_spec.py --prd PRD.md --sdd SDD.md > /tmp/parsed.json
python ../../scripts/check_compliance.py --spec-json /tmp/parsed.json --repo-root repo > /tmp/payload.json
python ../../scripts/write_report.py --payload /tmp/payload.json --out /tmp/REPORT.md
python ../../scripts/validate_output.py --file /tmp/REPORT.md
```

## What this demonstrates
- **Status `partial`** — one component is implemented, one is missing; one REQ is referenced, one is not.
- **`missing-component` deviation** — COMP-002 (RankingEngine) has no file at `src/search/ranking.py`.
- **`unreferenced-requirement` deviation** — REQ-002 is not mentioned in any source or test file.
- **No `scope-creep`** — the only `REQ-NNN` token in the repo (REQ-001) is declared in the PRD.
