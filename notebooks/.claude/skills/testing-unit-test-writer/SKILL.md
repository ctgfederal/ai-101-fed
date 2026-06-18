---
name: unit-test-writer
description: Write focused unit tests for individual functions, methods, and components following AAA pattern and best practices.
version: 1.0.0
---

# Unit Test Writer Skill

## Purpose
Write focused unit tests for individual functions, methods, and components following AAA pattern and best practices.

## Inputs
- Functions/components to test
- Test cases from test-case-generator
- Project test framework (Jest, Vitest, pytest, etc.)

## Output
Unit test files with:
- Descriptive test names
- AAA pattern (Arrange, Act, Assert)
- Mocked dependencies
- Edge case coverage
- Clear assertions

## Process
1. Create test file following project conventions
2. Search for existing mocks and test utilities to reuse
3. Import function/component and all dependencies
4. Mock external dependencies
5. Write tests using AAA pattern
6. Cover happy path, edge cases, errors
7. Use descriptive test names
8. **Run quality checks** (ruff/eslint) and fix all issues before completing

## Template

```typescript
// src/auth/__tests__/hashPassword.test.ts
import { hashPassword } from '../hashPassword';
import bcrypt from 'bcrypt';

jest.mock('bcrypt');

describe('hashPassword', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should hash password using bcrypt with 10 salt rounds', async () => {
    // Arrange
    const password = 'SecurePass123!';
    const expectedHash = '$2b$10$abcdef...';
    (bcrypt.hash as jest.Mock).mockResolvedValue(expectedHash);

    // Act
    const result = await hashPassword(password);

    // Assert
    expect(bcrypt.hash).toHaveBeenCalledWith(password, 10);
    expect(result).toBe(expectedHash);
  });

  it('should throw error when password is empty', async () => {
    // Arrange
    const password = '';

    // Act & Assert
    await expect(hashPassword(password)).rejects.toThrow('Password cannot be empty');
  });

  it('should handle very long passwords', async () => {
    // Arrange
    const password = 'a'.repeat(1000);
    const expectedHash = '$2b$10$xyz...';
    (bcrypt.hash as jest.Mock).mockResolvedValue(expectedHash);

    // Act
    const result = await hashPassword(password);

    // Assert
    expect(result).toBe(expectedHash);
  });
});
```

## Best Practices
- Test behavior, not implementation
- One assertion per test (when possible)
- Clear, descriptive test names
- Mock external dependencies
- Test edge cases and errors
- Keep tests independent
- Use beforeEach for setup, afterEach for cleanup
- **Search for and reuse existing mocks** - check test helpers/fixtures
- **Import all dependencies** - never use undefined functions or variables
- **Run quality checker after writing tests** - ensure no linting/type errors
- **Don't assign variables in pytest.raises()** - just call the function directly
