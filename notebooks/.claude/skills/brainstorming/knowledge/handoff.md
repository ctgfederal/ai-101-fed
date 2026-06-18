# Handoff Options

After validating the captured brainstorm, ask the user via `AskUserQuestion`:

> "Brainstorm captured at `<path>`. What next?"

| Option | When to recommend | What happens next |
|---|---|---|
| `/build` (Recommended for most) | Vision is clear, design tradeoffs await | Walks every design decision interactively, ranks by simplicity → security → scalability → compliance |
| `/specify` | Vision + design already settled | Generates PRD/SDD/PLAN; auto-reads the brainstorm |
| Refine further | Open questions remain or vision feels thin | Re-enter brainstorm, ask remaining questions |
| Done for now | User wants to step away | File is saved with `status: complete`; resume later by re-running `/brainstorm <topic>` |

## When to push back

- If `Scope: Out` is empty, push back: "Let's name what's out before we move on."
- If `Open Questions` has unresolved items that block design, push back: "Answer these first or `/build` will stall on them."
- If the user wants `/specify` but the brainstorm has design decisions in `Principles`, recommend `/build` first.
