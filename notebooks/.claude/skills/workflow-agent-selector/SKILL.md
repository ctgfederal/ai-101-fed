---
name: workflow-agent-selector
version: 2.0.0
description: |
  Select the best specialized agent(s) for a task by reading every `~/.claude/agents/*.md` frontmatter and ranking them by keyword match against the task's technology, domain, and intent. Returns a deterministic ranked list (`Agent | Score | Reason | Tools | Model`) plus a primary recommendation, alternatives, and a delegation prompt — so commands like `/implement` and `/swarm-implement` know which subagent to spawn. Use when a user asks "which agent should I use", runs `/implement` and needs an agent picked, or before any `Task` tool delegation. Do NOT use for choosing skills (use `plan-deepener`'s skill matcher), authoring new agents (different artifact), or assigning humans to work — this skill ranks agents only.
triggers:
  - "which agent should I use"
  - "pick an agent for"
  - "select agent"
  - "agent selection"
  - "find the right agent"
  - "/implement"
  - "before delegating with Task tool"
  - "rank agents for this task"
tools:
  - Read
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# workflow-agent-selector

Given a task description, produce a ranked list of specialized agents that can implement it, with a primary recommendation and a ready-to-paste delegation prompt. All ranking is deterministic — the LLM's only job is to extract good keywords from the task and choose tie-breakers.

## Files

### Templates (`templates/`)
- `match-results.md.template` — Canonical markdown template for the rendered results report. Placeholders: `{{TASK_SUMMARY}}`, `{{KEYWORDS}}`, `{{AGENTS_TOTAL}}`, `{{RESULT_COUNT}}`, `{{RESULT_ROWS}}`, `{{PRIMARY_AGENT}}`, `{{PRIMARY_REASON}}`, `{{ALTERNATIVES_BLOCK}}`, `{{STEERING_BLOCK}}`, `{{DELEGATION_PROMPT}}`.
- `query.example.json` — Example match-query payload with `keywords`, `min_score`, `max_results`.

### Scripts (`scripts/`)
- `parse_agent_frontmatter.py` — Deterministic. Reads every `*.md` under `--agents-root` and emits a JSON list `[{name, description, tools, model, file}]`. Skips `CLAUDE.md` and files without parseable frontmatter. Args: `--agents-root <path>`.
- `match_agents.py` — Deterministic. Given a query payload (`{keywords, min_score, max_results}` or a bare list of keywords) on stdin or via `--keywords-json`, ranks agents by name → name-token → description-token → tool match (see `knowledge/selection-rules.md`). Prints JSON list `[{agent, score, reason, tools, model, file}]` sorted by score descending. Args: `--keywords-json <path>` `--agents-root <path>`.
- `validate_match_query.py` — Deterministic. Validates a match-query JSON against the schema (1..32 string keywords, optional `min_score` in `0..1`, optional positive-int `max_results`). Args: `--file <path>` (or stdin). Exit 0 = valid, 1 = invalid.
- `validate_output.py` — Deterministic. Given a rendered `match-results.md` report, asserts the table has the columns `Agent | Score | Reason` and every Score parses as a float in `0.0..1.0`. Args: `--file <path>`. Exit 0 = pass.

### Knowledge (`knowledge/`)
- `selection-rules.md` — Canonical match-tier table (exact name → name-token → description-token → tool) with weights and the normalization formula. Read when explaining why an agent ranked where it did.
- `agent-categories.md` — High-level categories (frontend, backend, AI/ML, infra, …) with the keywords most likely to surface their agents. Read when expanding a raw task description into a keyword list.
- `tie-breakers.md` — How to break ties when scores are close: specificity wins, smaller tool surface wins, model capability for high-stakes tasks, project steering overrides.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any selection result produced by this skill.

### Tests (`tests/`)
- `unit/test_parse_agent_frontmatter.py` — Unit tests for frontmatter parsing. Covers inline string, inline list tools, block-list tools, block-scalar description, skip of `CLAUDE.md` and files without frontmatter.
- `unit/test_match_agents.py` — Unit tests for scoring and ranking. Covers exact-name, name-token, description-token, tool match, no-match, descending sort, `min_score` filter, `max_results` cap.
- `unit/test_validate_match_query.py` — Unit tests for query schema. Covers happy path, missing keywords, empty list, oversize list, non-string keyword, out-of-range `min_score`, non-positive `max_results`, unexpected fields.
- `unit/test_validate_output.py` — Unit tests for output validation. Covers happy path, missing columns, non-numeric Score, out-of-range Score, no data rows, empty Agent cell.
- `integration/test_real_agents.py` — Runs against the real `~/.claude/agents/` (gated by `RUN_INTEGRATION_TESTS=1`). Asserts parsing and ranking work on real data.
- `evals/agent_selector_eval.py` — Three eval cases for keyword extraction quality: happy (clean keywords), edge (single keyword), adversarial (noisy keywords with red herrings). Asserts the correct specialist still ranks first.
- `smoke/test_e2e.py` — End-to-end: validate a query, parse agents, rank, render to markdown, validate the rendered report.
- `conftest.py` — Shared fixtures: `tmp_agents_root` (small fixture tree), `valid_query`, `invalid_query_no_keywords`, `fixture_results_md`.

### Examples (`examples/`)
- `react-form-component/` — A complete worked example: input task, query JSON, and rendered match-results report. Demonstrates: keyword expansion from a free-form task, multi-agent ranking, primary + alternative selection, delegation prompt formatting.

## Contract

Given a task description plus an optional list of required tools, produce one rendered markdown report such that:

1. The report contains a single markdown table with columns at minimum: `Agent`, `Score`, `Reason`, plus optionally `Tools` and `Model`.
2. Every row's `Score` parses as a float in `[0.0, 1.0]`.
3. Every `Agent` value corresponds to a real file at `~/.claude/agents/<agent>.md`.
4. The table is sorted by `Score` descending, with `match_agents.py`'s tie-breakers (smaller tool surface, then alphabetical) applied.
5. A "Recommended Primary" section names exactly one agent from the table.
6. `python scripts/validate_output.py --file <path>` exits 0 against the rendered report.
7. The match query passed to `match_agents.py` first passes `python scripts/validate_match_query.py`.
8. No agent file is modified; no new agent file is created.

## Knowledge

### What this skill is for
Commands like `/implement`, `/swarm-implement`, `/review`, and `/debug` need to spawn subagents via the `Task` tool. Picking the right `subagent_type` is the difference between a clean implementation and a generalist trying to do specialist work. This skill turns "what subagent should I use" into a deterministic, repeatable lookup against `~/.claude/agents/`.

### Why determinism matters
LLM-only agent selection drifts: today the model picks `react-specialist`, tomorrow `frontend-developer`, with no clear rule. Pushing the ranking into `match_agents.py` (a 200-line script) makes the choice auditable and reproducible. The LLM's job shrinks to (a) extracting good keywords from the task and (b) applying tie-breakers from `knowledge/tie-breakers.md`.

### How the score is computed
See `knowledge/selection-rules.md` for the full table. In short:
- Exact agent-name match: weight `1.00`.
- Name token match (kebab-split): `0.70`.
- Name substring (≥3 chars): `0.56`.
- Description token: `0.30`.
- Description substring (≥3 chars): `0.18`.
- Tool match: `0.15`.

The score is the sum of best-tier matches per keyword, divided by `max_weight × num_keywords`, clipped to `[0, 1]`.

### When NOT to use
- Picking *skills* (use `plan-deepener`'s skill matcher).
- Authoring a new agent (write a new `~/.claude/agents/<name>.md` directly).
- Choosing *humans* for work — this skill matches LLM agents only.
- For trivial tasks where the agent is obvious (a one-line refactor doesn't need a ranking).

## Steps

1. **Read the task.** Extract: the primary domain (frontend / backend / db / infra / ai / quality / writing / research), the technology stack (react, postgres, k8s, …), the task type (build / refactor / test / review / design), and any required tools.

2. **Expand to keywords.** Read `knowledge/agent-categories.md`. Pick 3–6 keywords covering domain + technology + task-type. Avoid more than 6 — noise hurts ranking.

3. **Build the query.** Assemble `{"keywords": [...], "min_score": 0.05, "max_results": 5}`. Save to `query.json` (or stream over stdin).

4. **Validate the query.** Run `python scripts/validate_match_query.py --file query.json`. Fix errors before continuing.

5. **Rank agents.** Run:
   ```
   python scripts/match_agents.py --keywords-json query.json --agents-root ~/.claude/agents
   ```
   Capture the JSON output.

6. **Apply tie-breakers.** If the top two scores are within ~0.05 of each other, read `knowledge/tie-breakers.md` and decide: specialist over generalist, smaller tool surface, project steering. Re-order rows if needed and note the reason.

7. **Render the report.** Substitute the ranking into `templates/match-results.md.template`. Fill the primary agent, alternatives, steering references, and a delegation prompt.

8. **Validate the report.** Run `python scripts/validate_output.py --file match-results.md`. Exit 0 required.

9. **Announce.** Print:
   ```
   Selected primary agent: <agent>
   Score: <score>
   Reason: <reason>

   Alternatives: <agent>, <agent>
   Use the delegation prompt at the bottom of the report when calling Task.
   ```

## Output

A single markdown report (caller chooses the path) conforming to `templates/match-results.md.template`. No filesystem side effects beyond that one file. The report has:

- A header block with task summary and keyword list.
- A ranked markdown table with columns `Agent | Score | Reason | Tools | Model`.
- A `## Recommended Primary` section.
- An optional `## Alternatives` block listing any close-scoring agents.
- A `## Steering / Skill References` block listing relevant agent / steering / skill files.
- A `## Delegation Prompt` code block ready to paste into a `Task` tool invocation.

## Antipatterns

- **Skipping the script and asking the LLM to "just pick".** Defeats determinism. Always run `match_agents.py`.
- **Stuffing 12 keywords into the query.** Past 6 keywords noise dominates and the cap normalization shrinks every score. Pick the most discriminating 3–6.
- **Hard-filtering on tools inside `match_agents.py`.** It deliberately doesn't — tools downgrade score. Hard filtering is the caller's job and is reversible.
- **Picking the top row blindly when it's a generalist.** If a specialist scores within `~0.05`, prefer the specialist (see `knowledge/tie-breakers.md`).
- **Writing the report by hand.** Use the template. The validator will catch column / score errors but won't fix layout drift.
- **Editing agent frontmatter to "boost" a match.** That changes every future ranking. If an agent is missing keywords, fix the agent description in a separate change with its own justification.
- **Running against a stale agents tree.** `parse_agent_frontmatter.py` reads the live filesystem; if you cached results, re-run after any change under `~/.claude/agents/`.

## Validation

Pass criteria:
1. `python scripts/validate_match_query.py --file <query>` exits 0.
2. `python scripts/validate_output.py --file <report>` exits 0.
3. `pytest tests/unit/` exits 0.
4. `pytest tests/smoke/` exits 0.
5. `pytest tests/evals/` exits 0 (keyword-extraction quality).
6. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0 against the real `~/.claude/agents/` tree.
7. Every item in `validation/quality-checklist.md` is checked.
8. The selected primary agent's file (`~/.claude/agents/<name>.md`) exists and is readable.

## Examples

- **`examples/react-form-component/`** — Full worked example: a free-form React form task expanded into the keywords `["react", "form", "frontend", "component", "validation"]`, the query JSON, the resulting ranked table, the chosen primary (`react-specialist`), alternatives (`frontend-developer`, `nextjs-developer`), and the delegation prompt. Demonstrates: keyword expansion, primary vs alternatives, tie-breaker reasoning.
