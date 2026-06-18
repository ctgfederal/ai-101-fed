---
name: fixture-planner
description: Plan test data requirements including fixtures, mocks, stubs, factories, and seed data for comprehensive test coverage.
version: 1.0.0
---

# Fixture Planner Skill

## Purpose
Plan test data requirements including fixtures, mocks, stubs, factories, and seed data for comprehensive test coverage.

## Inputs
- Test cases from test-case-generator
- Data models from design.md
- External dependencies from architecture

## Output
Test data plan specifying:
- Fixture files needed (JSON, CSV, SQL)
- Mock objects for dependencies
- Factory functions for test objects
- Seed data for integration tests
- Test data organization structure

## Process

### Step 1: Identify Data Entities
List all entities/models requiring test data:
- User accounts (various roles, states)
- Business objects (products, orders, etc.)
- Configuration data
- Lookup tables

### Step 2: Plan Fixtures
Create static data files for:
- Common test scenarios (valid user, admin, inactive user)
- Reference data (countries, categories)
- Sample responses from external APIs

### Step 3: Plan Mocks
Identify dependencies to mock:
- External APIs
- Email/SMS services
- Payment gateways
- File storage
- Third-party integrations

### Step 4: Plan Factories
Design factory functions for:
- Generating unique test objects
- Creating test data with specific attributes
- Bulk data generation
- Realistic fake data (using faker library)

### Step 5: Plan Seed Data
Determine database seed requirements:
- Minimal data for tests to run
- User accounts for authentication tests
- Sample data for query tests
- Relationship data for join tests

## Output Template

```markdown
## Test Data Plan

### Fixtures
**tests/fixtures/users.json**
- validUser: Standard user account
- adminUser: Administrator account
- inactiveUser: Inactive account
- unverifiedUser: Account pending email verification

**tests/fixtures/api-responses.json**
- successfulPayment: Valid payment gateway response
- failedPayment: Declined payment response

### Factories
**tests/factories/user.factory.ts**
```typescript
UserFactory.create() // Random user
UserFactory.createAdmin() // Admin user
UserFactory.createMany(10) // 10 users
UserFactory.withEmail(email) // Specific email
```

### Mocks
**tests/mocks/emailService.mock.ts**
- send(email, subject, body)
- sendBatch(emails)
- Returns: { messageId, status }

**tests/mocks/paymentGateway.mock.ts**
- processPayment(amount, token)
- Returns: { transactionId, status }

### Seed Data
**tests/fixtures/seed.sql**
```sql
INSERT INTO users VALUES (...);
INSERT INTO roles VALUES (...);
INSERT INTO permissions VALUES (...);
```

### Directory Structure
```
tests/
├── fixtures/
│   ├── users.json
│   ├── products.json
│   └── seed.sql
├── factories/
│   ├── user.factory.ts
│   └── product.factory.ts
└── mocks/
    ├── emailService.mock.ts
    └── paymentGateway.mock.ts
```
```

## Remember
- Plan for all test types (unit, integration, e2e)
- Use fixtures for static, predictable data
- Use factories for dynamic, randomized data
- Mock external dependencies to avoid real API calls
- Organize test data logically and keep it maintainable
