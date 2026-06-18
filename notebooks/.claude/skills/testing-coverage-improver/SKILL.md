---
name: coverage-improver
description: Generate actionable improvement plans with phased approach, effort estimates, and test stubs for closing coverage gaps.
version: 1.0.0
---

# Coverage Improver Skill

## Purpose
Generate actionable improvement plans with phased approach, effort estimates, and test stubs for closing coverage gaps.

## Inputs
- Coverage gaps from coverage-gap-finder
- Target coverage threshold
- Test strategy document

## Output
Phased improvement plan with:
- Tasks organized by priority
- Effort estimates
- Expected coverage increase
- Test code stubs
- Success criteria

## Process
1. Group gaps by priority (P0, P1, P2)
2. Estimate effort for each gap
3. Calculate expected coverage increase
4. Create phased plan
5. Generate test stubs for high-priority gaps

## Output Template

```markdown
## Coverage Improvement Plan

**Current Coverage**: 73.5%
**Target Coverage**: 85%
**Gap**: 11.5 percentage points

### Phase 1: Critical Gaps (Est: 6 hours)
Target: 73.5% → 85%

#### Task 1.1: Test Authentication Module (2h)
**Files**: src/auth/password.ts, src/auth/session.ts
**Current**: 45.2% | **Target**: 95%
**Expected Increase**: +8 percentage points
**Tests to Add**: 8 unit tests

**Stub**:
```typescript
describe('Password Hashing', () => {
  it('should hash password using bcrypt', async () => {
    // TODO: Implement test
  });
  it('should generate unique salt', async () => {
    // TODO: Implement test
  });
});
```

#### Task 1.2: Test Payment Validation (3h)
**Files**: src/payments/validate.ts
**Current**: 12.5% | **Target**: 100%
**Expected Increase**: +2.5 percentage points
**Tests to Add**: 12 unit + 3 integration tests

### Phase 2: High-Impact Gaps (Est: 4 hours)
Target: 85% → 88%
[Details...]

### Phase 3: Polish (Est: 2 hours)
Target: 88% → 90%
[Details...]

**Total Effort**: 12 hours
**Final Coverage**: 90%
```

## Remember
- Provide concrete, actionable tasks
- Estimate effort realistically
- Generate test stubs to guide implementation
- Phase by priority and impact
