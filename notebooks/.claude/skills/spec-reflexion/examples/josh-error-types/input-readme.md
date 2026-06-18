# Spec README — feature-123

## Overview

Add typed error responses to the public API.

## Decisions

- D-007: Use explicit error subclasses; reject Result<T, E>.

## Learnings

### Phase T-005 — Error wrapper rollout

**Implementation Insights**

| Phase | Insight | Category | Impact |
|---|---|---|---|
| T-005 | REQ-104 was renumbered after the merge from main | spec-reality-mismatch | Updated three downstream files |
| T-005 | The Result wrapper hides stack traces — debugging took 40 minutes longer | gotcha | Switched to explicit subclasses |

**What Worked**
- Explicit `ApiError extends Error` subclass; clear stack traces.

**What Didn't Work**
- Wrapping every controller return in `Result<T, E>` — too noisy.

### For /memorize (Global Learnings)

- [ ] Josh prefers explicit error types over Result wrappers — keeps stack traces clean and the type system honest. → type: `user`
- [ ] Always renumber REQ ids before merging branches → type: `feedback`
