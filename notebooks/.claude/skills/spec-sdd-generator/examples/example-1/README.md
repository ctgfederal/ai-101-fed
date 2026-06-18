# Example: Feature Search SDD

End-to-end SDD generation.

```bash
python ../../scripts/init_sdd.py --feature feature-search --specs-root /tmp/specs
python ../../scripts/write_sdd.py --payload payload.json --out /tmp/specs/feature-search/SDD.md --prd /tmp/specs/feature-search/PRD.md
python ../../scripts/validate_output.py --file /tmp/specs/feature-search/SDD.md --prd /tmp/specs/feature-search/PRD.md
```

Demonstrates: 4 components, traceability covers REQ-001 + REQ-002, contract for every component, alternatives section non-empty.
