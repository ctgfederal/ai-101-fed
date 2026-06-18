---
name: plan-deepener
version: 2.0.0
description: |
  Enrich a build-decisions or PLAN document with parallel research findings — best practices, edge cases, solutions archive matches, external documentation, and matched skills — by spawning Explore sub-agents per major section, deduplicating their findings, and appending a `### Research Insights` block under each section while preserving original content. Use when a user runs `/deepen`, asks "deepen this plan", or has a build-decisions section ready and wants enrichment before `/specify`. Do NOT use to *create* decisions or plans (those are `/build` and `/specify`), to write code, or as a substitute for actually solving the design problems — this skill annotates existing thinking, it doesn't replace it.
triggers:
  - "/deepen"
  - "deepen this plan"
  - "enrich the decisions"
  - "research insights for"
  - "add research to plan"
  - "deepen build decisions"
  - "find related solutions"
  - "what should I know about this design"
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Task
model: claude-sonnet-4-6
---

# plan-deepener

Spawn parallel research per section, dedupe findings, append `### Research Insights` blocks. Original content is preserved exactly.

## Files

### Templates (`templates/`)
- `research-insights.md.template` — The block appended under each section. Placeholders: `{{SOLUTIONS}}`, `{{BEST_PRACTICES}}`, `{{EDGE_CASES}}`, `{{PERFORMANCE}}`, `{{REFERENCES}}`.
- `deepening-summary.md.template` — Top-of-document summary block. Placeholders: `{{DATE}}`, `{{SECTIONS_COUNT}}`, `{{SOLUTIONS_COUNT}}`, `{{SKILLS_LIST}}`, `{{KEY_FINDINGS}}`, `{{NEW_RISKS}}`.

### Scripts (`scripts/`)
- `parse_target.py` — Deterministic. Parses a markdown document into sections. Extracts technologies (from code fences, links, and named entities), decision categories (from `### Headings`), open questions (from `### Open Questions` blocks). Args: `--file <path>`. Prints JSON of `{sections, technologies, categories, open_questions}` to stdout. Exit 0.
- `match_skills.py` — Deterministic. Given a JSON list of `--keywords`, scans `~/.claude/skills/*/SKILL.md` reading frontmatter `name` and `description`, returns matched skills. Match rule: keyword ∈ skill name OR keyword ∈ skill description (case-insensitive). Args: `--keywords-json <path-or-stdin>` `--skills-root <path>`. Prints JSON list of `{skill, why}` to stdout. Exit 0.
- `merge_research.py` — Deterministic. Given a JSON payload of per-section findings (solutions hits, best practices, edge cases, performance notes, references), renders the `research-insights.md.template` per section and inserts under each section heading in the target document. Refuses if a `### Research Insights` already exists in a section without `--force`. Args: `--target <path>` `--findings-json <path-or-stdin>` `[--force]`. Exit 0.
- `validate_output.py` — Deterministic. Validates the deepened document: every section has either `### Research Insights` or an explicit "_(no findings)_" marker; deepening summary block is at the top; original section bodies are unchanged (verified via length/structure checksums when `--baseline-json` is provided). Args: `--target <path>` `[--baseline-json <path>]`. Exit 0.

### Knowledge (`knowledge/`)
- `research-protocol.md` — How to spawn Explore sub-agents in parallel: per-section task framing, what each agent is asked to return, return-text-only rule, dedup rules.
- `solutions-search.md` — How to use `compound-docs/scripts/search_solutions.py` to find prior art for each section's tags/modules.
- `dedup-rules.md` — Deduplication strategy when multiple sources surface the same recommendation.
- `README.md` — Index.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for a deepened document.

### Tests (`tests/`)
- `unit/test_parse_target.py` — Section extraction, technology extraction, open-questions detection, malformed input.
- `unit/test_match_skills.py` — Empty keywords, name-match, description-match, multi-keyword, no skills root.
- `unit/test_merge_research.py` — Insertion under a section, idempotency check, force-overwrite, malformed payload.
- `unit/test_validate_output.py` — Happy, missing summary, modified original body, missing insights block.
- `integration/test_plan_deepener_integration.py` — Placeholder; this skill itself runs no external endpoints.
- `evals/plan_deepener_eval.py` — LLM evals for research synthesis quality (happy / sparse / contradictory sources).
- `smoke/test_e2e.py` — End-to-end: parse → match skills → merge fixture findings → validate.
- `conftest.py` — Shared fixtures.

### Examples (`examples/`)
- `example-1/` — Worked example: `target-before.md` (a build-decisions section), `findings.json` (mock parallel research output), `target-after.md` (the deepened result).

## Contract

Given a target markdown document (build-decisions section or PLAN.md) and parallel research findings, produce the same document with:

1. A `## Deepening Summary` block at the top (after the document title) with date, sections count, solutions count, matched skills list, key findings, new risks.
2. A `### Research Insights` block inserted under every section that has findings, containing five subsections (`From Solutions Archive`, `Best Practices`, `Edge Cases`, `Performance`, `References`). Subsections may be `_(none)_` but cannot be omitted.
3. Original section bodies preserved character-for-character (no rewording, no reordering).
4. `python scripts/validate_output.py --target <path>` exits 0.
5. The skill is idempotent: running it again on a deepened document either skips already-deepened sections or refreshes them only with `--force`.

## Knowledge

### What deepening adds and does not add
Research findings, prior art, edge cases, performance notes — never new design decisions. If research surfaces a clearly better choice, that becomes a *recommendation in the insights block*, not a rewrite of the original decision. Decision changes are the user's call in a follow-up `/build` session.

### Search the solutions archive first
Run `python ~/.claude/skills/compound-docs/scripts/search_solutions.py --solutions-root .claude/solutions --tag <X>` for every primary tag in the parsed document. Surface every matching solution as a finding for that section.

### Match available skills
Run `python scripts/match_skills.py --keywords-json <keywords> --skills-root ~/.claude/skills` to find skills whose `name` or `description` mentions the keywords. Cite matches in the insights block's "References" subsection.

### Parallel research
For each section, spawn an Explore sub-agent with the framing in `knowledge/research-protocol.md`. Sub-agents return text only — never write files. Collect, dedupe, merge.

## Steps

1. **Locate target.** Check `.claude/decisions-log.md` (latest section), `.claude/specs/<feature>/PLAN.md`, or a path argument. Exit if not found.

2. **Parse.** Run `python scripts/parse_target.py --file <target>`. Capture `sections`, `technologies`, `categories`, `open_questions` from JSON.

3. **Search solutions.** For each technology and each open question, run `compound-docs/scripts/search_solutions.py`. Collect all hits.

4. **Match skills.** Run `python scripts/match_skills.py --keywords-json <tech-and-categories> --skills-root ~/.claude/skills`. Collect matches.

5. **Spawn parallel research.** For each section, spawn an `Explore` sub-agent per `knowledge/research-protocol.md`. Each returns: best practices, edge cases, performance notes, references. Sub-agents return text only.

6. **Synthesize.** Dedupe by hashable summary; merge sources where they agree; flag where they disagree per `knowledge/dedup-rules.md`.

7. **Build findings JSON.** One entry per section with the five subsection arrays.

8. **Merge into target.** Run `python scripts/merge_research.py --target <path> --findings-json <path>`. Refuse `--force` unless user explicitly asked to overwrite previously-deepened sections.

9. **Validate.** Run `python scripts/validate_output.py --target <path>`. Exit 0 required.

10. **Handoff.** Surface the deepening summary; offer next steps (`/specify`, deepen again, view diff, done).

## Output

The same target document, with:
- A `## Deepening Summary` block inserted at the top.
- A `### Research Insights` block inserted under every section that received findings.
- All original content preserved character-for-character.

## Antipatterns

- **Rewriting the original decision.** Findings annotate, never replace. Disagreements with the original go in the insights block as recommendations, not edits to the decision itself.
- **Sub-agents writing files.** Sub-agents return text only — only `merge_research.py` writes the deepened document. Multiple writers cause partial-write corruption.
- **Skipping the solutions archive.** Re-discovering known patterns wastes research budget.
- **Not deduping.** Three sources saying "use prepared statements" should appear once with three citations, not three times.
- **Embedding the template in SKILL.md.** Output template lives in `templates/`.
- **Reading every skill's full SKILL.md to match.** `match_skills.py` reads frontmatter only — fast and complete.
- **Running deepen on a doc that hasn't had `/build` finish.** Deepening before decisions are made amplifies incomplete thinking.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --target <path>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0.
6. Every item in `validation/quality-checklist.md` is checked.
7. Original section bodies are byte-identical to pre-deepen baseline (verified by checksum when baseline is provided).

## Examples

- **`examples/example-1/`** — A build-decisions section about feature-search is deepened with prior-art links, three best practices, two edge cases, performance notes, and skill references. Demonstrates: idempotency check on second run, dedup across two sources surfacing the same pg_trgm recommendation.
