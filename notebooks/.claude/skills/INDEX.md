# Skills Registry

This index catalogs all skills available in `.claude/skills/`, organized by category. Each skill is a self-contained unit with templates, scripts, knowledge, and tests.

## Workflow Commands

Skills used by `/brainstorm`, `/build`, `/deepen`, `/specify`, `/implement`, `/review`:

| Skill | Version | Purpose | Triggers |
|-------|---------|---------|----------|
| [brainstorming](brainstorming/) | 3.0.0 | Explore WHY and FOR WHOM before design decisions | `/brainstorm`, "let's brainstorm" |
| [build-decisions](build-decisions/) | - | Walk through design decisions interactively | `/build` |
| [plan-deepener](plan-deepener/) | - | Enrich decisions with research in parallel | `/deepen` |
| [spec-prd-generator](spec-prd-generator/) | - | Generate Product Requirements Documents | `/specify` |
| [spec-sdd-generator](spec-sdd-generator/) | - | Generate Solution Design Documents | `/specify` |
| [spec-plan-generator](spec-plan-generator/) | - | Generate Implementation Plans | `/specify` |
| [spec-readme](spec-readme/) | - | Generate spec README with metadata | `/specify` |
| [spec-execution](spec-execution/) | - | Execute PLAN tasks with TDD swarm | `/implement` |
| [spec-validation](spec-validation/) | - | Validate spec quality (3-Cs check) | `/review` |
| [steering-docs-creator](steering-docs-creator/) | - | Create product/tech/structure docs | `/create-steering-docs` |

## Specification Management

Skills for managing the spec lifecycle:

| Skill | Purpose |
|-------|---------|
| [spec-compliance](spec-compliance/) | Check spec compliance |
| [spec-deviation](spec-deviation/) | Detect and document deviations |
| [spec-reflexion](spec-reflexion/) | Capture learnings from spec execution |
| [spec-requirement-tracer](spec-requirement-tracer/) | Trace requirements through implementation |
| [spec-task-validator](spec-task-validator/) | Validate task structure and completeness |

## Architecture & Design

Skills for architectural decisions and documentation:

| Skill | Purpose |
|-------|---------|
| [architecture-adr-generator](architecture-adr-generator/) | Generate Architecture Decision Records |
| [architecture-pattern-enforcer](architecture-pattern-enforcer/) | Enforce architectural patterns |
| [architecture-performance-budgeter](architecture-performance-budgeter/) | Set and track performance budgets |
| [architecture-tech-debt-tracker](architecture-tech-debt-tracker/) | Track technical debt |
| [architecture-technology-evaluator](architecture-technology-evaluator/) | Evaluate technology choices |

## Testing

Skills for test planning and generation:

| Skill | Purpose |
|-------|---------|
| [testing-coverage-gap-finder](testing-coverage-gap-finder/) | Identify coverage gaps |
| [testing-coverage-improver](testing-coverage-improver/) | Suggest coverage improvements |
| [testing-coverage-reporter](testing-coverage-reporter/) | Generate coverage reports |
| [testing-e2e-test-writer](testing-e2e-test-writer/) | Write end-to-end tests |
| [testing-fixture-planner](testing-fixture-planner/) | Plan test fixtures |
| [testing-gate-validator](testing-gate-validator/) | Validate test gates |
| [testing-integration-test-writer](testing-integration-test-writer/) | Write integration tests |
| [testing-metrics-collector](testing-metrics-collector/) | Collect test metrics |
| [testing-mock-generator](testing-mock-generator/) | Generate test mocks |
| [testing-quality-checker](testing-quality-checker/) | Check test quality |
| [testing-test-case-generator](testing-test-case-generator/) | Generate test cases |
| [testing-test-pyramid-designer](testing-test-pyramid-designer/) | Design test pyramid strategy |
| [testing-uat-workflow-patterns](testing-uat-workflow-patterns/) | UAT workflow patterns |
| [testing-unit-test-writer](testing-unit-test-writer/) | Write unit tests |

## Documentation

Skills for documentation and knowledge management:

| Skill | Purpose |
|-------|---------|
| [auto-documentation](auto-documentation/) | Generate documentation automatically |
| [compound-docs](compound-docs/) | Compound solutions into docs |

## Agent Coordination

Skills for multi-agent workflows:

| Skill | Purpose |
|-------|---------|
| [agent-delegation](agent-delegation/) | Delegate tasks to specialist agents |
| [swarm-delegation](swarm-delegation/) | Coordinate swarm execution |
| [workflow-agent-selector](workflow-agent-selector/) | Select appropriate agents |

---

## How to Use

Each skill follows the FOLDER · CONTRACT · SCRIPT · TEST pattern:

- **FOLDER**: Skill lives in its own directory with all artifacts
- **CONTRACT**: SKILL.md defines inputs, outputs, and behavior
- **SCRIPT**: Deterministic Python scripts for setup/validation
- **TEST**: Four test layers (unit, integration, smoke, evals)

Skills are invoked by commands in `.claude/commands/` or can be called directly when their triggers match user intent.