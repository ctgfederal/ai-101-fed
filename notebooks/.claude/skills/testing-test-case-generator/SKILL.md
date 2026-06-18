---
name: test-case-generator
description: Generate comprehensive test cases from requirements and acceptance criteria. Map each test case to specific requirements, covering happy paths, edge cases, and error scenarios.
version: 1.0.0
---

# Test Case Generator Skill

## Purpose
Generate comprehensive test cases from requirements and acceptance criteria. Map each test case to specific requirements, covering happy paths, edge cases, and error scenarios.

## Inputs
- **Requirements Document**: `.claude/specs/{feature_name}/requirements.md` with EARS-format acceptance criteria
- **Design Document**: Component and module specifications
- **Risk Analysis**: Critical paths and security-sensitive operations

## Output
Detailed test cases including:
- Test case descriptions
- Mapping to requirements/acceptance criteria
- Priority (P0/P1/P2)
- Test data needed
- Expected results
- Coverage analysis

## Test Case Structure

```markdown
### TC-{NUMBER}: {Test Case Name}
**Requirement**: {REQ-ID} - {Requirement description}
**Priority**: {P0|P1|P2}
**Type**: {unit|integration|e2e}
**Description**: {What this test validates}

**Preconditions**:
- {Setup required before test}

**Test Steps**:
1. {Action 1}
2. {Action 2}
3. {Action 3}

**Expected Result**:
- {What should happen}

**Test Data**:
- {Data needed for test}
```

## Process

### Step 1: Extract Acceptance Criteria
Parse requirements.md and identify all EARS-format criteria:
- WHEN events → Event-driven test cases
- IF conditions → Conditional test cases
- WHILE states → State-based test cases
- System SHALL → Functional test cases

### Step 2: Generate Happy Path Tests
For each user story, create test for successful scenario:
```markdown
### TC-001: User Can Register with Valid Email and Password
**Requirement**: REQ-001.1 - Email Registration
**Priority**: P0
**Type**: integration
**Description**: Verify user can successfully register with valid credentials

**Preconditions**:
- Email not already registered
- Registration endpoint available

**Test Steps**:
1. Navigate to registration page
2. Enter valid email (test@example.com)
3. Enter valid password (SecurePass123!)
4. Submit registration form

**Expected Result**:
- User account created in database
- Verification email sent
- User redirected to "Check your email" page

**Test Data**:
- email: "test@example.com"
- password: "SecurePass123!"
```

### Step 3: Generate Edge Case Tests
For each acceptance criterion, identify edge cases:
- Boundary values (min, max, zero, one)
- Empty/null inputs
- Special characters
- Concurrent operations
- Timeout scenarios

```markdown
### TC-002: Registration Rejects Invalid Email Format
**Requirement**: REQ-001.1 - Email Registration (AC-2)
**Priority**: P1
**Type**: unit
**Description**: Verify system validates email format before registration

**Test Steps**:
1. Enter invalid email formats:
   - "notanemail"
   - "@example.com"
   - "test@"
   - "test..double@example.com"
2. Submit form

**Expected Result**:
- Validation error displayed
- Account not created
- Error message: "Invalid email format"
```

### Step 4: Generate Error Scenario Tests
For each failure condition, create test:
- Invalid inputs
- Unauthorized access
- Resource not found
- System errors
- Network failures

```markdown
### TC-003: Registration Fails for Existing Email
**Requirement**: REQ-001.1 - Email Registration (AC-4)
**Priority**: P0
**Type**: integration
**Description**: Verify system prevents duplicate email registration

**Preconditions**:
- User with email "existing@example.com" already registered

**Test Steps**:
1. Attempt to register with "existing@example.com"
2. Enter valid password
3. Submit form

**Expected Result**:
- Registration fails
- Error message: "Email already registered"
- User redirected to login page link
- No duplicate account created
```

### Step 5: Map to Test Pyramid
Assign each test case to appropriate layer:
- **Unit**: Tests for single functions, validation logic, utilities
- **Integration**: Tests for API endpoints, database operations, module interactions
- **E2E**: Tests for complete user workflows

### Step 6: Prioritize Test Cases
Assign priority based on:
- **P0 (Critical)**: Core functionality, security, data integrity
- **P1 (High)**: Important features, common user paths
- **P2 (Medium)**: Nice-to-have, rare scenarios

## Output Template

```markdown
## Test Cases

### Requirement: REQ-001 - User Registration

#### Happy Path Tests

##### TC-001: Successful Registration with Valid Data
**Requirement**: REQ-001.1 (AC-1)
**Priority**: P0
**Type**: integration
[Full test case details...]

#### Edge Case Tests

##### TC-002: Email Validation
**Requirement**: REQ-001.1 (AC-2)
**Priority**: P1
**Type**: unit
[Full test case details...]

##### TC-003: Password Strength Requirements
**Requirement**: REQ-001.1 (AC-3)
**Priority**: P0
**Type**: unit
[Full test case details...]

#### Error Scenario Tests

##### TC-004: Duplicate Email Prevention
**Requirement**: REQ-001.1 (AC-4)
**Priority**: P0
**Type**: integration
[Full test case details...]

##### TC-005: Email Service Unavailable
**Requirement**: REQ-001.1 (AC-5)
**Priority**: P1
**Type**: integration
[Full test case details...]

### Summary
- Total Test Cases: 15
- P0 (Critical): 8
- P1 (High): 5
- P2 (Medium): 2
- Unit Tests: 7
- Integration Tests: 6
- E2E Tests: 2
```

## Coverage Analysis
Map test cases back to requirements:
```markdown
## Requirements Coverage

| Requirement | Test Cases | Coverage |
|-------------|------------|----------|
| REQ-001.1 Email Registration | TC-001, TC-002, TC-003, TC-004, TC-005 | 100% |
| REQ-001.2 Email Verification | TC-006, TC-007, TC-008 | 100% |
| REQ-002.1 User Login | TC-009, TC-010, TC-011, TC-012 | 100% |
| REQ-002.2 Password Reset | TC-013, TC-014, TC-015 | 100% |

**Overall Coverage**: 100% of acceptance criteria have test cases
```

## Best Practices
- Map every acceptance criterion to at least one test case
- Include both positive and negative test cases
- Test boundaries and edge cases
- Consider security implications
- Think about performance and load
- Document clear expected results
- Make test cases executable (specific steps)

## Remember
- Test cases should be traceable to requirements
- Every acceptance criterion must have coverage
- Prioritize based on risk and business impact
- Balance thoroughness with practicality
- Test cases should be clear enough for anyone to execute
