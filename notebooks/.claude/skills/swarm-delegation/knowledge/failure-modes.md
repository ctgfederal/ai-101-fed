# Failure Modes

Six failure modes cover almost every broken delegation. The schema and chain validators catch most of them; the rest require human judgment.

## 1. Lost context

**Symptom:** Receiving agent re-reads or re-derives information the sender already had.

**Cause:** `context_files` was empty or the `task` assumed shared state that does not exist.

**Catch:** `validate_handoff.py` will not flag empty `context_files` (that's legal), but missing context manifests as a vague task. Heuristic: if the task is shorter than 80 chars and `context_files` is empty, ask the sender what the receiver actually needs.

## 2. Type mismatch

**Symptom:** Agent A returns a unified diff; agent B expects a list of test names.

**Cause:** `output_type` and `expected_input_type` are not set, or they don't match.

**Catch:** `check_chain.py` flags `type mismatch step[i].output_type=X != step[i+1].expected_input_type=Y` deterministically.

## 3. Cycle

**Symptom:** Chain runs forever (or until a token cap), or loops between two agents redoing the same work.

**Cause:** A self-handoff (`from_agent == to_agent`) or a directed cycle in the chain graph.

**Catch:** `validate_handoff.py` flags self-handoffs. `check_chain.py` runs DFS cycle detection on the full handoff graph.

## 4. Deadline gap

**Symptom:** Step 3 was supposed to finish before step 4 needed its output, but step 3 ran long and step 4 produced nothing useful.

**Cause:** No explicit `deadline` field, or deadlines that don't compose (step 1 deadline = "T+10min", step 2 deadline = "T+5min").

**Catch:** Not mechanically validated today. Surface in human review: when scheduling a chain, deadlines must monotonically increase or each step needs a hard timeout.

## 5. Ambiguous return

**Symptom:** Caller can't merge children's outputs because each returned a different shape.

**Cause:** `return_format` is too vague ("the result"), or each child interpreted "the result" differently.

**Catch:** `validate_handoff.py` requires `return_format` to be non-empty, but does not enforce schema. Heuristic: prefer JSON shapes ("`{count, items}`") over prose ("a summary").

## 6. Undefined merge

**Symptom:** Fan-in step can't decide what to do when child outputs disagree, overlap, or are partial.

**Cause:** The merger's `task` doesn't specify a merge protocol (precedence order, conflict resolution, partial-result handling).

**Catch:** Not mechanically validated. When you see fan-in, the merger's `task` field should explicitly answer: "what do you do if two children write to the same key?"

## Rule of thumb

If `validate_handoff.py` exits 0 and `check_chain.py` exits 0, you've eliminated 1, 2, 3, and 5. Failure modes 4 and 6 are human-judgment checks on top.
