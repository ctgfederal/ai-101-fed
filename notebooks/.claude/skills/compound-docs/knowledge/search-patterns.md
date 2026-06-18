# How the solutions archive is searched

Other commands grep `.claude/solutions/` to find prior fixes. Knowing **how** they search dictates what makes a solution discoverable.

## Patterns in active use

### By tag (most common)
```bash
grep -rl "tags:.*activerecord" .claude/solutions/
grep -rl "tags:.*n+1" .claude/solutions/
```
Used by `/brainstorm` and `/build` when designing features that touch tagged technologies.

### By module
```bash
grep -rl "^module:.*BriefGenerator" .claude/solutions/
```
Used by `/specify` and `/review` when the active spec or PR touches a known module.

### By symptom keyword
```bash
grep -rli "timeout\|deadlock\|n+1" .claude/solutions/
```
Used by `/debug` and the four `/kaizen-*` commands when investigating a new instance of a familiar symptom.

### By category
Folder traversal — `ls .claude/solutions/performance-issues/` — is also common.

## Implications for authors

- **Tag the technology AND the pattern.** `[postgres, deadlock]` beats `[postgres]` or `[deadlock]` alone — both grep paths hit.
- **Quote the real error in `symptom`.** `grep -i` finds it later. Paraphrasing breaks retrieval.
- **Name the originating module exactly.** Camel-case it, match the codebase. Searchers use `^module:` to anchor.
- **Pick the best category — don't sprinkle.** A solution lives in one folder; cross-cutting concerns belong in `tags`.

## What does NOT help retrieval

- Long prose hidden in the body where grep can't anchor on a field name.
- Markdown emphasis around terms (`**N+1**` doesn't help; the plain word does).
- Synonyms in the title without being mirrored into tags.
