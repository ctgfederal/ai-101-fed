# Quality checklist — scrap-coder

Walk this cold against the artifact before bumping version.

- [ ] All 8 sections present in SKILL.md, in order
- [ ] Description includes "Use when..." AND "Do NOT use for..."
- [ ] Every script in scripts/ has a matching tests/unit/test_*.py
- [ ] total_cost.py is deterministic (same input -> same output)
- [ ] Cost table in knowledge/ matches UNIT_COST in total_cost.py
- [ ] Examples/simple/ has a worked input + expected output
