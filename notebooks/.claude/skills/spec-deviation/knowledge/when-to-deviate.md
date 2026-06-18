# When to Deviate

A deviation is for **forced** changes. Not preference. Not "I found a slightly nicer way".

## Test: would the spec hold if you tried harder?

If yes → not a deviation.

If no → deviation.

## Forced (deviation)

- Spec says "use WebSockets" but the target runtime does not support persistent connections.
- Spec says "store in Postgres" but the data must live in a different database for compliance.
- Spec says "respond in 200ms" but the chosen primitive cannot meet 200ms even with optimal implementation.
- Spec relies on an upstream API that has changed shape since approval.
- Spec ambiguity surfaces a decision that was never actually made — and the implementer cannot guess.

## Not forced (TODO, /build re-run, or just implement)

- "I prefer a different naming convention" → just implement, file a refactor note.
- "Library X is more idiomatic than library Y" → preference, not deviation.
- "I think a different architecture would be cleaner" → re-run `/build`; this is a decision change, not a deviation.
- "I forgot to implement this" → that's a TODO in the PLAN.
- "This is a small detail the spec didn't cover" → TODO; spec doesn't have to cover everything at the leaf level.

## Triviality test

If you can fix it without changing what the user gets, what the SDD says, or what the PRD requires → not a deviation.

If users / approvers / reviewers would care about the difference → deviation.

## Why this matters

A `## Deviations` section bloated with preference changes is noise. The signal is: "the spec was wrong / impossible / ambiguous, here is the trail". Keep it for that.

## When in doubt

Ask the spec owner *before* logging the deviation. The block is permanent (rejected ones stay), so cheap to log but expensive to clutter.
