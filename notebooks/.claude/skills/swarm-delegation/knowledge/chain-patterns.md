# Chain Patterns

Three patterns cover ~95% of useful delegation chains. `check_chain.py` reports which one a chain looks like and validates it accordingly.

## Linear (A → B → C)

Each agent's output feeds the next. Useful when each step depends strictly on the previous.

```
orchestrator -> backend-developer -> test-implementation
```

**Type-checked.** `check_chain.py` confirms `step[i].output_type == step[i+1].expected_input_type` for every consecutive pair.

**Pitfalls:**
- One slow step blocks the whole chain — the more steps, the more wall time.
- Type mismatch breaks everything downstream of the mismatch.
- Cycles look harmless on a whiteboard ("then it goes back to orchestrator!") but `check_chain.py` will flag them.

## Fan-out (A → {B, C, D})

One agent dispatches independent subtasks. Useful when subtasks don't depend on each other and can run in parallel.

```
                orchestrator
               /     |     \
       backend-  frontend-  docs-
       developer developer  writer
```

**Not type-checked.** Each child is a fresh chain root.

**Pitfalls:**
- Children secretly depending on each other ("backend writes the schema first, then frontend reads it"). If they need a shared output, that's not fan-out — that's a fan-out followed by a fan-in.
- File collisions when two children edit the same path. Pre-allocate file ownership in each handoff's `success_criteria`.
- No merger means no place for the parent to assemble the children's results. Fan-out without an explicit merge step is half a pattern.

## Fan-in ({B, C, D} → A)

One agent merges parallel results.

```
       backend-  frontend-  docs-
       developer developer  writer
               \     |     /
                merge-agent
```

**Loosely type-checked.** Each child's `output_type` should match one of the merger's `expected_input_type` slots; this is a soft check today (`check_chain.py` reports missing types as issues but does not enforce slot maps).

**Pitfalls:**
- Merger lacks a defined merge protocol — "just combine them" is not a protocol.
- One child's output type doesn't match any merger slot.
- Children deliver at different times; the merger needs a clear "wait for all" rule.

## Mixed

Real-world chains often combine patterns: a fan-out whose children are themselves linear, or a fan-out followed by a fan-in. `check_chain.py` reports `pattern: "mixed"` and runs all relevant checks. Avoid more than one level of nesting — the cognitive overhead exceeds the parallelism benefit.

## Choosing a pattern

| You have | Use |
|---|---|
| Strict ordering | Linear |
| Independent subtasks, no merger needed | Fan-out only |
| Independent subtasks that must merge | Fan-out + fan-in |
| Both ordering and parallelism | Mixed (sparingly) |
