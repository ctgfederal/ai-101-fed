---
name: uat-workflow-patterns
description: Reusable Gherkin pattern templates for common user workflows including CRUD, authentication, wizards, search/filter, bulk operations, and file uploads.
version: 1.0.0
---

# UAT Workflow Patterns Skill

## Purpose

Provide standardized Gherkin pattern templates for common user workflows in browser-based UAT testing. These patterns ensure consistency across UAT scenarios and maximize step definition reuse.

## When to Use

- Generating UAT scenarios from user stories
- Writing browser-based acceptance tests
- Implementing Playwright-BDD feature files
- Creating reusable step definitions

## Pattern Categories

1. **CRUD Operations** - Create, Read, Update, Delete workflows
2. **Authentication** - Login, logout, registration, password reset, MFA
3. **Multi-Step Wizards** - Progress tracking, navigation, validation
4. **Search & Filter** - Text search, filters, pagination, sorting
5. **Bulk Operations** - Multi-select, bulk actions, confirmations
6. **File Operations** - Upload, drag-drop, progress, validation

---

## 1. CRUD Operations

### 1.1 Create Form Pattern

```gherkin
@uat @crud @create
Feature: Create {Entity}

  Background:
    Given I am logged in as "{role}"
    And I am on the "{entity}" management page

  @happy-path
  Scenario: Successfully create new {entity} with valid data
    When I click "Create New {Entity}"
    And I fill in the {entity} form:
      | field       | value          |
      | name        | Test {Entity}  |
      | description | Test description |
    And I submit the form
    Then I should see a success message "{Entity} created successfully"
    And I should be redirected to the {entity} list
    And the new {entity} should appear in the list

  @validation @error
  Scenario: Fail to create {entity} with missing required fields
    When I click "Create New {Entity}"
    And I submit the form without filling required fields
    Then I should see validation errors for required fields
    And the form should not be submitted
    And I should remain on the create page

  @validation @error
  Scenario: Fail to create {entity} with invalid data
    When I click "Create New {Entity}"
    And I fill in the {entity} form with invalid data:
      | field | value | expected_error         |
      | email | bad   | Invalid email format   |
      | phone | abc   | Invalid phone number   |
    And I submit the form
    Then I should see field-level validation errors
    And the form should not be submitted
```

**Step Definition Template:**
```typescript
When('I click {string}', async ({ page }, buttonText: string) => {
  await page.getByRole('button', { name: buttonText }).click();
});

When('I fill in the {word} form:', async ({ page }, entity: string, dataTable: DataTable) => {
  const formData = dataTable.rowsHash();
  for (const [field, value] of Object.entries(formData)) {
    await page.getByLabel(field, { exact: false }).fill(value);
  }
});

When('I submit the form', async ({ page }) => {
  await page.getByRole('button', { name: /submit|save|create/i }).click();
});

Then('I should see a success message {string}', async ({ page }, message: string) => {
  await expect(page.getByRole('alert')).toContainText(message);
});
```

### 1.2 Read List Pattern

```gherkin
@uat @crud @read @list
Feature: View {Entity} List

  Background:
    Given I am logged in as "{role}"

  @happy-path
  Scenario: View list of {entities} with data
    Given there are {count} {entities} in the system
    When I navigate to the {entity} list page
    Then I should see a list of {entities}
    And each {entity} should display:
      | column      |
      | name        |
      | status      |
      | created_at  |
    And pagination should be available if more than {page_size} items

  @empty-state
  Scenario: View empty state when no {entities} exist
    Given there are no {entities} in the system
    When I navigate to the {entity} list page
    Then I should see an empty state message
    And I should see a "Create {Entity}" call-to-action

  @navigation
  Scenario: Navigate to {entity} detail from list
    Given there is at least one {entity} in the system
    And I am on the {entity} list page
    When I click on a {entity} row
    Then I should be taken to the {entity} detail page
    And I should see the full {entity} information
```

### 1.3 Read Detail Pattern

```gherkin
@uat @crud @read @detail
Feature: View {Entity} Details

  Background:
    Given I am logged in as "{role}"
    And a {entity} with id "{id}" exists

  @happy-path
  Scenario: View {entity} detail page
    When I navigate to the {entity} detail page for "{id}"
    Then I should see the {entity} header with name
    And I should see all {entity} attributes:
      | attribute   |
      | name        |
      | description |
      | status      |
      | created_at  |
    And I should see action buttons for edit and delete

  @not-found
  Scenario: View non-existent {entity}
    When I navigate to a non-existent {entity} detail page
    Then I should see a 404 error page
    And I should see a link to return to the {entity} list
```

### 1.4 Update Form Pattern

```gherkin
@uat @crud @update
Feature: Update {Entity}

  Background:
    Given I am logged in as "{role}"
    And a {entity} with id "{id}" exists

  @happy-path
  Scenario: Successfully update {entity}
    When I navigate to the {entity} edit page for "{id}"
    Then the form should be pre-filled with existing data
    When I update the {entity} name to "{new_name}"
    And I save the changes
    Then I should see a success message "{Entity} updated successfully"
    And I should be redirected to the {entity} detail page
    And the {entity} should reflect the new values

  @cancel
  Scenario: Cancel {entity} update
    When I navigate to the {entity} edit page for "{id}"
    And I modify some fields
    And I click "Cancel"
    Then I should be redirected without saving
    And the {entity} should retain its original values

  @concurrent-edit
  Scenario: Handle concurrent edit conflict
    Given another user has modified the {entity}
    When I try to save my changes
    Then I should see a conflict warning
    And I should be given options to review or overwrite
```

### 1.5 Delete Pattern

```gherkin
@uat @crud @delete
Feature: Delete {Entity}

  Background:
    Given I am logged in as "{role}"
    And a {entity} with id "{id}" exists

  @happy-path
  Scenario: Successfully delete {entity} with confirmation
    When I am on the {entity} detail page for "{id}"
    And I click "Delete"
    Then I should see a confirmation dialog
    And the dialog should warn about permanent deletion
    When I confirm the deletion
    Then I should see a success message "{Entity} deleted"
    And I should be redirected to the {entity} list
    And the {entity} should no longer appear in the list

  @cancel
  Scenario: Cancel {entity} deletion
    When I am on the {entity} detail page for "{id}"
    And I click "Delete"
    And I cancel the confirmation dialog
    Then the {entity} should not be deleted
    And I should remain on the detail page

  @constraint
  Scenario: Prevent deletion of {entity} with dependencies
    Given the {entity} has dependent records
    When I try to delete the {entity}
    Then I should see an error message about dependencies
    And the {entity} should not be deleted
```

---

## 2. Authentication Flows

### 2.1 Login Pattern

```gherkin
@uat @auth @login
Feature: User Login

  Background:
    Given I am not logged in
    And I am on the login page

  @happy-path
  Scenario: Successful login with valid credentials
    When I enter my email "{email}"
    And I enter my password "{password}"
    And I click "Log in"
    Then I should be logged in successfully
    And I should be redirected to the dashboard
    And I should see my profile information in the header

  @error @invalid-credentials
  Scenario: Failed login with incorrect password
    When I enter my email "{email}"
    And I enter an incorrect password
    And I click "Log in"
    Then I should see an error message "Invalid email or password"
    And I should remain on the login page
    And the password field should be cleared

  @error @invalid-email
  Scenario: Failed login with non-existent email
    When I enter a non-registered email
    And I enter any password
    And I click "Log in"
    Then I should see an error message "Invalid email or password"
    And I should remain on the login page

  @security @lockout
  Scenario: Account locked after multiple failed attempts
    When I fail to login {max_attempts} times consecutively
    Then I should see an error message "Account temporarily locked"
    And I should see instructions to reset my password or wait

  @remember-me
  Scenario: Login with remember me option
    When I enter valid credentials
    And I check "Remember me"
    And I click "Log in"
    Then I should be logged in successfully
    And my session should persist after browser restart
```

**Step Definition Template:**
```typescript
Given('I am not logged in', async ({ page }) => {
  await page.context().clearCookies();
});

Given('I am on the login page', async ({ page }) => {
  await page.goto('/login');
});

When('I enter my email {string}', async ({ page }, email: string) => {
  await page.getByLabel('Email').fill(email);
});

When('I enter my password {string}', async ({ page }, password: string) => {
  await page.getByLabel('Password').fill(password);
});

Then('I should be logged in successfully', async ({ page }) => {
  await expect(page).not.toHaveURL('/login');
  await expect(page.getByTestId('user-menu')).toBeVisible();
});
```

### 2.2 Logout Pattern

```gherkin
@uat @auth @logout
Feature: User Logout

  Background:
    Given I am logged in as "{role}"

  @happy-path
  Scenario: Successful logout
    When I click on my profile menu
    And I click "Sign Out"
    Then I should be logged out
    And I should be redirected to the login page
    And I should not see my profile information

  @session
  Scenario: Session invalidated after logout
    When I log out
    And I navigate directly to a protected page
    Then I should be redirected to the login page
    And I should see a message to log in again
```

### 2.3 Registration Pattern

```gherkin
@uat @auth @registration
Feature: User Registration

  Background:
    Given I am not logged in
    And I am on the registration page

  @happy-path
  Scenario: Successful registration with valid data
    When I fill in the registration form:
      | field            | value              |
      | email            | newuser@example.com|
      | password         | SecurePass123!     |
      | confirm_password | SecurePass123!     |
      | name             | New User           |
    And I accept the terms of service
    And I submit the registration form
    Then I should see "Registration successful"
    And I should receive a verification email
    And I should be redirected to the email verification page

  @error @duplicate-email
  Scenario: Registration fails for existing email
    Given a user with email "{existing_email}" already exists
    When I try to register with email "{existing_email}"
    And I submit the registration form
    Then I should see an error message "Email already registered"
    And I should see a link to login or reset password

  @validation @password
  Scenario: Registration fails for weak password
    When I enter a password that doesn't meet requirements
    And I submit the registration form
    Then I should see password requirement errors:
      | requirement                    |
      | At least 8 characters          |
      | At least one uppercase letter  |
      | At least one number            |
      | At least one special character |

  @validation @password-match
  Scenario: Registration fails when passwords don't match
    When I enter different values for password and confirm password
    And I submit the registration form
    Then I should see an error "Passwords do not match"
```

### 2.4 Password Reset Pattern

```gherkin
@uat @auth @password-reset
Feature: Password Reset

  @request
  Scenario: Request password reset
    Given I am on the login page
    When I click "Forgot password?"
    And I enter my registered email "{email}"
    And I submit the reset request
    Then I should see "Password reset link sent"
    And I should receive a password reset email

  @reset
  Scenario: Reset password with valid token
    Given I have a valid password reset token
    When I click the reset link in my email
    And I enter a new valid password
    And I confirm the new password
    And I submit the password reset form
    Then I should see "Password updated successfully"
    And I should be redirected to the login page
    And I should be able to login with my new password

  @expired-token
  Scenario: Reset fails with expired token
    Given I have an expired password reset token
    When I click the reset link
    Then I should see an error "Reset link has expired"
    And I should be prompted to request a new reset link
```

### 2.5 MFA Pattern

```gherkin
@uat @auth @mfa
Feature: Multi-Factor Authentication

  @enrollment
  Scenario: Enroll in MFA with authenticator app
    Given I am logged in
    And MFA is not enabled for my account
    When I navigate to security settings
    And I click "Enable MFA"
    Then I should see a QR code for authenticator setup
    When I scan the QR code with my authenticator app
    And I enter the verification code from my app
    Then MFA should be enabled
    And I should see backup recovery codes
    And I should be prompted to save recovery codes

  @login
  Scenario: Login with MFA enabled
    Given MFA is enabled for my account
    When I enter valid credentials on login page
    And I click "Log in"
    Then I should be prompted for my MFA code
    When I enter a valid MFA code
    Then I should be logged in successfully

  @recovery
  Scenario: Login with recovery code
    Given MFA is enabled for my account
    And I don't have access to my authenticator
    When I complete the login form
    And I click "Use recovery code instead"
    And I enter a valid recovery code
    Then I should be logged in successfully
    And that recovery code should be invalidated
```

---

## 3. Multi-Step Wizards

### 3.1 Multi-Step Wizard Pattern

```gherkin
@uat @wizard
Feature: {Wizard Name} Wizard

  Background:
    Given I am logged in as "{role}"
    And I am starting the {wizard} wizard

  @progress
  Scenario: Progress through wizard steps
    Then I should see step 1 of {total_steps}
    And the progress indicator should show step 1 active
    When I complete step 1 with valid data
    And I click "Next"
    Then I should be on step 2
    And the progress indicator should show step 2 active
    And step 1 should be marked as completed

  @navigation @back
  Scenario: Navigate back to previous steps
    Given I have completed steps 1 and 2
    And I am on step 3
    When I click "Back"
    Then I should be on step 2
    And my previously entered data should be preserved
    When I click "Back" again
    Then I should be on step 1
    And my data from step 1 should still be there

  @validation
  Scenario: Validation prevents advancing with invalid data
    Given I am on step 2
    When I enter invalid data for step 2
    And I click "Next"
    Then I should see validation errors
    And I should remain on step 2
    And the progress indicator should not advance

  @save-draft
  Scenario: Save wizard progress as draft
    Given I have completed steps 1 and 2
    When I click "Save as Draft"
    Then my progress should be saved
    And I should see a confirmation message
    When I return to the wizard later
    Then I should be able to resume from step 3

  @completion
  Scenario: Complete wizard successfully
    Given I have completed all steps
    When I review the summary on the final step
    And I click "Submit"
    Then I should see a success message
    And the {entity} should be created with all wizard data
    And I should be redirected to the {entity} detail page
```

**Step Definition Template:**
```typescript
Given('I am starting the {word} wizard', async ({ page }, wizardName: string) => {
  await page.goto(`/wizards/${wizardName}`);
});

Then('I should see step {int} of {int}', async ({ page }, current: number, total: number) => {
  await expect(page.getByTestId('step-indicator')).toContainText(`Step ${current} of ${total}`);
});

When('I complete step {int} with valid data', async function(step: number) {
  const stepData = this.testData.wizard[`step${step}`];
  await fillWizardStep(this.page, stepData);
});

Then('my previously entered data should be preserved', async function() {
  const previousData = this.testData.wizard.previousStep;
  for (const [field, value] of Object.entries(previousData)) {
    await expect(this.page.getByLabel(field)).toHaveValue(value);
  }
});
```

---

## 4. Search & Filter

### 4.1 Text Search Pattern

```gherkin
@uat @search @text
Feature: Text Search

  Background:
    Given I am logged in
    And there are multiple {entities} in the system
    And I am on the {entity} list page

  @happy-path
  Scenario: Search by text query
    When I enter "{search_term}" in the search field
    And I click "Search" or press Enter
    Then I should see only {entities} matching "{search_term}"
    And the search term should be highlighted in results
    And the result count should be updated

  @no-results
  Scenario: Search with no matching results
    When I search for "nonexistent_item_xyz"
    Then I should see "No results found"
    And I should see suggestions to modify my search

  @clear
  Scenario: Clear search and show all results
    Given I have an active search for "{search_term}"
    When I clear the search field
    Then all {entities} should be displayed
    And the result count should be restored
```

### 4.2 Advanced Filters Pattern

```gherkin
@uat @search @filter
Feature: Advanced Filtering

  Background:
    Given I am logged in
    And there are {entities} with various attributes
    And I am on the {entity} list page

  @single-filter
  Scenario: Filter by single criterion
    When I select "{value}" from the "{field}" filter
    Then only {entities} with {field} = "{value}" should be shown
    And the active filter should be displayed as a chip/tag
    And the result count should reflect the filter

  @multiple-filters
  Scenario: Filter by multiple criteria
    When I apply the following filters:
      | field    | value      |
      | status   | Active     |
      | category | Category A |
      | date     | Last 30 days |
    Then only {entities} matching ALL criteria should be shown
    And all active filters should be displayed

  @clear-filters
  Scenario: Clear all filters
    Given I have applied multiple filters
    When I click "Clear all filters"
    Then all filters should be removed
    And all {entities} should be shown

  @save-filter
  Scenario: Save filter preset
    Given I have applied a complex filter combination
    When I click "Save filter"
    And I name the filter "{preset_name}"
    Then the filter should be saved
    And I should be able to apply it later from saved filters
```

### 4.3 Pagination Pattern

```gherkin
@uat @search @pagination
Feature: Pagination

  Background:
    Given I am logged in
    And there are more than {page_size} {entities}
    And I am on the {entity} list page

  @navigation
  Scenario: Navigate between pages
    Then I should see page 1 of results
    And I should see pagination controls
    When I click "Next" or page 2
    Then I should see page 2 of results
    And the URL should reflect the current page

  @page-size
  Scenario: Change page size
    When I select "{new_size}" from the page size dropdown
    Then {new_size} items should be displayed per page
    And pagination should adjust accordingly

  @direct-navigation
  Scenario: Go to specific page
    When I enter page number "{page}" in the page input
    And I press Enter
    Then I should be taken to page {page}
```

### 4.4 Sorting Pattern

```gherkin
@uat @search @sort
Feature: Sorting

  Background:
    Given I am logged in
    And there are multiple {entities}
    And I am on the {entity} list page

  @ascending
  Scenario: Sort by column ascending
    When I click on the "{column}" column header
    Then results should be sorted by {column} ascending
    And the column header should show an ascending indicator

  @descending
  Scenario: Sort by column descending
    Given results are sorted by {column} ascending
    When I click on the "{column}" column header again
    Then results should be sorted by {column} descending
    And the column header should show a descending indicator

  @multi-column
  Scenario: Sort by multiple columns
    When I sort by "{primary_column}"
    And I shift-click "{secondary_column}"
    Then results should be sorted by both columns
```

---

## 5. Bulk Operations

### 5.1 Multi-Select Pattern

```gherkin
@uat @bulk @select
Feature: Multi-Select

  Background:
    Given I am logged in
    And there are at least 10 {entities}
    And I am on the {entity} list page

  @individual
  Scenario: Select individual items
    When I check the checkbox for 3 {entities}
    Then the selection count should show "3 selected"
    And the bulk action toolbar should appear

  @select-all-page
  Scenario: Select all items on current page
    When I check the "Select all" checkbox in the header
    Then all visible {entities} on the page should be selected
    And I should see an option to "Select all {total} items"

  @select-all-results
  Scenario: Select all items across all pages
    When I check "Select all"
    And I click "Select all {total} items"
    Then all {entities} across all pages should be selected
    And the selection count should show "{total} selected"

  @deselect
  Scenario: Deselect items
    Given I have selected 5 {entities}
    When I uncheck one {entity}
    Then the selection count should show "4 selected"
    When I click "Clear selection"
    Then no {entities} should be selected
```

### 5.2 Bulk Delete Pattern

```gherkin
@uat @bulk @delete
Feature: Bulk Delete

  Background:
    Given I am logged in as "{role}" with delete permission
    And there are at least 10 {entities}
    And I am on the {entity} list page

  @happy-path
  Scenario: Bulk delete selected items
    Given I have selected 5 {entities}
    When I click "Delete selected"
    Then I should see a confirmation dialog
    And the dialog should show "Delete 5 items?"
    When I confirm the deletion
    Then the 5 {entities} should be deleted
    And I should see a success message "5 items deleted"
    And the list should be updated

  @cancel
  Scenario: Cancel bulk delete
    Given I have selected 5 {entities}
    When I click "Delete selected"
    And I cancel the confirmation
    Then no {entities} should be deleted
    And my selection should be preserved

  @partial-failure
  Scenario: Handle partial delete failure
    Given I have selected {entities} including some with dependencies
    When I attempt bulk delete
    Then {entities} without dependencies should be deleted
    And I should see a message about items that couldn't be deleted
    And the failed items should be listed
```

### 5.3 Bulk Export Pattern

```gherkin
@uat @bulk @export
Feature: Bulk Export

  Background:
    Given I am logged in
    And there are {entities} to export
    And I am on the {entity} list page

  @export-selected
  Scenario: Export selected items
    Given I have selected 10 {entities}
    When I click "Export selected"
    And I choose "{format}" format
    Then a file should be downloaded
    And the file should contain 10 {entities}
    And the file format should be {format}

  @export-all
  Scenario: Export all items
    When I click "Export all"
    And I choose "{format}" format
    Then a file should be downloaded
    And the file should contain all {entities}

  @export-filtered
  Scenario: Export filtered results
    Given I have applied filters showing 25 {entities}
    When I click "Export results"
    Then the export should contain only filtered {entities}
```

---

## 6. File Operations

### 6.1 Single Upload Pattern

```gherkin
@uat @upload @single
Feature: Single File Upload

  Background:
    Given I am logged in
    And I am on a page with file upload

  @happy-path
  Scenario: Upload valid file
    When I click "Choose file"
    And I select a valid file "{filename}"
    Then the file name should be displayed
    When I click "Upload"
    Then I should see upload progress
    And the upload should complete successfully
    And the file should appear in my files

  @validation @type
  Scenario: Reject invalid file type
    When I try to upload a file with invalid type
    Then I should see an error "File type not allowed"
    And the accepted file types should be listed
    And the file should not be uploaded

  @validation @size
  Scenario: Reject file exceeding size limit
    When I try to upload a file larger than {max_size}
    Then I should see an error "File exceeds maximum size"
    And the maximum allowed size should be shown
    And the file should not be uploaded
```

### 6.2 Multiple Upload Pattern

```gherkin
@uat @upload @multiple
Feature: Multiple File Upload

  Background:
    Given I am logged in
    And I am on a page supporting multiple file upload

  @happy-path
  Scenario: Upload multiple files
    When I select 3 valid files
    Then all 3 files should be listed
    When I click "Upload all"
    Then I should see progress for each file
    And all files should upload successfully
    And all files should appear in my file list

  @partial
  Scenario: Handle partial upload failure
    When I select 3 files including one invalid file
    And I click "Upload all"
    Then valid files should upload successfully
    And the invalid file should show an error
    And I should be able to retry the failed upload

  @remove-before-upload
  Scenario: Remove file before uploading
    Given I have selected 3 files
    When I click remove on one file
    Then only 2 files should remain in the queue
```

### 6.3 Drag and Drop Pattern

```gherkin
@uat @upload @drag-drop
Feature: Drag and Drop Upload

  Background:
    Given I am logged in
    And I am on a page with drag-drop upload zone

  @happy-path
  Scenario: Upload via drag and drop
    When I drag a valid file over the drop zone
    Then the drop zone should highlight
    And I should see "Drop file here"
    When I drop the file
    Then the file should start uploading
    And the file should appear when complete

  @multiple
  Scenario: Drop multiple files
    When I drag 3 files to the drop zone
    And I drop them
    Then all 3 files should be queued
    And upload should start automatically
    And progress should show for each file

  @invalid
  Scenario: Drop invalid file type
    When I drop an invalid file type
    Then I should see an error message
    And the file should be rejected
    And the drop zone should return to normal state
```

### 6.4 Upload Progress Pattern

```gherkin
@uat @upload @progress
Feature: Upload Progress

  Background:
    Given I am uploading a large file

  @progress-indicator
  Scenario: Show upload progress
    Then I should see a progress bar
    And the progress percentage should update
    And the estimated time remaining should be shown

  @cancel
  Scenario: Cancel upload in progress
    When I click "Cancel upload"
    Then the upload should stop
    And the partial file should not be saved
    And the upload queue should be cleared

  @retry
  Scenario: Retry failed upload
    Given the upload failed due to network error
    When I click "Retry"
    Then the upload should restart
    And resume from where it left off if supported
```

---

## Pattern Usage Guidelines

### Selecting Patterns

1. **Match to user story type**:
   - "As a user, I want to create..." → CRUD Create Pattern
   - "As a user, I want to log in..." → Auth Login Pattern
   - "As a user, I want to search..." → Search Pattern

2. **Combine patterns for complex flows**:
   - Registration + Email Verification + Login = Onboarding workflow
   - Search + Filter + Bulk Delete = Data management workflow

3. **Customize placeholders**:
   - Replace `{entity}` with actual entity name (User, Product, Order)
   - Replace `{role}` with actual user role
   - Replace `{field}` with actual field names

### Tag Conventions

| Tag | Purpose |
|-----|---------|
| `@uat` | All UAT tests |
| `@P0`, `@P1`, `@P2` | Priority levels |
| `@happy-path` | Success scenarios |
| `@error` | Error handling |
| `@validation` | Input validation |
| `@crud`, `@auth`, `@wizard`, `@search`, `@bulk`, `@upload` | Category |

### Step Definition Organization

```
tests/uat/steps/
├── common/
│   ├── navigation.steps.ts   # Given I am on...
│   ├── authentication.steps.ts # Given I am logged in...
│   └── assertions.steps.ts   # Then I should see...
├── patterns/
│   ├── crud.steps.ts
│   ├── auth.steps.ts
│   ├── wizard.steps.ts
│   ├── search.steps.ts
│   ├── bulk.steps.ts
│   └── upload.steps.ts
└── features/
    └── {feature}.steps.ts    # Feature-specific overrides
```
