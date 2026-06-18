# Learning Types

A promoted learning becomes a typed memory file. Pick exactly one of the four
types. The type controls **how Claude treats the content** in future sessions
and **how it groups in the index**.

## `feedback`

What the user explicitly told Claude to do (or stop doing). Hard-edge directives
that should change Claude's behaviour.

**Examples**
- "Don't use aspirational language in ISO 9001 manuals."
- "Always include a TL;DR at the top of policy docs."
- "Stop adding emoji to engineering docs."

**Heuristic** — verbatim or near-verbatim from the user, phrased as a rule.

## `project`

Decisions or facts about a specific project / system / repo. Useful only inside
that project's universe but stable across sessions.

**Examples**
- "`/plan-next-week-health` uses the `superhuman-diet` skill, not `nutrition-programming`."
- "Catalog imports live in `pipelines/catalog/` and are scheduled by Airflow."
- "We standardised on Postgres for all new services."

**Heuristic** — references a specific project name, file path, or system. Not a
general best practice.

## `reference`

Stable factual knowledge with no behavioural directive. Things you'd look up
again rather than memorise.

**Examples**
- "Anthropic's Sonnet 4.6 1M-context context window costs 1.6× the 200K SKU at the head and 2× past 200K input tokens."
- "AWS Lambda max execution time is 15 minutes."
- "The MoSCoW prioritisation values are exactly: Must, Should, Could, Won't."

**Heuristic** — pure information. No "should" or "we" attached.

## `user`

Stable preferences and patterns *about the user themselves* — Josh's style, how
Josh writes, decisions Josh tends to make. Cross-cutting; survives projects.

**Examples**
- "Josh prefers explicit error types over Result wrappers."
- "Josh writes in short declarative sentences; no qualifiers."
- "Josh runs `/quality` before every commit."

**Heuristic** — about the *human*, not the project.

## Picking when it's ambiguous

If the learning is...
- a directive to Claude     → `feedback`
- about a specific repo/sys → `project`
- a fact you'd Google again → `reference`
- about Josh as a person    → `user`

When two fit, pick the **narrower** one (`feedback` > `project` > `user` > `reference`).
Narrower types surface earlier and apply with more confidence.
