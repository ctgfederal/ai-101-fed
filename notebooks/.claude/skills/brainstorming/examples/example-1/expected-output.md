---
topic: "AI-powered code review for solo devs"
date: 2026-02-14
status: complete
---

# AI-powered code review for solo devs

## Inspiration

Solo developers ship without code review and small mistakes compound. Existing tools (Sourcegraph, GitHub Copilot review) are team-focused, expensive, and require PRs. The trigger: a contractor friend shipped a regression that a 30-second review would have caught.

## Projects

1. CLI tool that reviews staged diffs locally. 2. Git pre-push hook. 3. Optional GitHub action for those who use PRs even solo.

## Audience

Indie hackers, contractors, solo founders. Pain: no second pair of eyes; time pressure; embarrassment when shipping bugs. Context: working on personal repos or single-author professional projects.

## Use Cases

- A solo dev runs `airev` before `git push`; gets 5 inline comments in 30 seconds.
- A contractor checks a feature branch against the project's conventions before client demo.
- A founder runs `airev --severity high` to surface only blocking issues during crunch.

## Desired Outcomes

Fewer regressions shipped to production. Faster ship cadence (review takes seconds, not minutes). Objective second eye replaces self-doubt loops. Confidence to ship after long days when self-review degrades.

## Guiding Principles

Speed over completeness — incomplete fast review beats thorough slow review. Suggestion over prescription — surface concerns, never block. Offline-first — no PII leaves the dev's machine without explicit opt-in. Convention-aware — read the project's tone, don't impose generic style.

## Constraints

Must run on consumer hardware (M2 MacBook, 16GB minimum). No PII to third parties without opt-in. Per-review latency budget: 30s for diffs under 500 LOC. Must work fully offline (local LLM).

## Scope

**In:** Static review of staged diffs; rule-based + LLM hybrid; CLI with optional git hook; convention learning from project history.

**Out:** Auto-fixing changes; full project linting (use existing linters); PR auto-merge; team workflows; CI integration as primary path; cloud-only operation.

## Open Questions

- Pricing model: free + paid LLM tier vs all-local vs sponsorship?
- Which local LLMs to support out of the box (llama, mistral, phi)?
- How to bootstrap convention learning on a fresh repo?

## Related Solutions

_(none yet — search solutions archive on first session)_
