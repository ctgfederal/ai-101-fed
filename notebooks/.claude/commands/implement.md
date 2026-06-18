---
description: "Execute implementation with parallel specialist agent swarms. Spawns appropriate agents based on task requirements for maximum velocity."
argument-hint: "spec-id [phase] (e.g., '001' or '001 3' or 'user-auth')"
allowed-tools: ["Task", "Read", "Write", "Edit", "Bash", "Grep", "Glob", "TaskCreate", "TaskUpdate", "AskUserQuestion"]
version: 3.1.0
last-updated: 2026-04-18
---

> **Sub-agent policy:** Sub-agents ARE allowed during /implement (workflow-enforcement.md updated 2026-04-18). Spawn specialist swarms for parallel work; verify outputs by reading changed files; do NOT trust agent self-reports as completion proof.

# /implement - Swarm-Based Implementation

**Specification**: $ARGUMENTS

## Coding Identity

Apply the **principled-coder** framework (`@agents/principled-coder.md`) to every line of code written. Specialist agents spawned by this command inherit these four pillars in order:

1. **Simplicity** — boring patterns, works out of the box, readable cold; no premature abstraction
2. **Modularity** — respect domain boundaries (TUI, commands, CLI, teams, agents, run); a single task must not cross them
3. **Security** — no secrets in code or logs; validate at trust boundaries; config-gated open vs locked posture
4. **Scalability** — stateless handlers, idempotent operations, bounded queues; concurrency-safe primitives only

TDD is mandatory: test first, verify it fails for the right reason, minimal code to pass, refactor. When priorities conflict, resolve in this order.

## Overview

Spawns parallel specialist agent swarms to execute implementation plans. Analyzes PLAN tasks and delegates to appropriate specialists simultaneously.

## How It Works

```
Load Spec (spec-loader)
   ↓
Analyze Tasks → Categorize by specialist type
   ↓
Spawn Parallel Agent Swarms:
   ├─ test-implementation-agent (all test tasks)
   ├─ backend-developer (API/service tasks)
   ├─ frontend-developer (UI/component tasks)
   ├─ database-administrator (DB/migration tasks)
   ├─ fullstack-developer (integrated tasks)
   ├─ security-engineer (auth/security tasks)
   ├─ api-designer (endpoint design tasks)
   └─ ... (other specialists as needed)
   ↓
Coordinate Results (parallel-coordinator)
   ├─ Detect file collisions
   ├─ Execute in waves if conflicts
   └─ Merge all changes
   ↓
Phase Validation + Reflexion
   ↓
Advance to next phase or complete
```

## Execution

### Phase 1: Load & Analyze Spec

```
Task(
  subagent_type: "spec-loader",
  description: "Load and validate spec",
  prompt: "Load specification: $ARGUMENTS

  1. Use spec-init.sh to locate spec
  2. Validate PRD, SDD, PLAN exist
  3. Parse all tasks from PLAN.md/PLAN.json
  4. Categorize each task by specialist type:
     - 'test': test-implementation-agent
     - 'api', 'service', 'backend': backend-developer
     - 'ui', 'component', 'frontend': frontend-developer
     - 'db', 'migration', 'schema': database-administrator
     - 'auth', 'security': security-engineer
     - 'endpoint', 'route': api-designer
     - 'mixed', 'fullstack': fullstack-developer
  5. Group tasks by phase
  6. Identify parallel execution opportunities

  Return:
  - spec_path
  - phases with categorized tasks
  - specialist_assignments (task_id → agent_type)
  - parallel_groups (tasks with no file conflicts)"
)
```

### Phase 2: Spawn Specialist Swarm

For each phase, spawn all required specialists IN PARALLEL:

```
# Spawn ALL specialists simultaneously - they work in parallel!
# Example for a phase with API, UI, and DB tasks:

Task(
  subagent_type: "test-implementation-agent",
  description: "Write tests for phase {N}",
  run_in_background: true,
  prompt: "Write failing tests for these tasks: {test_tasks}

  TDD RED phase - tests must fail initially.
  Use spec-execution skill for TDD procedures.
  Output test files created and verification of RED state."
)

Task(
  subagent_type: "backend-developer",
  description: "Implement API tasks",
  run_in_background: true,
  prompt: "Implement these API/service tasks: {api_tasks}

  WAIT for tests to be written first (coordinate via files).
  Implement minimal code to pass tests.
  Use existing patterns from codebase.
  Output files changed and test status."
)

Task(
  subagent_type: "frontend-developer",
  description: "Implement UI tasks",
  run_in_background: true,
  prompt: "Implement these UI/component tasks: {ui_tasks}

  Follow existing component patterns.
  Ensure accessibility and responsiveness.
  Output files changed and test status."
)

Task(
  subagent_type: "database-administrator",
  description: "Implement DB tasks",
  run_in_background: true,
  prompt: "Implement these database tasks: {db_tasks}

  Create migrations, update schemas.
  Ensure rollback capability.
  Output files changed and migration status."
)

Task(
  subagent_type: "security-engineer",
  description: "Implement security tasks",
  run_in_background: true,
  prompt: "Implement these security tasks: {security_tasks}

  Follow OWASP guidelines.
  Implement auth, validation, sanitization.
  Output files changed and security checklist."
)

# ... spawn additional specialists as needed based on task categorization
```

### Phase 3: Coordinate & Merge

```
Task(
  subagent_type: "parallel-coordinator",
  description: "Coordinate swarm results",
  prompt: "Coordinate results from specialist swarm for Phase {N}:

  Background agents spawned:
  {list of agent IDs and types}

  1. Wait for all agents to complete
  2. Collect results from each
  3. Check for file conflicts
  4. If conflicts: resolve with merge strategy
  5. Run compliance check on merged result
  6. Update PLAN.md checkboxes for completed tasks

  Use agent-delegation skill for coordination.

  Output:
  - tasks_completed by specialist
  - files_changed (merged)
  - conflicts_resolved
  - compliance_status"
)
```

### Phase 4: Validate & Reflexion

```
Task(
  subagent_type: "final-validator",
  description: "Phase validation",
  prompt: "Validate Phase {N} completion:

  1. Run compliance-check.sh
  2. Verify all tests pass (RED → GREEN complete)
  3. Verify PLAN.md tasks checked
  4. Update README.md with phase findings
  5. If all phases done: set spec status Complete

  Use spec-reflexion skill for learning capture."
)
```

## Specialist Agent Selection

| Task Keywords | Specialist Agent |
|---------------|------------------|
| test, spec, verify | test-implementation-agent |
| api, service, endpoint, route | backend-developer |
| api design, openapi, schema | api-designer |
| ui, component, page, view | frontend-developer |
| db, migration, schema, query | database-administrator |
| auth, security, permission | security-engineer |
| fullstack, integrated | fullstack-developer |
| graphql, resolver | graphql-architect |
| websocket, realtime | websocket-engineer |
| mobile, ios, android | mobile-developer |

## Parallel Execution Rules

1. **Tests First**: test-implementation-agent runs first, others wait for RED state
2. **No File Conflicts**: Tasks touching same files run in waves, not parallel
3. **Dependencies Respected**: If task B depends on task A, B waits
4. **Merge Strategy**: Last writer wins, with conflict resolution
5. **Validation Gate**: All parallel tasks must pass before phase advances

## Output

- All phase tasks implemented by appropriate specialists
- Tests passing (TDD cycle complete)
- PLAN.md checkboxes updated
- README.md updated with learnings
- Spec status updated

**Next Step**: Run `/review` for quality gate and memory promotion
