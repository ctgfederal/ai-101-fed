---
name: spec-readme
version: 2.0.0
description: |
  Create and maintain `.claude/specs/<feature>/README.md` — the human-facing entry point for a spec folder that lists PRD/SDD/PLAN status, decision-log links, and captures phase-boundary learnings/insights for use by `spec-reflexion`. Use when a user runs `/specify` and the spec folder is new, asks "create the spec README", asks to mark PRD/SDD/PLAN as approved, or wants to record a phase note during `/implement`. Do NOT use to write the PRD itself (use `spec-prd-generator`), the SDD (use `spec-sdd-generator`), the PLAN (use `spec-plan-generator`), or to capture global learnings — those go in `~/.claude/projects/<cwd>/memory/` via `/memorize`. This skill manages the spec folder's index file only; it is not for free-form note-taking.
triggers:
  - "/specify"
  - "create spec README"
  - "init spec readme"
  - "mark PRD approved"
  - "update spec status"
  - "append phase note"
  - "spec README for"
  - "phase boundary note"
  - "log learning to spec"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-readme

Manage `.claude/specs/<feature>/README.md` deterministically. Three actions: **init** the file, **toggle** PRD/SDD/PLAN status, and **append** phase-boundary notes. The LLM never edits the README directly — it always goes through one of the three scripts.

## Files

### Templates (`templates/`)
- `readme.md.template` — Canonical README layout with placeholders: `{{FEATURE}}`, `{{FEATURE_TITLE}}`, `{{CREATED}}`. Used by `init_readme.py`. Contains every required section pre-stubbed (Status, Steering Refs, Decision Log Snippets, Phase Notes, Learnings, Open Questions).
- `payload.example.json` — Example JSON for the init payload (feature name, title, created date).

### Scripts (`scripts/`)
- `init_readme.py` — Deterministic. Given a feature name and specs root, creates `<root>/<feature>/README.md` from `templates/readme.md.template` with all status checkboxes unchecked. Args: `--feature <name>` `--specs-root <path>` `[--force]`. Exit 0 on write, 1 if exists without `--force`.
- `update_status.py` — Deterministic. Toggles PRD/SDD/PLAN status block to one of `draft|approved|deprecated` and appends a timestamped status line under the corresponding doc's status. Args: `--feature <name>` `--specs-root <path>` `--doc <prd|sdd|plan>` `--status <draft|approved|deprecated>`. Exit 0 on update.
- `append_phase_note.py` — Deterministic. Appends a `### Phase N: <name>` block (with ISO-8601 timestamp) under the `## Phase Notes` section. Note text comes from `--note` flag or stdin. Args: `--feature <name>` `--specs-root <path>` `--phase <int>` `--name <str>` `[--note <str>]`. Exit 0 on append.
- `validate_output.py` — Deterministic. Validates a written README: required sections present in order, status block valid (every doc has one of allowed statuses), all relative links resolve. Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `readme-schema.md` — Required `##` sections, allowed status values per doc, link format for steering and decision-log references.
- `phase-notes-format.md` — What belongs in a phase note (decision summary, surprises, blockers) and what does not (full code diffs, off-topic ideas).
- `learnings-vs-decisions.md` — How to choose between writing to the spec README's Learnings section vs. `.claude/decisions-log.md` vs. global memory.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any spec README this skill produces or updates.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `specs_root`, `valid_feature`, `seeded_readme`.
- `unit/test_init_readme.py` — Unit tests for `init_readme.py`: creates file, refuses existing without force, validates feature name, populates template placeholders.
- `unit/test_update_status.py` — Unit tests for `update_status.py`: toggles each doc, rejects unknown status, rejects unknown doc, errors when README missing.
- `unit/test_append_phase_note.py` — Unit tests for `append_phase_note.py`: appends in order, accepts stdin note, rejects non-positive phase numbers, errors when README missing.
- `unit/test_validate_output.py` — Unit tests for `validate_output.py`: happy path, missing section, invalid status, dangling steering link.
- `integration/test_spec_readme_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/spec_readme_eval.py` — Three-case eval shape: empty README (init), partial README (status update), README with phase notes (append).
- `smoke/test_e2e.py` — End-to-end: `init_readme.py` → `update_status.py` → `append_phase_note.py` → `validate_output.py` against a tmp specs root.

### Examples (`examples/`)
- `example-1/` — Worked example: `feature-search` README after init + PRD approved + one phase note appended. Includes `README.md` (the rendered file) and `flow.md` (the exact commands used).

## Contract

Given a feature name and specs root, produce or update one file at `<specs-root>/<feature>/README.md` such that:

1. Path matches `^.+/[a-z][a-z0-9-]+/README\.md$`.
2. Body has these `##` sections in order: `## Status`, `## Steering References`, `## Decision Log Snippets`, `## Phase Notes`, `## Learnings`, `## Open Questions`.
3. The `## Status` section has exactly three entries — `PRD`, `SDD`, `PLAN` — each with a status of `draft`, `approved`, or `deprecated`.
4. Phase notes are appended under `## Phase Notes` with `### Phase <int>: <name>` headers, in monotonic phase-number order.
5. Steering references use relative paths (`../../steering/<file>.md`) and decision-log references use relative paths (`../../decisions-log.md#D-NNN`).
6. `python scripts/validate_output.py --file <path>` exits 0.
7. The LLM does not edit the README directly — every change goes through `init_readme.py`, `update_status.py`, or `append_phase_note.py`.

## Knowledge

### README is an index, not a doc dump
The README links to PRD/SDD/PLAN; it does not duplicate their content. It exists so a human (or future Claude) opening `.claude/specs/<feature>/` can answer in 30 seconds: what state are we in, where are the docs, what was decided, what was surprising. See `knowledge/readme-schema.md`.

### Status values are closed
Each of PRD/SDD/PLAN has exactly one of three statuses: `draft` (in progress, do not trust), `approved` (signed off, build against this), `deprecated` (replaced — see successor doc). No other values. See `knowledge/readme-schema.md`.

### Phase notes capture surprise, not progress
A phase note is the answer to "what did we learn at the end of this phase that the spec did not predict?" Decision summary, spec-reality mismatches, blockers encountered. Not "we wrote 3 functions and 5 tests" — that's a commit log. See `knowledge/phase-notes-format.md`.

### Learnings vs. decisions vs. memory
Local learnings (this feature only) → spec README `## Learnings`. Cross-feature decisions with rationale → `.claude/decisions-log.md` via `/build`. Globally reusable patterns → `~/.claude/projects/<cwd>/memory/` via `/memorize`. See `knowledge/learnings-vs-decisions.md`.

## Steps

1. **Resolve feature.** Confirm the feature name (kebab-case) and specs root (default `.claude/specs`).

2. **Decide action.** One of:
   - `init` — README does not exist yet (typically at start of `/specify`).
   - `update_status` — PRD/SDD/PLAN reached a new state (draft → approved, etc.).
   - `append_phase_note` — phase boundary hit during `/implement`.

3. **Run the right script.**
   - Init: `python scripts/init_readme.py --feature <name> --specs-root .claude/specs`. Exits 1 if README exists without `--force`.
   - Status: `python scripts/update_status.py --feature <name> --specs-root .claude/specs --doc <prd|sdd|plan> --status <draft|approved|deprecated>`.
   - Phase note: `python scripts/append_phase_note.py --feature <name> --specs-root .claude/specs --phase <int> --name <str> --note <str>` (or pipe note via stdin).

4. **Validate.** Run `python scripts/validate_output.py --file <readme-path>`. Must exit 0.

5. **Announce.** Print the action taken and the README path. Example:
   ```
   spec-readme: init feature-search
   File: .claude/specs/feature-search/README.md
   Status: PRD draft, SDD draft, PLAN draft
   ```

## Output

A single markdown file at `<specs-root>/<feature>/README.md` rendered from `templates/readme.md.template` (on init) or surgically updated (on status/phase actions). No other side effects. The file is the source of truth for that spec folder's index.

## Antipatterns

- **LLM writes the README directly.** Every change goes through one of the three scripts. The LLM does not Edit or Write the README outside of those tools.
- **Skipping validation.** A README that has not been seen by `validate_output.py` is not done.
- **Embedding PRD/SDD/PLAN content.** The README links to those files; it never copies their bodies.
- **Inventing new status values.** Exactly three: `draft`, `approved`, `deprecated`. No "in-review", no "wip", no emoji.
- **Phase-note as commit log.** "Wrote N functions" belongs in git. Phase notes capture surprise: spec-reality mismatch, decision evolution, dependency discovered.
- **Embedding the template in SKILL.md.** Lives in `templates/readme.md.template`.
- **Mixing local and global learnings.** Promote globally-useful patterns to memory via `/memorize`; keep feature-specific notes in the spec README.
- **Editing decision-log via this skill.** Cross-feature decisions live in `.claude/decisions-log.md` and are managed by `/build` — this skill only references them.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. Every item in `validation/quality-checklist.md` is checked.
6. Every action on the README went through one of the three scripts (no direct LLM edits).

## Examples

- **`examples/example-1/`** — Worked example: `feature-search` after init, PRD approval, and one phase note appended. Demonstrates: init populates all six sections, `update_status` flips PRD `draft` → `approved` with a timestamp, `append_phase_note` adds `### Phase 1: Foundation` under Phase Notes. Includes the rendered `README.md` and a `flow.md` with the exact command sequence.
