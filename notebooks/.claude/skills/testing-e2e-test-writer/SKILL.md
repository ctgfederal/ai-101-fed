---
name: e2e-test-writer
description: Write end-to-end tests that simulate real user workflows from UI to database, validating complete feature functionality.
version: 1.0.0
---

# E2E Test Writer Skill

## Purpose
Write end-to-end tests that simulate real user workflows from UI to database, validating complete feature functionality.

## Inputs
- E2E test cases from test-case-generator
- User workflows from requirements
- E2E framework (Playwright, Cypress)

## Output
E2E test files with:
- Complete user workflows
- UI interactions
- Navigation and assertions
- Screenshots on failure
- Critical path validation

## Process
1. Search for existing page objects and test utilities to reuse
2. Import all required dependencies and helpers
3. Navigate to application
4. Interact with UI elements
5. Fill forms, click buttons
6. Validate navigation and state changes
7. Assert expected outcomes
8. **Run quality checks** (eslint/ruff) and fix all issues before completing

## Template

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Login Flow', () => {
  test('should successfully log in user with valid credentials', async ({ page }) => {
    // Arrange - Navigate to login page
    await page.goto('/login');

    // Act - Fill form and submit
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'ValidPassword123!');
    await page.click('button[type="submit"]');

    // Assert - Verify successful login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome, Test User');
    await expect(page.locator('.user-menu')).toBeVisible();
  });

  test('should show error message for invalid credentials', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'WrongPassword');
    await page.click('button[type="submit"]');

    // Assert
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
    await expect(page).toHaveURL('/login'); // Should stay on login page
    await expect(page.locator('.user-menu')).not.toBeVisible();
  });

  test('should navigate to password reset from login page', async ({ page }) => {
    // Arrange
    await page.goto('/login');

    // Act
    await page.click('text=Forgot password?');

    // Assert
    await expect(page).toHaveURL('/reset-password');
    await expect(page.locator('h1')).toContainText('Reset Password');
  });
});
```

## Best Practices
- Test critical user workflows only
- Keep E2E tests minimal (slow and brittle)
- Use stable selectors (data-testid)
- Add wait conditions for async operations
- Take screenshots on failure
- Run against stable test environment
- **Search for and reuse existing page objects** - avoid duplicating selectors
- **Import all dependencies** - never use undefined functions or variables
- **Run quality checker after writing tests** - ensure no linting/type errors
