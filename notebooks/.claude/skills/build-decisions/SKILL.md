---
name: build-decisions
version: 3.0.0
description: |
  Walk through every design decision a feature requires — interactively, one at a time — through 12 ordered categories (architecture, data, API, observability, audit, security, integration, performance, extensibility, testing, deployment, UI). Auto-applies federal mandates, ranks options by Simplicity → Modularity → Security → Scalability, allocates monotonic global decision IDs (D-NNN), and appends every choice to `.claude/decisions-log.md`. State persists in `.claude/builds/<feature>/state.json` so sessions can be paused and resumed. Use when a user runs `/build`, asks "let's walk the design decisions", or needs to lock down architecture before `/specify`. Do NOT use for shaping vision (that's `/brainstorm`), writing the formal spec (that's `/specify`), implementation, or pure architecture review.
triggers:
  - "/build"
  - "let's walk the design decisions"
  - "build decisions for"
  - "design decisions before specify"
  - "make build choices"
  - "walk the architecture"
  - "design walkthrough"
  - "go through the build decisions"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
model: claude-sonnet-4-6
---

# build-decisions

One question at a time across 12 ordered decision categories. Auto-applies federal mandates. Logs every decision to `.claude/decisions-log.md` with a globally-unique `D-NNN` ID. State persists for resumable sessions.

## Files

### Templates (`templates/`)
- `decision-section.md.template` — Canonical markdown template for one category section in the decisions log. Placeholders: `{{CATEGORY}}`, `{{DECISIONS_BLOCK}}`.
- `feature-section.md.template` — Top-level feature section in the log: header, summary, auto-applied table, per-category sections, open questions, related solutions.
- `state.example.json` — Example state-file shape with explanatory comments.

### Scripts (`scripts/`)
- `state_manager.py` — Deterministic. Initialize, read, and write `.claude/builds/<feature>/state.json`. Subcommands: `init` (creates dir + state), `read` (prints state to stdout), `update` (merges JSON patch from `--patch` or stdin into state). Args: `--feature <name>` `--builds-root <path>`. Exit 0 = success.
- `allocate_ids.py` — Deterministic. Reads `.claude/decisions-log.md`, finds the highest `D-NNN`, allocates the next `--count` IDs. Args: `--log <path>` `--count <int>`. Prints space-separated allocation to stdout. Exit 0 even on empty/missing log (returns `D-001 D-002 ...`).
- `federal_mandates.py` — Deterministic. Looks up auto-apply decisions by category and decision-name. Subcommands: `list` (all mandates), `lookup --category <cat> --name <decision>` (returns mandated answer + citation, or exit 1 if none). Backed by `knowledge/federal-mandates.json`.
- `append_decisions.py` — Deterministic. Given a JSON payload of one feature's decisions (auto-applied + user-decided), renders `feature-section.md.template` and appends to `.claude/decisions-log.md`. Refuses if any decision lacks a `D-NNN` ID. Args: `--payload <path-or-stdin>` `--log <path>` `[--force]`. Exit 0 = appended.
- `validate_output.py` — Deterministic. Validates the appended section: parses, checks every decision has an ID in the allocated range, checks IDs are unique within the file, checks every required category appears OR is documented as "not applicable". Args: `--log <path>` `--feature <name>`. Exit 0 = pass.

### Knowledge (`knowledge/`)
- `decision-categories.md` — The 12 ordered categories with the canonical sub-decisions in each. Reference during the walk.
- `federal-mandates.json` — Machine-readable federal auto-apply table: `[{category, name, answer, citation, applies_when}]`. Read by `federal_mandates.py`.
- `priority-framework.md` — The four-priority ranking (Simplicity → Modularity → Security → Scalability) and how to apply it when presenting options.
- `lockdown-tiers.md` — How `personal` / `enterprise` / `federal` tiers map to enforcement (block / warn / allow) and to optional pip extras.
- `id-convention.md` — The global monotonic `D-NNN` ID rules: never renumber, append-only, cross-section follow-ups reuse IDs.
- `README.md` — Index of knowledge files.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any build-decisions session.

### Tests (`tests/`)
- `unit/test_state_manager.py` — Init, read, update merge semantics, missing-state error.
- `unit/test_allocate_ids.py` — Empty log, log with `D-001`, log with `D-099`, gaps, malformed entries.
- `unit/test_federal_mandates.py` — Lookup hit, lookup miss, list output shape.
- `unit/test_append_decisions.py` — Payload validation, ID-required enforcement, append vs. force, template rendering.
- `unit/test_validate_output.py` — Happy path, duplicate IDs, missing category, ID outside allocated range.
- `integration/test_build_decisions_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/build_decisions_eval.py` — LLM evals for option-presentation (priority alignment) and tier-notes generation.
- `smoke/test_e2e.py` — End-to-end: init state → allocate IDs → append decisions → validate.
- `conftest.py` — Shared fixtures: `tmp_builds_root`, `tmp_log_path`, `valid_payload`.

### Examples (`examples/`)
- `example-1/` — Worked example: state JSON for "feature-search", payload of 8 decisions (3 auto-applied, 5 user), the resulting decisions-log.md section.

## Contract

Given a feature name and an interactive user, produce:

1. A persistent state file at `.claude/builds/<feature>/state.json` updated through every interaction.
2. An appended section in `.claude/decisions-log.md` with:
   - Header `## <Feature> — Build Decisions (YYYY-MM-DD)` and a metadata line (`Phase: build | Status: complete | Total decisions: N (M user, P auto-applied) | ID range: D-NNN to D-MMM`).
   - One auto-applied table listing every federally-mandated decision with citation.
   - One subsection per applicable category, each containing 0..N decisions with globally-unique `D-NNN` IDs.
   - Optional `### Open Questions` and `### Related Solutions` blocks.
3. Every decision in the appended section has an ID in the contiguous range allocated by `scripts/allocate_ids.py` for this run.
4. No category is silently skipped — categories not applicable to the feature are explicitly documented as such.
5. `python scripts/validate_output.py --log <path> --feature <name>` exits 0.

## Knowledge

### Priority framework
Every multi-option decision is ranked **Simplicity → Modularity → Security → Scalability**. The recommended option must be the highest in this order; tradeoffs against lower priorities are stated explicitly. See `knowledge/priority-framework.md`.

### Federal auto-apply
Some decisions have one mandated answer (audit retention, encryption at rest, TLS version, etc.). Auto-apply: state the decision, cite the mandate, tag `auto-applied: federal-mandate`, move on. The full table is in `knowledge/federal-mandates.json`; lookup via `scripts/federal_mandates.py`.

### Lockdown tiers
The system has **one codebase**. Tiers (`personal` / `enterprise` / `federal`) map to enforcement (`info` / `warn` / `block`) via config + optional pip extras (`[enterprise]`, `[federal]`). Every decision must answer: "What does the policy layer do at each tier?" See `knowledge/lockdown-tiers.md`.

### Global D-NNN IDs
One monotonic counter across the entire decisions log. Never renumber. Append-only. Cross-section follow-ups reuse IDs by reference. See `knowledge/id-convention.md`.

## Steps

1. **Init / resume.** Run `python scripts/state_manager.py init --feature <name> --builds-root <repo>/.claude/builds`. If state exists, announce position and surface notes from previous session.

2. **Load context.** Read brainstorm at `.claude/brainstorms/`, scan `.claude/solutions/` for relevant prior art (use `compound-docs/scripts/search_solutions.py`), read project steering docs at `.claude/steering/`. Surface anything that pre-decides choices.

3. **Walk categories in order.** Read `knowledge/decision-categories.md` for the 12 ordered categories and the canonical sub-decisions in each. For each sub-decision:
   - **Federal check.** Run `python scripts/federal_mandates.py lookup --category <cat> --name <decision>`. If exit 0, auto-apply silently and announce in batch at end of category.
   - **Solutions check.** Search `.claude/solutions/` for prior decisions on this exact question.
   - **Present options.** Use `AskUserQuestion` with 2–4 options ranked per `knowledge/priority-framework.md`, with tier notes per `knowledge/lockdown-tiers.md`.
   - **Wait.** Do NOT proceed until user decides.
   - **Update state.** Run `python scripts/state_manager.py update --feature <name>` with a JSON patch.

4. **Allocate IDs.** Once the walk is complete, count decisions (auto-applied + user-decided). Run `python scripts/allocate_ids.py --log .claude/decisions-log.md --count <N>`. Capture the allocated range.

5. **Assemble payload.** Build the JSON payload for `append_decisions.py`: feature, date, summary, auto_applied (list of `{id, category, name, answer, citation}`), categories (dict of category → list of `{id, title, decision, priority, alternatives, rationale, tiers}`), open_questions, related_solutions.

6. **Append to log.** Run `python scripts/append_decisions.py --payload <path> --log .claude/decisions-log.md`. Refuses without `--force` if the same feature header already exists for today.

7. **Validate.** Run `python scripts/validate_output.py --log .claude/decisions-log.md --feature <name>`. Exit 0 required.

8. **Handoff.** Use `AskUserQuestion`: continue to `/deepen`, jump to `/specify`, review the decisions, or pause.

## Output

A new section appended to `.claude/decisions-log.md` matching `templates/feature-section.md.template`, plus an updated `.claude/builds/<feature>/state.json`. No other files touched.

## Antipatterns

- **Asking questions when a federal mandate already decides.** Auto-apply mandates silently; don't waste the user's time.
- **Renumbering decision IDs.** IDs are append-only and globally unique. Use `[superseded by D-NNN]` annotations instead.
- **Letting the user skip categories silently.** Categories not applicable must be explicitly marked, not omitted.
- **Embedding the federal mandate table in SKILL.md.** It lives in `knowledge/federal-mandates.json` so `federal_mandates.py` and the LLM both read the same source.
- **Recommending the lowest-priority option.** When tradeoffs conflict, name the tension explicitly and recommend the higher-priority option.
- **Writing code in this skill.** This is decisions-only. Implementation is `/implement`.
- **Skipping tier notes.** Every decision must say what `personal`/`enterprise`/`federal` do.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --log <log> --feature <name>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0.
6. Every item in `validation/quality-checklist.md` is checked.
7. The appended section IDs are contiguous in the range `allocate_ids.py` returned for this run.

## Examples

- **`examples/example-1/`** — Worked example: feature `feature-search` with 8 decisions (3 auto-applied federal mandates: TLS 1.2+, AES-256 at rest, audit retention; 5 user decisions across architecture/data/API/security). Demonstrates: state JSON shape, payload JSON shape, allocated ID range `D-042 to D-049`, the resulting `.claude/decisions-log.md` section.
