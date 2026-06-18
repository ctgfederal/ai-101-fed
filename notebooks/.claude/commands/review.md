---
description: "Post-implementation review with parallel specialist agent swarms. Spawns security, architecture, testing, performance, and clean code reviewers simultaneously."
argument-hint: "spec ID (e.g., 001), feature-name, or 'last' for most recent spec"
allowed-tools: ["Task"]
version: 3.0.0
last-updated: 2026-02-02
---

# /review - Swarm-Based Code Review

**Specification**: $ARGUMENTS

## Coding Identity

Apply the **principled-coder** framework (`@agents/principled-coder.md`) as the review rubric. Review agents must verify the implementation against all four pillars in order:

1. **Simplicity** — is this the simplest thing that works? Flag clever one-liners, junk-drawer utilities, speculative abstractions, dead code.
2. **Modularity** — do changes respect TUI / commands / CLI / teams / agents / run boundaries? Flag cross-module leakage, circular deps, shared mutable state.
3. **Security** — no secrets in code/logs, trust-boundary validation, config-gated posture, least privilege, audit logs present. Flag anything that breaks the on-prem/air-gapped path.
4. **Scalability** — stateless handlers, idempotency, bounded queues, backpressure, horizontal-scale friendly. Flag ad-hoc locks, unbounded memory, per-instance state.

A PR **fails review** if it violates any pillar, regardless of functional correctness. When pillars conflict, resolve in order above.

## Overview

Spawns parallel specialist review agents to analyze implementation from multiple perspectives simultaneously. Combines findings for comprehensive quality gate.

## How It Works

```
Load Spec & Implementation
   ↓
Search Solutions Archive (.claude/solutions/)
   ↓
Spawn Parallel Review Swarm:
   ├─ security-engineer (OWASP, vulnerabilities, secrets)
   ├─ architect-reviewer (patterns, boundaries, SDD compliance)
   ├─ code-reviewer (clean code, DRY, SOLID, readability)
   ├─ code-simplifier (simplify, clarify, reduce complexity)
   ├─ coverage-analyzer (test coverage, gap analysis)
   ├─ performance-engineer (N+1, memory, bottlenecks)
   ├─ qa-expert (edge cases, error handling)
   └─ compliance-auditor (standards, regulations if applicable)
   ↓
Collect & Synthesize Findings
   ↓
Generate Post-Deploy Monitoring Plan
   ↓
Generate ADRs (architecture decisions)
   ↓
Capture Learnings (spec-reflexion)
   ↓
Promote to Memory (spec-processor)
   ↓
Git Merge (if all critical checks pass)
   ↓
Offer /compound (document solutions discovered)
```

## Execution

### Phase 1: Load Spec & Solutions Context

```
Task(
  subagent_type: "spec-loader",
  description: "Load spec for review",
  prompt: "Load specification: $ARGUMENTS

  1. Locate spec by ID, name, or path
  2. Get list of all files changed in implementation
  3. Load PRD for requirement verification
  4. Load SDD for architecture verification
  5. Identify test files vs implementation files
  6. Search .claude/solutions/ for relevant past solutions:
     - grep -rl tags matching technologies used
     - grep -rl modules matching affected components
     - Surface known pitfalls and patterns

  Return:
  - spec_path
  - changed_files[]
  - test_files[]
  - prd_requirements[]
  - sdd_architecture
  - relevant_solutions[]"
)
```

### Phase 2a: Wave 1 — Blocking Reviewers (4 IN PARALLEL)

Wave 1 runs all potentially-blocking reviewers first. If any fail, Wave 2 can be skipped.

```
# Security Review (BLOCKING: critical vulns)
Task(
  subagent_type: "security-engineer",
  description: "Security audit",
  run_in_background: true,
  prompt: "Security review for spec: {spec_path}

  Files to review: {changed_files}

  Analyze:
  1. OWASP Top 10 vulnerabilities
  2. Authentication/authorization implementation
  3. Input validation and sanitization
  4. Secret/credential exposure
  5. Dependency vulnerabilities (npm audit, pip-audit)
  6. SQL injection, XSS, CSRF risks
  7. Secure communication (TLS, encryption)
  8. Rate limiting and DoS protection

  Severity levels: Critical, High, Medium, Low, Info

  Output JSON:
  {
    'vulnerabilities': [],
    'recommendations': [],
    'critical_count': n,
    'passed': bool
  }"
)

# Test Coverage Analysis (BLOCKING: <80% coverage)
Task(
  subagent_type: "coverage-analyzer",
  description: "Coverage analysis",
  run_in_background: true,
  prompt: "Coverage analysis for spec: {spec_path}

  Implementation files: {changed_files}
  Test files: {test_files}

  Analyze:
  1. Line coverage percentage
  2. Branch coverage percentage
  3. Uncovered critical paths
  4. Missing edge case tests
  5. Integration test coverage
  6. Error path coverage
  7. Business-critical code coverage
  8. Gap prioritization by impact

  Output JSON:
  {
    'line_coverage': n%,
    'branch_coverage': n%,
    'critical_gaps': [],
    'recommended_tests': [],
    'passed': bool (>80% line coverage)
  }"
)

# QA Expert Review (BLOCKING: missing PRD reqs)
Task(
  subagent_type: "qa-expert",
  description: "QA edge case review",
  run_in_background: true,
  prompt: "QA review for spec: {spec_path}

  PRD requirements: {prd_requirements}
  Implementation files: {changed_files}

  Analyze:
  1. All PRD requirements implemented
  2. Edge cases handled
  3. Error messages user-friendly
  4. Graceful degradation
  5. Input boundary conditions
  6. Null/undefined handling
  7. Concurrent access scenarios
  8. Rollback/recovery paths

  Output JSON:
  {
    'requirements_covered': [],
    'requirements_missing': [],
    'edge_cases_missing': [],
    'passed': bool
  }"
)

# Clean Code Review (core quality)
Task(
  subagent_type: "code-reviewer",
  description: "Clean code review",
  run_in_background: true,
  prompt: "Clean code review for spec: {spec_path}

  Files to review: {changed_files}

  Analyze:
  1. DRY violations (duplicated code)
  2. SOLID principles adherence
  3. Function/method length and complexity
  4. Naming conventions
  5. Code readability
  6. Error handling patterns
  7. Comments quality (not too many, not too few)
  8. Magic numbers/strings
  9. Dead code
  10. Consistent formatting

  Output JSON:
  {
    'violations': [],
    'improvements': [],
    'complexity_issues': [],
    'passed': bool
  }"
)
```

**Collect Wave 1 results.** Read all 4 background agent output files.

**Short-circuit check:** If any blocking reviewer FAILed (critical security vuln, <80% coverage, missing PRD requirements), STOP and report failures. Do NOT proceed to Wave 2.

### Phase 2b: Wave 2 — Advisory Reviewers (4 IN PARALLEL)

Only runs if Wave 1 passed all blocking checks.

```
# Architecture Review
Task(
  subagent_type: "architect-reviewer",
  description: "Architecture review",
  run_in_background: true,
  prompt: "Architecture review for spec: {spec_path}

  SDD to verify against: {sdd_architecture}
  Files to review: {changed_files}

  Analyze:
  1. Component boundaries respected
  2. Dependency direction correct
  3. Patterns match SDD specification
  4. No inappropriate coupling
  5. Proper abstraction layers
  6. Scalability considerations
  7. Maintainability assessment
  8. Technical debt introduced

  Output JSON:
  {
    'deviations_from_sdd': [],
    'concerns': [],
    'tech_debt_items': [],
    'adrs_needed': [],
    'passed': bool
  }"
)

# Code Simplification
Task(
  subagent_type: "code-simplifier",
  description: "Code simplification",
  run_in_background: true,
  prompt: "Code simplification review for spec: {spec_path}

  Files to review: {changed_files}

  Analyze recently modified code for:
  1. Unnecessary complexity and nesting
  2. Redundant abstractions and dead code
  3. Unclear variable/function naming
  4. Nested ternaries (replace with switch/if-else)
  5. Overly compact one-liners that sacrifice readability
  6. Inconsistent patterns across modified files
  7. Opportunities to consolidate related logic
  8. Comments describing obvious code

  Apply project coding standards from CLAUDE.md.
  Preserve all existing functionality.

  Output JSON:
  {
    'simplifications_applied': [{file, line, description}],
    'simplifications_suggested': [{file, line, description, risk}],
    'files_reviewed': n,
    'files_modified': n,
    'passed': bool
  }"
)

# Performance Review
Task(
  subagent_type: "performance-engineer",
  description: "Performance review",
  run_in_background: true,
  prompt: "Performance review for spec: {spec_path}

  Files to review: {changed_files}

  Analyze:
  1. N+1 query patterns
  2. Unnecessary database calls
  3. Memory leaks potential
  4. Blocking operations in async code
  5. Large payload handling
  6. Caching opportunities missed
  7. Inefficient algorithms (O(n²) when O(n) possible)
  8. Resource cleanup (connections, handles)

  Output JSON:
  {
    'issues': [],
    'optimizations': [],
    'severity': 'high|medium|low',
    'passed': bool
  }"
)

# Tech Debt Assessment
Task(
  subagent_type: "principal-engineer",
  description: "Tech debt assessment",
  run_in_background: true,
  prompt: "Tech debt assessment for spec: {spec_path}

  Files to review: {changed_files}

  Analyze:
  1. TODOs and FIXMEs introduced
  2. Temporary workarounds
  3. Missing abstractions
  4. Deprecated patterns used
  5. Documentation gaps
  6. Test shortcuts
  7. Configuration hardcoding
  8. Refactoring opportunities

  Use architecture-tech-debt-tracker skill.

  Output JSON:
  {
    'debt_items': [],
    'priority': 'high|medium|low',
    'estimated_impact': 'string',
    'remediation_suggestions': []
  }"
)
```

**Collect Wave 2 results.** Read all 4 background agent output files.

### Phase 3: Synthesize Findings

```
Task(
  subagent_type: "post-implementation-review",
  description: "Synthesize review findings",
  prompt: "Synthesize findings from review swarm:

  Collect results from all background agents:
  - security-engineer: {security_result}
  - architect-reviewer: {architecture_result}
  - code-reviewer: {code_result}
  - code-simplifier: {simplification_result}
  - coverage-analyzer: {coverage_result}
  - performance-engineer: {performance_result}
  - qa-expert: {qa_result}
  - principal-engineer: {tech_debt_result}

  1. Aggregate all findings by severity
  2. Identify blocking issues (critical security, <60% coverage)
  3. Generate unified review report
  4. Create action items list
  5. Determine PASS/FAIL status

  Blocking criteria:
  - ANY critical security vulnerability → FAIL
  - Coverage < 60% → FAIL
  - Missing PRD requirements → FAIL
  - Build broken → FAIL

  Non-blocking (log and continue):
  - Medium/low security issues
  - Architecture concerns
  - Code quality improvements
  - Code simplification suggestions
  - Performance optimizations
  - Tech debt items

  Output:
  - review_status: PASS|FAIL
  - blocking_issues: []
  - action_items: []
  - full_report: {}"
)
```

### Phase 4: Generate ADRs

```
Task(
  subagent_type: "architect-reviewer",
  description: "Generate ADRs",
  prompt: "Generate Architecture Decision Records for: {spec_path}

  Based on architecture review findings:
  {architecture_result.adrs_needed}

  For each significant decision:
  1. Create ADR in standard format
  2. Document context, decision, consequences
  3. List alternatives considered
  4. Add to SDD.md Architecture Decisions section

  Use architecture-adr-generator skill."
)
```

### Phase 5: Capture Learnings & Promote

```
Task(
  subagent_type: "spec-processor",
  description: "Capture and promote learnings",
  prompt: "Process review findings for memory promotion:

  All review findings: {synthesized_report}

  1. Extract globally-useful learnings:
     - Patterns that worked well
     - Anti-patterns discovered
     - Conventions established
     - Decisions made
  2. Update spec README.md with review findings
  3. Filter out project-specific items
  4. Promote to native memory (write typed files in ~/.claude/projects/<cwd>/memory/, update MEMORY.md)

  Use spec-reflexion skill for learning capture."
)
```

### Phase 5.5: Post-Deploy Monitoring Plan

Include a monitoring plan in the review report:

```
Based on implementation analysis, generate:

1. **Key Metrics to Watch** (first 48 hours)
   - Error rates for new endpoints/components
   - Response time baselines
   - Resource utilization changes

2. **Alerts to Configure**
   - Error rate thresholds
   - Latency spikes
   - Resource limits

3. **Rollback Triggers**
   - Conditions that warrant immediate rollback
   - Rollback procedure steps

4. **Verification Checklist**
   - [ ] Feature works in production
   - [ ] No error rate increase
   - [ ] Performance within budget
   - [ ] No unexpected side effects
```

This section is included in the PR description when created.

### Phase 6: Git Operations (If PASS)

```
Task(
  subagent_type: "git-workflow-manager",
  description: "Complete git workflow",
  prompt: "Execute git workflow for spec: {spec_path}

  Review status: {review_status}

  If PASS:
  1. Commit any review fixes
  2. If all phases complete:
     - Merge feature branch to develop
     - Push develop
     - Merge develop to master
     - Push master
     - Return to develop
  3. Clean up feature branch

  If FAIL:
  1. Do NOT merge
  2. Report blocking issues
  3. Require fixes before re-running /review"
)
```

## Review Agent Responsibilities

| Agent | Focus Area | Blocking If |
|-------|------------|-------------|
| security-engineer | OWASP, vulns, secrets | Critical vuln found |
| architect-reviewer | Patterns, boundaries, SDD | N/A (advisory) |
| code-reviewer | Clean code, SOLID, DRY | N/A (advisory) |
| code-simplifier | Clarity, complexity reduction | N/A (advisory) |
| coverage-analyzer | Test coverage gaps | < 60% coverage |
| performance-engineer | N+1, memory, bottlenecks | N/A (advisory) |
| qa-expert | Requirements, edge cases | PRD requirements missing |
| principal-engineer | Tech debt assessment | N/A (advisory) |

## Output

**Review Report includes:**
- Security audit results
- Architecture compliance
- Code quality assessment
- Coverage analysis
- Performance findings
- QA validation
- Tech debt inventory
- Post-deploy monitoring plan
- ADRs generated
- Learnings promoted
- Solutions archive references (if any matched)

**Final Status:**
- PASS: All blocking criteria met, merged to develop/master
- FAIL: Blocking issues found, requires fixes

**Next Steps:**
- If PASS: Code is merged. Run `/compound` to document any non-trivial solutions discovered during implementation.
- If FAIL: Fix issues and re-run `/review`.
