---
name: quality-checker
description: Validate code quality, run linting, check syntax/types, and execute tests after implementation to ensure code meets project standards.
version: 1.0.0
---

# Quality Checker Skill

## Purpose
Validate code quality, run linting, check syntax/types, and execute tests after implementation to ensure code meets project standards.

## Inputs
- **Implementation Path**: Path to implemented files
- **Project Root**: Root directory of the project
- **Technology Stack**: Languages and frameworks in use
- **Task Context**: What was implemented

## Output
Returns quality check result with:
- Linting results (errors/warnings)
- Type checking results
- Test execution results
- Code style violations
- Overall pass/fail status
- Remediation recommendations

## Quality Check Categories

### 1. Linting
Run appropriate linters based on technology:
- **JavaScript/TypeScript**: ESLint
- **Python**: pylint, flake8, ruff
- **Rust**: clippy
- **CSS**: stylelint

### 2. Formatting
Check code formatting:
- **JavaScript/TypeScript**: Prettier
- **Python**: black, isort
- **Rust**: rustfmt
- **Go**: gofmt

### 3. Type Checking
Verify type safety:
- **TypeScript**: tsc --noEmit
- **Python**: mypy, pyright
- **Rust**: cargo check

### 4. Testing
Execute relevant tests:
- **Unit tests**: Jest, pytest, cargo test
- **Integration tests**: As configured
- **Type tests**: If applicable

### 5. Security
Basic security checks:
- **Dependencies**: Known vulnerabilities
- **Secrets**: No hardcoded secrets
- **SQL**: No obvious injection risks

## Check Process

### Phase 1: Identify Tools
Based on project structure, identify:
- Package manager (npm, yarn, pnpm, pip, cargo)
- Lint configuration (.eslintrc, pyproject.toml, etc.)
- Test framework (package.json scripts, pytest, etc.)
- Type checking setup (tsconfig.json, mypy.ini, etc.)

### Phase 2: Run Checks
Execute checks in order:
1. Linting (fastest, catches syntax errors)
2. Type checking (catches type issues)
3. Tests (validates behavior)
4. Formatting (code style)

### Phase 3: Aggregate Results
Collect all results and categorize:
- **Critical**: Errors that must be fixed
- **Warning**: Issues that should be addressed
- **Info**: Suggestions for improvement

### Phase 4: Generate Report
Create structured report with:
- Summary (pass/fail)
- Detailed results per check
- File-by-file breakdown
- Recommendations for fixes

## Quality Check Output Format

```markdown
# Quality Check Report

## Summary
Status: ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

### Overview
- Files checked: {count}
- Errors: {count}
- Warnings: {count}
- Tests: {passed}/{total}

## Linting Results

### ESLint (JavaScript/TypeScript)
Status: ✅ PASS / ❌ FAIL

```
{eslint output or summary}
```

**Issues Found:**
- ❌ {file}:{line}: {error message}
- ⚠️ {file}:{line}: {warning message}

## Type Checking Results

### TypeScript Compiler
Status: ✅ PASS / ❌ FAIL

```
{tsc output or summary}
```

**Type Errors:**
- ❌ {file}:{line}: {type error}

## Test Results

### Unit Tests (Jest)
Status: ✅ PASS / ❌ FAIL

```
Test Suites: {passed} passed, {total} total
Tests:       {passed} passed, {total} total
Time:        {time}
```

**Failed Tests:**
- ❌ {test suite} › {test name}
  - Expected: {expected}
  - Received: {received}

## Code Formatting

### Prettier
Status: ✅ PASS / ⚠️ NEEDS FORMATTING

**Files needing formatting:**
- {file1}
- {file2}

## Security Scan

### Dependency Check
Status: ✅ PASS / ⚠️ VULNERABILITIES FOUND

**Vulnerabilities:**
- ⚠️ {package}@{version}: {vulnerability description}

### Secrets Scan
Status: ✅ PASS / ❌ SECRETS FOUND

## Recommendations

### Critical (Must Fix)
1. {Critical issue and how to fix}
2. {Another critical issue}

### Warnings (Should Fix)
1. {Warning and suggestion}
2. {Another warning}

### Improvements (Optional)
1. {Code improvement suggestion}
2. {Another suggestion}

## Next Steps
- [ ] Fix all critical errors
- [ ] Address warnings
- [ ] Rerun quality checks
- [ ] Commit changes once all checks pass
```

## Example: TypeScript/React Project

```markdown
# Quality Check Report

## Summary
Status: ⚠️ WARNINGS

### Overview
- Files checked: 3
- Errors: 0
- Warnings: 2
- Tests: 8/8 passed

## Linting Results

### ESLint
Status: ⚠️ WARNINGS

**Issues Found:**
- ⚠️ src/components/RegisterForm.tsx:45: React Hook useEffect has a missing dependency: 'onSuccess'. Either include it or remove the dependency array. (react-hooks/exhaustive-deps)
- ⚠️ src/components/RegisterForm.tsx:67: Unexpected console.log statement. (no-console)

## Type Checking Results

### TypeScript Compiler
Status: ✅ PASS

All types check successfully. No errors found.

## Test Results

### Unit Tests (Jest)
Status: ✅ PASS

```
 PASS  src/components/RegisterForm.test.tsx
  RegisterForm
    ✓ renders email and password fields (45 ms)
    ✓ validates email format (32 ms)
    ✓ validates password complexity (28 ms)
    ✓ shows password strength indicator (15 ms)
    ✓ disables submit during loading (12 ms)
    ✓ displays error messages (18 ms)
    ✓ calls onSuccess after successful registration (25 ms)
    ✓ handles API errors gracefully (22 ms)

Test Suites: 1 passed, 1 total
Tests:       8 passed, 8 total
Time:        2.147 s
```

## Code Formatting

### Prettier
Status: ✅ PASS

All files are properly formatted.

## Security Scan

### Dependency Check
Status: ✅ PASS

No known vulnerabilities in dependencies.

### Secrets Scan
Status: ✅ PASS

No hardcoded secrets detected.

## Recommendations

### Critical (Must Fix)
None - no critical errors!

### Warnings (Should Fix)
1. **Missing dependency in useEffect** (RegisterForm.tsx:45)
   - Add `onSuccess` to dependency array OR wrap in useCallback
   - This can cause stale closure bugs

2. **Remove console.log** (RegisterForm.tsx:67)
   - Remove debug console.log before committing
   - Use proper logging library if needed

### Improvements (Optional)
1. Consider adding more edge case tests (empty form submission, etc.)
2. Add JSDoc comments to component props interface

## Next Steps
- [ ] Fix ESLint warnings (2 warnings)
- [ ] Rerun quality checks
- [ ] Implementation ready for review once warnings fixed
```

## Example: Python Project

```markdown
# Quality Check Report

## Summary
Status: ❌ FAIL

### Overview
- Files checked: 2
- Errors: 3
- Warnings: 1
- Tests: 5/6 passed (1 failure)

## Linting Results

### Ruff
Status: ❌ FAIL

**Issues Found:**
- ❌ src/services/auth_service.py:23: F401 'bcrypt' imported but unused
- ❌ src/services/auth_service.py:45: E501 Line too long (91 > 88 characters)
- ⚠️ src/services/auth_service.py:67: W291 Trailing whitespace

## Type Checking Results

### mypy
Status: ❌ FAIL

**Type Errors:**
- ❌ src/services/auth_service.py:52: error: Argument 1 to "hash_password" has incompatible type "Optional[str]"; expected "str"

## Test Results

### Unit Tests (pytest)
Status: ❌ FAIL

```
============================= test session starts ==============================
collected 6 items

tests/test_auth_service.py::test_register_valid PASSED                   [ 16%]
tests/test_auth_service.py::test_register_invalid_email PASSED           [ 33%]
tests/test_auth_service.py::test_register_weak_password PASSED           [ 50%]
tests/test_auth_service.py::test_login_valid PASSED                      [ 66%]
tests/test_auth_service.py::test_login_invalid_password FAILED           [ 83%]
tests/test_auth_service.py::test_login_nonexistent_email PASSED          [100%]

=================================== FAILURES ===================================
_____________________________ test_login_invalid_password ______________________

    def test_login_invalid_password():
        with pytest.raises(AuthenticationError):
>           auth_service.login("user@example.com", "wrongpassword")
E           Failed: DID NOT RAISE AuthenticationError

tests/test_auth_service.py:42: Failed
============================== 1 failed, 5 passed in 1.23s ==============================
```

**Failed Tests:**
- ❌ test_auth_service.py::test_login_invalid_password
  - Expected AuthenticationError to be raised with invalid password
  - No exception was raised - login method may not be validating passwords correctly

## Code Formatting

### black
Status: ✅ PASS

Code formatting is correct.

## Security Scan

### Dependency Check
Status: ⚠️ VULNERABILITIES FOUND

**Vulnerabilities:**
- ⚠️ cryptography@38.0.0: GHSA-x4qr-2fvf-3mr5 (Moderate severity)
  - Recommendation: Upgrade to cryptography>=39.0.1

### Secrets Scan
Status: ✅ PASS

No hardcoded secrets detected.

## Recommendations

### Critical (Must Fix)
1. **Fix failed test** (test_login_invalid_password)
   - login() method is not raising AuthenticationError for invalid passwords
   - Review password validation logic in auth_service.py

2. **Fix type error** (auth_service.py:52)
   - password parameter can be None but hash_password expects str
   - Add null check or make password required

3. **Remove unused import** (auth_service.py:23)
   - Remove `import bcrypt` if not used, or use it

### Warnings (Should Fix)
1. **Line too long** (auth_service.py:45)
   - Break long line into multiple lines
   - Run: `black src/services/auth_service.py`

2. **Trailing whitespace** (auth_service.py:67)
   - Remove trailing whitespace

3. **Update dependency** (cryptography package)
   - Update to fix security vulnerability
   - Run: `pip install --upgrade cryptography>=39.0.1`

## Next Steps
- [ ] Fix login validation bug (critical)
- [ ] Fix type error (critical)
- [ ] Remove unused import
- [ ] Fix formatting issues
- [ ] Update cryptography dependency
- [ ] Rerun all checks
- [ ] All checks must pass before proceeding
```

## Tool Commands by Project Type

### JavaScript/TypeScript
```bash
# Linting
npx eslint src/**/*.{ts,tsx,js,jsx}

# Type checking
npx tsc --noEmit

# Tests
npm test

# Formatting
npx prettier --check src/**/*.{ts,tsx,js,jsx}
```

### Python
```bash
# Linting
ruff check .
# or
pylint src/

# Type checking
mypy src/

# Tests
pytest

# Formatting
black --check src/
isort --check src/
```

### Rust
```bash
# Linting
cargo clippy

# Type checking
cargo check

# Tests
cargo test

# Formatting
cargo fmt --check
```

## Process Flow

1. **Detect Project Type**
   - Check for package.json (JS/TS)
   - Check for pyproject.toml/requirements.txt (Python)
   - Check for Cargo.toml (Rust)

2. **Find Configuration**
   - ESLint config (.eslintrc.json, .eslintrc.js)
   - TypeScript config (tsconfig.json)
   - Python config (pyproject.toml, setup.cfg)
   - Test config (jest.config.js, pytest.ini)

3. **Run Checks Sequentially**
   - Start with fastest (linting)
   - Stop on critical errors or continue for full report
   - Collect all output

4. **Parse Results**
   - Extract errors, warnings, info
   - Group by file and type
   - Calculate pass/fail status

5. **Generate Report**
   - Format as structured markdown
   - Include actionable recommendations
   - Prioritize fixes (critical → warning → improvement)

6. **Return to Execution Agent**
   - Pass/fail status
   - Detailed report
   - Next steps

## Edge Cases

### No Linter Configured
- Note in report
- Suggest basic linting setup
- Don't fail quality check

### Tests Don't Exist
- Note in report
- Don't fail quality check (tests task may be separate)
- Recommend adding tests

### Tool Not Installed
- Try to detect from package.json
- If tool not available, skip that check
- Note in report what was skipped

### Check Times Out
- Set reasonable timeout (2-5 minutes)
- If exceeds, note in report
- Don't block on slow tests

## Output Interpretation

### Status Levels
- ✅ **PASS**: All critical checks passed, implementation ready
- ⚠️ **WARNINGS**: No critical errors but has warnings, should fix
- ❌ **FAIL**: Critical errors found, must fix before proceeding

### Critical vs. Warnings
- **Critical (Block)**: Type errors, test failures, syntax errors
- **Warning (Don't block)**: Linting warnings, formatting issues, missing comments
- **Info (FYI)**: Code suggestions, optimization opportunities

## Integration with Spec Execution
After specialized agent implements task:
1. spec-execution-agent invokes quality-checker
2. quality-checker runs all checks
3. If FAIL: agent asks implementing agent to fix issues
4. If WARNINGS: agent presents to user with option to fix or proceed
5. If PASS: agent proceeds to requirement-tracer validation