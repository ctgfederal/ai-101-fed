# Agent Categories and Trigger Keywords

Use this map to expand a user's task description into the keyword list
fed to `match_agents.py`. Each row gives a category, the kind of work it
covers, and the keywords most likely to surface its agents.

## Frontend

- **Examples**: `frontend-developer`, `react-specialist`, `vue-expert`,
  `nextjs-developer`, `ui-designer`, `flutter-expert`.
- **Trigger keywords**: `frontend`, `ui`, `component`, `react`, `vue`,
  `next`, `nextjs`, `tailwind`, `accessibility`, `mobile`, `flutter`,
  `form`, `state`, `storybook`.

## Backend / API

- **Examples**: `backend-developer`, `api-designer`, `graphql-architect`,
  `websocket-engineer`, `microservices-architect`, `fullstack-developer`.
- **Trigger keywords**: `backend`, `api`, `rest`, `graphql`, `endpoint`,
  `service`, `microservice`, `websocket`, `realtime`, `auth`, `middleware`.

## Database

- **Examples**: `database-optimizer`, `database-administrator`,
  `postgres-pro`, `sql-pro`.
- **Trigger keywords**: `database`, `db`, `sql`, `query`, `index`,
  `schema`, `migration`, `postgres`, `mysql`, `mongodb`, `redis`.

## AI / LLM / ML

- **Examples**: `llm-architect`, `ai-engineer`, `nlp-engineer`,
  `machine-learning-engineer`, `mlops-engineer`, `prompt-engineer`.
- **Trigger keywords**: `llm`, `ai`, `ml`, `machine-learning`, `model`,
  `embedding`, `rag`, `vector`, `prompt`, `langchain`, `langgraph`,
  `langsmith`, `nlp`, `inference`, `training`.

## DevOps / Infrastructure

- **Examples**: `devops-engineer`, `cloud-architect`, `kubernetes-specialist`,
  `terraform-engineer`, `platform-engineer`, `sre-engineer`.
- **Trigger keywords**: `devops`, `ci`, `cd`, `pipeline`, `kubernetes`,
  `k8s`, `terraform`, `aws`, `azure`, `gcp`, `docker`, `helm`, `slo`,
  `sre`, `observability`.

## Quality / Security

- **Examples**: `test-automator`, `qa-expert`, `security-engineer`,
  `security-auditor`, `code-reviewer`, `accessibility-tester`,
  `performance-engineer`.
- **Trigger keywords**: `test`, `tests`, `tdd`, `coverage`, `qa`,
  `security`, `pentest`, `audit`, `vuln`, `review`, `lint`, `a11y`,
  `accessibility`, `performance`.

## Language Specialists

- **Examples**: `python-pro`, `javascript-pro`, `typescript-pro`,
  `rust-engineer`, `go-engineer`.
- **Trigger keywords**: `python`, `javascript`, `js`, `typescript`,
  `ts`, `rust`, `go`, `golang`.

## Writing / Content

- **Examples**: `josh-writer`, `legendary-copywriter`, `technical-writer`,
  `nlp-engineer`.
- **Trigger keywords**: `copy`, `blog`, `tweet`, `thread`, `email`,
  `landing`, `documentation`, `tutorial`, `release-notes`.

## Research / Analysis

- **Examples**: `codebase-analyzer`, `codebase-locator`,
  `codebase-pattern-finder`, `web-search-researcher`.
- **Trigger keywords**: `research`, `analyze`, `audit`, `find`, `locate`,
  `search`, `pattern`, `discovery`.

## How to expand a task to keywords

1. Identify the **primary domain** (frontend/backend/db/etc.) → 1 keyword.
2. Identify the **technology** (react/postgres/k8s/etc.) → 1 keyword.
3. Identify the **task type** (test/refactor/design/build) → 1 keyword.
4. Add 1–3 nouns specific to the work (e.g., `form`, `endpoint`, `migration`).

Aim for 3–6 keywords. Too few → low recall. Too many → noisy ranking.
