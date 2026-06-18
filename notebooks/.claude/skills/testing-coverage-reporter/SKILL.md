---
name: coverage-reporter
description: Parse and present test coverage reports with clear metrics, visualizations, and gap identification.
version: 1.0.0
---

# Coverage Reporter Skill

## Purpose
Parse and present test coverage reports with clear metrics, visualizations, and gap identification.

## Inputs
- Coverage report files (lcov, JSON, XML, HTML)
- Coverage thresholds from config
- Previous coverage data for trends

## Output
Coverage summary with:
- Overall metrics (line, branch, function, statement %)
- Per-file/module breakdown
- Files with low coverage highlighted
- Trend analysis if historical data available

## Process
1. Locate coverage report (coverage/lcov-report/index.html, htmlcov/)
2. Parse coverage data
3. Extract metrics
4. Identify low-coverage files
5. Generate summary table
6. Compare to thresholds

## Output Template

```markdown
## Coverage Summary

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Line Coverage | 73.5% | 80% | ❌ -6.5% |
| Branch Coverage | 68.2% | 75% | ❌ -6.8% |
| Function Coverage | 81.3% | 85% | ⚠️ -3.7% |
| Statement Coverage | 72.8% | 80% | ❌ -7.2% |

## Coverage by Module

| Module | Lines | Branches | Functions |
|--------|-------|----------|-----------|
| src/auth/ | 45.2% 🚨 | 38.5% | 50.0% |
| src/api/ | 78.3% ⚠️ | 71.2% | 82.1% |
| src/utils/ | 92.1% ✅ | 88.7% | 95.2% |

## Low Coverage Files (< 70%)
- src/auth/password.ts: 45.2%
- src/auth/session.ts: 52.8%
- src/payments/validate.ts: 12.5%
```

## Remember
- Highlight critical gaps
- Compare to historical data
- Focus on actionable insights
- Use visual indicators (✅❌⚠️)
