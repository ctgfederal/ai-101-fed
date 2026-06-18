---
name: agent-delegation
version: 2.0.0
description: |
  Generate structured agent prompts with explicit FOCUS and EXCLUDE blocks for delegating tasks to specialist sub-agents, and detect file-path collisions before launching multiple parallel agents. Use when the user asks to "launch an agent", "delegate this", "spawn a sub-agent", "run agents in parallel", "break this into tasks", or runs `/swarm-implement`, `/swarm-analyze`, `/swarm-debug`. Do NOT use for writing requirements (PRD via spec-prd-generator), design decisions (SDD via spec-sdd-generator), implementation tasks (PLAN via spec-plan-generator), or simple single-tool calls — this skill produces delegation prompts and collision reports, it does not write code or specs.
triggers:
  - "/swarm-implement"
  - "/swarm-analyze"
  - "/swarm-debug"
  - "delegate this to an agent"
  - "spawn a sub-agent"
  - "launch parallel agents"
  - "create a FOCUS/EXCLUDE prompt"
  - "break this into parallel tasks"
  - "check for file collisions"
  - "render an agent prompt"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# agent-delegation

Render a copy-pasteable agent prompt from a JSON delegation payload, and detect file-path collisions across multiple delegation payloads before parallel launch. The output prompt has five required blocks (`FOCUS`, `EXCLUDE`, `TASK`, `SUCCESS`, `RETURN`) so the receiving agent has crisp scope, prevents scope creep, and never collides with siblings on a shared file.

## Files

### Templates (`templates/`)
- `delegation-prompt.md.template` — Canonical agent-prompt layout with placeholders for `{{AGENT_TYPE}}`, `{{TASK}}`, `{{FOCUS_LIST}}`, `{{EXCLUDE_LIST}}`, `{{SUCCESS_LIST}}`, `{{RETURN_FORMAT}}`. Rendered by `scripts/render_prompt.py`.
- `payload.example.json` — Example delegation payload showing every required field with realistic values.
- `payloads.example.json` — Example multi-payload list used by `scripts/check_collisions.py`.

### Scripts (`scripts/`)
- `validate_delegation.py` — Deterministic. Validates a single delegation JSON payload: `agent_type` is non-empty string, `task` is non-empty string, `focus_files` and `exclude_files` are lists of strings, FOCUS and EXCLUDE do not overlap, `success_criteria` is a list with ≥1 item, `return_format` is non-empty. Args: `--payload <path-or-stdin>`. Exit 0 = valid; 1 = invalid (errors on stderr).
- `render_prompt.py` — Deterministic. Renders `templates/delegation-prompt.md.template` from a validated JSON payload. Output is a complete copy-pasteable agent prompt. Args: `--payload <path-or-stdin>` `--out <path>` `[--force]`. Exit 0 = wrote file; prints output path.
- `check_collisions.py` — Deterministic. Given a list of multiple delegation payloads, detects file-path overlap between FOCUS sets (paths or simple glob expansions). Args: `--payloads-json <path>`. Prints JSON `{"collisions": [{"agents": [...], "files": [...]}], "safe": bool}`. Exit 0 always; non-empty `collisions` means unsafe to run in parallel.
- `validate_output.py` — Deterministic. Given a rendered prompt file, validates required sections (`FOCUS`, `EXCLUDE`, `TASK`, `SUCCESS`, `RETURN`) are present and that the FOCUS, EXCLUDE, and SUCCESS lists are non-empty. Args: `--file <path>`. Exit 0 = pass.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files.
- `focus-exclude-rules.md` — What counts as a path or glob, FOCUS-vs-EXCLUDE precedence, how to scope by directory vs single file, when to use globs over explicit paths.
- `delegation-patterns.md` — Common patterns: research-only (no edits), focused build (single dir owner), parallel-build (collision-free), sequential build with handoff, retry-on-scope-creep.
- `success-criteria.md` — How to write actionable, testable, verifiable success criteria the agent can self-check.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any rendered delegation prompt.

### Tests (`tests/`)
- `unit/test_validate_delegation.py` — Happy, missing field, FOCUS/EXCLUDE overlap, empty success_criteria, empty agent_type.
- `unit/test_render_prompt.py` — Render substitution, no `{{` markers leak, list rendering, refuses overwrite without `--force`.
- `unit/test_check_collisions.py` — No overlap, exact path overlap, glob overlap, multiple-agent collisions, single-payload (always safe).
- `unit/test_validate_output.py` — Happy, missing block, empty FOCUS list, empty SUCCESS list.
- `integration/test_agent_delegation_integration.py` — Placeholder integration harness; gated by `RUN_INTEGRATION_TESTS=1`.
- `evals/agent_delegation_eval.py` — Eval shape tests for LLM payload assembly: happy (clear task), edge (vague task), adversarial (scope creep in success criteria).
- `smoke/test_e2e.py` — End-to-end: validate payload → render prompt → validate rendered file → run check_collisions on a 2-payload set.
- `conftest.py` — Shared pytest fixtures: `valid_payload`, `invalid_payload`, `colliding_payloads`, `safe_payloads`.

### Examples (`examples/`)
- `parallel-build/` — Worked example: two delegation payloads (`auth-agent` and `billing-agent`) building separate dirs, the rendered prompts, and a collision report proving they're parallel-safe.

## Contract

Given a delegation payload (or list of payloads), produce one rendered agent prompt per payload at the requested path such that:

1. The output file contains the five required blocks in order: `## FOCUS`, `## EXCLUDE`, `## TASK`, `## SUCCESS`, `## RETURN`.
2. Each FOCUS, EXCLUDE, and SUCCESS list is non-empty.
3. No file under `FOCUS` is also under `EXCLUDE` (validator rejects overlap).
4. `python scripts/validate_output.py --file <path>` exits 0.
5. When multiple payloads are provided, `python scripts/check_collisions.py --payloads-json <path>` returns `{"safe": true, ...}` before any agent is launched.
6. Re-running the script on the same `--out` without `--force` fails — previous prompts are never silently overwritten.
7. No file other than the rendered prompt(s) is created or modified.

## Knowledge

### Why FOCUS/EXCLUDE
Sub-agents over-trigger on adjacent code. An explicit `EXCLUDE` block tells the agent what *looks* in scope but isn't, so it stops scope creep before it starts. See `knowledge/focus-exclude-rules.md`.

### Why collision detection before parallel launch
Two agents writing to overlapping FOCUS sets will produce partial-write corruption — last-writer-wins on every shared file, with no merge. `check_collisions.py` runs before launch so the orchestrator can re-scope or sequence. See `knowledge/delegation-patterns.md`.

### Why testable success criteria
"Make it work" is not a success criterion an agent can verify. Each item must be a check the agent can run (test passes, file exists, lint clean). See `knowledge/success-criteria.md`.

## Steps

1. **Confirm a real delegation is needed.** If the work is one tool call or single-file edit, do not delegate — call the tool directly. Delegate only when the task warrants a fresh context window or parallel execution.

2. **Assemble the payload.** Build a JSON object with `agent_type`, `task`, `focus_files` (list), `exclude_files` (list), `success_criteria` (list with ≥1 actionable item), `return_format` (string). Use `templates/payload.example.json` as the shape reference.

3. **Validate the payload.** Run `python scripts/validate_delegation.py --payload <path>`. Fix any errors before continuing.

4. **Render the prompt.** Run `python scripts/render_prompt.py --payload <path> --out <out-path>`. Refuse `--force` unless the user explicitly asks to overwrite.

5. **Validate the rendered prompt.** Run `python scripts/validate_output.py --file <out-path>`. Exit 0 required.

6. **(Parallel only) Check collisions.** If launching multiple agents in parallel, write all payloads to a JSON list and run `python scripts/check_collisions.py --payloads-json <path>`. If `safe: false`, re-scope FOCUS sets or sequence the agents — do not launch.

7. **Hand off.** Print:
   ```
   Delegation prompt rendered:
     <out-path>
   Agent: <agent_type>
   FOCUS: <N> entries
   EXCLUDE: <N> entries
   Parallel-safe: <yes/no/n/a>
   ```

## Output

A rendered agent-prompt markdown file per payload, conforming to `templates/delegation-prompt.md.template`. No other side effects.

Filename pattern: caller-supplied path (commonly `prompts/<agent>-<task-slug>.md`).

## Antipatterns

- **Embedding the prompt template in SKILL.md.** The template lives in `templates/delegation-prompt.md.template`. Editing prose inline drifts from the schema and breaks `validate_output.py`.
- **Skipping FOCUS or EXCLUDE.** A prompt with no EXCLUDE invites scope creep. Even an empty list signals "no exclusions intended" — but most real delegations have at least one EXCLUDE entry.
- **Vague success criteria.** "Looks good" is not testable. Every entry must be a check the agent can run (`pytest tests/X passes`, `file Y exists`, `lint clean`). See `knowledge/success-criteria.md`.
- **Launching parallel agents without `check_collisions.py`.** Two agents writing the same file = corruption. Run the collision check first, every time.
- **Overwriting prompts silently.** `--force` requires explicit user direction; a duplicate path means the orchestrator already issued this delegation.
- **Roles instead of activities.** "Backend engineer does X" couples the work to a job title. Decompose by *what* (`design schema`, `implement endpoint`), not *who*.
- **Free-form prompt assembly.** If you find yourself hand-typing FOCUS/EXCLUDE blocks in the chat, you've skipped `render_prompt.py`. Use the script.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0 if integration tests are enabled.
6. Every item in `validation/quality-checklist.md` is checked.
7. For any parallel launch, `python scripts/check_collisions.py --payloads-json <path>` reports `safe: true`.

## Examples

- **`examples/parallel-build/`** — Worked example: two delegation payloads (`auth-agent` building `src/auth/`, `billing-agent` building `src/billing/`), the rendered prompts, and the collision report showing `safe: true`. Demonstrates how to scope by directory, write testable success criteria, and verify parallel-safety before launch.
