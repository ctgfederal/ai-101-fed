---
name: brainstorming
version: 3.0.0
description: |
  Explore the WHY and FOR WHOM behind an idea — inspiration, audience, use cases, desired outcomes, and guiding principles — through one-question-at-a-time interactive dialogue, then capture the result as a structured markdown file under `.claude/brainstorms/YYYY-MM-DD-<topic>.md` for use by `/build` and `/specify`. Use when a user starts with `/brainstorm`, asks "let's brainstorm X", or has a vague idea that needs vision-shaping before any design or technical decisions. Do NOT use for making design decisions (that's `/build`), writing formal specs (that's `/specify`), debugging code, or any task where the WHY is already settled.
triggers:
  - "/brainstorm"
  - "let's brainstorm"
  - "I want to explore an idea"
  - "help me think through"
  - "I have a vague idea about"
  - "what could we build for"
  - "shape this concept"
  - "explore the why"
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

# brainstorming

Explore the WHY and FOR WHOM through one-question-at-a-time dialogue. Captures inspiration, audience, use cases, outcomes, principles, constraints, and scope as a structured markdown file.

## Files

### Templates (`templates/`)
- `brainstorm.md.template` — Canonical output template for a captured brainstorm. Placeholders: `{{TOPIC}}`, `{{DATE}}`, `{{INSPIRATION}}`, `{{AUDIENCE}}`, `{{USE_CASES}}`, `{{OUTCOMES}}`, `{{PRINCIPLES}}`, `{{CONSTRAINTS}}`, `{{SCOPE_IN}}`, `{{SCOPE_OUT}}`, `{{OPEN_QUESTIONS}}`, `{{RELATED}}`.
- `question-progression.md` — The 8 ordered question categories with example phrasings. Reference, not LLM input.

### Scripts (`scripts/`)
- `init_brainstorm.py` — Deterministic. Creates `.claude/brainstorms/` if absent, computes the slug+date filename, returns the target path. Args: `--topic <str>` `--brainstorms-root <path>` `[--date YYYY-MM-DD]`. Refuses to overwrite without `--force`. Exit 0 = path printed.
- `write_brainstorm.py` — Deterministic. Given a JSON payload of brainstorm fields, renders `brainstorm.md.template` and writes the file. Args: `--payload <path-or-stdin>` `--out <path>` `[--force]`. Exit 0 = wrote file.
- `validate_output.py` — Deterministic. Validates a written brainstorm file: frontmatter (`topic`, `date`, `status`), required body sections (Inspiration, Audience, Use Cases, Desired Outcomes, Guiding Principles, Constraints, Scope, Open Questions). Args: `--file <path>`. Exit 0 = valid.

### Knowledge (`knowledge/`)
- `question-flow.md` — How to run the dialogue: clarity assessment, question progression, when to stop, when to skip.
- `brainstorm-schema.md` — Frontmatter and body section requirements with examples and antipatterns.
- `handoff.md` — How to hand off to `/build` or `/specify` after capture.
- `README.md` — Index of knowledge files.

### Validation (`validation/`)
- `quality-checklist.md` — Pass criteria for any captured brainstorm.

### Tests (`tests/`)
- `unit/test_init_brainstorm.py` — Slug generation, date handling, overwrite protection, root creation.
- `unit/test_write_brainstorm.py` — Payload validation, template rendering, file write semantics.
- `unit/test_validate_output.py` — Frontmatter and body validation across happy / missing-section / malformed cases.
- `integration/test_brainstorming_integration.py` — Placeholder; this skill hits no external endpoints.
- `evals/brainstorming_eval.py` — LLM evals on the question-progression decision (clear / directional / exploratory inputs).
- `smoke/test_e2e.py` — End-to-end: init → write → validate against fixture payload.
- `conftest.py` — Shared fixtures: `tmp_brainstorms_root`, `valid_payload`.

### Examples (`examples/`)
- `example-1/` — A worked example: `payload.json` for "AI-powered code review for solo devs", and the resulting captured `expected-output.md`.

## Contract

Given an unclear idea + optional `/brainstorm <topic>` argument, produce exactly one markdown file at `.claude/brainstorms/<YYYY-MM-DD>-<topic-slug>.md` such that:

1. The file path matches `^\.claude/brainstorms/\d{4}-\d{2}-\d{2}-[a-z0-9-]{1,60}\.md$`.
2. YAML frontmatter contains `topic`, `date`, `status` (one of `complete`, `in-progress`).
3. Body contains 8 headed sections in order: `## Inspiration`, `## Projects`, `## Audience`, `## Use Cases`, `## Desired Outcomes`, `## Guiding Principles`, `## Constraints`, `## Scope`. `## Open Questions` and `## Related Solutions` are optional but recommended.
4. Each section is ≤ 300 words.
5. `python scripts/validate_output.py --file <path>` exits 0.
6. No design or technical decisions are recorded — those belong to `/build`.
7. No file outside `.claude/brainstorms/` is created or modified.

## Knowledge

### What brainstorming does and does not do
This skill explores **why** and **for whom**, never **how**. The deliverable is a vision document that `/build` consumes to ground design decisions and `/specify` consumes to scope the spec. If the user starts proposing technical solutions, redirect them to `/build`.

### One question at a time
Question batching exhausts users and produces shallow answers. Ask, wait, listen, follow up. The 8-question progression in `templates/question-progression.md` is a starting order — adapt to user energy.

### Search the solutions archive first
Before exploring, run `python ~/.claude/skills/compound-docs/scripts/search_solutions.py --solutions-root .claude/solutions --tag <topic>` to surface prior art. Cite any matches in the captured `Related Solutions` section.

See `knowledge/question-flow.md` for the full dialogue protocol and `knowledge/brainstorm-schema.md` for the field schema.

## Steps

1. **Search prior art.** Run `search_solutions.py` against the topic's likely tags. Surface any matches at the start of the conversation: "Found related solution: [title]. This may inform our thinking."

2. **Assess clarity.** Read user's opening: clear (vision + audience + outcomes already stated), directional (goal known, scope unclear), exploratory (vague spark). Read `knowledge/question-flow.md` for the rules. If clear, propose skipping to `/build`. If exploratory, plan to ask all 8.

3. **Init the file.** Run `python scripts/init_brainstorm.py --topic "<topic>" --brainstorms-root <repo>/.claude/brainstorms`. Capture the returned path; refuse to overwrite without `--force`.

4. **Walk the question progression.** Use `AskUserQuestion` one at a time. Order: inspiration → projects → audience → use cases → outcomes → principles → constraints → scope. Skip what the user already answered. Stop when vision is clear OR user says "proceed".

5. **Resolve open questions.** Before writing, surface any remaining unknowns; ask each one explicitly with `AskUserQuestion`. Move resolved items to a "Resolved" section in the open-questions list.

6. **Assemble payload.** Build a JSON payload with all required fields and section bodies. See `templates/brainstorm.md.template` for the shape and `examples/example-1/payload.json` for a worked example.

7. **Write the file.** Run `python scripts/write_brainstorm.py --payload <path> --out <init-output-path>`. Refuse `--force` unless the user explicitly asks to overwrite.

8. **Validate.** Run `python scripts/validate_output.py --file <output>`. Exit 0 required.

9. **Handoff.** Use `AskUserQuestion` to ask "What next?" with options: `/build`, `/specify`, refine further, done. See `knowledge/handoff.md`.

## Output

A single markdown file at `.claude/brainstorms/<YYYY-MM-DD>-<topic-slug>.md`, conforming to `templates/brainstorm.md.template`. No other side effects.

## Antipatterns

- **Asking multiple questions at once.** Batching exhausts users and produces shallow answers; one question, listen, follow up.
- **Letting the user skip into HOW.** Brainstorming is WHY. If they propose technical decisions, capture the impulse as an open question and redirect to `/build`.
- **Writing the file before the user signals "proceed".** A premature capture freezes a half-formed vision.
- **Skipping the solutions archive.** Re-discovering known patterns wastes the user's time and produces duplicate brainstorms.
- **Embedding the template inline in SKILL.md.** Output template lives in `templates/`. Drift kills the schema.
- **Inventing fields the schema doesn't have.** The capture is what `/build` and `/specify` consume — adding ad-hoc fields breaks downstream tools.
- **Capturing > 300 words per section.** Brainstorms set vision; novellas defeat the purpose.

## Validation

Pass criteria:
1. `python scripts/validate_output.py --file <output>` exits 0.
2. `pytest tests/unit/` exits 0.
3. `pytest tests/smoke/` exits 0.
4. `pytest tests/evals/` exits 0.
5. `RUN_INTEGRATION_TESTS=1 pytest tests/integration/` exits 0.
6. Every item in `validation/quality-checklist.md` is checked.
7. Captured brainstorm contains zero design or technical decisions (those belong to `/build`).

## Examples

- **`examples/example-1/`** — Worked example: input topic ("AI-powered code review for solo devs"), the assembled payload, and the resulting captured brainstorm at `.claude/brainstorms/2026-02-14-ai-code-review-solo-devs.md`. Demonstrates the full 8-section structure and a populated open-questions list.
