---
name: mock-generator
description: Generate mock implementations of external dependencies, services, and APIs for isolated unit testing.
version: 1.0.0
---

# Mock Generator Skill

## Purpose
Generate mock implementations of external dependencies, services, and APIs for isolated unit testing.

## Inputs
- Dependencies to mock (from imports)
- Interface/type definitions
- Expected behaviors

## Output
Mock files with:
- Jest/Vitest mock implementations
- MSW handlers for API mocking
- Stub responses
- Configurable behaviors

## Templates

### Service Mock
```typescript
// tests/mocks/emailService.mock.ts
import { IEmailService } from '../../src/services/IEmailService';

export const mockEmailService: jest.Mocked<IEmailService> = {
  send: jest.fn().mockResolvedValue({
    messageId: 'mock-msg-123',
    status: 'sent',
  }),
  sendBatch: jest.fn().mockResolvedValue([]),
  verifyEmail: jest.fn().mockResolvedValue(true),
};

export const resetEmailServiceMock = () => {
  mockEmailService.send.mockClear();
  mockEmailService.sendBatch.mockClear();
  mockEmailService.verifyEmail.mockClear();
};
```

### API Mock (MSW)
```typescript
// tests/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      email: 'test@example.com',
      name: 'Test User',
    });
  }),

  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json();
    if (body.password === 'valid') {
      return HttpResponse.json({ token: 'mock-token' });
    }
    return HttpResponse.json({ error: 'Invalid' }, { status: 401 });
  }),
];
```

## Best Practices
- Mock at module boundaries
- Provide realistic responses
- Make mocks configurable
- Reset mocks between tests
- Document mock behavior
