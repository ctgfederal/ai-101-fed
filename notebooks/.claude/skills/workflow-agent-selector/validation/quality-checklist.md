# Quality Checklist — workflow-agent-selector

Walk through every item before declaring an agent-selection result done.

## YAML Metadata
- [ ] `name` matches the folder name (`workflow-agent-selector`)
- [ ] `description` includes both "use when" and "do not use for" clauses
- [ ] `version` is set (semver)
- [ ] `triggers` has at least 5 specific phrases
- [ ] `tools` lists only tools actually used in Steps
- [ ] `model` is a real Claude model identifier

## Required Sections
- [ ] Files section lists every file in the folder
- [ ] Contract section is numbered and testable
- [ ] Knowledge section points to `knowledge/`
- [ ] Steps are numbered and reference scripts by relative path
- [ ] Output section describes the report structure concretely
- [ ] Antipatterns section has at least 3 items
- [ ] Validation section references this checklist
- [ ] Examples section points to at least one worked example

## Deterministic-First Audit
- [ ] Frontmatter parsing is in `scripts/parse_agent_frontmatter.py`, not inline
- [ ] Ranking is in `scripts/match_agents.py`, not inline LLM reasoning
- [ ] Query schema is enforced by `scripts/validate_match_query.py`
- [ ] Output schema is enforced by `scripts/validate_output.py`
- [ ] Category list lives in `knowledge/agent-categories.md`, not in SKILL.md prose
- [ ] Selection rules live in `knowledge/selection-rules.md`, not in SKILL.md prose

## File Integrity
- [ ] Every file mentioned in Files section actually exists
- [ ] Every script in `scripts/` has `if __name__ == "__main__"` and argparse
- [ ] At least one example exists under `examples/`
- [ ] `validation/quality-checklist.md` exists (this file)

## Tests
- [ ] `tests/` directory exists
- [ ] Every script in `scripts/` has a corresponding `tests/unit/test_<script>.py`
- [ ] Unit tests cover happy + edge + error paths for each script
- [ ] Tests do NOT reimplement the script's logic — they hard-code expected values
- [ ] LLM-extraction evals exist (happy / edge / adversarial)
- [ ] End-to-end smoke test exists and passes
- [ ] `pytest tests/unit/` exits 0
- [ ] `pytest tests/smoke/` exits 0

## Output-Specific Checks
- [ ] Report has a markdown table with columns `Agent | Score | Reason`
- [ ] Every Score in the table is a float in `0.0..1.0`
- [ ] Every Agent in the table corresponds to a real `~/.claude/agents/<name>.md` file
- [ ] Primary agent's `tools` cover what the task needs (or override is justified)
- [ ] If multiple agents are returned, splits are non-overlapping

## Capability Check
- [ ] Selected agent's description matches the task's primary domain
- [ ] Tie-breakers from `knowledge/tie-breakers.md` were applied if scores were close
- [ ] Project steering (`.claude/steering/tech.md`, etc.) was consulted
