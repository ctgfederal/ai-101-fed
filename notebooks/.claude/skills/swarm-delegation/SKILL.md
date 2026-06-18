---
name: swarm-delegation
version: 2.0.0
description: |
  Define agent-to-agent delegation rules in multi-agent systems: who can hand off to whom, what context must accompany a handoff, and what the receiver returns. Generates handoff prompts from a structured payload (`from_agent`, `to_agent`, `task`, `context_files`, `success_criteria`, `return_format`, optional `deadline`), validates handoff schemas, and checks planned chains for cycles or output/input type mismatches. Use when orchestrating parallel specialists, planning a `/swarm-implement` chain, sketching a fan-out/fan-in workflow, or asking "who delegates to whom for X". Do NOT use for free-form prompt rewriting (use the `agent-delegation` skill for FOCUS/EXCLUDE templates), for selecting which specialist to hire (use `workflow-agent-selector`), for writing the agent prompts themselves, or for evaluating delegation outcomes — this skill defines and validates handoffs, it does not execute them.
triggers:
  - "/swarm-delegation"
  - "swarm delegation"
  - "agent handoff"
  - "validate this handoff"
  - "check the delegation chain"
  - "render handoff prompt"
  - "who delegates to whom"
  - "fan-out fan-in pattern"
  - "delegation schema"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# swarm-delegation

Define and validate agent-to-agent handoffs in a multi-agent swarm. The handoff is a structured payload — not free-form prose — so chains can be statically checked for cycles and type mismatches before any agent runs. The LLM does not invent the validation result; the scripts do.

## Files

### Templates (`templates/`)
- `handoff.md.template` — Canonical layout for a rendered handoff prompt the receiving agent will see. Placeholders: `{{FROM}}`, `{{TO}}`, `{{TASK}}`, `{{CONTEXT}}`, `{{SUCCESS}}`, `{{RETURN}}`, `{{DEADLINE}}`. Used by `render_handoff.py`.
- `handoff.example.json` — Example JSON payload showing the exact shape `validate_handoff.py` accepts and `render_handoff.py` consumes.
- `chain.example.json` — Example chain payload (list of handoffs) for `check_chain.py`.

### Scripts (`scripts/`)
- `validate_handoff.py` — Deterministic. Reads a handoff JSON payload, validates the schema: `from_agent` non-empty, `to_agent` non-empty, `task` non-empty, `success_criteria` is a non-empty list, `context_files` is a list, `return_format` non-empty, `deadline` optional. Args: `--file <path>` or `--stdin`. Prints JSON `{valid: bool, errors: [...]}` to stdout. Exit 0 = valid, 1 = invalid.
- `render_handoff.py` — Deterministic. Renders `templates/handoff.md.template` from a validated payload and writes the prompt the receiving agent will see. Args: `--payload <path>` `--out <path>` `[--force]`. Exit 0 on write.
- `check_chain.py` — Deterministic. Given a list of planned handoffs, checks for cycles and validates that each agent's `output_type` matches the next agent's `expected_input_type`. Args: `--chain-json <path>`. Prints JSON `{valid: bool, issues: [...]}` to stdout. Exit 0 = valid chain, 1 = chain has issues.
- `validate_output.py` — Deterministic. Validates a rendered handoff prompt: required sections (FROM, TO, TASK, CONTEXT, SUCCESS, RETURN) present and in order, no unsubstituted `{{...}}` template tokens. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `handoff-schema.md` — Authoritative schema: every required and optional field of a handoff payload, allowed types for `output_type` / `expected_input_type`, and the validation contract.
- `chain-patterns.md` — Common chain patterns: linear (A→B→C), fan-out (A→{B,C,D}), fan-in (sum of {B,C,D} → A), and pitfalls of each.
- `failure-modes.md` — What goes wrong in delegation: lost context, type mismatch between agents, cycles in the chain, missing deadline gap, ambiguous return format.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any rendered handoff this skill produces.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `valid_handoff`, `invalid_handoff`, `valid_chain`, `cyclic_chain`, `mismatched_chain`.
- `unit/test_validate_handoff.py` — Unit tests for the schema validator: every required field, edge cases (missing field, empty list, non-list, wrong type).
- `unit/test_render_handoff.py` — Unit tests for template substitution, payload validation, write semantics, `--force` behavior, deadline omission.
- `unit/test_check_chain.py` — Unit tests for chain validation: linear pass, fan-out, fan-in, cycle detection, type mismatch detection.
- `unit/test_validate_output.py` — Unit tests for the rendered-prompt validator: happy path, missing section, sections out of order, unsubstituted token.
- `integration/test_swarm_delegation_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/swarm_delegation_eval.py` — Three-case eval: clear handoff (valid), ambiguous handoff (invalid), cyclic chain (caught). Verifies eval harness shape.
- `smoke/test_e2e.py` — End-to-end: `validate_handoff.py` → `render_handoff.py` → `validate_output.py` for a single handoff; `check_chain.py` for a multi-step chain.

### Examples (`examples/`)
- `example-1/` — Worked example: orchestrator → backend-developer → test-implementation linear chain. Includes `chain.json`, individual `handoff-1.json` / `handoff-2.json` payloads, the rendered `handoff-1.md` and `handoff-2.md` prompts, and `chain-validation.json` from `check_chain.py`.

## Contract

Given a structured handoff payload (or a list of them as a chain), produce one of:
1. A rendered handoff prompt at `--out` such that the body has these `##` sections in order: `## FROM`, `## TO`, `## TASK`, `## CONTEXT`, `## SUCCESS`, `## RETURN`. `## DEADLINE` is optional and appears only if the payload provides one.
2. A chain validation JSON `{valid, issues}` where `valid` is true only if (a) no cycle exists in the directed handoff graph and (b) every consecutive `output_type` matches the next `expected_input_type`.

Additional invariants:
3. `python scripts/validate_handoff.py --file <payload>` exits 0 before rendering.
4. `python scripts/validate_output.py --file <rendered>` exits 0 after rendering.
5. The rendered prompt has no unsubstituted `{{TOKEN}}` placeholders.
6. The schema lives in `knowledge/handoff-schema.md`; the LLM does not invent fields.
7. `check_chain.py` is the source of truth for cycle and type-mismatch detection; the LLM does not override its result.

## Knowledge

### What a handoff payload is
A handoff is a structured JSON object, not a paragraph. The seven fields (`from_agent`, `to_agent`, `task`, `context_files`, `success_criteria`, `return_format`, optional `deadline`, plus `output_type` / `expected_input_type` for chain checking) are the contract between two agents. Free-form delegation prose is a synonym for "lost context".

### Why mechanical chain checks
A delegation chain that the LLM eyeballs as fine often has cycles (`A→B→A`) or type mismatches (agent X promises `code-diff`, agent Y expects `test-list`). Both fail at runtime, after agents have already burned tokens. `check_chain.py` catches these before any agent runs.

### Three core patterns
- **Linear** (A→B→C): each agent's output feeds the next. Fails on type mismatch or cycle.
- **Fan-out** (A→{B,C,D}): one agent dispatches independent subtasks. Fails when the children have implicit dependencies on each other (they shouldn't).
- **Fan-in** ({B,C,D}→A): one agent merges parallel results. Fails when the merger lacks a defined merge protocol or when one child's output type doesn't match the merger's input slot.

See `knowledge/chain-patterns.md` for full pattern references and `knowledge/failure-modes.md` for the six known failure modes.

## Steps

1. **Identify the handoff(s).** From the user's request, extract: who is delegating, who is receiving, what the task is, what files the receiver needs, what success looks like, what shape the receiver returns. If any of these are missing, ask one focused question — do not invent.

2. **Assemble payload.** Build a JSON payload with all required fields. See `templates/handoff.example.json` for the exact shape.

3. **Validate handoff.** Run `python scripts/validate_handoff.py --file <payload>`. Must exit 0. Fix and re-run on failure.

4. **Render prompt.** Run `python scripts/render_handoff.py --payload <payload> --out <prompt-path>`. Default prompt path: `<feature>/handoff-<n>.md`.

5. **Validate rendered prompt.** Run `python scripts/validate_output.py --file <prompt-path>`. Must exit 0.

6. **(Multi-step only) Check chain.** If the user described more than one handoff, assemble a chain JSON (a list of payloads with `output_type` and `expected_input_type` set on each step). Run `python scripts/check_chain.py --chain-json <chain>`. Must exit 0; surface any cycles or type mismatches before continuing.

7. **Announce.** Print the rendered prompt path, the chain pattern (linear / fan-out / fan-in), and any issues `check_chain.py` surfaced. Example:
   ```
   Handoff rendered: <prompt-path>
   FROM: orchestrator
   TO:   backend-developer
   Pattern: linear (step 1 of 3)
   Chain: VALID
   ```

## Output

A rendered handoff prompt at `--out`, conforming to `templates/handoff.md.template`. Optionally, a chain-validation JSON file. No other side effects.

Suggested filename for prompts: `handoff-<from>-to-<to>.md`.

## Antipatterns

- **LLM inventing the validation result.** `valid: true` comes from the script. The LLM may explain *why* something failed but never overrides it.
- **Free-form prose handoff.** "Hey backend-developer, please look at the user service" is unstructured and unverifiable. Use the payload.
- **Skipping `validate_output.py`.** A rendered prompt the validator hasn't seen is not done.
- **Cycles "the LLM is sure are fine".** `check_chain.py` catches them deterministically; trust the script.
- **Type mismatches papered over with "the agent will figure it out".** They won't. Fix the contract before running.
- **Embedding the prompt template in SKILL.md.** Lives in `templates/handoff.md.template`.
- **Confusing this with `agent-delegation`.** That skill writes FOCUS/EXCLUDE *prompts* for one-shot delegations. This skill defines *contracts* and validates *chains*.
- **Bundling agent selection.** Picking which specialist to hire is `workflow-agent-selector`'s job — this skill assumes you already know.

## Validation

Pass criteria:
1. `python scripts/validate_handoff.py --file <payload>` exits 0 for the input payload.
2. `python scripts/validate_output.py --file <rendered>` exits 0 for the rendered prompt.
3. `python scripts/check_chain.py --chain-json <chain>` exits 0 for the chain (if multi-step).
4. `pytest tests/unit/` exits 0.
5. `pytest tests/smoke/` exits 0.
6. `pytest tests/evals/` exits 0.
7. Every item in `validation/quality-checklist.md` is checked.
8. The rendered prompt has all six required sections in order with no unsubstituted tokens.

## Examples

- **`examples/example-1/`** — Worked example: a three-step linear chain `orchestrator → backend-developer → test-implementation`. Demonstrates: payload shape with `output_type`/`expected_input_type`, two rendered prompts, and a passing `chain-validation.json`. Useful as the canonical reference for assembling multi-step handoffs.
