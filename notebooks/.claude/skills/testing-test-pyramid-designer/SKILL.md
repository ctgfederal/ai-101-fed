---
name: test-pyramid-designer
description: Design balanced test distribution across unit, integration, and E2E tests following the test pyramid principle. Analyze feature complexity and determine optimal test counts for each layer.
version: 1.0.0
---

# Test Pyramid Designer Skill

## Purpose
Design balanced test distribution across unit, integration, and E2E tests following the test pyramid principle. Analyze feature complexity and determine optimal test counts for each layer.

## Inputs
- **Feature Specification**: Requirements, design, and tasks from `.claude/specs/{feature_name}/`
- **Codebase Analysis**: Components, modules, and architecture to test
- **Existing Tests**: Current test structure and conventions

## Output
Test pyramid specification with:
- Test distribution percentages (recommended: 70% unit, 20% integration, 10% E2E)
- Concrete test counts per layer
- Justification for distribution
- Mapping of components to test layers

## Test Pyramid Principles

### The Pyramid Shape
```
      /\
     /E2E\      10% - Slow, expensive, brittle
    /------\
   /  Int.  \   20% - Medium speed, test interactions
  /----------\
 /   Unit     \ 70% - Fast, cheap, focused
/--------------\
```

### Guidelines
- **Unit Tests (70%)**: Test individual functions, methods, components in isolation
- **Integration Tests (20%)**: Test module interactions, API endpoints, database operations
- **E2E Tests (10%)**: Test complete user workflows, critical paths

### Anti-Patterns to Avoid
- ❌ **Ice Cream Cone**: Too many E2E tests (slow, brittle)
- ❌ **Hourglass**: Too few integration tests (gap in coverage)
- ❌ **Inverted Pyramid**: Too few unit tests (slow feedback)

## Process

### Step 1: Analyze Feature Scope
1. Count components/functions to test:
   - UI components
   - Business logic functions
   - API endpoints
   - Database operations
   - Utilities and helpers
2. Identify complexity:
   - Simple (CRUD, getters/setters)
   - Moderate (business logic, validation)
   - Complex (algorithms, state machines)
3. Determine criticality:
   - Critical path features
   - Security-sensitive operations
   - High-traffic functionality

### Step 2: Calculate Test Distribution
1. **Unit Test Count**:
   - 1-3 tests per simple function
   - 3-7 tests per moderate function
   - 7-15 tests per complex function
   - Count all components, functions, methods

2. **Integration Test Count**:
   - 1-2 tests per API endpoint
   - 1-3 tests per module interaction
   - 1-2 tests per database operation

3. **E2E Test Count**:
   - 1 test per critical user workflow
   - 1-2 tests per major feature flow
   - Focus on happy path + 1-2 error scenarios

### Step 3: Validate Pyramid Shape
1. Calculate percentages:
   ```
   total_tests = unit + integration + e2e
   unit_pct = (unit / total_tests) * 100
   integration_pct = (integration / total_tests) * 100
   e2e_pct = (e2e / total_tests) * 100
   ```

2. Ensure pyramid shape:
   - Unit: 65-75%
   - Integration: 15-25%
   - E2E: 5-15%

3. Adjust if needed:
   - If too many E2E: Move some to integration
   - If too few unit: Add tests for edge cases
   - If unbalanced: Rebalance based on value

### Step 4: Map Components to Layers
Create mapping table:

| Component | Unit Tests | Integration Tests | E2E Tests | Total |
|-----------|------------|-------------------|-----------|-------|
| LoginForm | 8 | 0 | 0 | 8 |
| hashPassword | 5 | 0 | 0 | 5 |
| validateUser | 6 | 0 | 0 | 6 |
| /api/auth/login | 0 | 3 | 0 | 3 |
| User registration flow | 0 | 0 | 2 | 2 |
| **Total** | **35** | **10** | **5** | **50** |
| **Percentage** | **70%** | **20%** | **10%** | **100%** |

## Output Template

```markdown
## Test Pyramid

### Distribution
| Type | Count | Percentage | Justification |
|------|-------|------------|---------------|
| Unit | 35 | 70% | Testing 12 components/functions with avg 3 tests each |
| Integration | 10 | 20% | Testing 5 API endpoints + 3 module interactions |
| E2E | 5 | 10% | Testing 2 critical workflows + 3 error scenarios |
| **Total** | **50** | **100%** | Balanced pyramid for {feature-name} |

### Component Mapping

#### Unit Tests (35 tests)
- **LoginForm component** (8 tests):
  - Render with email/password fields
  - Validate email format
  - Validate password requirements
  - Show error on validation failure
  - Disable submit while loading
  - Clear form on success
  - Handle keyboard events
  - Accessibility checks

- **hashPassword function** (5 tests):
  - Hash with bcrypt and salt
  - Generate unique salt each time
  - Handle empty password
  - Handle very long password
  - Match hash verification

[Continue for all components...]

#### Integration Tests (10 tests)
- **POST /api/auth/login** (3 tests):
  - Return JWT for valid credentials
  - Return 401 for invalid credentials
  - Lock account after 5 failed attempts

[Continue for all endpoints...]

#### E2E Tests (5 tests)
- **Complete login flow** (2 tests):
  - Happy path: Enter credentials → Login → Redirect to dashboard
  - Error: Invalid credentials → Show error → Stay on login page

[Continue for all workflows...]

### Pyramid Validation
✅ Unit tests: 70% (target: 65-75%)
✅ Integration tests: 20% (target: 15-25%)
✅ E2E tests: 10% (target: 5-15%)
✅ Pyramid shape: VALID
```

## Adjustments for Different Feature Types

### API-Heavy Features
- Unit: 60-65% (less UI, more logic)
- Integration: 30-35% (many endpoints)
- E2E: 5-10% (API workflows)

### UI-Heavy Features
- Unit: 75-80% (many components)
- Integration: 10-15% (fewer endpoints)
- E2E: 10-15% (user interactions)

### Data Processing Features
- Unit: 70-75% (algorithms, transformations)
- Integration: 20-25% (database, file I/O)
- E2E: 5-10% (pipeline workflows)

## Validation Checklist
- ✅ Total test count is realistic (not too few, not too many)
- ✅ Pyramid shape maintained (more unit, fewer E2E)
- ✅ Critical paths covered at multiple layers
- ✅ Each component has appropriate test count
- ✅ E2E tests focus on user workflows, not implementation
- ✅ Integration tests cover module boundaries
- ✅ Unit tests cover edge cases and business logic

## Remember
- Favor more unit tests for faster feedback
- E2E tests are expensive - be selective
- Integration tests fill the gap between unit and E2E
- Adjust distribution based on feature characteristics
- Quality over quantity - every test should add value
