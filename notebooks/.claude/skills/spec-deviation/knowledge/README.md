# spec-deviation — knowledge

| File | Contents | When to load |
|---|---|---|
| `deviation-schema.md` | Required and optional fields; allowed values for `reason_category` and `status`; ID formats. | Building or validating a deviation payload; debugging a payload-rejection error. |
| `approval-workflow.md` | The `proposed → approved/rejected` lifecycle, who approves what, and the rule that rejected deviations are kept (not deleted). | Flipping status; explaining the workflow to the user; resolving "what happens after proposed?". |
| `when-to-deviate.md` | Guardrails: what counts as a forced deviation vs. what should stay a TODO or trigger a `/build` re-run. | Before logging any deviation; if the user is unsure whether something needs a deviation. |
