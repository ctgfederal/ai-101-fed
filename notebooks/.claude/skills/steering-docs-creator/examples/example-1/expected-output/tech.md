# Tech Steering

> Stable technical context referenced by feature specs in `.claude/specs/`.
> Downstream consumers: `spec-sdd-generator` (tech stack, conventions).

## Tech Stack


> Languages, frameworks, runtimes. Cite exact versions where they matter.

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| Language | TypeScript | 5.4 | strict mode |
| Framework | Next.js | 14 | App Router |
| Database | PostgreSQL | 16 | hosted on Neon |
| Auth | Supabase Auth | 2.x | OAuth + magic link |
| Styling | Tailwind | 3.4 | with @tailwindcss/forms |

## Conventions

> Code-style, naming, and review conventions every feature must follow.

### Naming

| Item | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Hooks | `useCamelCase` | `useUserProfile.ts` |
| Utilities | camelCase | `formatDate.ts` |
| DB tables | snake_case, plural | `user_profiles` |

### Style

- Linter: [NEEDS CLARIFICATION: e.g., ESLint with X config]
- Formatter: [e.g., Prettier]
- Type-check: [e.g., `tsc --noEmit`]

### Review

- All PRs require [NEEDS CLARIFICATION: number] approvers.
- All PRs must pass CI before merge.

## Library Choices

> Standard libraries that every feature should reuse rather than reinvent.

| Purpose | Library | Why |
|---------|---------|-----|
| HTTP client | [NEEDS CLARIFICATION] | [Reason] |
| Validation | [e.g., Zod] | [Reason] |
| Logging | [e.g., pino] | [Reason] |
| Testing | [e.g., Vitest] | [Reason] |

## Build & CI

> Canonical commands; the CI gate; deploy targets.

### Commands

```bash
# Dev
[NEEDS CLARIFICATION: e.g., npm run dev]

# Test
[e.g., npm test]

# Lint
[e.g., npm run lint]

# Type-check
[e.g., npm run typecheck]

# Build
[e.g., npm run build]
```

### CI Gates

| Gate | Threshold |
|------|-----------|
| Line coverage | ≥80% |
| Lint | 0 errors |
| Type errors | 0 |
| Critical vulns | 0 |

## Observability

> How features emit logs, metrics, traces.

| Signal | Tool | Convention |
|--------|------|------------|
| Logs | [NEEDS CLARIFICATION] | Structured JSON |
| Metrics | [e.g., Prometheus] | Per-endpoint p95 |
| Traces | [e.g., OpenTelemetry] | Request-scoped |
| Errors | [e.g., Sentry] | Captured server + client |
