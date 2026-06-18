# Phase Notes Format

A phase note is the answer to one question:

> What did we learn at the end of this phase that the spec did not predict?

If the answer is "nothing" — skip it. Empty phase notes are worse than missing ones.

## What belongs in a phase note

- **Decision summary** — A choice you had to make that the spec didn't pin down.
  Example: "Spec said 'caching layer'; we picked Redis with 60s TTL because of memory pressure on the Pi."
- **Spec-reality mismatch** — Where the SDD/PLAN was wrong, incomplete, or surprising in execution.
  Example: "PLAN T-018 assumed Stripe webhooks were idempotent; they are not. Added dedupe table."
- **Blockers encountered (and how resolved)** — Anything that delayed the phase by more than an hour.
  Example: "Migration locked on production-sized table; switched to `pt-online-schema-change`."
- **Dependency discovered** — Something not listed in the SDD that turned out to be required.
  Example: "Needed `node-postgres` >= 8.11 for native named-cursors; bumped from 8.6."

## What does not belong in a phase note

- **Commit log.** "Wrote 3 functions and 5 tests." Git already has this.
- **Tutorial content.** Explaining how Postgres MVCC works. Link to the doc instead.
- **Undated speculation.** "Maybe we'll need X someday." Either it blocks → Open Questions, or drop it.
- **Personal style notes.** "I prefer named functions over arrows." Goes in your editor config, not the spec.

## Length

Two to ten bullets is the sweet spot. If the note runs longer than that, split it across multiple phase boundaries or write a proper ADR (`architecture-adr-generator`) and link to it from the note.

## Tone

Plain. Past tense. Specific. Names of files, IDs of requirements/tasks, exact error messages where relevant. The future reader is yourself in three months — write so they can verify the claim, not just believe it.

## When to append

At the **end of a phase**, not during it. Drafting a note during work is fine; commit it (via `append_phase_note.py`) only when the phase is complete and the surprises are real, not predicted.

## Tooling

Always use `scripts/append_phase_note.py`. Never hand-edit the README to insert a phase note — the script enforces monotonic ordering, timestamping, and deduplication.

```bash
python scripts/append_phase_note.py \
  --feature feature-search --specs-root .claude/specs \
  --phase 2 --name "Core" \
  --note "Spec assumed inverted index; pgvector was simpler. T-014 dropped."
```

To pipe a long note via stdin:

```bash
cat note.txt | python scripts/append_phase_note.py \
  --feature feature-search --specs-root .claude/specs \
  --phase 2 --name "Core"
```
