# Auto-Documentation Categories

Exactly four categories. The `category` field in auto-doc frontmatter must be one of these. The category is also the folder name under `.claude/docs/auto/`.

| Category | What it is | When to use |
|---|---|---|
| `business-rule` | Domain logic the business cares about | Permission checks, pricing rules, workflow states, validation that reflects policy (not technical constraints). "Non-admins can only edit their own posts." |
| `technical-pattern` | *How we build things* — reusable architectural / code patterns | Caching strategy, error-handling convention, repository pattern, retry wrapper, the way we structure background jobs. Not domain logic. |
| `service-interface` | Third-party API or webhook contracts and the way we integrate them | Stripe webhook timing, Auth0 token refresh, internal RPC contract drift, Twilio rate limits. The *contract*, not our wrapper. |
| `domain-rule` | Invariants and entity behaviors specific to the modeled domain | "An `Order` cannot ship before paid." "A `User` cannot reference itself as parent." Business-meaningful invariants that constrain entity state. |

## How to choose

A useful disambiguation:

- If a non-engineer would care → `business-rule` or `domain-rule`.
- If only engineers would care → `technical-pattern` or `service-interface`.
- If it describes *what is true about an entity* → `domain-rule`.
- If it describes *what users are allowed to do* → `business-rule`.
- If it describes *how our code is shaped* → `technical-pattern`.
- If it describes *how we talk to outside systems* → `service-interface`.

## Examples by category

### business-rule
- `admin-edit-policy.md` — Admins can edit any user post.
- `pro-trial-extension.md` — Pro trials can be extended once, max 14 days.
- `refund-window.md` — Refunds allowed within 30 days of purchase.

### technical-pattern
- `repository-pattern.md` — Data access goes through repository classes, never direct ORM in controllers.
- `error-envelope.md` — All API errors return `{error, code, retry_after}`.
- `idempotency-keys.md` — POST endpoints accept `Idempotency-Key` header.

### service-interface
- `stripe-webhook-timing.md` — Stripe retries webhooks for 3 days with exponential backoff; we must be idempotent.
- `auth0-token-refresh.md` — Refresh tokens rotate; old token invalidates after one use.
- `sendgrid-event-batching.md` — Sendgrid batches events up to 30s; expect duplicates.

### domain-rule
- `order-paid-before-ship.md` — `Order.ship!` raises if `paid_at` is nil.
- `user-no-self-parent.md` — `User.parent_id` cannot equal `User.id`.
- `cart-single-currency.md` — All `LineItem`s in a `Cart` share one currency.

## What is NOT a category

- A specific technology (`postgres`, `stripe`) — that's a `tag`.
- A specific module (`UserService`) — that's the `scope` field.
- A severity or priority — auto-docs do not carry severity.

## Adding a new category

There are four. Adding a fifth is a structural change because every search pattern walks these folders. **Stop and ask the user.** A new category requires updating this file, `categorize.py`, and `validate_output.py` in the same change.
