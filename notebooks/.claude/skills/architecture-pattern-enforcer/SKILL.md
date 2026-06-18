---
name: pattern-enforcer
description: Analyze code and designs for compliance with established architectural patterns and conventions.
version: 1.0.0
---

# Pattern Enforcer Skill

## Purpose
Analyze code and designs for compliance with established architectural patterns and conventions.

## Inputs
- **Code/Design to Review**: File paths or design document
- **Pattern Categories**: Which patterns to check (api, data-access, state, error, security, testing)
- **Established Patterns**: Path to pattern documentation (default: `architecture/patterns/`)

## Output
Pattern compliance report with:
- Violations found
- Pattern recommendations
- Severity (critical, warning, suggestion)
- Code examples of correct patterns

## Pattern Categories

### 1. API Design Patterns
**Location**: `architecture/patterns/api-patterns.md`

**Checks**:
- RESTful URL structure
- HTTP method usage
- Response format consistency
- Error response format
- Pagination pattern
- Filtering/sorting pattern

**Violations**:
```typescript
// ❌ Violation: Non-RESTful URL
POST /api/getUserById

// ✅ Correct: RESTful resource URL
GET /api/users/{id}
```

### 2. Data Access Patterns
**Location**: `architecture/patterns/data-access-patterns.md`

**Checks**:
- Repository pattern usage
- DAO vs Active Record
- Query optimization
- N+1 query prevention
- Transaction management
- Connection pooling

**Violations**:
```typescript
// ❌ Violation: Direct database access in controller
controller.getUser = async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = ?', [req.params.id]);
};

// ✅ Correct: Repository pattern
controller.getUser = async (req, res) => {
  const user = await userRepository.findById(req.params.id);
};
```

### 3. State Management Patterns
**Location**: `architecture/patterns/state-management-patterns.md`

**Checks**:
- Global state vs local state
- State update patterns
- Side effect handling
- State immutability
- Derived state computation

**Violations**:
```typescript
// ❌ Violation: Direct state mutation
state.users.push(newUser);

// ✅ Correct: Immutable update
setState({ users: [...state.users, newUser] });
```

### 4. Error Handling Patterns
**Location**: `architecture/patterns/error-handling-patterns.md`

**Checks**:
- Custom error classes
- Error propagation
- Error logging
- User-facing messages
- HTTP status codes

**Violations**:
```typescript
// ❌ Violation: Generic error throw
throw new Error('Something went wrong');

// ✅ Correct: Custom error with context
throw new ValidationError('Invalid email format', { field: 'email' });
```

### 5. Security Patterns
**Location**: `architecture/patterns/security-patterns.md`

**Checks**:
- Input validation
- SQL injection prevention
- XSS prevention
- Authentication patterns
- Authorization patterns
- Secret management

**Violations**:
```typescript
// ❌ Violation: SQL injection risk
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`);

// ✅ Correct: Parameterized query
db.query('SELECT * FROM users WHERE id = ?', [req.params.id]);
```

### 6. Testing Patterns
**Location**: `architecture/patterns/testing-patterns.md`

**Checks**:
- Test structure (AAA pattern)
- Mock vs stub usage
- Test data factories
- Test naming conventions
- Test isolation

**Violations**:
```typescript
// ❌ Violation: Unclear test name
test('test1', () => { ... });

// ✅ Correct: Descriptive test name
test('should return 404 when user not found', () => { ... });
```

## Analysis Process

### Step 1: Load Established Patterns
Read pattern documents from `architecture/patterns/`

### Step 2: Parse Code/Design
- Identify patterns being used
- Extract code snippets for analysis
- Note design decisions

### Step 3: Match Against Established Patterns
For each pattern category:
- Check if pattern is being followed
- Identify deviations
- Assess severity

### Step 4: Generate Report

```markdown
# Pattern Compliance Report

## Summary
- ✅ Compliant: 15 patterns
- ⚠️ Warnings: 3 patterns
- ❌ Violations: 2 patterns

## Critical Violations

### API-001: Non-RESTful URL Structure
**Location**: `src/controllers/user.controller.ts:45`
**Severity**: Critical

**Issue**: Using RPC-style URL instead of RESTful resource URL

**Current**:
```typescript
POST /api/getUserById
```

**Should Be**:
```typescript
GET /api/users/{id}
```

**Pattern**: API Design > RESTful URLs
**Reference**: `architecture/patterns/api-patterns.md#restful-urls`

## Warnings

### DATA-003: Missing Transaction
**Location**: `src/services/order.service.ts:78`
**Severity**: Warning

**Issue**: Multiple database operations without transaction

**Recommendation**: Wrap in transaction for consistency

**Pattern**: Data Access > Transaction Management
**Reference**: `architecture/patterns/data-access-patterns.md#transactions`

## Suggestions

### TEST-002: Test Name Could Be More Descriptive
**Location**: `tests/user.test.ts:12`
**Severity**: Suggestion

**Current**: `test('creates user', ...)`
**Suggested**: `test('should create user with valid email and return 201', ...)`

**Pattern**: Testing > Test Naming
**Reference**: `architecture/patterns/testing-patterns.md#naming`

## Compliant Patterns

✅ Error handling follows custom error class pattern
✅ Repository pattern consistently applied
✅ State management uses immutable updates
```

### Step 5: Provide Guidance
- Link to pattern documentation
- Show code examples
- Suggest corrections

## Severity Levels

### Critical (❌)
- Security vulnerabilities
- Data integrity risks
- Major architectural violations
- **Action**: Must fix before merging

### Warning (⚠️)
- Performance concerns
- Inconsistency with patterns
- Maintainability issues
- **Action**: Should fix, can be tracked as tech debt

### Suggestion (💡)
- Style improvements
- Better practices available
- Minor inconsistencies
- **Action**: Optional improvement

## Pattern Documentation Format

Each pattern document should contain:

```markdown
# {Category} Patterns

## Pattern 1: {Name}

### Intent
What problem does this solve?

### Implementation
How to implement correctly

### Example
```code
// Correct implementation
```

### Anti-Patterns
```code
// Wrong implementation
```

### When to Use
When is this pattern appropriate?

### When Not to Use
When should you avoid this pattern?

### Related Patterns
- Pattern 2
- Pattern 3
```

## Creating New Pattern Docs

When a new pattern is established:

1. **Document in appropriate file**:
   - `api-patterns.md` for API design
   - `data-access-patterns.md` for database
   - `state-management-patterns.md` for state
   - `error-handling-patterns.md` for errors
   - `security-patterns.md` for security
   - `testing-patterns.md` for tests

2. **Include**:
   - Pattern name and intent
   - Correct implementation example
   - Anti-pattern examples
   - When to use/not use
   - Related patterns

3. **Update pattern-enforcer skill** to check for new pattern

## Integration with Code Review

During code review, pattern-enforcer runs automatically:

1. spec-execution-agent completes task
2. code-review-orchestrator runs checks
3. pattern-enforcer analyzes code
4. Violations added to review feedback
5. Developer addresses violations
6. Re-check before approval

## Metrics Tracked

- Pattern violations per review
- Violation trends over time
- Most common violations
- Compliance rate by pattern category

## Remember

Patterns exist to:
- ✅ Maintain consistency
- ✅ Reduce cognitive load
- ✅ Prevent common mistakes
- ✅ Enable maintainability

But patterns should serve the team, not constrain it. Balance enforcement with pragmatism.
