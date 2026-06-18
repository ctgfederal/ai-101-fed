# Approval Workflow

A deviation is a request, not a fact. Until an approver flips its status, the implementation is not authorized to deviate.

## States

```
            ┌──────────┐
        ──▶│ proposed │──▶ approved   (implementation may proceed)
            └────┬─────┘
                 │
                 └──▶ rejected   (implementation follows original decision)
```

## Who approves

The **spec owner** — the human who signed off on the PRD/SDD. The skill does not enforce this (no auth model); the workflow is procedural.

## How to flip status

1. The approver decides: `approved` or `rejected`.
2. Re-run `append_deviation.py` with `--force` and an updated payload (same `deviation_id`, new `status`).
3. The block is replaced in place, preserving its original date and original decision.

## Rule: rejected deviations are not deleted

A rejected deviation is **kept** as historical record. Why:

- Future implementers can see "this was tried and rejected" — preventing rediscovery.
- Reviewers can audit the spec's resilience under pressure.
- It is the difference between "the spec was wrong" and "the spec was clear and held".

If a second attempt at the same problem is needed, allocate a new `DEV-NNN`. Do not mutate the rejected one.

## Rule: do not implement on `proposed`

`proposed` is *requested*, not authorized. If implementation merges code that does not match the spec while a deviation is still `proposed`, the spec and the code are out of sync and the deviation has lost its purpose. Wait for `approved`.

## Rule: one block per deviation

If two `REQ-NNN`s need separate deviations for the same root cause, allocate two `DEV-NNN`s. Bundling is silent ambiguity — each deviation deserves its own approval decision.
