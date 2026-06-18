---
name: tech-debt-tracker
description: Track, prioritize, and manage technical debt items systematically.
version: 1.0.0
---

# Tech Debt Tracker Skill

## Purpose
Track, prioritize, and manage technical debt items systematically.

## Inputs
- **Action**: add, list, prioritize, detail, update, resolve
- **Item Details**: For add/update operations
- **Filters**: For list operations (priority, impact, location)

## Output
- Tech debt items with metadata
- Priority scores
- Recommendations for remediation
- Trend analysis

## Tech Debt Item Structure

```json
{
  "id": "TD-{number}",
  "title": "Short description",
  "description": "Detailed explanation",
  "location": "file/directory path",
  "impact": "low|medium|high",
  "effort": "small|medium|large",
  "priority": "low|medium|high|critical",
  "priorityScore": 0-15,
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD",
  "tags": ["architecture", "performance", "security"],
  "relatedADR": "ADR-XXX",
  "estimatedHours": 0-100,
  "assignedTo": "agent-name",
  "status": "identified|planned|in-progress|resolved"
}
```

## Priority Calculation

```
Priority Score = (Impact × 3) + (Urgency × 2) - (Effort)

Impact (1-5):
5 = Critical (system down, security breach)
4 = High (major feature broken, significant performance)
3 = Medium (feature partially broken, noticeable issues)
2 = Low (minor issues, cosmetic problems)
1 = Trivial (nice-to-have improvements)

Urgency (1-5):
5 = Must fix now (production issue)
4 = Fix this sprint (blocking work)
3 = Fix next sprint (impacting development)
2 = Fix this quarter (accumulating debt)
1 = Fix when convenient (minor debt)

Effort (1-5):
5 = Very large (> 40 hours)
4 = Large (20-40 hours)
3 = Medium (8-20 hours)
2 = Small (2-8 hours)
1 = Trivial (< 2 hours)

Priority Ranges:
12-15: Critical (stop and fix now)
9-11: High (plan for next sprint)
5-8: Medium (backlog, address within quarter)
1-4: Low (revisit quarterly)
```

## Operations

### Add Tech Debt

```typescript
{
  "action": "add",
  "item": {
    "title": "Refactor authentication service",
    "description": "Auth service has mixed concerns...",
    "location": "src/services/auth.ts",
    "impact": "high",
    "effort": "medium",
    "tags": ["architecture", "security"]
  }
}

// Calculates priority score
// Assigns TD number
// Adds to tech-debt.json
```

### List Tech Debt

```typescript
{
  "action": "list",
  "filters": {
    "priority": "high",
    "tags": ["security"]
  }
}

// Returns filtered list
// Sorted by priority score
```

### Prioritize All Items

```typescript
{
  "action": "prioritize"
}

// Recalculates all priority scores
// Re-sorts items
// Identifies items needing attention
```

### Get Item Details

```typescript
{
  "action": "detail",
  "id": "TD-001"
}

// Returns full item details
// Related ADRs
// Resolution history
```

### Update Item

```typescript
{
  "action": "update",
  "id": "TD-001",
  "changes": {
    "impact": "critical",
    "urgency": 5
  }
}

// Updates fields
// Recalculates priority
```

### Resolve Item

```typescript
{
  "action": "resolve",
  "id": "TD-001",
  "resolution": "Refactored auth service into separate concerns",
  "pr": "PR-456"
}

// Marks as resolved
// Records resolution details
// Archives item
```

## Tech Debt Categories

### Architecture Debt
- Mixed concerns
- Missing abstractions
- Tight coupling
- Violated patterns

### Performance Debt
- Slow queries
- Memory leaks
- Inefficient algorithms
- Missing caching

### Security Debt
- Outdated dependencies
- Missing auth checks
- SQL injection risks
- Weak encryption

### Testing Debt
- Missing tests
- Flaky tests
- Low coverage
- Hard-to-test code

### Documentation Debt
- Missing docs
- Outdated docs
- Unclear APIs
- No examples

### Code Quality Debt
- Code duplication
- Complex functions
- Magic numbers
- Poor naming

## Storage Format

File: `architecture/tech-debt.json`

```json
{
  "items": [
    {
      "id": "TD-001",
      "title": "Refactor authentication service",
      "description": "Current auth service mixes authentication, authorization, and session management. Should be split into separate concerns.",
      "location": "src/services/auth.ts",
      "impact": "high",
      "effort": "medium",
      "urgency": 4,
      "priority": "high",
      "priorityScore": 11,
      "created": "2025-10-15",
      "updated": "2025-10-18",
      "tags": ["architecture", "security"],
      "relatedADR": "ADR-023",
      "estimatedHours": 16,
      "status": "identified"
    }
  ],
  "stats": {
    "total": 15,
    "critical": 1,
    "high": 3,
    "medium": 8,
    "low": 3,
    "totalEstimatedHours": 240
  },
  "history": [
    {
      "id": "TD-000",
      "title": "Legacy API endpoints",
      "resolvedDate": "2025-10-10",
      "resolution": "Migrated to new API structure"
    }
  ]
}
```

## Trend Analysis

Track over time:
- Total debt items
- Priority distribution
- Resolution rate
- Average age of items
- Debt by category

## Recommendations

Based on current debt:

```markdown
## Tech Debt Recommendations

**Immediate Action Required** (Critical):
- TD-007: Replace deprecated crypto library (SECURITY)
  Impact: High, Effort: Small, Score: 14
  Action: Schedule for today

**Next Sprint** (High):
- TD-001: Refactor authentication service
  Impact: High, Effort: Medium, Score: 11
  Action: Plan for next sprint

**This Quarter** (Medium):
- TD-012: Split monolithic UserService
  Impact: High, Effort: Large, Score: 8
  Action: Add to quarterly goals

**Trend**: Debt increasing by 2 items/month
**Recommendation**: Dedicate 20% of sprint capacity to debt reduction
```

## Integration Points

### During Spec Creation
- design-researcher checks for new debt creation
- Documents potential debt in design

### During Code Review
- Reviewers can flag new debt
- Auto-creates tech debt items

### During Sprint Planning
- TPM reviews high-priority debt
- Plans debt remediation tasks

### During Architecture Review
- principal-engineer assesses debt impact
- Updates priority scores

## Remember

Tech debt is not inherently bad - it's a trade-off. The key is:
- ✅ Track it consciously
- ✅ Prioritize systematically
- ✅ Address it strategically
- ✅ Don't let it accumulate unchecked
