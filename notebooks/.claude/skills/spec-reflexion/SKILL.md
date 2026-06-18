---
name: spec-reflexion
version: 2.0.0
description: |
  Capture learnings during spec-driven development in two passes — Part 1 appends phase-boundary insights to `.claude/specs/<feature>/README.md` (local, feature-specific), and Part 2 filters globally-useful items and promotes them to native auto-memory at `~/.claude/projects/<sanitized-cwd>/memory/<type>_<slug>.md` with a typed YAML frontmatter (`feedback`, `project`, `reference`, or `user`) and an updated `MEMORY.md` index. Use when the user runs `/reflect`, finishes a phase boundary, completes a spec, or asks "save this learning" / "promote to memory" / "what did we learn from this spec". Do NOT use for free-form journaling (no spec context), to write the spec itself (use `spec-prd-generator` / `spec-sdd-generator`), to author solution archives (use `compound-docs`), or to make architecture decisions (use `architecture-adr-generator`) — this skill captures *what was learned*, not *what was decided*.
triggers:
  - "/reflect"
  - "phase boundary reflection"
  - "save this learning"
  - "promote to memory"
  - "capture spec learnings"
  - "what did we learn from this spec"
  - "update spec README with learnings"
  - "memorize this insight"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
model: claude-sonnet-4-6
---

# spec-reflexion

Two-part learning capture. Part 1 appends phase-boundary insights to a spec's
`README.md`. Part 2 filters globally-useful items and promotes them to typed
auto-memory files, updating `MEMORY.md` so they are findable forever. The
deterministic scripts handle extraction, classification, file writing, and
index updates; the LLM only narrates and chooses the right memory type.

## Files

### Templates (`templates/`)
- `memory-file.md.template` — Canonical layout for a written memory file. Placeholders: `{{NAME}}`, `{{DESCRIPTION}}`, `{{TYPE}}`, `{{BODY}}`. Used by `promote_to_memory.py`.
- `spec-readme-learnings.md.template` — Skeleton block to append under `## Learnings` in a spec README at a phase boundary. Used by Part 1.
- `payload.example.json` — Example JSON payload for `promote_to_memory.py`, showing every field with sample values.

### Scripts (`scripts/`)
- `extract_learnings.py` — Deterministic. Parses a spec README and returns a JSON list of learning items. Each item has `text`, `phase`, and `scope` (`local` | `global`). Recognises `## Learnings`, `## Phase Notes`, `## Implementation Insights`, `## What Worked`, `## What Didn't Work`, and `### For /memorize (Global Learnings)` sections. Args: `--readme <path>`. Exit 0 always; empty list is normal.
- `classify_learning.py` — Deterministic. Heuristic-based local-vs-global classifier for a single learning text. Local signals: `our X`, `we use`, project paths, pinned IDs. Global signals: framework nouns, pattern verbs, user-preference markers. Defaults to `local` on a tie. Args: `--text <str>` or stdin. Prints exactly `local` or `global`.
- `promote_to_memory.py` — Deterministic. Writes a typed memory file (`feedback` / `project` / `reference` / `user`) at `<memory-root>/<type>_<slug>.md` with frontmatter from the supplied text, then appends or replaces a corresponding bullet in `MEMORY.md`. Refuses to overwrite without `--force`. Args: `--text` `--type` `--name` `--memory-root` `[--title]` `[--description]` `[--force]`. Exit 0 = wrote file; prints output path.
- `validate_output.py` — Deterministic. Given a written memory file, validates frontmatter (`name`, `description`, `type`), confirms `type` is one of the four allowed values, ensures the body is non-empty, and asserts a matching bullet exists in the sibling `MEMORY.md`. Args: `--file <path>`. Exit 0 = pass.

### Knowledge (`knowledge/`)
- `README.md` — Index of knowledge files and when to load each.
- `learning-types.md` — Definitions of `feedback`, `project`, `reference`, and `user` types; heuristics for picking when ambiguous.
- `local-vs-global.md` — Heuristics that drive `classify_learning.py`; what stays in spec README vs. promotes to memory.
- `memory-format.md` — Exact frontmatter format and `MEMORY.md` index conventions; matches Claude Code's auto-memory protocol.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any memory file produced by this skill.

### Tests (`tests/`)
- `conftest.py` — Shared pytest fixtures: `tmp_memory_root`, `sample_readme`, `empty_readme`, `valid_promotion_payload`.
- `unit/test_extract_learnings.py` — Unit tests for the README parser. Covers local + global detection, phase capture, checkbox stripping, empty-readme behaviour, `--readme` CLI.
- `unit/test_classify_learning.py` — Unit tests for the classifier: framework-pattern globals, user-preference globals, project-path locals, pinned-ID locals, tie-breaker default.
- `unit/test_promote_to_memory.py` — Unit tests for memory writing: file shape, MEMORY.md index update, dedup-replace, `--force` behaviour, invalid type, empty text.
- `unit/test_validate_output.py` — Unit tests for the output validator: happy path, missing fields, bad type, empty body, missing index entry.
- `integration/test_spec_reflexion_integration.py` — Optional smoke against the user's real `~/.claude/projects/.../memory` directory. Gated by `RUN_INTEGRATION_TESTS=1`.
- `evals/spec_reflexion_eval.py` — Three-case eval: clear global, clear local, and borderline mixed-signal cases. Verifies eval shape and classifier agreement on the clear cases.
- `smoke/test_e2e.py` — End-to-end: `extract_learnings.py` → `classify_learning.py` → `promote_to_memory.py` → `validate_output.py` against a fixture spec README.

### Examples (`examples/`)
- `josh-error-types/` — Worked example: an `input-readme.md` with both local and global learnings, the extractor's `extracted.json`, the classifier's verdict on the candidate global bullet, and the resulting `expected-memory.md` plus `expected-index.md`.

## Contract

Given a spec `README.md` (Part 1) and zero or more candidate global learnings
(Part 2), produce these artefacts such that:

1. **Part 1.** The spec's `README.md` gains (or extends) a `## Learnings`
   section that includes at least one phase-tagged insight, captured under
   `### Phase <phase-id>`. No other section of the README is rewritten.
2. **Part 2.** For each globally-useful learning, exactly one memory file is
   written at `<memory-root>/<type>_<slug>.md` such that:
   - Filename matches `^(feedback|project|reference|user)_[a-z0-9_]{1,60}\.md$`
   - YAML frontmatter has `name`, `description`, `type`; `type` is one of
     `feedback` | `project` | `reference` | `user`
   - Body is non-empty
3. The sibling `MEMORY.md` has exactly one bullet of form
   `- [<filename>](<filename>) - <description>` per written file (no
   duplicates, no orphans).
4. `python scripts/validate_output.py --file <path>` exits 0 for each
   written file.
5. If the target file already exists, the run fails unless `--force` is
   passed; previous content is never silently overwritten.
6. The integer scope (`local` / `global`) and memory `type` are *advisory* —
   the LLM may override the classifier's choice with explicit `--type` and
   `--name` arguments. The deterministic scripts will not invent classifications
   on the LLM's behalf.

## Knowledge

### Why two parts

A learning that's specific to *this* feature ("REQ-104 was renumbered after
the merge") belongs in the spec's README — it dies with the spec, and that's
fine. A learning that's generally useful ("Josh prefers explicit error types")
belongs in global memory, where every future session sees it.

Splitting capture from promotion lets us be **liberal** at the spec level
(write everything down) and **conservative** at the global level (only the
broadly applicable bits). The classifier defaults to local on ties for
exactly this reason — false positives in global memory clutter every future
session forever.

### Memory types in one paragraph

`feedback` — a directive Josh gave Claude. `project` — a fact about a
specific project. `reference` — stable factual knowledge with no behaviour
attached. `user` — a stable preference or pattern about Josh personally. See
`knowledge/learning-types.md` for examples and tie-breakers.

### Why the deterministic split

Memory files are read at the top of every session via `MEMORY.md`. A
mis-typed entry, missing description, or duplicated bullet pollutes Claude's
context across thousands of future runs. The validator catches all four
failure modes before the file lands. The classifier is heuristic but
explainable: every signal is a regex documented in `knowledge/local-vs-global.md`.

## Steps

1. **Resolve the spec.** Confirm the path to `.claude/specs/<feature>/README.md`.
   If the user passes a feature ID, locate the README inside that folder.

2. **Part 1 — Extract local learnings.** Run
   `python scripts/extract_learnings.py --readme <path>`. Capture the JSON.
   Group items by `phase`. The LLM may add narrative under each phase but
   does not rewrite existing rows.

3. **Part 1 — Append to README.** Use `templates/spec-readme-learnings.md.template`
   as the shape. Append (do not replace) under `## Learnings`. If the
   section does not exist, create it at the end of the file.

4. **Part 2 — Identify global candidates.** Items with `scope == "global"`
   from step 2 are candidates. Borderline items can be re-checked with
   `python scripts/classify_learning.py --text "<bullet>"` for a second
   opinion.

5. **Part 2 — Pick a memory type per item.** Read `knowledge/learning-types.md`.
   Pick the narrowest fit (`feedback` > `project` > `user` > `reference`).

6. **Part 2 — Resolve memory root.** Default to the user's project memory
   directory:
   `~/.claude/projects/<sanitized-cwd>/memory/`, where `<sanitized-cwd>` is
   the current working directory with `/` replaced by `-`.

7. **Part 2 — Promote each item.** For each global learning:
   ```bash
   python scripts/promote_to_memory.py \
       --text "<learning text>" \
       --type <feedback|project|reference|user> \
       --name <slug> \
       --memory-root <path>
   ```
   `--name` is the slug only — the `<type>_` prefix is added automatically.
   The script also updates `MEMORY.md`.

8. **Validate each output.** For every written file run
   `python scripts/validate_output.py --file <path>`. Must exit 0.

9. **Announce.** Print a summary like:
   ```
   spec-reflexion complete:
     spec README updated: .claude/specs/<feature>/README.md (3 local insights)
     promoted to memory:
       <memory-root>/user_josh_explicit_error_types.md
       <memory-root>/feedback_renumber_req_ids.md
   ```

## Output

Two side effects:

1. The spec `README.md` gains a phase-tagged block under `## Learnings`.
2. Zero or more typed memory files at `<memory-root>/<type>_<slug>.md`,
   plus a corresponding bullet in `<memory-root>/MEMORY.md`.

No other files are created or modified. The exact memory file shape is
defined in `templates/memory-file.md.template`.

## Antipatterns

- **Promoting everything to memory.** Memory files load at every session
  start. Each one costs context budget. Default to local; promote only items
  that pass the classifier *and* the type filter.
- **Writing files from sub-agents.** Only `scripts/promote_to_memory.py`
  ever writes the final memory file. Sub-agents return text only — multiple
  writers cause partial-write corruption of `MEMORY.md`.
- **Skipping `validate_output.py`.** A memory file the validator hasn't seen
  is not done; it can silently miss a frontmatter field and corrupt the
  index for every future session.
- **Inventing memory types.** The four types are exactly `feedback`,
  `project`, `reference`, `user`. Anything else fails validation.
- **Overwriting without consent.** `--force` requires explicit user
  direction. A duplicate slug means run `extract_learnings.py` against the
  existing `MEMORY.md` first to see if there is already a similar entry.
- **Embedding the templates in SKILL.md.** Layout lives in
  `templates/memory-file.md.template` and `templates/spec-readme-learnings.md.template`.
- **Using this skill outside spec context.** Free-form journaling without
  a spec README is not what this skill is for. For arbitrary insights with
  no spec context, run `/memorize` directly.

## Validation

Pass criteria:

1. `python scripts/validate_output.py --file <output>` exits 0 for every
   memory file written.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0 against the
   real memory directory (or skips cleanly).
6. Every item in `validation/quality-checklist.md` is checked.
7. `MEMORY.md` has exactly one bullet per memory file written; no
   duplicates and no orphan bullets.

## Examples

- **`examples/josh-error-types/`** — Full worked example. A spec README
  with two local insights and two global candidates. The extractor finds
  all four; the classifier marks the user-preference and the directive as
  `global`; the user-preference is promoted as `type: user`. Demonstrates
  scope detection, slug generation, frontmatter assembly, and `MEMORY.md`
  index update. Includes `input-readme.md`, `extracted.json`,
  `classification.txt`, `expected-memory.md`, and `expected-index.md`.
