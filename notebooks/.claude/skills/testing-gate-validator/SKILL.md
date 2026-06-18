---
name: gate-validator
description: Validate collected metrics against quality gate thresholds, calculate scores, and generate pass/fail status with detailed violations.
version: 1.0.0
---

# Gate Validator Skill

## Purpose
Validate collected metrics against quality gate thresholds, calculate scores, and generate pass/fail status with detailed violations.

## Inputs
- Metrics from metrics-collector
- Quality gate thresholds (.claude/quality-gates.json or defaults)
- Enforcement mode (check vs enforce)

## Output
Validation results with:
- Pass/fail status for each gate
- Quality score (0-100)
- Grade (A-F)
- Detailed violations
- Recommended actions

## Process
1. Load thresholds from config or defaults
2. Compare each metric to threshold
3. Calculate pass/fail/warning status
4. Calculate weighted quality score
5. Generate violations list
6. Provide remediation recommendations

## Output Template

```markdown
## Quality Gate Results

| Gate | Current | Threshold | Status |
|------|---------|-----------|--------|
| Line Coverage | 73.5% | ≥80% | ❌ FAIL |
| Branch Coverage | 68.2% | ≥75% | ❌ FAIL |
| Complexity | 15 max | ≤10 | ❌ FAIL |
| Security (Critical) | 0 | 0 | ✅ PASS |
| Linting Errors | 0 | 0 | ✅ PASS |
| Bundle Size | 487 KB | ≤500 KB | ✅ PASS |

**Quality Score**: 87/100 (B - Good)
**Overall Status**: ❌ FAIL (3 gates failed)

## Violations

### ❌ Line Coverage Below Threshold
**Current**: 73.5% | **Required**: 80%
**Gap**: -6.5 percentage points
**Action**: Run `/coverage improve` to generate improvement plan

### ❌ Cyclomatic Complexity Exceeded
**Functions over limit**:
- src/payments/process.ts:processPayment() - 15 (limit: 10)
- src/auth/validate.ts:validateUser() - 12 (limit: 10)
**Action**: Refactor complex functions into smaller units
```

## Quality Score Calculation
```
Score = Σ(category_score * weight)

Weights:
- Coverage: 25%
- Complexity: 15%
- Linting: 15%
- Security: 20%
- Performance: 10%
- Maintainability: 15%
```

## Remember
- Security gates (critical/high) are non-negotiable
- Provide actionable violation details
- Calculate score consistently
- Support both check and enforce modes
