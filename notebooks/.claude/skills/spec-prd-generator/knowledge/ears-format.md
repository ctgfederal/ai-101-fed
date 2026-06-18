# EARS Format

EARS (Easy Approach to Requirements Syntax) — every functional requirement is one of five patterns. Pick the smallest pattern that fits.

| Pattern | Template | Example |
|---|---|---|
| **Ubiquitous** | The system SHALL `<action>`. | The system SHALL log every authentication event. |
| **Event-driven** | WHEN `<event>` THEN the system SHALL `<response>`. | WHEN a user clicks "Search" THEN the system SHALL return results within 200ms. |
| **State-driven** | WHILE `<state>` the system SHALL `<action>`. | WHILE the user is on the search page the system SHALL show typeahead suggestions. |
| **Optional** | WHERE `<condition>` the system SHALL `<action>`. | WHERE a user has saved searches the system SHALL show them in the sidebar. |
| **Complex** | IF `<precondition>` THEN the system SHALL `<response>`. | IF the search index is rebuilding THEN the system SHALL return cached results. |

## Picking a pattern

- The action is always true while the system runs → **Ubiquitous**.
- The action is triggered by a discrete event → **Event-driven**.
- The action is continuous during a state → **State-driven**.
- The action only applies in a feature/configuration variant → **Optional**.
- The action depends on a precondition that may or may not hold → **Complex**.

## Antipatterns

- "User can search." — not EARS; rewrite as "WHEN a user submits a query THEN the system SHALL ..."
- "The system should be fast." — not testable; rewrite with a measurable predicate.
- Combining two patterns in one requirement — split into two REQs.
- Using "may" or "might" — EARS uses SHALL exclusively.
