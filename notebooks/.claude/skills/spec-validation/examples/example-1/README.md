# Example: Feature Search PRD with one dangling cross-reference

Demonstrates the full pipeline: `score_3cs.py` → `write_report.py` → `validate_output.py`.

## Files
- `input-spec.md` — fixture PRD; references `REQ-104` which is not defined in the same file.
- `payload.json` — JSON output produced by `score_3cs.py` for that spec.
- `expected-report.md` — rendered report produced by `write_report.py` from the payload.

## Flow

```bash
python ../../scripts/score_3cs.py --file input-spec.md > /tmp/payload.json
python ../../scripts/write_report.py --payload /tmp/payload.json --out /tmp/report.md
python ../../scripts/validate_output.py --file /tmp/report.md
```

## What this demonstrates
- **Completeness 10/10** — all sections present, no markers.
- **Consistency 8/10** — one dangling cross-reference (`REQ-104` referenced, not defined).
- **Correctness 10/10** — all requirements EARS-formatted, valid MoSCoW values.
- **Verdict PASS** — all three sub-scores ≥ 8 hits the PASS threshold; the dangling reference is still surfaced as an issue to address but is not severe enough to flip the verdict.
