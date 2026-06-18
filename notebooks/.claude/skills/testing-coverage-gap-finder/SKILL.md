---
name: coverage-gap-finder
description: Identify untested code paths, prioritize by business impact, and map gaps to requirements for targeted improvement.
version: 1.0.0
---

# Coverage Gap Finder Skill

## Purpose
Identify untested code paths, prioritize by business impact, and map gaps to requirements for targeted improvement.

## Inputs
- Coverage report data
- Requirements document
- Source code files
- Complexity metrics

## Output
Prioritized list of coverage gaps with:
- Uncovered lines/functions
- Business impact assessment
- Mapped to requirements
- Recommended test cases

## Process
1. Parse coverage report for uncovered lines
2. Read source files to understand uncovered code
3. Categorize by criticality:
   - Critical: Auth, payments, security, data integrity
   - High: Business logic, error handling
   - Medium: UI, formatting, utilities
   - Low: Getters, simple wrappers
4. Map to requirements (if available)
5. Prioritize by impact

## Output Template

```markdown
## Critical Coverage Gaps (Priority: P0)

### 1. Password Hashing - UNCOVERED
**File**: src/auth/password.ts
**Lines**: 45-52, 67-71
**Coverage**: 0%
**Impact**: Security vulnerability - passwords not being hashed
**Requirement**: REQ-002 (Secure password storage)
**Recommended Tests**:
- Test bcrypt hashing
- Test salt generation
- Test hash verification
- Test empty password handling

### 2. Payment Validation - PARTIAL COVERAGE
**File**: src/payments/validate.ts
**Lines**: 23-35 (amount validation), 89-94 (fraud detection)
**Coverage**: 12.5%
**Impact**: Financial risk - invalid transactions may be processed
**Requirement**: REQ-015 (Payment validation)
**Recommended Tests**:
- Test amount min/max validation
- Test currency validation
- Test fraud detection rules
```

## Remember
- Prioritize by business impact, not just %
- Focus on critical paths first
- Map to requirements for traceability
- Provide concrete test recommendations
