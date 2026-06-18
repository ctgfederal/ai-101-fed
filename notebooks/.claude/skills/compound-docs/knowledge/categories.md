# Solution Categories

Canonical category list. The `category` field in solution frontmatter must be one of these. The category is also the folder name under `.claude/solutions/`.

| Category | When to use |
|---|---|
| `build-errors` | Compilation, linker, bundler, transpiler, dependency-resolution failures. The build itself fails. |
| `test-failures` | Tests fail (or flake) without a build error. Includes flaky tests with confirmed root cause. |
| `runtime-errors` | The code builds and tests pass, but a specific runtime path raises or panics in dev / staging / prod. |
| `performance-issues` | Slow queries, N+1, memory leaks, latency regressions, cache misses, hot loops. Functionally correct, too slow. |
| `database-issues` | Schema migrations, locking, deadlocks, replication lag, index choice, query planner surprises. |
| `security-issues` | CVEs, secret leaks, auth/authz bugs, injection vectors, supply-chain. Must redact actual exploit details. |
| `ui-bugs` | Visual / interaction defects: layout, focus, accessibility, browser compat, mobile-only failures. |
| `integration-issues` | Failures at trust boundaries: 3rd-party API, webhook, queue, cross-service contract drift. |
| `logic-errors` | Incorrect business logic with no error: wrong totals, wrong filters, wrong state transitions. |
| `configuration-fixes` | Env vars, feature flags, infrastructure config, IAM, networking — all "the code is fine, the config wasn't". |
| `deployment-issues` | CI/CD, container, image, k8s manifest, rollout, rollback, staging↔prod drift. |
| `tooling-issues` | Editor, language server, formatter, lint, dev container — anything blocking developer flow but not the code itself. |

## Adding a new category
If nothing fits, **stop** and ask the user before inventing. Adding a category is a cross-cutting decision because every search pattern (`/brainstorm`, `/build`, `/specify`, `/review`) walks these folders. New categories require a one-line description added here in the same change.

## What is NOT a category
- A specific technology (`postgres`, `react`) — that's a `tag`.
- A specific module (`UserService`) — that's the `module` field.
- A severity level (`critical`) — that's `severity`.
