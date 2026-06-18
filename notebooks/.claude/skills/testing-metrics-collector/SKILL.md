---
name: metrics-collector
description: Collect comprehensive quality metrics from all available tools (coverage, linting, complexity, security, performance, etc.).
version: 1.0.0
---

# Metrics Collector Skill

## Purpose
Collect comprehensive quality metrics from all available tools (coverage, linting, complexity, security, performance, etc.).

## Inputs
- Project files and configuration
- Test framework setup
- Linting configuration
- Build configuration

## Output
Structured metrics data:
```json
{
  "coverage": { "line": 73.5, "branch": 68.2, "function": 81.3 },
  "complexity": { "max_per_function": 15, "avg_per_file": 6.2 },
  "linting": { "errors": 0, "warnings": 8 },
  "security": { "critical": 0, "high": 0, "medium": 1 },
  "performance": { "bundle_size_kb": 487, "build_time_s": 45 },
  "duplication": { "percentage": 2.1 },
  "documentation": { "percentage": 68.5 }
}
```

## Process
1. Run coverage: `npm run test -- --coverage`
2. Run linting: `npm run lint`
3. Run complexity analysis: `npx complexity-report src/`
4. Run security audit: `npm audit`
5. Collect build metrics: `npm run build`
6. Check duplication: `npx jscpd src/`
7. Aggregate all metrics into structured format

## Tools by Language

### JavaScript/TypeScript
- Coverage: Jest, Vitest (c8)
- Linting: ESLint
- Complexity: complexity-report, ts-complexity
- Security: npm audit, snyk
- Duplication: jscpd

### Python
- Coverage: pytest-cov
- Linting: pylint, flake8, ruff
- Complexity: radon
- Security: pip-audit, safety, bandit
- Duplication: radon (raw metrics)

## Remember
- Gracefully handle missing tools
- Return null for unavailable metrics
- Document which tools were used
- Cache results to avoid re-running
