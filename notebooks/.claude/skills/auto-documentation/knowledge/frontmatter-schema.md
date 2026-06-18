# Auto-Doc Frontmatter Schema

Authoritative spec for the YAML frontmatter on every auto-doc file. `validate_output.py` enforces this; the LLM should follow it when assembling the payload.

## Required fields

| Field | Type | Format / rules |
|---|---|---|
| `title` | string | 8–120 chars. Descriptive, naming the *rule/pattern/contract*: "Admins can edit any user post", not "auth thing". Quote in YAML. |
| `category` | string | Exactly one of `business-rule`, `technical-pattern`, `service-interface`, `domain-rule`. Lowercase, kebab. |
| `date` | date | `YYYY-MM-DD`. The date the insight was *captured*. |
| `tags` | list[string] | 2–8 items. Lowercase. Tag the *technology* (`stripe`, `rails`), the *layer* (`api`, `worker`, `webhook`), and the *concept* (`permissions`, `caching`, `idempotency`). No spaces — use hyphens. |
| `scope` | string | The affected area: a class, module, endpoint, route, or path. Specific: `UserPostController#update`, `POST /v1/charges`, `BackgroundJobs::Mailer`. Free-form but identifiable. |
| `source` | string | Where the insight came from: `discovery during /implement on SPEC-NNN`, `Stripe API changelog 2026-05-01`, `pair session with @alex 2026-05-08`. Provenance matters for re-verification. |

## Optional fields

| Field | Type | Format / rules |
|---|---|---|
| `version` | string | If the insight applies to a specific version of an external service or internal module: `"stripe-api/2024-04-10"`, `"app@v3.2"`. |
| `expires_at` | date | If the insight is known to be valid only until a specific date (e.g., a vendor contract that ends). `YYYY-MM-DD`. |
| `related_specs` | list[string] | Spec IDs that produced this insight: `["SPEC-2026-014"]`. |

## Validation rules

1. YAML must parse cleanly (no embedded tabs, no smart quotes).
2. `date` is in the past or today — never the future.
3. `tags` contains no duplicates, all lowercase, no whitespace inside a tag.
4. `category` is one of the four canonical values.
5. No required field is the empty string.

## Common mistakes

- **`tags: ["doc", "info", "rule"]`** — these are not tags, they're noise. Tag the technology, layer, and concept.
- **`scope: "the codebase"`** — useless. Pick the originating class, route, or module.
- **`source: "I just figured it out"`** — provenance must be re-verifiable. Cite the file, PR, conversation, or external doc.
- **`title: "auth"`** — see above. Be searchable.
- **`category: "other"`** — there are four. If nothing fits, the insight likely belongs in a different skill.
