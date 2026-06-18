---
name: integration-test-writer
description: Write integration tests that verify module interactions, API endpoints, and database operations with real or test dependencies.
version: 1.0.0
---

# Integration Test Writer Skill

## Purpose
Write integration tests that verify module interactions, API endpoints, and database operations with real or test dependencies.

## Inputs
- Integration test cases from test-case-generator
- API endpoints and services to test
- Database schema and models
- Integration test framework (Supertest, @testing-library, pytest)

## Output
Integration test files with:
- Test database setup/teardown
- Real HTTP requests to APIs
- Database operations validation
- Module interaction tests
- Proper cleanup after tests

## Process
1. Search for existing test helpers and fixtures to reuse
2. Import all required models, types, and utilities
3. Set up test database/services
4. Seed test data
5. Write tests with real requests/operations
6. Validate responses and side effects
7. Add cleanup/teardown
8. **Run quality checks** (ruff/eslint) and fix all issues before completing

## Template

```typescript
// tests/integration/auth.test.ts
import request from 'supertest';
import { app } from '../../src/app';
import { setupTestDatabase, teardownTestDatabase, seedUsers } from '../helpers/database';

describe('POST /api/auth/login', () => {
  beforeAll(async () => {
    await setupTestDatabase();
    await seedUsers();
  });

  afterAll(async () => {
    await teardownTestDatabase();
  });

  it('should return JWT token for valid credentials', async () => {
    // Arrange
    const credentials = {
      email: 'test@example.com',
      password: 'ValidPassword123!',
    };

    // Act
    const response = await request(app)
      .post('/api/auth/login')
      .send(credentials);

    // Assert
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('token');
    expect(response.body.token).toMatch(/^eyJ/); // JWT format
    expect(response.body.user).toMatchObject({
      email: credentials.email,
    });
  });

  it('should return 401 for invalid credentials', async () => {
    // Arrange
    const credentials = {
      email: 'test@example.com',
      password: 'WrongPassword',
    };

    // Act
    const response = await request(app)
      .post('/api/auth/login')
      .send(credentials);

    // Assert
    expect(response.status).toBe(401);
    expect(response.body.error).toBe('Invalid credentials');
  });
});
```

## Best Practices
- Use test database (not production)
- Clean up after each test
- Seed necessary data
- Test real interactions
- Validate side effects (DB changes, emails sent)
- Use transactions for rollback
- **Search for and reuse existing test helpers** - avoid duplicating utilities
- **Import all dependencies** - never use undefined functions or variables
- **Run quality checker after writing tests** - ensure no linting/type errors
